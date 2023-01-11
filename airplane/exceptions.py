from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Optional


class RunPendingException(Exception):
    """Exception that indicates a run is still in pending state."""


class PromptPendingException(Exception):
    """Exception that indicates a prompt is still in pending state."""


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

    status: str

    def __str__(self) -> str:
        return f"Run {str(self.status).lower()}"


@dataclass
class InvalidAnnotationException(Exception):
    """Exception that indicates an invalid annotation was provided in task definition."""

    param_name: str
    prefix: str
    func_name: Optional[str] = None

    def __str__(self) -> str:
        source = (
            f"function `{self.func_name}`" if self.func_name else "prompt definition"
        )
        return dedent(
            f"""{self.prefix} for parameter `{self.param_name}` from {source}.

            Type must be one of (str, int, float, bool, datetime.date, datetime.datetime,
            airplane.LongText, airplane.File, airplane.ConfigVar, airplane.SQL,
            Optional[T], Annotated[T, airplane.ParamConfig(...)]).
            """
        )


class UnsupportedDefaultTypeException(Exception):
    """Exception that indicates a default value isn't supported for a given type."""


class InvalidTaskConfigurationException(Exception):
    """Exception that indicates an inline task configuration is invalid."""
