from typing import Any, Dict, List, Optional

import backoff
import deprecation
import requests

from airplane._version import __version__
from airplane.api.client import api_client_from_env
from airplane.api.entities import PromptReviewers, Run, RunStatus, TaskReviewer
from airplane.exceptions import (
    TASK_MUST_BE_REQUESTED_ERROR_CODE,
    HTTPError,
    PromptCancelledError,
    PromptPendingException,
    RequestPendingException,
    RequestRejectedException,
    RunPendingException,
    RunTerminationException,
)
from airplane.params import ParamTypes, SerializedParam


def execute(
    slug: str,
    param_values: Optional[Dict[str, ParamTypes]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> Run:
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
        ValueError: If the task is missing a form trigger.
        RequestRejectedException: If the request for the task is rejected.
    """

    client = api_client_from_env()
    try:
        run_id = client.execute_task(slug, param_values, resources)
    except HTTPError as err:
        if err.error_code != TASK_MUST_BE_REQUESTED_ERROR_CODE:
            if err.status_code >= 400 and err.status_code < 500:
                err.message = f'Failed to execute task "{slug}": {err.message}'
            raise
        task_reviewers_info = client.get_task_reviewers(slug)
        form_trigger = None
        if "task" in task_reviewers_info:
            for trigger in task_reviewers_info["task"].get("triggers", []):
                if trigger["kind"] == "form":
                    form_trigger = trigger

        if form_trigger is None:
            # pylint: disable=raise-missing-from
            raise ValueError("Missing form trigger for task, unable to create request")

        reviewers = task_reviewers_info.get("reviewers")
        if reviewers:
            reviewers = [
                TaskReviewer(user_id=r.get("userID"), group_id=r.get("groupID"))
                for r in reviewers
            ]
        trigger_request_id = client.create_task_request(
            trigger_id=form_trigger["triggerID"],
            param_values=param_values,
            reason="Automatically generated from parent run.",
            reviewers=reviewers,
        )

        trigger_request_info = __wait_for_request_completion(trigger_request_id)
        if trigger_request_info["status"] == "rejected":
            # pylint: disable=raise-missing-from
            raise RequestRejectedException(f"Request for task {slug} was rejected")

        run_id = ""
        if "triggerReceipt" in trigger_request_info:
            run_id = trigger_request_info["triggerReceipt"].get("taskRunID", "")

        if not run_id:
            # pylint: disable=raise-missing-from
            raise HTTPError(
                message="Unable to find run ID for completed request",
                status_code=err.status_code,
                error_code=err.error_code,
            )

    run_info = __wait_for_run_completion(run_id)
    use_zone = run_info.get("zoneID", None) is not None
    if use_zone:
        outputs = client.get_run_output_from_zone(run_id)
    else:
        outputs = client.get_run_output(run_id)

    # pylint: disable=redefined-outer-name
    run = Run(
        id=run_info["id"],
        task_id=run_info.get("taskID", None),
        param_values=run_info["paramValues"],
        status=RunStatus(run_info["status"]),
        output=outputs,
    )

    if run.status in {RunStatus.FAILED, RunStatus.CANCELLED}:
        raise RunTerminationException(run, slug)

    return run


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
    use_zone = run_info.get("zoneID", None) is not None
    if use_zone:
        outputs = client.get_run_output_from_zone(run_id)
    else:
        outputs = client.get_run_output(run_id)

    return {"status": run_info["status"], "outputs": outputs}


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


@backoff.on_exception(
    lambda: backoff.expo(factor=0.1, max_value=5),
    (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        RequestPendingException,
    ),
)
def __wait_for_request_completion(trigger_request_id: str) -> Dict[str, Any]:
    client = api_client_from_env()
    trigger_request_info = client.get_trigger_request(trigger_request_id)
    if trigger_request_info["status"] == "pending":
        raise RequestPendingException()
    return trigger_request_info


def prompt_background(
    serialized_params: List[SerializedParam],
    *,
    reviewers: Optional[PromptReviewers] = None,
    confirm_text: Optional[str] = None,
    cancel_text: Optional[str] = None,
    description: Optional[str] = None,
    notify: bool = True,
) -> str:
    """Creates a prompt in the background, returning the prompt ID."""

    client = api_client_from_env()
    return client.create_prompt(
        parameters=serialized_params,
        reviewers=reviewers,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        description=description,
        notify=notify,
    )


@backoff.on_exception(
    lambda: backoff.expo(factor=0.1, max_value=5),
    (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        PromptPendingException,
    ),
)
def wait_for_prompt(prompt_id: str) -> Dict[str, Any]:
    """Waits until a prompt is submitted and returns the prompt values."""
    client = api_client_from_env()
    prompt_info = client.get_prompt(prompt_id)
    if prompt_info["cancelledAt"]:
        raise PromptCancelledError()
    if not prompt_info["submittedAt"]:
        raise PromptPendingException()
    return prompt_info


def get_prompt(prompt_id: str) -> Dict[str, Any]:
    """Fetches a prompt by ID."""
    client = api_client_from_env()
    return client.get_prompt(prompt_id)


def get_user(user_id: str) -> Dict[str, Any]:
    """Fetches a user by ID."""
    client = api_client_from_env()
    return client.get_user(user_id)
