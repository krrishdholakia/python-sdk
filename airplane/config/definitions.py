import dataclasses
import datetime
import inspect
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import inflection
import typing_extensions
from docstring_parser import parse
from slugify import slugify  # type: ignore

from airplane.config.types import (
    SQL,
    ConfigVar,
    EnvVar,
    File,
    FuncT,
    InputParamTypes,
    LabeledOption,
    LongText,
    ParamConfig,
    ParamType,
    Resource,
    RuntimeType,
    Schedule,
)
from airplane.exceptions import (
    InvalidAnnotationException,
    InvalidTaskConfigurationException,
    UnsupportedDefaultTypeException,
)


@dataclasses.dataclass
class ParamDef:
    """Parameter definition"""

    # ParamDefs have a subset of types that are built in and serializable.
    ParamDefTypes = Union[str, int, float]
    ParamDefOptions = Union[
        List[LabeledOption[str]],
        List[LabeledOption[int]],
        List[LabeledOption[float]],
    ]

    # Represents the original function's argument name.
    # We need this in order to be able to map slug -> arg_name in case they differ.
    arg_name: str
    slug: str
    name: str
    type: ParamType
    description: Optional[str]
    default: Optional[ParamDefTypes]
    required: Optional[bool]
    options: Optional[ParamDefOptions]
    regex: Optional[str]

    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    DATETIME_MILLISECONDS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    def serialize_param(
        val: InputParamTypes,
    ) -> ParamDefTypes:
        """Transforms a general parameter into a format supported by parameter definition"""
        if isinstance(val, datetime.datetime):
            return val.strftime(ParamDef.DATETIME_FORMAT)
        if isinstance(val, datetime.date):
            return val.strftime(ParamDef.DATE_FORMAT)
        if isinstance(val, ConfigVar):
            return val.name
        return val


@dataclasses.dataclass
class TaskDef:
    """Task definition"""

    func: Callable[..., Any]
    slug: str
    name: str
    runtime: RuntimeType
    entrypoint_func: str
    description: Optional[str]
    require_requests: Optional[bool]
    allow_self_approvals: Optional[bool]
    timeout: Optional[int]
    constraints: Optional[Dict[str, str]]
    resources: Optional[List[Resource]]
    schedules: Optional[List[Schedule]]
    parameters: Optional[List[ParamDef]]
    env_vars: Optional[List[EnvVar]]

    def run(self, params: Dict[str, Any]) -> Any:
        """Execute task function from param dictionary"""
        func_args: Dict[str, Any] = {}
        for param in self.parameters or []:
            # If the user didn't provide a value for the parameter slug
            if param.slug not in params:
                # Fill in None values for optional parameters that aren't provided
                if not param.required:
                    func_args[param.arg_name] = None
                # Otherwise, we fall back to the function default arguments.
            elif param.type == "date":
                func_args[param.arg_name] = datetime.datetime.strptime(
                    params[param.slug], ParamDef.DATE_FORMAT
                ).date()
            elif param.type == "datetime":
                func_args[param.arg_name] = datetime.datetime.strptime(
                    params[param.slug],
                    ParamDef.DATETIME_MILLISECONDS_FORMAT
                    if "." in params[param.slug]
                    else ParamDef.DATETIME_FORMAT,
                )
            elif param.type == "upload":
                func_args[param.arg_name] = File(
                    id=params[param.slug]["id"],
                    url=params[param.slug]["url"],
                )
            elif param.type == "configvar":
                func_args[param.arg_name] = ConfigVar(
                    name=params[param.slug]["name"],
                    value=params[param.slug]["value"],
                )
            else:
                func_args[param.arg_name] = params[param.slug]

        return self.func(**func_args)

    @classmethod
    def build(
        cls,
        func: FuncT,
        runtime: RuntimeType,
        slug: Optional[str],
        name: Optional[str],
        description: Optional[str],
        require_requests: bool,
        allow_self_approvals: bool,
        timeout: int,
        constraints: Optional[Dict[str, str]],
        resources: Optional[List[Resource]],
        schedules: Optional[List[Schedule]],
        env_vars: Optional[List[EnvVar]],
    ) -> "TaskDef":
        """Construct a task definition from a function."""
        task_description = description
        if func.__doc__ is None:
            param_descriptions = {}
        else:
            docstring = parse(func.__doc__)
            param_descriptions = {
                param.arg_name: param.description for param in docstring.params
            }
            task_description = (
                description or docstring.long_description or docstring.short_description
            )
        type_hints = typing_extensions.get_type_hints(func, include_extras=True)
        sig = inspect.signature(func)
        parameters: List[ParamDef] = []
        for param in sig.parameters.values():
            type_hint = type_hints.get(param.name)
            if type_hint is None:
                raise InvalidAnnotationException(
                    prefix="Missing type annotation",
                    func_name=func.__name__,
                    param_name=param.name,
                )
            resolved_type, is_optional, param_config = _resolve_type(
                func.__name__, param.name, type_hint
            )
            if param_config is None:
                param_config = ParamConfig()

            if param.default is inspect.Signature.empty:
                default = None
            else:
                default = ParamDef.serialize_param(param.default)
                if isinstance(default, File):
                    raise UnsupportedDefaultTypeException(
                        "File defaults are not currently supported with inline code configuration."
                    )

            options: Optional[ParamDef.ParamDefOptions]
            if param_config.options is None:
                options = None
            else:
                options = []  # type: ignore
                for option in param_config.options:
                    if isinstance(option, LabeledOption):
                        labeled_option = LabeledOption(
                            label=option.label,
                            value=ParamDef.serialize_param(option.value),
                        )
                    else:
                        value = ParamDef.serialize_param(option)
                        labeled_option = LabeledOption(
                            label=str(value),
                            value=value,
                        )
                    options.append(labeled_option)  # type: ignore

            default_slug = make_slug(param.name)
            parameters.append(
                ParamDef(
                    arg_name=param.name,
                    # Parameter slug is the parameter's name in snakecase
                    slug=param_config.slug or default_slug,
                    name=param_config.name or inflection.humanize(default_slug),
                    type=_to_airplane_type(func.__name__, param.name, resolved_type),
                    description=param_config.description
                    or param_descriptions.get(param.name),
                    required=not is_optional,
                    default=default,
                    options=options,
                    regex=param_config.regex,
                )
            )

        def _check_duplicates(counter: Counter, duplicate_type: str) -> None:
            duplicates = [slug for slug, count in counter.items() if count > 1]
            if duplicates:
                raise InvalidTaskConfigurationException(
                    f"Function {func.__name__} has duplicate {duplicate_type} {duplicates}"
                )

        _check_duplicates(Counter([p.slug for p in parameters]), "parameter slugs")
        _check_duplicates(Counter([s.slug for s in schedules or []]), "schedule slugs")
        _check_duplicates(Counter([e.name for e in env_vars or []]), "env var names")

        # Convert schedule param values to the correct default types
        for schedule in schedules or []:
            if schedule.param_values is not None:
                for param_name, param_value in schedule.param_values.items():
                    if param_value is not None:
                        schedule.param_values[param_name] = ParamDef.serialize_param(
                            param_value
                        )

        # pylint: disable=protected-access
        default_slug = make_slug(func.__name__)
        return cls(
            func=func,
            runtime=runtime,
            slug=slug or default_slug,
            name=name or inflection.humanize(default_slug),
            description=task_description,
            require_requests=require_requests,
            allow_self_approvals=allow_self_approvals,
            timeout=timeout,
            constraints=constraints,
            schedules=schedules,
            resources=resources,
            parameters=parameters,
            env_vars=env_vars,
            entrypoint_func=func.__name__,
        )


