import dataclasses
import datetime
from typing import Any, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, Union

from typing_extensions import Annotated, Literal, get_args, get_origin

from airplane.exceptions import InvalidAnnotationException
from airplane.types import SQL, ConfigVar, File, LongText

SERIALIZED_DATE_FORMAT = "%Y-%m-%d"
SERIALIZED_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
SERIALIZED_DATETIME_MILLISECONDS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


# Types users can provide for a parameter value.
InputParam = Union[
    str,
    LongText,
    SQL,
    bool,
    File,
    int,
    float,
    datetime.date,
    datetime.datetime,
    ConfigVar,
]

PromptParamTypes = Union[
    Type[str],
    Type[LongText],
    Type[SQL],
    Type[bool],
    Type[File],
    Type[int],
    Type[float],
    Type[datetime.date],
    Type[datetime.datetime],
    Type[ConfigVar],
    # To support Annotated types
    object,
]

SerializedParamType = Union[
    Literal["string"],
    Literal["boolean"],
    Literal["upload"],
    Literal["integer"],
    Literal["float"],
    Literal["date"],
    Literal["datetime"],
    Literal["configvar"],
]


SerializedParamComponent = Union[
    Literal["editor-sql"],
    Literal["textarea"],
]

ParamType = Literal[
    "shorttext",
    "longtext",
    "sql",
    "boolean",
    "upload",
    "integer",
    "float",
    "date",
    "datetime",
    "configvar",
]
SerializedParamValue = Union[str, bool, int, float]


@dataclasses.dataclass(frozen=True)
class Constraints:
    """Parameter constraints."""

    optional: bool
    regex: Optional[str] = None
    options: Optional[Any] = None


@dataclasses.dataclass(frozen=True)
class SerializedParam:
    """Serialized parameter."""

    slug: str
    name: str
    type: SerializedParamType
    constraints: Constraints
    desc: Optional[str] = None
    component: Optional[SerializedParamComponent] = None
    default: Optional[SerializedParamValue] = None


DefaultParamT = TypeVar(
    "DefaultParamT",
    bound=InputParam,
)


@dataclasses.dataclass(frozen=True)
class LabeledOption(Generic[DefaultParamT]):
    """Parmeter select option with a label."""

    label: str
    value: DefaultParamT


OptionsT = Sequence[Union[DefaultParamT, LabeledOption[DefaultParamT]]]

AllOptions = Union[
    OptionsT[str],
    OptionsT[int],
    OptionsT[float],
    OptionsT[datetime.date],
    OptionsT[datetime.datetime],
    OptionsT[ConfigVar],
]


@dataclasses.dataclass(frozen=True)
class ParamConfig:
    """Task parameter configuration.

    Attributes:
        slug:
            Human-friendly identifier used to reference this parameter. Parameter slugs
            must be unique within an individual task / workflow. Defaults to the function
            argument's name.
        name:
            Parameter name displayed on the Airplane app. Defaults to the function
            argument's name in sentence case.
        description:
            Parameter description displayed on the Airplane app. If not provided, the description
            will be pulled from the docstring of the decorated function.
        options:
            Option constraint for the parameter. Select options allow users to specify exactly
            which values are allowed for a given parameter. Options may specify a label which
            is shown to the user on the Airplane app instead of the value.
        regex:
            Regex contraint for the parameter, only valid for string arguments.
        default:
            Default value for the parameter. This field should only be used for prompt
            parameters, not task parameters. For task parameters, use the Python native
            default function parameter syntax, .e.g. `def my_task(my_param: str = "default")`.
    """

    slug: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[AllOptions] = None
    regex: Optional[str] = None
    default: Optional[InputParam] = None


def to_airplane_type(
    param_name: str,
    type_hint: Any,
    func_name: Optional[str] = None,
) -> ParamType:
    """Converts a Python type hint to an Airplane type."""
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


def to_serialized_airplane_type(
    param_name: str,
    type_hint: Any,
    func_name: Optional[str] = None,
) -> Tuple[SerializedParamType, Optional[SerializedParamComponent]]:
    """Converts a Python type hint to a serialized Airplane type."""
    if type_hint == str:
        return "string", None
    if type_hint == LongText:
        return "string", "textarea"
    if type_hint == SQL:
        return "string", "editor-sql"
    if type_hint == bool:
        return "boolean", None
    if type_hint == File:
        return "upload", None
    if type_hint == int:
        return "integer", None
    if type_hint == float:
        return "float", None
    if type_hint == datetime.date:
        return "date", None
    if type_hint == datetime.datetime:
        return "datetime", None
    if type_hint == ConfigVar:
        return "configvar", None

    raise InvalidAnnotationException(
        prefix=f"Invalid type annotation `{type_hint}`",
        func_name=func_name,
        param_name=param_name,
    )


def resolve_type(
    param_name: str,
    type_hint: Any,
    func_name: Optional[str] = None,
) -> Tuple[Any, bool, Optional[ParamConfig]]:
    """Parses a parameter's type hint to extract its underlying type,
    whether it's optional, and a ParamConfig if provided."""

    origin_type = get_origin(type_hint)
    if origin_type == Union:
        type_args = get_args(type_hint)
        if len(type_args) != 2 or type_args[1] is not type(None):
            raise InvalidAnnotationException(
                prefix=f"Unsupported Union type `{type_hint}`",
                func_name=func_name,
                param_name=param_name,
            )
        underlying_type, _, param_config = resolve_type(
            param_name, type_args[0], func_name
        )
        return underlying_type, True, param_config

    if origin_type == Annotated:
        type_args = get_args(type_hint)
        param_configs = [t for t in type_args if isinstance(t, ParamConfig)]
        # Don't support multiple parameter configs within the same annotation.
        if len(param_configs) > 1:
            raise InvalidAnnotationException(
                prefix=f"Found multiple ParamConfig annotations `{type_hint}`",
                func_name=func_name,
                param_name=param_name,
            )
        param_config = param_configs[0] if param_configs else None
        underlying_type, is_optional, _ = resolve_type(
            param_name, type_args[0], func_name
        )
        return underlying_type, is_optional, param_config
    return type_hint, False, None


# ParamDefs have a subset of types that are built in and serializable.
ParamDefOptions = Union[
    List[LabeledOption[str]],
    List[LabeledOption[int]],
    List[LabeledOption[float]],
]


def serialize_param(
    val: InputParam,
) -> SerializedParamValue:
    """Transforms a general parameter into a format supported by parameter definition"""
    if isinstance(val, datetime.datetime):
        return val.strftime(SERIALIZED_DATETIME_FORMAT)
    if isinstance(val, datetime.date):
        return val.strftime(SERIALIZED_DATE_FORMAT)
    if isinstance(val, ConfigVar):
        return val.name
    if isinstance(val, File):
        return val.id
    return val


def make_options(param_config: ParamConfig) -> Optional[ParamDefOptions]:
    """Builds a list of options for a parameter definition"""
    options: Optional[ParamDefOptions]
    if param_config.options is None:
        options = None
    else:
        options = []  # type: ignore
        for option in param_config.options:
            if isinstance(option, LabeledOption):
                labeled_option = LabeledOption(
                    label=option.label,
                    value=serialize_param(option.value),
                )
            else:
                value = serialize_param(option)
                labeled_option = LabeledOption(
                    label=str(value),
                    value=value,
                )
            options.append(labeled_option)  # type: ignore
    return options
