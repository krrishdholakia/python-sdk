from typing import Any, Optional, Tuple, Union

import pytest
from typing_extensions import Annotated

from airplane.exceptions import InvalidAnnotationException
from airplane.params import (
    ParamConfig,
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
            (
                str,
                False,
                None,
            ),
        ),
        (
            SQL,
            (
                SQL,
                False,
                None,
            ),
        ),
        (
            Annotated[str, ParamConfig(slug="hello")],
            (
                str,
                False,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[str],
            (
                str,
                True,
                None,
            ),
        ),
        (
            Annotated[Optional[str], ParamConfig(slug="hello")],
            (
                str,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Union[str, None],
            (
                str,
                True,
                None,
            ),
        ),
        (
            Annotated[Union[str, None], ParamConfig(slug="hello")],
            (
                str,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Union[Optional[str], None],
            (
                str,
                True,
                None,
            ),
        ),
        (
            Annotated[Union[Optional[str], None], ParamConfig(slug="hello")],
            (
                str,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[Union[str, None]],
            (
                str,
                True,
                None,
            ),
        ),
        (
            Annotated[Optional[Union[str, None]], ParamConfig(slug="hello")],
            (
                str,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
        (
            Optional[Annotated[str, ParamConfig(slug="hello")]],
            (
                str,
                True,
                ParamConfig(slug="hello"),
            ),
        ),
    ],
)
def test_resolve_type(type_: Any, resolved_type: Tuple[Any, bool, ParamConfig]) -> None:
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
