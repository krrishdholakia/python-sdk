from dataclasses import dataclass


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
