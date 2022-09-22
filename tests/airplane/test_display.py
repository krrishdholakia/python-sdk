import os
from unittest import mock

from airplane import display
from airplane._version import __version__


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.post")
def test_markdown(mocked_post: mock.MagicMock) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "output_id",
        },
    )
    display.markdown(
        """
        hello world
        """
    )

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/displays/create",
        json={"display": {"content": "\nhello world\n", "kind": "markdown"}},
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.post")
def test_json(mocked_post: mock.MagicMock) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "output_id",
        },
    )
    display.json({"foo": "bar"})

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/displays/create",
        json={"display": {"value": {"foo": "bar"}, "kind": "json"}},
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.post")
def test_table(mocked_post: mock.MagicMock) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "output_id",
        },
    )

    # No columns
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ]
    )

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/displays/create",
        json={
            "display": {
                "columns": [
                    {"slug": "column1", "name": None},
                    {"slug": "column2", "name": None},
                    {"slug": "column3", "name": None},
                ],
                "rows": [
                    {"column1": "data1", "column2": "data2"},
                    {"column2": "data3", "column3": "data4"},
                    {},
                ],
                "kind": "table",
            }
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": "0.3.10",
            "X-Airplane-Env-ID": "foo_env",
        },
    )
    mocked_post.reset_mock()

    # Columns as string
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ],
        ["column1", "column3", "column4"],
    )

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/displays/create",
        json={
            "display": {
                "columns": [
                    {"slug": "column1", "name": None},
                    {"slug": "column3", "name": None},
                    {"slug": "column4", "name": None},
                ],
                "rows": [{"column1": "data1"}, {"column3": "data4"}, {}],
                "kind": "table",
            }
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )

    mocked_post.reset_mock()

    # Columns with names
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ],
        [display.TableColumn("column1", name="Column 1 name"), "column3", "column4"],
    )

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/displays/create",
        json={
            "display": {
                "columns": [
                    {"slug": "column1", "name": "Column 1 name"},
                    {"slug": "column3", "name": None},
                    {"slug": "column4", "name": None},
                ],
                "rows": [{"column1": "data1"}, {"column3": "data4"}, {}],
                "kind": "table",
            }
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )
