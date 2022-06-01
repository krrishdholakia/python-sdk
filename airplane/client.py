import json
import re
import uuid

import backoff
import deprecation
import requests
from requests.models import HTTPError

from . import __version__  # pylint: disable=cyclic-import
from .exceptions import InvalidEnvironmentException, RunPendingException


class Airplane:
    """Client SDK for Airplane tasks."""

    def __init__(self, api_host, api_token):
        self._api_host = api_host
        self._api_token = api_token

    def set_output(self, value, *path):
        """Sets the task output. Optionally takes a JSON path which can be used
        to set a subpath of the output.
        """
        val = json.dumps(value, separators=(",", ":"))
        js_path = self.__to_js_path(path)
        maybe_path = "" if js_path == "" else f":{js_path}"
        self.__chunk_print(f"airplane_output_set{maybe_path} {val}")

    def append_output(self, value, *path):
        """Appends to an array in the task output. Optionally takes a JSON path
        which can be used to append to a subpath of the output.
        """
        val = json.dumps(value, separators=(",", ":"))
        js_path = self.__to_js_path(path)
        maybe_path = "" if js_path == "" else f":{js_path}"
        self.__chunk_print(f"airplane_output_append{maybe_path} {val}")

    @classmethod
    def __to_js_path(cls, path):
        ret = ""
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
    def write_output(self, value):
        """Writes the value to the task's output."""
        val = json.dumps(value, separators=(",", ":"))
        self.__chunk_print(f"airplane_output {val}")

    @deprecation.deprecated(
        deprecated_in="0.3.0",
        current_version=__version__,
        details="Use append_output(value, name) instead.",
    )
    def write_named_output(self, name, value):
        """Writes the value to the task's output, tagged by the key."""
        val = json.dumps(value, separators=(",", ":"))
        self.__chunk_print(f'airplane_output:"{name}" {val}')

    @classmethod
    def __chunk_print(cls, output):
        chunk_size = 8192
        if len(output) <= chunk_size:
            print(output)
        else:
            chunk_key = str(uuid.uuid4())
            for i in range(0, len(output), chunk_size):
                print(f"airplane_chunk:{chunk_key} {output[i:i+chunk_size]}")
            print(f"airplane_chunk_end:{chunk_key}")

    def run(self, task_id, parameters, env=None, constraints=None):
        """Triggers an Airplane task with the provided arguments."""
        self.__require_runtime()

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
        run_id = body["runID"]

        return self.__wait(run_id)

    @classmethod
    def __check_resp(cls, resp):
        if resp.status_code >= 400:
            raise HTTPError(resp.json()["error"])

    def __require_runtime(self):
        """Ensures that the current task is running inside of an Airplane task."""
        if self._api_host is None or self._api_token is None:
            raise InvalidEnvironmentException()

    @classmethod
    def __backoff(cls):
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
    def __wait(self, run_id):
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
        run_status = body["status"]

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
