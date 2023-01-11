import dataclasses
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, NewType, TypeVar, Union

from typing_extensions import Literal

JSONType = Union[None, int, float, str, bool, List[Any], Mapping[str, Any]]

RuntimeType = Literal["", "workflow"]

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


if TYPE_CHECKING:
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


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
class ConfigVar:
    """Airplane config variable parameter.

    Configs variables allow users to set team-wide values / secrets
    and use them in tasks. https://docs.airplane.dev/platform/parameters#config-variable
    """

    name: str
    value: str
