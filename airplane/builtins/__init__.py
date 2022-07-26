import json
import os
from typing import Any, Dict

from airplane.exceptions import (
    InvalidEnvironmentException,
    UnknownResourceAliasException,
)

__AIRPLANE_RESOURCES_ENV_VAR = "AIRPLANE_RESOURCES"
__AIRPLANE_RESOURCES_VERSION_ENV_VAR = "AIRPLANE_RESOURCES_VERSION"


def __convert_resource_alias_to_id(alias: str) -> str:
    """Converts a resource alias to a resource id.

    Args:
        alias: The resource alias to convert.

    Returns:
        The resource id that the provided alias corresponds to.

    Raises:
        InvalidEnvironmentException: If the environment does not contain resources information.
        UnknownResourceAliasException: If the resource alias cannot be found or converted.
        RunTerminationException: If the run fails or is cancelled.
    """

    resources_version = os.environ.get(__AIRPLANE_RESOURCES_VERSION_ENV_VAR, "")
    if resources_version != "2":
        raise InvalidEnvironmentException

    try:
        resources: Dict[str, Dict[str, Any]] = json.loads(
            os.environ.get(__AIRPLANE_RESOURCES_ENV_VAR, "{}")
        )
    except json.JSONDecodeError as decode_error:
        raise InvalidEnvironmentException from decode_error

    if alias not in resources:
        raise UnknownResourceAliasException(alias)

    if "id" not in resources[alias]:
        raise InvalidEnvironmentException

    return resources[alias]["id"]
