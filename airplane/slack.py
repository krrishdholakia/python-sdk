from airplane.execute import Run, __execute_internal


def message(
    channel_name: str,
    message: str,  # pylint: disable=redefined-outer-name
) -> Run:
    """Runs the builtin message function against a Slack Airplane resource.

    Args:
        channel_name: The slack channel to send a message to.
        message: The message to send to the slack channel.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the message builtin cannot be executed properly.
    """

    return __execute_internal(
        "airplane:slack_message",
        {
            "channelName": channel_name,
            "message": message,
        },
        {"slack": "res00000000zteamslack"},
    )
