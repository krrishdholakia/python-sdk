"""airplane - An SDK for writing Airplane tasks in Python"""

__version__ = "0.3.2"
__all__ = ["Airplane"]

import os
from typing import Any, Callable, Dict, Optional, Union

import deprecation

from airplane.client import Airplane

DEFAULT_CLIENT = None

_api_host = os.getenv("AIRPLANE_API_HOST")
_api_token = os.getenv("AIRPLANE_TOKEN")


def set_output(value: Any, *path: Union[str, int]) -> None:
    """Sets the task output. Optionally takes a JSON path which can be used
    to set a subpath
    """
    return _proxy("set_output", value, *path)


def append_output(value: Any, *path: Union[str, int]) -> None:
    """Appends to an array in the task output. Optionally takes a JSON path
    which can be used to append to a subpath
    """
    return _proxy("append_output", value, *path)


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value) instead.",
)
def write_output(value: Any) -> None:
    """Writes the value to the task's output."""
    return _proxy("write_output", value)


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value, name) instead.",
)
def write_named_output(name: str, value: Any) -> None:
    """Writes the value to the task's output, tagged by the key."""
    return _proxy("write_named_output", name, value)


def run(
    task_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Triggers an Airplane task with the provided arguments."""
    return _proxy("run", task_id, parameters, env=env, constraints=constraints)


def _proxy(method: str, *args: Any, **kwargs: Any) -> Any:
    global DEFAULT_CLIENT  # pylint: disable=global-statement
    if not DEFAULT_CLIENT:
        DEFAULT_CLIENT = Airplane(_api_host, _api_token)

    func: Callable[..., Any] = getattr(DEFAULT_CLIENT, method)
    return func(*args, **kwargs)
