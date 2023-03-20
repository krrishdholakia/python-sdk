import pytest

from airplane_tests.api.entities import RunStatus


@pytest.mark.parametrize(
    "run_status,is_terminal",
    [
        (RunStatus.NOT_STARTED, False),
        (RunStatus.QUEUED, False),
        (RunStatus.ACTIVE, False),
        (RunStatus.SUCCEEDED, True),
        (RunStatus.FAILED, True),
        (RunStatus.CANCELLED, True),
    ],
)
def test_run_status_is_terminal(run_status: RunStatus, is_terminal: bool) -> None:
    assert run_status.is_terminal() == is_terminal
