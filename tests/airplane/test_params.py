import sys
from typing import Any, List, Optional, Union

import pytest
from typing_extensions import Annotated

from airplane.exceptions import InvalidAnnotationException
from airplane.params import (
    ParamConfig,
    ParamInfo,
    resolve_type,
    to_airplane_type,
    to_serialized_airplane_type,
)
from airplane.types import SQL


@pytest.mark.parametrize(
    "type_,resolved_type",
    [
        (
            str,
            ParamInfo(
                str,
                False,
                False,
                None,
            ),
        ),
        (
            SQL,
            ParamInfo(
                SQL,
                False,
                False,
                None,
            ),
        ),
        (
            Annotated[str, ParamConfig(slug="hello")],
            ParamInfo(
                str,
                False,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[str],
            ParamInfo(
                str,
                True,
                False,
                None,
            ),
        ),
        (
            Annotated[Optional[str], ParamConfig(slug="hello")],
            ParamInfo(
                str,
                True,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Union[str, None],
            ParamInfo(
                str,
                True,
                False,
                None,
            ),
        ),
        (
            Annotated[Union[str, None], ParamConfig(slug="hello")],
            ParamInfo(
                str,
                True,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Union[Optional[str], None],
            ParamInfo(
                str,
                True,
                False,
                None,
            ),
        ),
        (
            Annotated[Union[Optional[str], None], ParamConfig(slug="hello")],
            ParamInfo(
                str,
                True,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[Union[str, None]],
            ParamInfo(
                str,
                True,
                False,
                None,
            ),
        ),
        (
            Annotated[Optional[Union[str, None]], ParamConfig(slug="hello")],
            ParamInfo(
                str,
                True,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[Annotated[str, ParamConfig(slug="hello")]],
            ParamInfo(
                str,
                True,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            List[str],
            ParamInfo(
                str,
                False,
                True,
                None,
            ),
        ),
        (
            Optional[List[Annotated[str, ParamConfig(slug="hello")]]],
            ParamInfo(
                str,
                True,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
    ],
)
def test_resolve_type(type_: Any, resolved_type: ParamInfo) -> None:
    assert resolve_type("param", type_) == resolved_type


def test_resolve_type_errors() -> None:
    with pytest.raises(
        InvalidAnnotationException, match="Found multiple ParamConfig.*"
    ):
        resolve_type(
            "param",
            Optional[
                Annotated[
                    Annotated[str, ParamConfig(slug="hello")],
                    ParamConfig(slug="override_hello"),
                ]
            ],
        )

    with pytest.raises(InvalidAnnotationException, match="Unsupported Union.*"):
        resolve_type(
            "param",
            Union[str, int],
        )

    with pytest.raises(
        InvalidAnnotationException, match="Unsupported Optional in List"
    ):
        resolve_type(
            "param",
            List[Optional[str]],
        )

    with pytest.raises(InvalidAnnotationException, match="Unsupported List of List"):
        resolve_type(
            "param",
            List[List[str]],
        )


class CustomType:
    pass


def test_invalid_type() -> None:
    with pytest.raises(
        InvalidAnnotationException,
        match="Invalid type annotation.*",
    ):
        to_airplane_type("param", CustomType)

    with pytest.raises(
        InvalidAnnotationException,
        match="Invalid type annotation.*",
    ):
        to_serialized_airplane_type("param", CustomType)


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10 optional syntax"
)
def test_python_uniontype_optional() -> None:
    # Have to use eval() to avoid syntax error
    optional_type = eval("str | None")
    info = resolve_type(
        "param",
        optional_type,
    )
    assert info.is_optional
    assert info.resolved_type == str
