import textwrap
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union, cast

from typing_extensions import Literal

from airplane.api.entities import BuiltInRun
from airplane.files import File, upload as file_upload
from airplane.runtime import __execute_internal


@dataclass
class MessageOption:
    """The options for sending a Slack message.

    This includes the same options as the Slack API's `chat.postMessage` method.
    """

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
    """Sends a message to a Slack channel.

    Args:
        channel_name: The Slack channel to send a message to. This can be a channel name (e.g.
            `#general`), a channel ID (e.g. `C1234567890`), or a user ID (e.g. `U1234567890`).
        message: The message to send. This can be a string, or a Slack message option object. The
            Slack message option object includes the same options as the Slack API's
            `chat.postMessage` method.
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


def upload(
    channel_name: str,
    payload: Union[bytes, str, File],
    filename: str,
    message: Optional[str] = None,  # pylint: disable=redefined-outer-name
) -> BuiltInRun[None]:
    """Uploads a file to a Slack channel.

    Args:
        channel_name: The Slack channel to send a message to. This can be a channel name (e.g.
            `#general`), a channel ID (e.g. `C1234567890`), or a user ID (e.g. `U1234567890`).
        payload: Payload to upload to Slack. Can be a string, bytes, or an Airplane file.
        filename: Name of the upload. This is used to determine the file type of the upload.
        message: Optional message to send with the upload.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the message builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    if isinstance(payload, File):
        file_url = payload.url
    else:
        file_url = file_upload(payload, filename).url
    param_values = {
        "channelName": channel_name,
        "fileURL": file_url,
        "fileName": filename,
    }
    if message is not None:
        param_values["message"] = message
    return cast(
        BuiltInRun[None],
        __execute_internal(
            "airplane:slack_upload",
            param_values,
            {"slack": "res00000000zteamslack"},
        ),
    )
