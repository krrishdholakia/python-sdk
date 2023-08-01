import textwrap
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union, cast

from typing_extensions import Literal

from airplane.api.entities import BuiltInRun
from airplane.runtime import __execute_internal


@dataclass
class MessageOption:
    """The options for the Slack message builtin."""

    attachments: Optional[List[Dict]] = None
    text: Optional[str] = None
    blocks: Optional[List[Dict]] = None
    mrkdwn: Optional[bool] = None
    parse: Optional[Literal["full", "none"]] = None
    reply_broadcast: Optional[bool] = None
    thread_ts: Optional[str] = None
    unfurl_links: Optional[bool] = None
    unfurl_media: Optional[bool] = None


def message(
    channel_name: str,
    message: Union[str, MessageOption],  # pylint: disable=redefined-outer-name
    dedent: bool = True,
) -> BuiltInRun[None]:
    """Runs the builtin message function against a Slack Airplane resource.

    Args:
        channel_name: The slack channel to send a message to.
        message: The message or message option to send to the slack channel.
        dedent: Whether or not to omit leading whitespace from `message`.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the message builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    param_values: Dict[str, Any]
    if isinstance(message, str):
        if dedent:
            message = textwrap.dedent(message)
        param_values = {
            "channelName": channel_name,
            "message": message,
        }
    else:
        param_values = {
            "channelName": channel_name,
            "message": "",
            "messageOption": asdict(message),
        }
    return cast(
        BuiltInRun[None],
        __execute_internal(
            "airplane:slack_message",
            param_values,
            {"slack": "res00000000zteamslack"},
        ),
    )
