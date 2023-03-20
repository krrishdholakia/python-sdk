from airplane_tests.api.entities import Run, RunStatus
from airplane_tests.exceptions import RunTerminationException


def test_run_termination_error() -> None:
    run = Run(
        id="run123",
        output="hello world",
        param_values={"name": "world"},
        status=RunStatus.FAILED,
        task_id="tsk123",
    )

    try:
        raise RunTerminationException(run)
    except RunTerminationException as err:
        assert err.run == run
        assert str(err) == "Run failed"

    run = Run(
        id="run123",
        output={"error": "Oops!"},
        param_values={"name": "world"},
        status=RunStatus.FAILED,
        task_id="tsk123",
    )

    try:
        raise RunTerminationException(run)
    except RunTerminationException as err:
        assert err.run == run
        assert str(err) == "Oops!"
