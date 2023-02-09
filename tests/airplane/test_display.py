from unittest import mock

from airplane import display
from airplane._version import __version__


@mock.patch("airplane.display.api_client_from_env")
def test_text(mocked_client: mock.MagicMock) -> None:
    create_text_display = mock.Mock()
    mocked_client.return_value = mock.Mock(create_text_display=create_text_display)

    display.text(
        """
        hello world
        """
    )

    create_text_display.assert_called_with("\nhello world\n")


@mock.patch("airplane.display.api_client_from_env")
def test_table(mocked_client: mock.MagicMock) -> None:
    create_table_display = mock.Mock()
    mocked_client.return_value = mock.Mock(create_table_display=create_table_display)

    # No columns
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ]
    )
    create_table_display.assert_called_with(
        columns=[
            {"slug": "column1", "name": None},
            {"slug": "column2", "name": None},
            {"slug": "column3", "name": None},
        ],
        rows=[
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ],
    )
    create_table_display.reset_mock()

    # Columns as string
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ],
        ["column1", "column3", "column4"],
    )
    create_table_display.assert_called_with(
        columns=[
            {"slug": "column1", "name": None},
            {"slug": "column3", "name": None},
            {"slug": "column4", "name": None},
        ],
        rows=[{"column1": "data1"}, {"column3": "data4"}, {}],
    )
    create_table_display.reset_mock()

    # Columns with names
    display.table(
        [
            {"column1": "data1", "column2": "data2"},
            {"column2": "data3", "column3": "data4"},
            {},
        ],
        [display.TableColumn("column1", name="Column 1 name"), "column3", "column4"],
    )
    create_table_display.assert_called_with(
        columns=[
            {"slug": "column1", "name": "Column 1 name"},
            {"slug": "column3", "name": None},
            {"slug": "column4", "name": None},
        ],
        rows=[{"column1": "data1"}, {"column3": "data4"}, {}],
    )
    create_table_display.reset_mock()
