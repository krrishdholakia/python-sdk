import textwrap
from enum import Enum
from typing import Any, Dict, Optional

from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import Run, __execute_internal


class TransactionMode(Enum):
    """Valid transaction modes for SQL Airplane resources."""

    AUTO = "auto"
    READ_ONLY = "readOnly"
    READ_WRITE = "readWrite"
    NONE = "none"


def query(
    sql_resource: str,
    query: str,  # pylint: disable=redefined-outer-name
    query_args: Optional[Dict[str, Any]] = None,
    transaction_mode: TransactionMode = TransactionMode.AUTO,
    dedent: bool = True,
) -> Run:
    """Runs the builtin query function against a SQL Airplane resource.

    Args:
        sql_resource: The alias of the SQL resource to execute the query against.
        query: The query to run on the SQL resource.
        query_args: Optional map of query arg names to values to insert into the query.
        transaction_mode: Optional transaction mode with which to run the query.
        dedent: Whether or not to omit leading whitespace from `query`.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the query builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """
    if dedent:
        query = textwrap.dedent(query)
    return __execute_internal(
        "airplane:sql_query",
        {
            "query": query,
            "queryArgs": query_args,
            "transactionMode": transaction_mode.value,
        },
        {"db": __convert_resource_alias_to_id(sql_resource)},
    )
