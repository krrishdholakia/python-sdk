import json
import uuid
from typing import Any, Iterable, Union

_CHUNK_SIZE = 8192


def set_output(value: Any, *path: Union[str, int]) -> None:
    """Sets the task output. Optionally takes a JSON path which can be used
    to set a subpath of the output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output_set{__to_output_path(path)} {val}")


def append_output(value: Any, *path: Union[str, int]) -> None:
    """Appends to an array in the task output. Optionally takes a JSON path
    which can be used to append to a subpath of the output.
    """
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output_append{__to_output_path(path)} {val}")


def deprecated_write_output(value: Any) -> None:
    """Writes the value to the task's output."""
    val = json.dumps(value, separators=(",", ":"))
    __chunk_print(f"airplane_output {val}")


def deprecated_write_named_output(name: str, value: Any) -> None:
    """Writes the value to the task's output, tagged by the key."""
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
    for i in range(0, len(output), _CHUNK_SIZE):
        print(f"airplane_chunk:{chunk_key} {output[i:i+_CHUNK_SIZE]}")
    print(f"airplane_chunk_end:{chunk_key}")
