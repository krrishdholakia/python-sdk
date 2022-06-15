from enum import Enum
from typing import Any, Dict, Optional, Union

from airplane.execute import Run, __execute_internal


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


def request(
    rest_resource_id: str,
    method: Method,
    path: str,
    headers: Optional[Dict[str, Any]] = None,
    url_params: Optional[Dict[str, Any]] = None,
    body_type: BodyType = BodyType.UNKNOWN,
    body: Optional[Union[Dict[str, Any], str]] = None,
    form_data: Optional[Dict[str, Any]] = None,
) -> Run:
    """Runs the builtin request function against a REST Airplane resource.

    Args:
        rest_resource_id: The id of the REST resource to use.
        method: The HTTP method of the request.
        path: The path of the request.
        headers: Optional headers to include in the request.
        url_params: Optional url params to include in the request.
        body_type: The type of the body if provided.
        body: The request body of type body_type to include in the request.
        form_data: The form data to include in the request.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the request builtin cannot be executed properly.
    """

    return __execute_internal(
        "airplane:rest_request",
        {
            "method": method.value,
            "path": path,
            "headers": headers,
            "urlParams": url_params,
            "bodyType": body_type.value,
            "body": body,
            "formData": form_data,
        },
        {"rest": rest_resource_id},
    )
