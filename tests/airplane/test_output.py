from typing import Any, Iterable

import pytest

from airplane.output import __to_output_path


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
