import json
import os
import requests
import backoff

from .exceptions import RunFailedException, RunPendingException


class Airplane:
    """Client SDK for Airplane tasks."""

    def __init__(self, api_host, api_token):
        self._api_host = api_host
        self._api_token = api_token

    def write_output(self, value):
        """Writes the value to the task's output."""
        print("airplane_output %s" % json.dumps(value, separators=(",", ":")))

    def write_named_output(self, name, value):
        """Writes the value to the task's output, tagged by the key."""
        print("airplane_output:%s %s" % name, json.dumps(value, separators=(",", ":")))

    def run(self, task_id, parameters, env={}, constraints={}):
        """Triggers an Airplane task with the provided arguments."""
        # Boot the new task:
        resp = requests.post(
            "%s/taskRuntime/runTask" % (self._api_host),
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
        body = resp.json()
        run_id = body["runID"]

        return self.__getOutput(run_id)

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
    def __getOutput(self, run_id):
        resp = requests.get(
            "%s/taskRuntime/getOutput" % self._api_host,
            params={"runID": run_id},
            headers={
                "X-Airplane-Token": self._api_token,
            },
        )
        body = resp.json()
        run_status, output = body["runStatus"], body["output"]
        if run_status == "Failed":
            raise RunFailedException()
        elif run_status == "Succeeded":
            return output
        else:
            raise RunPendingException()
