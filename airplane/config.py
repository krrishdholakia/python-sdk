import dataclasses
import datetime
import functools
import inspect
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Union

import inflection
import typing_extensions
from docstring_parser import parse

from airplane.api.entities import Run
from airplane.exceptions import (
    InvalidAnnotationException,
    InvalidTaskConfigurationException,
    UnsupportedDefaultTypeException,
)
from airplane.params import (
    SERIALIZED_DATE_FORMAT,
    SERIALIZED_DATETIME_FORMAT,
    SERIALIZED_DATETIME_MILLISECONDS_FORMAT,
    LabeledOption,
    ParamConfig,
    ParamDefTypes,
    ParamType,
    ParamTypes,
    make_options,
    resolve_type,
    serialize_param,
    to_airplane_type,
)
from airplane.runtime import execute
from airplane.types import ConfigVar, File, FuncT, RuntimeType
from airplane.utils import make_slug


@dataclasses.dataclass(frozen=True)
class Resource:
    """Airplane resource attachment.

    Resources in Airplane allow users to configure connections to external systems
    like databases and APIs and use them in tasks and runbooks.
    https://docs.airplane.dev/resources/overview

    Attributes:
        slug:
            Resource identifier.
        alias:
            Alias to reference the resource. Defaults to resource slug.
    """

    slug: str
    alias: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class EnvVar:
    """Airplane environment variable.

    Environment variables allow users to configure constant values or reference
    config variables. They can be accessed via `os.getenv("MY_ENV_VAR_NAME")`.

    Attributes:
        name:
            Environment variable name.
        value:
            Set a constant value for the environment variable.
        config_var_name:
            Name of the config variable to use. Configs variables allow users
            to set team-wide values / secrets.
    """

    name: str
    value: Optional[str] = None
    config_var_name: Optional[str] = None

    def __post_init__(self) -> None:
        if "=" in self.name:
            raise InvalidTaskConfigurationException(
                f'Environment variable name {self.name} cannot contain "="'
            )
        if (self.config_var_name and self.value) or (
            not self.config_var_name and not self.value
        ):
            raise InvalidTaskConfigurationException(
                "Exactly one of `config_var_name` or `value` should be set"
            )


@dataclasses.dataclass(frozen=True)
class Schedule:
    """Airplane schedule definition.

    Schedules allow users to automatically run tasks on a recurring schedule.
    https://docs.airplane.dev/schedules/schedules

    Attributes:
        slug:
            Human-friendly identifier used for the schedule. Schedule slugs must be unique
            within an individual task / workflow.
        cron:
            Schedule cron expression, e.g.  "0 * * * *"
        name:
            Schedule name. Defaults to the slug.
        description:
            Schedule description displayed on the Airplane app.
        param_values:
            Dictionary of parameter name to parameter value used for the scheduled execution.
            All required parameters must be defined.
    """

    slug: str
    cron: str
    name: Optional[str] = None
    description: Optional[str] = None
    param_values: Optional[Dict[str, Optional[ParamTypes]]] = None


