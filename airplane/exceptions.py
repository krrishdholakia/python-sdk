from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent

from airplane.api.entities import Run


class RunPendingException(Exception):
    """Exception that indicates a run is still in pending state."""


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

    def __str__(self) -> str:
        return f"Run {str(self.run.status.value).lower()}"


@dataclass
class InvalidAnnotationException(Exception):
    """Exception that indicates an invalid annotation was provided in task definition."""

    func_name: str
    param_name: str
    prefix: str

    def __str__(self) -> str:
        return dedent(
            f"""{self.prefix} for parameter `{self.param_name}` of
            function `{self.func_name}`.

            Type must be one of (str, int, float, bool, datetime.date, datetime.datetime,
            airplane.LongText, airplane.File, airplane.ConfigVar, airplane.SQL,
            Optional[T], Annotated[T, airplane.ParamConfig(...)]).
            """
        )


class UnsupportedDefaultTypeException(Exception):
    """Exception that indicates a default value isn't supported for a given type."""


class InvalidTaskConfigurationException(Exception):
    """Exception that indicates an inline task configuration is invalid."""
