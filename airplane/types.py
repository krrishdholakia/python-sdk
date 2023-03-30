import dataclasses
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    NewType,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from typing_extensions import Literal

JSONType = Union[None, int, float, str, bool, List[Any], Mapping[str, Any]]

RuntimeType = Literal["", "workflow"]

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


JSONTypeT = TypeVar(
    "JSONTypeT",
    bound=JSONType,
)


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


@dataclasses.dataclass
class PromptReviewers:
    """Reviewers that are allowed to approve the prompt.

    Args:
        groups: List of groups allowed to approve the prompt. Groups are
            referenced via their slugs.
        users: List of users allowed to approve the prompt. Users are
            referenced via their emails.
        allow_self_approvals: Whether or not the run creator is allowed to approve
            their own prompt.
    """

    groups: Optional[List[str]] = None
    users: Optional[List[str]] = None
    allow_self_approvals: bool = True


class RunStatus(Enum):
    """Valid statuses during a run's lifecycle."""

    NOT_STARTED = "NotStarted"
    QUEUED = "Queued"
    ACTIVE = "Active"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

    def is_terminal(self) -> bool:
        """Returns whether the status is terminal.

        Returns:
            Whether the status is terminal.
        """

        return self in [self.SUCCEEDED, self.FAILED, self.CANCELLED]


@dataclasses.dataclass
class TaskReviewer:
    """Reviewers that are allowed to approve the task.

    Args:
        group_id: The ID of the group allowed to approve the task.o
        user_id: The ID of the user allowed to approve the task.
    """

    group_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclasses.dataclass
class Run(Generic[JSONTypeT]):
    """Representation of an Airplane run.

    Attributes:
        id: The id of the run.
        task_id: The task id associated with the run (None for builtin tasks).
        param_values: The param values the run was provided.
        status: The current status of the run.
        output: The outputs (if any) of the run.
    """

    id: str
    task_id: Optional[str]
    param_values: Dict[str, Any]
    status: RunStatus
    output: JSONType


TriggerRequestStatus = Literal["pending", "approved", "rejected"]


class TriggerReceipt(TypedDict):
    taskRunID: Optional[str]
    runbookSessionID: Optional[str]


class Reviewer(TypedDict):
    userID: str
    groupID: str


class Trigger(TypedDict):
    triggerID: str
    teamID: str
    name: str
    description: str
    slug: Optional[str]
    taskID: Optional[str]
    runbookID: Optional[str]
    kind: TriggerKind
    disabledAt: Optional[str]
    disabledReason: Optional[str]
    envID: str
    createdAt: str
    createdBy: str
    updatedAt: str
    updatedBy: str
    archivedAt: Optional[str]
    archivedBy: Optional[str]


class Task(TypedDict):
    id: str
    name: str
    slug: str
    description: str
    image: Optional[str]
    command: List[str]
    arguments: List[str]
    parameters: Dict[str, Any]
    resourceRequests: dict[str, Any]
    resources: dict[str, Any]
    kindOptions: dict[str, Any]
    repo: str
    requireExplicitPermissions: bool
    timeout: int
    isArchived: bool
    parentFolderID: Optional[str]
    createdAt: str
    updatedAt: str
    revisionID: str
    deploymentID: Optional[str]
    triggers: List[Trigger]


class TriggerRequest(TypedDict):
    iD: str
    teamID: str
    createdAt: str
    createdBy: str
    reason: str
    triggerReceipt: Optional[TriggerReceipt]
    status: TriggerRequestStatus
    reviewers: List[Reviewer]
    executedAt: Optional[str]
    executedBy: Optional[str]
    rejectedReason: Optional[str]
    rejectedAt: Optional[str]
    rejectedBy: Optional[str]


class TaskReviewers(TypedDict):
    task: Optional[Task]
    reviewers: Optional[List[Reviewer]]
