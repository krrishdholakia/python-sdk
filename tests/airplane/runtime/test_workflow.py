import asyncio
from multiprocessing.connection import wait
from typing import Any, Dict

import pytest

from airplane.api.types import RunStatus
from airplane.runtime.workflow import SignalReceiver


@pytest.fixture(name="signal_receiver")
def fixture_signal_receiver() -> SignalReceiver:
    return SignalReceiver()


@pytest.fixture(name="run_id")
def fixture_run_id() -> str:
    return "foo"


@pytest.fixture(name="run_termination_signal")
def fixture_run_termination_signal() -> Dict[str, Any]:
    return {
        "taskID": None,
        "paramValues": {},
        "status": RunStatus.SUCCEEDED.value,
    }


@pytest.fixture(name="run_termination")
def fixture_run_termination() -> SignalReceiver.RunTermination:
    return SignalReceiver.RunTermination(
        task_id=None,
        param_values={},
        status=RunStatus.SUCCEEDED,
    )


def test_signal_receiver_receive_pre_wait(
    signal_receiver: SignalReceiver,
    run_id: str,
    run_termination_signal: Dict[str, Any],
    run_termination: SignalReceiver.RunTermination,
) -> None:
    signal_receiver.receive_signal(f"{run_id}-termination", run_termination_signal)
    signal_run_termination = signal_receiver.wait_for_run_termination(run_id)
    assert signal_run_termination == run_termination
