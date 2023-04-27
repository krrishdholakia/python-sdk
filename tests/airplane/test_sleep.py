import unittest
from datetime import datetime
from unittest import mock

from airplane._version import __version__
from airplane.sleep import calculate_end_time_iso, parse_time, sleep


class TestTimeMethods(unittest.TestCase):
    def test_parse_time(self) -> None:
        """Tests that parse_time parses the time correctly."""
        assert parse_time("50ms") == 0.05
        assert parse_time("57 milliseconds") == 0.057
        assert parse_time("1s") == 1
        assert parse_time("2 sec") == 2
        assert parse_time("1 min") == 60
        assert parse_time("1.5 min") == 90
        assert parse_time("3m") == 180
        assert parse_time("2 s") == 2
        assert parse_time("4 sec") == 4
        assert parse_time("1 m") == 60
        assert parse_time("1h") == 3600
        assert parse_time("2.5 hours") == 9000
        assert parse_time("1d") == 86400
        with self.assertRaises(ValueError):
            parse_time(123)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            parse_time("blah")
        with self.assertRaises(ValueError):
            parse_time("1bad")

    def test_calculate_time(self) -> None:
        """Tests that calculate_end_time_iso calculates the time correctly in UTC format."""
        datetime_str = "2022-12-15T21:00:00.000Z"
        datetime_object = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        assert calculate_end_time_iso(datetime_object, 1) == "2022-12-15T21:00:01.000Z"
        assert calculate_end_time_iso(datetime_object, 90) == "2022-12-15T21:01:30.000Z"


class TestSleepMethods(unittest.TestCase):
    @mock.patch("airplane.sleep.api_client_from_env")
    def test_empty_sleep(self, mocked_client: mock.MagicMock) -> None:
        create_sleep = mock.Mock(return_value="slp123")
        mocked_client.return_value = mock.Mock(create_sleep=create_sleep)
        with self.assertRaises(ValueError):
            sleep({})  # type: ignore[arg-type]

    @mock.patch("time.sleep")
    @mock.patch("airplane.sleep.api_client_from_env")
    def test_valid_sleep_string(
        self, mocked_client: mock.MagicMock, _: mock.MagicMock
    ) -> None:
        """Tests that sleep calls time.sleep with the correct time
        and calls create_sleep with the correct time and end_time.
        We mock time.sleep so that the test doesn't actually sleep for 2 minutes."""
        create_sleep = mock.Mock(return_value="slp123")
        end_time = "2022-12-15T21:01:30.000Z"
        mock_calculate_end_time_iso = mock.Mock(return_value=end_time)
        mocked_client.return_value = mock.Mock(create_sleep=create_sleep)
        with mock.patch(
            "airplane.sleep.calculate_end_time_iso", mock_calculate_end_time_iso
        ):
            sleep("2min")
            create_sleep.assert_called_with(120, end_time)

    @mock.patch("time.sleep")
    @mock.patch("airplane.sleep.api_client_from_env")
    def test_valid_sleep_float(
        self, mocked_client: mock.MagicMock, _: mock.MagicMock
    ) -> None:
        """Tests that sleep calls time.sleep with the correct time
        and calls create_sleep with the correct time and end_time.
        We mock time.sleep so that the test doesn't actually sleep for 2 minutes."""
        create_sleep = mock.Mock(return_value="slp123")
        end_time = "2022-12-15T21:01:30.000Z"
        mock_calculate_end_time_iso = mock.Mock(return_value=end_time)
        mocked_client.return_value = mock.Mock(create_sleep=create_sleep)
        with mock.patch(
            "airplane.sleep.calculate_end_time_iso", mock_calculate_end_time_iso
        ):
            sleep("40")  # 40 seconds
            create_sleep.assert_called_with(40, end_time)
