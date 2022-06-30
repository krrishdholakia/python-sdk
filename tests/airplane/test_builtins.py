import os
from typing import Any
from unittest import mock

import pytest

from airplane.builtins import __convert_resource_alias_to_id
from airplane.exceptions import (
    InvalidEnvironmentException,
    UnknownResourceAliasException,
)


def test_check_env_vars() -> None:
    with pytest.raises(InvalidEnvironmentException):
        __convert_resource_alias_to_id("foo")


@mock.patch.dict(
    os.environ, {"AIRPLANE_RESOURCES": "{}", "AIRPLANE_RESOURCES_VERSION": "3"}
)
def test_check_resources_version() -> None:
    with pytest.raises(InvalidEnvironmentException):
        __convert_resource_alias_to_id("foo")


@mock.patch.dict(
    os.environ, {"AIRPLANE_RESOURCES": "{", "AIRPLANE_RESOURCES_VERSION": "2"}
)
def test_invalid_json() -> None:
    with pytest.raises(InvalidEnvironmentException):
        __convert_resource_alias_to_id("foo")


@mock.patch.dict(
    os.environ, {"AIRPLANE_RESOURCES": "{}", "AIRPLANE_RESOURCES_VERSION": "2"}
)
def test_missing_alias() -> None:
    with pytest.raises(UnknownResourceAliasException):
        __convert_resource_alias_to_id("foo")


@mock.patch.dict(
    os.environ, {"AIRPLANE_RESOURCES": '{"foo": {}}', "AIRPLANE_RESOURCES_VERSION": "2"}
)
def test_incorrect_resource_format() -> None:
    with pytest.raises(InvalidEnvironmentException):
        __convert_resource_alias_to_id("foo")


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_RESOURCES": '{"foo": {"id": "bar"} }',
        "AIRPLANE_RESOURCES_VERSION": "2",
    },
)
def test_converts_alias() -> None:
    assert __convert_resource_alias_to_id("foo") == "bar"
