"""airplane - An SDK for writing Airplane tasks in Python"""

__version__ = "0.2.0"
__all__ = ["Airplane"]

import os

from .client import Airplane

default_client = None

_api_host = os.getenv("AP_TASK_RUNTIME_API_HOST")
_api_token = os.getenv("AP_TASK_RUNTIME_TOKEN")


def write_output(value):
    """Writes the value to the task's output."""
    return _proxy("write_output", value)


def write_named_output(name, value):
    """Writes the value to the task's output, tagged by the key."""
    return _proxy("write_named_output", name, value)


def run(task_id, parameters, env={}, constraints={}):
    """Triggers an Airplane task with the provided arguments."""
    return _proxy("run", task_id, parameters, env=env, constraints=constraints)


def _proxy(method, *args, **kwargs):
    global default_client
    if not default_client:
        default_client = Airplane(_api_host, _api_token)

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
