import os
from unittest import mock

import pytest

from airplane import InvalidEnvironmentException
from airplane.api.client import api_client_from_env, client_opts_from_env


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
def test_client_opts_from_env() -> None:
    opts = client_opts_from_env()

    assert opts.api_host == "https://api.airplane.dev"
    assert opts.api_token == "foo_token"
    assert opts.env_id == "foo_env"


def test_client_opts_invalid_env_throws() -> None:
    with pytest.raises(InvalidEnvironmentException):
        client_opts_from_env()


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
def test_api_client_from_env() -> None:
    client = api_client_from_env()
    assert client is not None
