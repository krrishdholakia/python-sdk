from airplane.api.entities import Run, RunStatus
from airplane.exceptions import RunTerminationException


def test_run_termination_error() -> None:
    run = Run(
        id="run123",
        output="hello world",
        param_values={"name": "world"},
        status=RunStatus.FAILED,
        task_id="tsk123",
    )

    try:
        raise RunTerminationException(run, "my_slug")
    except RunTerminationException as err:
        assert err.run == run
        assert str(err) == 'Run for task "my_slug" failed'
    run = Run(
        id="run123",
        output="hello world",
        param_values={"name": "world"},
        status=RunStatus.CANCELLED,
        task_id="tsk123",
    )
    try:
        raise RunTerminationException(run, "my_slug")
    except RunTerminationException as err:
        assert err.run == run
        assert str(err) == 'Run for task "my_slug" cancelled'

    run = Run(
        id="run123",
        output={"error": "Oops!"},
        param_values={"name": "world"},
        status=RunStatus.FAILED,
        task_id="tsk123",
    )

    try:
        raise RunTerminationException(run, "tsk123")
    except RunTerminationException as err:
        assert err.run == run
        assert str(err) == "Oops!"
