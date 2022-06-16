from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import backoff
import deprecation
import requests

from airplane._version import __version__
from airplane.client import api_client_from_env
from airplane.exceptions import RunPendingException


class RunStatus(Enum):
    """Valid statused during a run's lifecycle."""

    NOT_STARTED = "NotStarted"
    QUEUED = "Queued"
    ACTIVE = "Active"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


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
    output: Any


@deprecation.deprecated(
    deprecated_in="0.3.2",
    current_version=__version__,
    details="Use execute(slug, param_values) instead.",
)
def run(
    task_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Creates an Airplane run, waits for execution, and returns its output and status.

    Args:
        task_id: The id of the task to run.
        parameters: Optional map of parameter slugs to values.
        env: Optional map of environment variables.
        constraints: Optional map of run constraints.

    Returns:
        The status and outputs of the run.

    Raises:
        HTTPError: If the run cannot be created or executed properly.
    """
    client = api_client_from_env()
    run_id = client.create_run(task_id, parameters, env, constraints)
    run_info = __wait_for_run_completion(run_id)
    outputs = client.get_run_output(run_id)
    return {"status": run_info["status"], "outputs": outputs}


def execute(slug: str, param_values: Optional[Dict[str, Any]] = None) -> Run:
    """Executes an Airplane task, waits for execution, and returns run metadata.

    Args:
        slug: The slug of the task to run.
        param_values: Optional map of parameter slugs to values.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the task cannot be executed properly.
    """
    return __execute_internal(slug, param_values)


def __execute_internal(
    slug: str,
    param_values: Optional[Dict[str, Any]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> Run:
    client = api_client_from_env()
    run_id = client.execute_task(slug, param_values, resources)
    run_info = __wait_for_run_completion(run_id)
    outputs = client.get_run_output(run_id)

    return Run(
        id=run_info["id"],
        task_id=run_info.get("taskID", None),
        param_values=run_info["paramValues"],
        status=RunStatus(run_info["status"]),
        output=outputs,
    )


@backoff.on_exception(
    lambda: backoff.expo(factor=0.1, max_value=5),
    (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        RunPendingException,
    ),
)
def __wait_for_run_completion(run_id: str) -> Dict[str, Any]:
    client = api_client_from_env()
    run_info = client.get_run(run_id)
    if run_info["status"] in ("NotStarted", "Queued", "Active"):
        raise RunPendingException()
    return run_info
