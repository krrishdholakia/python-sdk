import textwrap
from typing import cast

from airplane.execute import Run, execute


def message(
    channel_name: str,
    message: str,  # pylint: disable=redefined-outer-name
    dedent: bool = True,
) -> Run[None]:
    """Runs the builtin message function against a Slack Airplane resource.

    Args:
        channel_name: The slack channel to send a message to.
        message: The message to send to the slack channel.
        dedent: Whether or not to omit leading whitespace from `message`.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the message builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    if dedent:
        message = textwrap.dedent(message)
    return cast(
        Run[None],
        execute(
            "airplane:slack_message",
            {
                "channelName": channel_name,
                "message": message,
            },
            {"slack": "res00000000zteamslack"},
        ),
    )
