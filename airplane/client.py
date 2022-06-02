from typing import Any, Dict, Optional

import requests
from requests import Response
from requests.models import HTTPError


class APIClient:
    _api_host: str
    _headers: Dict[str, str]

    def __init__(self, api_host: str, api_token: str, version: str):
        self._api_host = api_host
        self._headers = {
            "X-Airplane-Token": api_token,
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": version,
        }

    def create_run(
        self,
        task_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        env: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Triggers an Airplane task and returns the run id."""
        resp = requests.post(
            f"{self._api_host}/v0/runs/create",
            json={
                "taskID": task_id,
                "params": parameters,
                "env": env or {},
                "constraints": constraints or {},
            },
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["runID"]

    def get_run_status(self, run_id: str) -> str:
        """Gets the status of an Airplane task run."""
        resp = requests.get(
            f"{self._api_host}/v0/runs/get",
            params={"id": run_id},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["status"]

    def get_run_outputs(self, run_id: str) -> Any:
        """Gets the outputs of an Airplane task run."""
        resp = requests.get(
            f"{self._api_host}/v0/runs/getOutputs",
            params={"id": run_id},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["output"]

    @classmethod
    def __maybe_error_on_response(cls, resp: Response) -> None:
        if resp.status_code >= 400:
            raise HTTPError(resp.json()["error"])
