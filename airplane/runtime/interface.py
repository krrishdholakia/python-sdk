import abc
from enum import Enum
from typing import Any, Dict, List, Optional

from airplane.params import SerializedParam
from airplane.types import JSONType, PromptReviewers


class Runtime(abc.ABC):
    """Runtime interface."""

    # pylint: disable=missing-function-docstring
    @staticmethod
    @abc.abstractmethod
    def execute_background(
        slug: str,
        param_values: Optional[Dict[str, Any]] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    @staticmethod
    @abc.abstractmethod
    def wait_for_run(run_id: str) -> Dict[str, Any]:
        ...

    @staticmethod
    @abc.abstractmethod
    def get_run_output(run_id: str) -> JSONType:
        ...

    @staticmethod
    @abc.abstractmethod
    def prompt_background(
        serialized_params: List[SerializedParam],
        *,
        reviewers: Optional[PromptReviewers] = None,
        confirm_text: Optional[str] = None,
        cancel_text: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        ...

    @staticmethod
    @abc.abstractmethod
    def wait_for_prompt(prompt_id: str) -> Dict[str, Any]:
        ...


class RuntimeKind(Enum):
    """Valid runtime kinds for Airplane runs."""

    DEV = "dev"
    STANDARD = ""
    WORKFLOW = "workflow"
