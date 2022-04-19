"""airplane - An SDK for writing Airplane tasks in Python"""

__version__ = "0.3.1"
__all__ = ["Airplane"]

import deprecation
import os

from .client import Airplane

default_client = None

_api_host = os.getenv("AIRPLANE_API_HOST")
_api_token = os.getenv("AIRPLANE_TOKEN")

def set_output(value, *path):
    """Sets the task output. Optionally takes a JSON path which can be used
    to set a subpath
    """
    return _proxy("set_output", value, *path)

def append_output(value, *path):
    """Appends to an array in the task output. Optionally takes a JSON path
    which can be used to append to a subpath
    """
    return _proxy("append_output", value, *path)

@deprecation.deprecated(
        deprecated_in="0.3.0", 
        current_version=__version__,
        details="Use set_output or append_output instead, append_output should have a similar result as this function.")
def write_output(value):
    """Writes the value to the task's output."""
    return _proxy("write_output", value)


@deprecation.deprecated(
        deprecated_in="0.3.0",
        current_version=__version__,
        details="Use set_output or append_output instead, append_output with path equal to the name should have a similar result as this function.")
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
