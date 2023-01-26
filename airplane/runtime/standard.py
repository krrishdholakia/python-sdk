from typing import Any, Dict, List, Optional

import backoff
import requests

from airplane._version import __version__
from airplane.client import api_client_from_env
from airplane.exceptions import PromptPendingException, RunPendingException
from airplane.params import InputParam, SerializedParam
from airplane.runtime.interface import Runtime
from airplane.types import JSONType, PromptReviewers


class StandardRuntime(Runtime):
    """Standard runtime for Airplane tasks."""

    @staticmethod
    def execute_background(
        slug: str,
        param_values: Optional[Dict[str, Optional[InputParam]]] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Executes an Airplane task in the background, returning a run ID."""

        return api_client_from_env().execute_task(slug, param_values, resources)

    @staticmethod
    @backoff.on_exception(
        lambda: backoff.expo(factor=1, max_value=5),
        (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            RunPendingException,
        ),
    )
    def wait_for_run(run_id: str) -> Dict[str, Any]:
        """Waits until a run is complete and returns the run metadata."""

        run_info = api_client_from_env().get_run(run_id)
        if run_info["status"] in ("NotStarted", "Queued", "Active"):
            raise RunPendingException()
        return run_info

    @staticmethod
    def get_run_output(run_id: str) -> JSONType:
        """Fetches an Airplane's run output."""

        return api_client_from_env().get_run_output(run_id)

    @staticmethod
    def prompt_background(
        serialized_params: List[SerializedParam],
        *,
        reviewers: Optional[PromptReviewers] = None,
        confirm_text: Optional[str] = None,
        cancel_text: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """Creates a prompt in the background, returning the prompt ID."""

        return api_client_from_env().create_prompt(
            parameters=serialized_params,
            reviewers=reviewers,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            description=description,
        )

    @staticmethod
    @backoff.on_exception(
        lambda: backoff.expo(factor=1, max_value=5),
        (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            PromptPendingException,
        ),
    )
    def wait_for_prompt(prompt_id: str) -> Dict[str, Any]:
        """Waits until a prompt is submitted and returns the prompt values."""

        prompt_info = api_client_from_env().get_prompt(prompt_id)
        if not prompt_info["submittedAt"]:
            raise PromptPendingException()
        return prompt_info
