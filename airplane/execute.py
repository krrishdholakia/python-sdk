from typing import Any, Dict, Optional

from airplane._version import __version__
from airplane.exceptions import RunTerminationException
from airplane.runtime import get_runtime
from airplane.types import JSONType, Run, RunStatus


def execute(
    slug: str,
    param_values: Optional[Dict[str, Any]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> Run[JSONType]:
    """Standard executes an Airplane task, waits for execution, and returns run metadata.

    Args:
        slug: The slug of the task to run.
        param_values: Optional map of parameter slugs to values.
        resources: Optional map of resource aliases to ids.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the task cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    runtime = get_runtime()

    run_id = runtime.execute_background(slug, param_values, resources)
    run_info = runtime.wait_for_run(run_id)
    outputs = runtime.get_run_output(run_id)

    # pylint: disable=redefined-outer-name
    run = Run[JSONType](
        id=run_info["id"],
        task_id=run_info.get("taskID", None),
        param_values=run_info["paramValues"],
        status=RunStatus(run_info["status"]),
        output=outputs,
    )

    if run.status in (RunStatus.FAILED, RunStatus.CANCELLED):
        raise RunTerminationException(run)

    return run
