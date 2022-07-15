from airplane.api.types import Run, RunStatus
from airplane.exceptions import RunTerminationException


def test_run_termination_exception() -> None:
    exception = RunTerminationException(
        Run(
            id="run123",
            task_id="task123",
            param_values={},
            status=RunStatus.FAILED,
            output=None,
        )
    )
    assert exception.__str__() == "Run failed"
