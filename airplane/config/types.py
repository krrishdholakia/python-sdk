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

from airplane.exceptions import InvalidTaskConfigurationException

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

    File uploads are serialized as an object when passed to tasks.
    https://docs.airplane.dev/platform/parameters#file

    NOTE: Inline task definitions are currently unable to set default File parameters.

    Attributes:
        id:
            File upload ID.
        url:
            Signed URL that can be used to access the uploaded file.
            An HTTP GET to this URL will respond with the uploaded file encoded as a
            byte stream in the response's body.
    """

    id: str
    url: str


@dataclasses.dataclass
class ConfigVar:
    """Airplane config variable parameter.

    Configs variables allow users to set team-wide values / secrets
    and use them in tasks. https://docs.airplane.dev/platform/parameters#config-variable
    """

    name: str
    value: str


@dataclasses.dataclass
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


InputParamTypes = Union[
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
    bound=InputParamTypes,
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
    param_values: Optional[Dict[str, Optional[InputParamTypes]]] = None


@dataclasses.dataclass
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


@dataclasses.dataclass
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
    """

    slug: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[AllOptions] = None
    regex: Optional[str] = None


FuncT = TypeVar("FuncT", bound=Callable[..., Any])
