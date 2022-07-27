import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from temporalio import activity, workflow

from airplane.api.client import ClientOpts, api_client, client_opts_from_env
from airplane.api.entities import Run, RunStatus


@activity.defn
def execute_task_activity(
    client_opts: ClientOpts,
    slug: str,
    param_values: Optional[Dict[str, Any]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> str:
    """Requests task execution in a temporal activity.

    Args:
        client_opts: The ClientOpts to use in the APIClient.
        slug: The slug of the task to run.
        param_values: Optional map of parameter slugs to values.
        resources: Optional map of resource aliases to ids.

    Returns:
        The id of the created run.

    Raises:
        HTTPError: If the task cannot be executed properly.
    """

    client = api_client(client_opts)
    return client.execute_task(slug, param_values, resources)


@activity.defn
def get_run_output_activity(client_opts: ClientOpts, run_id: str) -> Any:
    """Gets run output in a temporal activity.

    Args:
        client_opts: The ClientOpts to use in the APIClient.
        run_id: The id of the Airplane run.

    Returns:
        The output of the run.

    Raises:
        HTTPError: If the task cannot be executed properly.
    """
    client = api_client(client_opts)
    return client.get_run_output(run_id)


class SignalReceiver:
    """Receives signals passed to the workflow."""

    @dataclass
    class SignalState:
        """Contains signal state information."""

        event: asyncio.Event = asyncio.Event()
        value: Any = None

    signals: Dict[str, SignalState] = {}

    # Option dynamic=true sends all workflow signals to this signal reciever,
    # since we don't know the run id ahead of time. We keep all incoming signals
    # so that anyone who wants to listen to them can do so. Right now, we only
    # allow reading run termination signals but can easily expand this to any
    # other type of signal.
    @workflow.signal(dynamic=True)
    def receive_signal(self, name: str, *args: Any) -> None:
        """Receives all signals for this workflow.

        Args:
            name: The name of the signal.
            args: The args passed by the signal sender.
        """

        if name not in self.signals:
            self.signals[name] = self.SignalState()

        self.signals[name].value = args[0]  # Assume all args passed as one value
        self.signals[name].event.set()

    @dataclass
    class RunTermination:
        """Contains all run termination information."""

        task_id: Optional[str]
        param_values: Dict[str, Any]
        status: RunStatus

    def wait_for_run_termination(self, run_id: str) -> RunTermination:
        """Returns run termination information."""

        signal_name = f"{run_id}-termination"
        if signal_name not in self.signals:
            self.signals[signal_name] = self.SignalState()

        asyncio.run(self.signals[signal_name].event.wait())
        state: Dict[str, Any] = dict(self.signals[signal_name].value)
        return self.RunTermination(
            task_id=state["taskID"],
            param_values=state["paramValues"],
            status=RunStatus(state["status"]),
        )


__SIGNAL_RECEIVER: SignalReceiver = SignalReceiver()


def execute(
    slug: str,
    param_values: Optional[Dict[str, Any]] = None,
    resources: Optional[Dict[str, Any]] = None,
) -> Run:
    """Workflow executes an Airplane task, waits for execution, and returns run metadata.

    Args:
        slug: The slug of the task to run.
        param_values: Optional map of parameter slugs to values.
        resources: Optional map of resource aliases to ids.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the task cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    client_opts = client_opts_from_env()
    run_id = asyncio.run(
        workflow.execute_activity(
            execute_task_activity,
            args=[client_opts, slug, param_values, resources],
            start_to_close_timeout=timedelta(seconds=120),
        )
    )

    run_termination = __SIGNAL_RECEIVER.wait_for_run_termination(run_id)

    output = asyncio.run(
        workflow.execute_activity(
            get_run_output_activity,
            args=[client_opts, run_id],
            start_to_close_timeout=timedelta(seconds=120),
        )
    )

    return Run(
        id=run_id,
        task_id=run_termination.task_id,
        param_values=run_termination.param_values,
        status=run_termination.status,
        output=output,
    )
