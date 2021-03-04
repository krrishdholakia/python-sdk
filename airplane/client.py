import json
import os
import requests
import backoff
from requests.models import HTTPError

from .exceptions import InvalidEnvironmentException, RunPendingException


class Airplane:
    """Client SDK for Airplane tasks."""

    def __init__(self, api_host, api_token):
        self._api_host = api_host
        self._api_token = api_token

    def write_output(self, value):
        """Writes the value to the task's output."""
        val = json.dumps(value, separators=(",", ":"))
        print(f"airplane_output {val}")

    def write_named_output(self, name, value):
        """Writes the value to the task's output, tagged by the key."""
        val = json.dumps(value, separators=(",", ":"))
        print(f"airplane_output:{name} {val}")

    def run(self, task_id, parameters, env={}, constraints={}):
        """Triggers an Airplane task with the provided arguments."""
        self.__require_runtime()

        # Boot the new task:
        resp = requests.post(
            f"{self._api_host}/v0/runs/create",
            json={
                "taskID": task_id,
                "params": parameters,
                "env": env,
                "constraints": constraints,
            },
            headers={
                "X-Airplane-Token": self._api_token,
            },
        )
        self.__check_resp(resp)
        body = resp.json()
        run_id = body["runID"]

        return self.__wait(run_id)

    def __check_resp(self, resp):
        if resp.status_code >= 400:
            raise HTTPError(resp.json()["error"])

    def __require_runtime(self):
        """Ensures that the current task is running inside of an Airplane task."""
        if self._api_host is None or self._api_token is None:
            raise InvalidEnvironmentException()

    def __backoff():
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
            params={"runID": run_id},
            headers={
                "X-Airplane-Token": self._api_token,
            },
        )
        self.__check_resp(resp)
        body = resp.json()
        run_status = body["run"]["status"]

        if run_status in ("NotStarted", "Queued", "Active"):
            # Retry...
            raise RunPendingException()

        resp = requests.get(
            f"{self._api_host}/v0/runs/getOutputs",
            params={"runID": run_id},
            headers={
                "X-Airplane-Token": self._api_token,
            },
        )
        self.__check_resp(resp)
        body = resp.json()

        return {"status": run_status, "outputs": body["outputs"]}
