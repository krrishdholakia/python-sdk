import json
import uuid
from typing import Any, Iterable, Union

import deprecation

from airplane._version import __version__

_CHUNK_SIZE = 8192


def set_output(value: Any, *path: Union[str, int]) -> None:
    """Sets the task output with optional subpath.

    Args:
        value: The value to output.
        path: Variadic parameter that denotes the subpath of the output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output_set{__to_output_path(path)} {val}")


def append_output(value: Any, *path: Union[str, int]) -> None:
    """Appends to an array in the task output with optional subpath.

    Args:
        value: The value to output.
        path: Variadic parameter that denotes the subpath of the output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output_append{__to_output_path(path)} {val}")


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value) instead.",
)
def write_output(value: Any) -> None:
    """Writes the value to the task's output.

    Args:
        value: The value to output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output {val}")


@deprecation.deprecated(
    deprecated_in="0.3.0",
    current_version=__version__,
    details="Use append_output(value, name) instead.",
)
def write_named_output(name: str, value: Any) -> None:
    """Writes the value to the task's output, tagged by the key.

    Args:
        name: The identifier to tag the output with.
        value: The value to output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f'airplane_output:"{name}" {val}')


def __to_output_path(path: Iterable[Union[str, int]]) -> str:
    ret = "".join([f"[{json.dumps(item)}]" for item in path])
    return "" if ret == "" else f":{ret}"


def __chunk_print(output: str) -> None:
    if len(output) <= _CHUNK_SIZE:
        print(output)
        return

    chunk_key = str(uuid.uuid4())
    for start in range(0, len(output), _CHUNK_SIZE):
        print(f"airplane_chunk:{chunk_key} {output[start:start+_CHUNK_SIZE]}")
    print(f"airplane_chunk_end:{chunk_key}")
