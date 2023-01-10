import textwrap
from dataclasses import asdict, dataclass, is_dataclass
from typing import List, Union, cast

from typing_extensions import TypedDict

from airplane.api.entities import BuiltInRun
from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import __execute_internal


@dataclass
class Contact:
    """Representation of an email contact (sender or recipient).

    Attributes:
        email: The email of the contact.
        name: The name of the contact.
    """

    email: str
    name: str


class MessageOutput(TypedDict):
    """The output of the email.message builtin."""

    number_of_recipients: int


def message(
    email_resource: str,
    sender: Contact,
    recipients: Union[List[Contact], List[str]],
    subject: str = "",
    message: str = "",  # pylint: disable=redefined-outer-name
    dedent: bool = True,
) -> BuiltInRun[MessageOutput]:
    """Runs the builtin message function against an email Airplane resource.

    Args:
        email_resource: The alias of the email resource to send the email with.
        sender: The email's sender information.
        recipients: List of the email's recipients.
        subject: The subject of the email.
        message: The message body of the email.
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
        BuiltInRun[MessageOutput],
        __execute_internal(
            "airplane:email_message",
            {
                "sender": asdict(sender),
                "recipients": [
                    asdict(recipient) if is_dataclass(recipient) else recipient
                    for recipient in recipients
                ],
                "subject": subject,
                "message": message,
            },
            {"email": __convert_resource_alias_to_id(email_resource)},
        ),
    )
