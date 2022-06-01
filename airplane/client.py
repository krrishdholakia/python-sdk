import json
import re
import uuid
from typing import Any, Dict, Iterable, Optional, Union

import backoff
import deprecation
import requests
from requests import Response
from requests.models import HTTPError

from airplane import __version__  # pylint: disable=cyclic-import

from .exceptions import InvalidEnvironmentException, RunPendingException


class Airplane:
    """Client SDK for Airplane tasks."""

    CHUNK_SIZE = 8192

    _api_host: Optional[str]
    _api_token: Optional[str]

    def __init__(self, api_host: Optional[str], api_token: Optional[str]) -> None:
        self._api_host = api_host
        self._api_token = api_token

    def set_output(self, value: Any, *path: Union[str, int]) -> None:
        """Sets the task output. Optionally takes a JSON path which can be used
        to set a subpath of the output.
        """
        val = json.dumps(value, separators=(",", ":"))
        js_path = self.__to_js_path(path)
        maybe_path = "" if js_path == "" else f":{js_path}"
        self.__chunk_print(f"airplane_output_set{maybe_path} {val}")

    def append_output(self, value: Any, *path: Union[str, int]) -> None:
        """Appends to an array in the task output. Optionally takes a JSON path
        which can be used to append to a subpath of the output.
        """
        val = json.dumps(value, separators=(",", ":"))
        js_path = self.__to_js_path(path)
        maybe_path = "" if js_path == "" else f":{js_path}"
        self.__chunk_print(f"airplane_output_append{maybe_path} {val}")

    @classmethod
    def __to_js_path(cls, path: Iterable[Union[str, int]]) -> str:
        ret: str = ""
        for i, val in enumerate(path):
            if isinstance(val, str):
                if re.search(r"^\w+$", val) is not None:
                    if i > 0:
                        ret += "."
                    ret += val
                else:
                    ret += '["' + val.replace("\\", "\\\\").replace('"', '\\"') + '"]'
            elif isinstance(val, int):
                ret += "[" + str(val) + "]"
        return ret

    @deprecation.deprecated(
        deprecated_in="0.3.0",
        current_version=__version__,
        details="Use append_output(value) instead.",
    )
    def write_output(self, value: Any) -> None:
        """Writes the value to the task's output."""
        val = json.dumps(value, separators=(",", ":"))
        self.__chunk_print(f"airplane_output {val}")

    @deprecation.deprecated(
        deprecated_in="0.3.0",
        current_version=__version__,
        details="Use append_output(value, name) instead.",
    )
    def write_named_output(self, name: str, value: Any) -> None:
        """Writes the value to the task's output, tagged by the key."""
        val = json.dumps(value, separators=(",", ":"))
        self.__chunk_print(f'airplane_output:"{name}" {val}')

    @classmethod
    def __chunk_print(cls, output: str) -> None:
        if len(output) <= cls.CHUNK_SIZE:
            print(output)
        else:
            chunk_key = str(uuid.uuid4())
            for i in range(0, len(output), cls.CHUNK_SIZE):
                print(f"airplane_chunk:{chunk_key} {output[i:i+cls.CHUNK_SIZE]}")
            print(f"airplane_chunk_end:{chunk_key}")

    def run(
        self,
        task_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        env: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Triggers an Airplane task with the provided arguments."""
        if self._api_host is None or self._api_token is None:
            raise InvalidEnvironmentException()

        # Boot the new task:
        resp = requests.post(
            f"{self._api_host}/v0/runs/create",
            json={
                "taskID": task_id,
                "params": parameters,
                "env": env or {},
                "constraints": constraints or {},
            },
            headers={
                "X-Airplane-Token": self._api_token,
                "X-Airplane-Client-Kind": "sdk/python",
                "X-Airplane-Client-Version": __version__,
            },
        )
        self.__check_resp(resp)
        body = resp.json()
        run_id: str = body["runID"]

        return self.__wait(run_id)

    @classmethod
    def __check_resp(cls, resp: Response) -> None:
        if resp.status_code >= 400:
            raise HTTPError(resp.json()["error"])

    @classmethod
    def __backoff(cls) -> Iterable[float]:
        yield from backoff.expo(factor=0.1, max_value=5)

    @backoff.on_exception(
        __backoff,
        (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            RunPendingException,
        ),
        max_tries=1000,
    )
    def __wait(self, run_id: str) -> Dict[str, Any]:
        if self._api_host is None or self._api_token is None:
            raise InvalidEnvironmentException()

        resp = requests.get(
            f"{self._api_host}/v0/runs/get",
            params={"id": run_id},
            headers={
                "X-Airplane-Token": self._api_token,
                "X-Airplane-Client-Kind": "sdk/python",
                "X-Airplane-Client-Version": __version__,
            },
        )
        self.__check_resp(resp)
        body = resp.json()
        run_status: str = body["status"]

        if run_status in ("NotStarted", "Queued", "Active"):
            # Retry...
            raise RunPendingException()

        resp = requests.get(
            f"{self._api_host}/v0/runs/getOutputs",
            params={"id": run_id},
            headers={
                "X-Airplane-Token": self._api_token,
                "X-Airplane-Client-Kind": "sdk/python",
                "X-Airplane-Client-Version": __version__,
            },
        )
        self.__check_resp(resp)
        body = resp.json()

        return {"status": run_status, "outputs": body["output"]}
