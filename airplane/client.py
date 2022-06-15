import os
from functools import lru_cache
from typing import Any, Dict, Optional

import requests
from requests import Response
from requests.models import HTTPError

from airplane._version import __version__
from airplane.exceptions import InvalidEnvironmentException


class APIClient:
    """API Client to interact with the public Airplane API."""

    _api_host: str
    _headers: Dict[str, str]

    def __init__(self, api_host: str, api_token: str, env_id: str, version: str):
        self._api_host = api_host
        self._headers = {
            "X-Airplane-Token": api_token,
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": version,
            "X-Airplane-Env-ID": env_id,
        }

    def create_run(
        self,
        task_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        env: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Creates an Airplane run with parameters, env and constraints from a task id.

        Args:
            task_id: The id of the task to run.
            parameters: Optional map of parameter slugs to values.
            env: Optional map of environment variables.
            constraints: Optional map of run constraints.

        Returns:
            The id of the run.

        Raises:
            HTTPError: If the run cannot be created or executed properly.
        """
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

    def execute_task(
        self,
        slug: str,
        param_values: Optional[Dict[str, Any]] = None,
        resources: Optional[Dict[str, str]] = None,
    ) -> str:
        """Executes an Airplane task with parameters and resources from a task slug.

        Args:
            slug: The slug of the task to run.
            param_values: Optional map of parameter slugs to values.
            resources: Optional map of resource aliases to ids.

        Returns:
            The id of the run.

        Raises:
            HTTPError: If the run cannot be executed.
        """
        resp = requests.post(
            f"{self._api_host}/v0/tasks/execute",
            json={
                "slug": slug,
                "paramValues": param_values or {},
                "resources": resources or {},
            },
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["runID"]

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Fetches an Airplane run.

        Args:
            run_id: The id of the run to fetch.

        Returns:
            The Airplane run's attributes.

        Raises:
            HTTPError: If the run cannot be fetched.
        """
        resp = requests.get(
            f"{self._api_host}/v0/runs/get",
            params={"id": run_id},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()

    def get_run_output(self, run_id: str) -> Any:
        """Fetches an Airplane's run output.

        Args:
            run_id: The id of the run for which to fetch output.

        Returns:
            The Airplane run's outputs.

        Raises:
            HTTPError: If the run outputs cannot be fetched.
        """
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


def api_client_from_env() -> APIClient:
    """Creates an APIClient from environment variables.

    Returns:
        An APIClient to interact with the Airplane API.

    Raises:
        InvalidEnvironmentException: If the environment is improperly configured.
    """
    api_host = os.getenv("AIRPLANE_API_HOST")
    api_token = os.getenv("AIRPLANE_TOKEN")
    env_id = os.getenv("AIRPLANE_ENV_ID")
    if any(not x for x in [api_host, api_token, env_id]):
        raise InvalidEnvironmentException()
    return api_client(api_host, api_token, env_id)


@lru_cache(maxsize=None)
def api_client(api_host: str, api_token: str, env_id: str) -> APIClient:
    """Creates an APIClient

    Args:
        api_host: The hostname of the Airplane API.
        api_token: The api token to pass to the API on each request.
        env_id: The id of the environment to pass to the API on each request.

    Returns:
        An APIClient to interact with the Airplane API.
    """
    return APIClient(api_host, api_token, env_id, __version__)
