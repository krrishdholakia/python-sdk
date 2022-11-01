from typing import Any, Dict, Optional

from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import Run, __execute_internal


def request(
    graphql_resource: str,
    query: str,
    operation_name: str = "",
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    url_params: Optional[Dict[str, Any]] = None,
) -> Run:
    """Runs the builtin request function against a GraphQL Airplane resource.

    Args:
        graphql_resource: The alias of the GraphQL resource to use.
        query: The set of GraphQL operations to use.
        operation_name: The name of the operation to execute. Can be blank if `query` contains only
            one operation.
        variables: Optional GraphQL variables to include in the request.
        headers: Optional headers to include in the request.
        url_params: Optional url params to include in the request.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the request builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return __execute_internal(
        "airplane:graphql_request",
        {
            "query": query,
            "operationName": operation_name,
            "variables": variables,
            "headers": headers,
            "urlParams": url_params,
        },
        {"api": __convert_resource_alias_to_id(graphql_resource)},
    )
