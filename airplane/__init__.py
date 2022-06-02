"""airplane - An SDK for writing Airplane tasks in Python"""

__version__ = "0.3.2"

import os
from functools import lru_cache
from typing import Any, Dict, Optional

import backoff
import deprecation
import requests

from airplane.client import APIClient
from airplane.exceptions import InvalidEnvironmentException, RunPendingException
from airplane.output import (
    append_output,
    deprecated_write_named_output as __deprecated_write_named_output,
    deprecated_write_output as __deprecated_write_output,
    set_output,
)


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value) instead.",
)
def write_output(value: Any) -> None:
    """Writes the value to the task's output."""
    return __deprecated_write_output(value)


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value, name) instead.",
)
def write_named_output(name: str, value: Any) -> None:
    """Writes the value to the task's output, tagged by the key."""
    return __deprecated_write_named_output(name, value)


def run(
    task_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Triggers an Airplane task with the provided arguments."""
    client = api_client_from_env()
    run_id = client.create_run(task_id, parameters, env, constraints)
    run_status = __wait_for_run_completion(run_id)
    outputs = client.get_run_outputs(run_id)
    return {"status": run_status, "outputs": outputs}


@backoff.on_exception(
    backoff.expo(factor=0.1, max_value=5),
    (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        RunPendingException,
    ),
    max_tries=1000,
)
def __wait_for_run_completion(run_id: str) -> str:
    client = api_client_from_env()
    run_status = client.get_run_status(run_id)
    if run_status in ("NotStarted", "Queued", "Active"):
        raise RunPendingException()
    return run_status


def api_client_from_env() -> APIClient:
    api_host = os.getenv("AIRPLANE_API_HOST")
    api_token = os.getenv("AIRPLANE_TOKEN")
    if api_host is None or api_token is None:
        raise InvalidEnvironmentException()
    return api_client(api_host, api_token)


@lru_cache(maxsize=None)
def api_client(api_host: str, api_token: str) -> APIClient:
    return APIClient(api_host, api_token, __version__)
