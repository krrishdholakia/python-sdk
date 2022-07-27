import os
from enum import Enum
from typing import Any, Dict, Optional

from airplane.api.entities import Run
from airplane.runtime.standard import execute as standard_execute
from airplane.runtime.workflow import execute as workflow_execute

__AIRPLANE_RUNTIME_ENV_VAR = "AIRPLANE_RUNTIME"


class RuntimeKind(Enum):
    """Valid runtime kinds for Airplane runs."""

    DEV = "dev"
    STANDARD = "standard"
    WORKFLOW = "workflow"


def execute(slug: str, param_values: Optional[Dict[str, Any]] = None) -> Run:
    """Executes an Airplane task, waits for execution, and returns run metadata.

    Args:
        slug: The slug of the task to run.
        param_values: Optional map of parameter slugs to values.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the task cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    return __execute_internal(slug, param_values)


def __execute_internal(
    slug: str,
    param_values: Optional[Dict[str, Any]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> Run:
    runtime_kind = os.environ.get(
        __AIRPLANE_RUNTIME_ENV_VAR, RuntimeKind.STANDARD.value
    )

    if runtime_kind == RuntimeKind.WORKFLOW.value:
        return workflow_execute(slug, param_values, resources)

    return standard_execute(slug, param_values, resources)
