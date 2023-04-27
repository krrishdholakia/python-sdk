from __future__ import annotations

import datetime
import time

import pytimeparse2

from airplane._version import __version__
from airplane.api.client import api_client_from_env


def sleep(duration: str | float | int) -> None:
    """Creates an Airplane sleep and sleeps for the specified duration.

    Args:
        duration: The duration to sleep for.
            Accepsts a float of how long to sleep in seconds.
            Or a string of how long to sleep with a specified unit of time.
            (e.g. '2' to sleep for 2 seconds, or '1h' to sleep for an hour)
    Raises:
        HTTPError: If the display could not be created.
        ValueError: If the duration is invalid.
    """
    try:
        if isinstance(duration, (float, int)):
            seconds = float(duration)
        else:
            seconds = parse_time(duration)
    except Exception as exc:
        raise ValueError(
            f"Invalid duration: {duration}. duration must be a string of how long"
            + " to sleep with a specified unit of time."
            + " (e.g. '1h' to sleep for an hour)"
        ) from exc

    if seconds < 1:
        raise ValueError("sleep duration must be at least 1 second")
    start_time = datetime.datetime.utcnow()
    end_time = calculate_end_time_iso(start_time, seconds)
    api_client_from_env().create_sleep(seconds, end_time)
    time.sleep(seconds)


def calculate_end_time_iso(start_time: datetime.datetime, duration_secs: float) -> str:
    """Takes in the start time and duration (secs)
    And returns the end time as an ISO string, ie. "2022-12-15T21:01:30.000Z"
    """
    end_time_ms = start_time + datetime.timedelta(seconds=duration_secs)
    return end_time_ms.isoformat(sep="T", timespec="milliseconds") + "Z"


def parse_time(duration_str: str) -> float:
    """Parses a millisecond formatted time string and returns the number of seconds.
    Args:
        duration_str: The duration to parse. Must be a ms formatted string.
            (e.g. '1h' to sleep for an hour)
    Returns:
        The duration in seconds.
    Raises:
        ValueError: If the duration is invalid.
    """
    if not duration_str:
        raise ValueError(
            "expected a duration for how long to sleep (e.g. '1h' to sleep for an hour)"
        )
    if not isinstance(duration_str, str):
        raise ValueError("duration_ms must be a string")
    try:
        secs = pytimeparse2.parse(duration_str)
        if secs is None:
            raise ValueError(f"Invalid duration: {duration_str}")
        return secs
    except Exception as exc:
        raise ValueError(f"Invalid duration: {duration_str}") from exc
