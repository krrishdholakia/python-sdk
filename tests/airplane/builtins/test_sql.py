import os
from typing import Any
from unittest import mock

import airplane_tests


@mock.patch.dict(
    os.environ,
    {"AIRPLANE_RESOURCES": '{"foo": {"id": "bar"}}', "AIRPLANE_RESOURCES_VERSION": "2"},
)
@mock.patch(
    "airplane.sql.__execute_internal",
    return_value=airplane_tests.Run("baz", None, {}, airplane_tests.RunStatus.SUCCEEDED, None),
)
def test_query(mock_execute_internal: Any) -> None:
    airplane_tests.sql.query(
        sql_resource="foo",
        query="SELECT * FROM foo",
    )
    mock_execute_internal.assert_called_with(
        "airplane:sql_query",
        {
            "query": "SELECT * FROM foo",
            "queryArgs": None,
            "transactionMode": airplane_tests.sql.TransactionMode.AUTO.value,
        },
        {
            "db": "bar",
        },
    )
