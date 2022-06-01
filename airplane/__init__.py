"""airplane - An SDK for writing Airplane tasks in Python"""

__version__ = "0.3.2"
__all__ = ["Airplane"]

import os

import deprecation

from .client import Airplane

DEFAULT_CLIENT = None

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
    details="Use append_output(value) instead.",
)
def write_output(value):
    """Writes the value to the task's output."""
    return _proxy("write_output", value)


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value, name) instead.",
)
def write_named_output(name, value):
    """Writes the value to the task's output, tagged by the key."""
    return _proxy("write_named_output", name, value)


def run(task_id, parameters, env=None, constraints=None):
    """Triggers an Airplane task with the provided arguments."""
    return _proxy("run", task_id, parameters, env=env, constraints=constraints)


def _proxy(method, *args, **kwargs):
    global DEFAULT_CLIENT  # pylint: disable=global-statement
    if not DEFAULT_CLIENT:
        DEFAULT_CLIENT = Airplane(_api_host, _api_token)

    func = getattr(DEFAULT_CLIENT, method)
    return func(*args, **kwargs)