def task(
    slug: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    require_requests: bool = False,
    allow_self_approvals: bool = True,
    timeout: int = 3600,
    constraints: Optional[Dict[str, str]] = None,
    resources: Optional[List[Resource]] = None,
    schedules: Optional[List[Schedule]] = None,
    env_vars: Optional[List[EnvVar]] = None,
) -> Callable[[FuncT], Callable[..., Run]]:
    """Decorator used to define an Airplane task.

    This decorator inspects the decorated function to create an Airplane task. The task's parameters
    are deduced from the function's arguments and type hints.

    Additional parameter metadata can be provided by attaching an airplane.ParamConfig to a
    typing.Annotated typehint (for versions of Python prior to 3.9, typing_extensions.Annotated
    can be used).

    The following map enumerates the supported Python types and equivalent Airplane
    parameter types (Airplane parameter details https://docs.airplane.dev/platform/parameters)::

        str: short text
        airplane.LongText: long text
        airplane.SQL: SQL
        bool: boolean
        int: integer
        float: number
        airplane.File: file
        datetime.date: date
        datetime.datetime: datetime
        airplane.ConfigVar: config variable

    Example:
        Sample task::

            @airplane.task()
            def add_two_numbers(first_number: int, second_number: int) -> int:
                return first_number + second_number

        Sample task with parameter annotation::

            @airplane.task()
            def capitalize_string(
                input: Annotated[str, airplane.ParamConfig(name="User string")]
            ) -> str:
                return input.capitalize()
    Args:
        slug:
            Human-friendly identifier used to reference this task. Must be unique
            across tasks and workflows. Defaults to function name.
        name:
            Task name displayed on the Airplane app. Defaults to funcion name in sentence case.
        description:
            Task description displayed on the Airplane app. If not provided, the description
            will be pulled from the docstring of the decorated function.
        require_requests:
            Whether or not this task requires a request to execute.
        allow_self_approvals:
            Whether or not this task allows self approvals.
        timeout:
            How long a task can run (in seconds) for before it is automatically cancelled.
        constraints:
            Constraints for which agents are allowed to execute this task's runs, only
            applicable for users with self hosted agents.
        resources:
            Resources to attach to this task. Resources can be accessed through environment
            variables or built-ins. Resources accessed by this task must be explicitly attached
            in the task's definition.
        schedules:
            Schedules to attach to this task. Schedules allow users to automatically run
            task on a recurring schedule.
        env_vars:
            Enviornment variables to attach to this task. Environment variables allow users
            to configure constant values or reference config variables.
    """

    def decorator(func: FuncT) -> Callable[..., Run]:
        """Assigns an __airplane attribute to a function to mark it as an Airplane object"""

        config = TaskDef.build(
            func=func,
            runtime="",
            slug=slug,
            name=name,
            description=description,
            require_requests=require_requests,
            allow_self_approvals=allow_self_approvals,
            timeout=timeout,
            constraints=constraints,
            resources=resources,
            schedules=schedules,
            env_vars=env_vars,
        )

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Run:
            kwargs.update(zip(func.__code__.co_varnames, args))
            return execute(config.slug, kwargs)

        # pylint: disable=protected-access
        wrapped.__airplane = config  # type: ignore
        return wrapped

    return decorator


# ParamDefs have a subset of types that are built in and serializable.
ParamDefOptions = Union[
    List[LabeledOption[str]],
    List[LabeledOption[int]],
    List[LabeledOption[float]],
]


@dataclasses.dataclass(frozen=True)
class ParamDef:
    """Parameter definition"""

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


@dataclasses.dataclass(frozen=True)
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
                    params[param.slug], SERIALIZED_DATE_FORMAT
                ).date()
            elif param.type == "datetime":
                func_args[param.arg_name] = datetime.datetime.strptime(
                    params[param.slug],
                    SERIALIZED_DATETIME_MILLISECONDS_FORMAT
                    if "." in params[param.slug]
                    else SERIALIZED_DATETIME_FORMAT,
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
            resolved_type, is_optional, param_config = resolve_type(
                param.name,
                type_hint,
                func_name=func.__name__,
            )
            if param_config is None:
                param_config = ParamConfig()

            if param.default is inspect.Signature.empty:
                default = None
            else:
                default = serialize_param(param.default)
                if isinstance(default, File):
                    raise UnsupportedDefaultTypeException(
                        "File defaults are not currently supported with inline code configuration."
                    )
            if param_config.default is not None and param_config.default != default:
                raise InvalidTaskConfigurationException(
                    f"Function {func.__name__} contains an invalid default value configuration "
                    f"for parameter {param.name}. Default values should be set via the Python "
                    "native default function parameter syntax, e.g. "
                    '`def my_task(my_param: str = "default")` instead of inside `ParamConfig`.'
                )

            default_slug = make_slug(param.name)
            parameters.append(
                ParamDef(
                    arg_name=param.name,
                    # Parameter slug is the parameter's name in snakecase
                    slug=param_config.slug or default_slug,
                    name=param_config.name or inflection.humanize(default_slug),
                    type=to_airplane_type(param.name, resolved_type, func.__name__),
                    description=param_config.description
                    or param_descriptions.get(param.name),
                    required=not is_optional,
                    default=default,
                    options=make_options(param_config),
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
                        schedule.param_values[param_name] = serialize_param(param_value)

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
