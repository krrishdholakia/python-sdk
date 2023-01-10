from enum import Enum
from typing import Any, Dict, Optional, Union, cast

from typing_extensions import TypedDict

from airplane.api.entities import BuiltInRun
from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import __execute_internal


class Method(Enum):
    """Valid HTTP methods for REST requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class BodyType(Enum):
    """Valid HTTP body types for REST requests."""

    UNKNOWN = ""
    JSON = "json"
    RAW = "raw"
    FORM_DATA = "form-data"
    FORM_URL_ENCODED = "x-www-form-urlencoded"


class RequestOutput(TypedDict):
    """The output of the rest.request builtin."""

    response: Union[str, Dict[str, Any]]


def request(
    rest_resource: str,
    method: Method,
    path: str,
    headers: Optional[Dict[str, Any]] = None,
    url_params: Optional[Dict[str, Any]] = None,
    body_type: BodyType = BodyType.UNKNOWN,
    body: Optional[Union[Dict[str, Any], str]] = None,
    form_data: Optional[Dict[str, Any]] = None,
    retry_failures: bool = False,
) -> BuiltInRun[RequestOutput]:
    """Runs the builtin request function against a REST Airplane resource.

    Args:
        rest_resource: The alias of the REST resource to use.
        method: The HTTP method of the request.
        path: The path of the request.
        headers: Optional headers to include in the request.
        url_params: Optional url params to include in the request.
        body_type: The type of the body if provided.
        body: The request body of type body_type to include in the request.
        form_data: The form data to include in the request.
        retry_failures: True to retry 500, 502, 503, and 504 error codes.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the request builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[RequestOutput],
        __execute_internal(
            "airplane:rest_request",
            {
                "method": method.value,
                "path": path,
                "headers": headers,
                "urlParams": url_params,
                "bodyType": body_type.value,
                "body": body,
                "formData": form_data,
                "retryFailures": retry_failures,
            },
            {"rest": __convert_resource_alias_to_id(rest_resource)},
        ),
    )
