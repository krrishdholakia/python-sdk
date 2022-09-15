import dataclasses
import datetime
import typing
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    NewType,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from typing_extensions import Literal

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


RuntimeType = Literal["", "workflow"]


if typing.TYPE_CHECKING:
    LongText = str
    SQL = str
else:
    # This is needed to differentiate LongText / SQL from str when building
    # the definition otherwise the label `param: LongText` would be indistinguishable
    # from str. We only want to do this at runtime in order to allow users to still
    # assign strings as default values without have to wrap their types,
    # e.g. param: LongText = "foo"
    LongText = NewType("LongText", str)
    SQL = NewType("SQL", str)


@dataclasses.dataclass
class File:
    """Airplane file parameter.

    File uploads are serialized as an object when passed to tasks. Default files
    are currently unable to be set with inline task definitions.

    https://docs.airplane.dev/platform/parameters#file
    """

    id: str
    url: str


@dataclasses.dataclass
class ConfigVar:
    """Airplane config variable parameter.

    Configs variables ("config vars") allow you to set team-wide values / secrets
    and use them in tasks.

    https://docs.airplane.dev/platform/parameters#config-variable
    """

    name: str
    value: str


@dataclasses.dataclass
class Resource:
    """Airplane resource attachment.

    Resources in Airplane allow you to easily configure connections to external systems
    like databases and APIs and use them in your tasks and runbooks.

    https://docs.airplane.dev/resources/overview
    """

    slug: str
    alias: Optional[str] = None


DefaultParamTypes = Union[
    str,
    LongText,
    SQL,
    bool,
    # File is not included since we don't allow users to provide default File values
    # via inline configuration yet.
    # File,
    int,
    float,
    datetime.date,
    datetime.datetime,
    ConfigVar,
]
DefaultParamT = TypeVar(
    "DefaultParamT",
    bound=DefaultParamTypes,
)


@dataclasses.dataclass
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


@dataclasses.dataclass
class Schedule:
    """Airplane schedule definition.

    Schedules allow you to automatically run tasks on a recurring schedule.

    https://docs.airplane.dev/schedules/schedules
    """

    slug: str
    cron: str
    name: Optional[str] = None
    description: Optional[str] = None
    param_values: Optional[Dict[str, DefaultParamTypes]] = None


@dataclasses.dataclass
class ParamConfig:
    """Task parameter configuration.

    Attributes:
        slug:
            Human-friendly identifier used to reference this parameter.
            Defaults to parameter name if not provided.
        name:
            Parameter name displayed on the Airplane app.
            Defaults to parameter name in sentence case if not provided.
        description:
            Parameter description displayed on the Airplane app.
            If not provided, the description will be pulled from the argument's function.
        options:
            Option constraint for the parameter.
        regex:
            Regex contraint for the parameter, only valid for string arguments.
    """

    slug: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[AllOptions] = None
    regex: Optional[str] = None


FuncT = TypeVar("FuncT", bound=Callable[..., Any])
