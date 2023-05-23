from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Optional

from airplane.api.entities import Run

TASK_MUST_BE_REQUESTED_ERROR_CODE = "task_must_be_requested"


@dataclass
class HTTPError(Exception):
    """Exception that indicates an HTTP error occurred."""

    status_code: int
    message: str
    error_code: Optional[str] = None

    def __str__(self) -> str:
        return f"Request failed {self.status_code}: {self.message}"


class RunPendingException(Exception):
    """Exception that indicates a run is still in pending state."""


class RequestPendingException(Exception):
    """Exception that indicates a request is still in pending state."""


class PromptPendingException(Exception):
    """Exception that indicates a prompt is still in pending state."""


class PromptCancelledError(Exception):
    """Exception that indicates a prompt has been cancelled."""

    def __str__(self) -> str:
        return "Prompt cancelled."


class InvalidEnvironmentException(Exception):
    """Exception that indicates an improperly configured environment."""

    def __str__(self) -> str:
        return "This task must be run inside of the Airplane runtime."


@dataclass
class UnknownResourceAliasException(Exception):
    """Exception that indicates a resource alias is unattached."""

    alias: str

    def __str__(self) -> str:
        return f"The resource alias {self.alias} is unknown (have you attached the resource?)."


@dataclass
class RunTerminationException(Exception):
    """Exception that indicates a run failed or was cancelled."""

    run: Run
    slug: Optional[str]

    def __str__(self) -> str:
        if isinstance(self.run.output, dict) and isinstance(
            self.run.output.get("error"), str
        ):
            return self.run.output["error"]
        if self.slug:
            return f'Run for task "{self.slug}" {str(self.run.status.value).lower()}'
        return f"Run {str(self.run.status.value).lower()}"


class RequestRejectedException(Exception):
    """Exception that indicates a request was rejected."""


@dataclass
class InvalidAnnotationException(Exception):
    """Exception that indicates an invalid annotation was provided in task definition."""

    param_name: str
    prefix: str
    func_name: Optional[str] = None

    def __str__(self) -> str:
        source = f" from function `{self.func_name}`" if self.func_name else ""
        return dedent(
            f"""
            {self.prefix} for parameter `{self.param_name}`{source}.

            Type must be one of (str, int, float, bool, datetime.date, datetime.datetime,
            airplane.LongText, airplane.File, airplane.ConfigVar, airplane.SQL,
            Optional[T], or Annotated[T, airplane.ParamConfig(...)]).
            """
        )


class UnsupportedDefaultTypeException(Exception):
    """Exception that indicates a default value isn't supported for a given type."""


class InvalidTaskConfigurationException(Exception):
    """Exception that indicates an inline task configuration is invalid."""


class InvalidZoneException(Exception):
    """Exception indicating that a run storage zone info is invalid."""
