import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import requests
from requests import Response
from requests.models import HTTPError

from airplane._version import __version__
from airplane.config.definitions import ParamDef
from airplane.config.types import InputParamTypes
from airplane.exceptions import InvalidEnvironmentException


@dataclass(frozen=True)
class ClientOpts:
    """Client options for an APIClient."""

    api_host: str
    api_token: str
    env_id: str


class APIClient:
    """API Client to interact with the public Airplane API."""

    _api_host: str
    _headers: Dict[str, str]

    def __init__(self, opts: ClientOpts, version: str):
        self._api_host = opts.api_host
        self._headers = {
            "X-Airplane-Token": opts.api_token,
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": version,
            "X-Airplane-Env-ID": opts.env_id,
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
        param_values: Optional[Dict[str, InputParamTypes]] = None,
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
        serialized_params = {}
        for key, val in (param_values or {}).items():
            serialized_params[key] = ParamDef.serialize_param(val)
        resp = requests.post(
            f"{self._api_host}/v0/tasks/execute",
            json={
                "slug": slug,
                "paramValues": serialized_params,
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

    def create_text_display(self, content: str) -> str:
        """Creates a text display.

        Args:
            content: Content to display

        Returns:
            The Airplane display's id.

        Raises:
            HTTPError: If the display could not be created.
        """
        resp = requests.post(
            f"{self._api_host}/v0/displays/create",
            json={"display": {"content": content, "kind": "markdown"}},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["id"]

    def create_json_display(
        self,
        payload: Union[Dict[str, Any], List[Any], int, str, float, bool, None],
    ) -> str:
        """Creates a json display.

        Args:
            payload: Payload to display

        Returns:
            The Airplane display's id.

        Raises:
            HTTPError: If the display could not be created.
        """
        resp = requests.post(
            f"{self._api_host}/v0/displays/create",
            json={"display": {"value": payload, "kind": "json"}},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["id"]

    def create_table_display(
        self,
        columns: Optional[List[Dict[str, Optional[str]]]],
        rows: List[Dict[str, Any]],
    ) -> str:
        """Creates a table display.

        Args:
            columns: Table columns containing keys slug and name
            rows: Table rows containing a map from column name to value.

        Returns:
            The Airplane display's id.

        Raises:
            HTTPError: If the display could not be created.
        """
        resp = requests.post(
            f"{self._api_host}/v0/displays/create",
            json={"display": {"columns": columns, "rows": rows, "kind": "table"}},
            headers=self._headers,
        )
        self.__maybe_error_on_response(resp)
        return resp.json()["id"]

    @classmethod
    def __maybe_error_on_response(cls, resp: Response) -> None:
        if resp.status_code >= 400:
            raise HTTPError(resp.json()["error"])


def client_opts_from_env() -> ClientOpts:
    """Creates ClientOpts from environment variables.

    Returns:
        Unvalidated ClientOpts from environment variables.

    Raises:
         InvalidEnvironmentException: If the environment is improperly configured.
    """

    opts = ClientOpts(
        api_host=os.getenv("AIRPLANE_API_HOST", ""),
        api_token=os.getenv("AIRPLANE_TOKEN", ""),
        env_id=os.getenv("AIRPLANE_ENV_ID", ""),
    )
    if any(not x for x in [opts.api_host, opts.api_token, opts.env_id]):
        raise InvalidEnvironmentException()
    return opts


def api_client_from_env() -> APIClient:
    """Creates an APIClient from environment variables.

    Returns:
        An APIClient to interact with the Airplane API.

    Raises:
        InvalidEnvironmentException: If the environment is improperly configured.
    """
    return api_client(client_opts_from_env())


@lru_cache(maxsize=None)
def api_client(opts: ClientOpts) -> APIClient:
    """Creates an APIClient

    Args:
        opts: The ClientOpts to use for the APIClient.

    Returns:
        An APIClient to interact with the Airplane API.
    """
    return APIClient(opts, __version__)
