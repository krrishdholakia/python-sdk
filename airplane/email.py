from dataclasses import asdict, dataclass, is_dataclass
from typing import List, Union

from airplane.execute import Run, __execute_internal


@dataclass
class Contact:
    """Representation of an email contact (sender or recipient).

    Attributes:
        email: The email of the contact.
        name: The name of the contact.
    """

    email: str
    name: str


def message(
    email_resource_id: str,
    sender: Contact,
    recipients: Union[List[Contact], List[str]],
    subject: str = "",
    message: str = "",  # pylint: disable=redefined-outer-name
) -> Run:
    """Runs the builtin message function against an email Airplane resource.

    Args:
        email_resource_id: The id of the email resource to send the email with.
        sender: The email's sender information.
        recipients: List of the email's recipients.
        subject: The subject of the email.
        message: The message body of the email.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the message builtin cannot be executed properly.
    """

    return __execute_internal(
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
        {"email": email_resource_id},
    )
