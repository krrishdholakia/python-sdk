from typing import Any, Dict, List, Optional, cast

from typing_extensions import TypedDict

from airplane.api.entities import BuiltInRun
from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import __execute_internal


class RequestOutput(TypedDict):
    """The output of the graphql.request builtin."""

    data: Optional[Dict[str, Any]]
    errors: Optional[List[Dict[str, Any]]]


def request(
    graphql_resource: str,
    operation: str,
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    url_params: Optional[Dict[str, Any]] = None,
    retry_failures: bool = False,
) -> BuiltInRun[RequestOutput]:
    """Runs the builtin request function against a GraphQL Airplane resource.

    Args:
        graphql_resource: The alias of the GraphQL resource to use.
        operation: The GraphQL operation to execute.
        variables: Optional GraphQL variables to include in the request.
        headers: Optional headers to include in the request.
        url_params: Optional url params to include in the request.
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
            "airplane:graphql_request",
            {
                "operation": operation,
                "variables": variables,
                "headers": headers,
                "urlParams": url_params,
                "retryFailures": retry_failures,
            },
            {"api": __convert_resource_alias_to_id(graphql_resource)},
        ),
    )