def _resolve_type(
    func_name: str, param_name: str, type_hint: Any
) -> Tuple[Any, bool, Optional[ParamConfig]]:
    """Parses a parameter's type hint to extract its underlying type,
    whether it's optional, and a ParamConfig if provided."""
    origin_type = typing_extensions.get_origin(type_hint)
    if origin_type == Union:
        type_args = typing_extensions.get_args(type_hint)
        if len(type_args) != 2 or type_args[1] is not type(None):
            raise InvalidAnnotationException(
                prefix=f"Unsupported Union type `{type_hint}`",
                func_name=func_name,
                param_name=param_name,
            )
        return type_args[0], True, None
    if origin_type == typing_extensions.Annotated:
        type_args = typing_extensions.get_args(type_hint)
        param_configs = [t for t in type_args if isinstance(t, ParamConfig)]
        # Don't support multiple parameter configs within the same annotation.
        if len(param_configs) > 1:
            raise InvalidAnnotationException(
                prefix=f"Found multiple ParamConfig annotations `{type_hint}`",
                func_name=func_name,
                param_name=param_name,
            )
        param_config = param_configs[0] if param_configs else None
        underlying_type, is_optional, _ = _resolve_type(
            func_name, param_name, type_args[0]
        )
        return underlying_type, is_optional, param_config
    return type_hint, False, None


def _to_airplane_type(func_name: str, param_name: str, type_hint: Any) -> ParamType:
    if type_hint == str:
        return "shorttext"
    if type_hint == LongText:
        return "longtext"
    if type_hint == SQL:
        return "sql"
    if type_hint == bool:
        return "boolean"
    if type_hint == File:
        return "upload"
    if type_hint == int:
        return "integer"
    if type_hint == float:
        return "float"
    if type_hint == datetime.date:
        return "date"
    if type_hint == datetime.datetime:
        return "datetime"
    if type_hint == ConfigVar:
        return "configvar"
    raise InvalidAnnotationException(
        prefix=f"Invalid type annotation `{type_hint}`",
        func_name=func_name,
        param_name=param_name,
    )


def make_slug(string: str) -> str:
    """Turns a string into a slug"""
    for target, replacement in [
        ("‒", "_"),  # figure dash
        ("–", "_"),  # en dash
        ("—", "_"),  # em dash
        ("―", "_"),  # horizontal bar
        ("&", "_and_"),
        ("@", "_at_"),
        ("%", "_percent_"),
    ]:
        string = string.replace(target, replacement)
    return slugify(inflection.underscore(string)).replace("-", "_")[:50]
