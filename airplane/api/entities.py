from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar

from airplane.types import JSONType


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


JSONTypeT = TypeVar(
    "JSONTypeT",
    bound=JSONType,
)


@dataclass
class BuiltInRun(Generic[JSONTypeT]):
    """Representation of an Airplane built-in run.

    Attributes:
        id: The id of the run.
        param_values: The param values the run was provided.
        status: The current status of the run.
        output: The outputs (if any) of the run.
    """

    id: str
    param_values: Dict[str, Any]
    status: RunStatus
    output: JSONTypeT


@dataclass
class Run:
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
