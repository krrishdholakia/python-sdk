from typing import Any, Iterable

import pytest

from airplane.output import __json_dumps, __to_output_path


@pytest.mark.parametrize(
    "path,expected_output",
    [
        ([], ""),
        (["foo"], ':["foo"]'),
        (['"foo"'], ':["\\"foo\\""]'),
        (["foo", 2, 3], ':["foo"][2][3]'),
        (["foo", True], ':["foo"][true]'),
        (["\\foo\\"], ':["\\\\foo\\\\"]'),
    ],
)
def test_to_output_path(path: Iterable[Any], expected_output: str) -> None:
    assert __to_output_path(path) == expected_output


@pytest.mark.parametrize(
    "json_value,expected_output",
    [
        ([], "[]"),
        ([float("Infinity"), 3.0, float("nan")], "[null,3.0,null]"),
    ],
)
def test_json_dumps(json_value: Iterable[Any], expected_output: str) -> None:
    assert __json_dumps(json_value) == expected_output
