import os

from airplane.runtime.interface import Runtime, RuntimeKind
from airplane.runtime.standard import StandardRuntime

_AIRPLANE_RUNTIME_ENV_VAR = "AIRPLANE_RUNTIME"


def get_runtime() -> Runtime:
    """Returns the runtime for the current run."""
    runtime_kind = os.environ.get(_AIRPLANE_RUNTIME_ENV_VAR, RuntimeKind.STANDARD.value)
    if runtime_kind == RuntimeKind.WORKFLOW.value:
        raise NotImplementedError("Workflow run not supported yet by python sdk")
    return StandardRuntime()
