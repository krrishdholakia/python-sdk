from unittest import mock

import pytest
from typing_extensions import Annotated

from airplane import SQL, LabeledOption, ParamConfig, PromptReviewers, prompt
from airplane._version import __version__
from airplane.exceptions import PromptCancelledError
from airplane.params import Constraints, SerializedParam


@mock.patch("airplane.runtime.standard.api_client_from_env")
def test_empty_prompt(mocked_client: mock.MagicMock) -> None:
    create_prompt = mock.Mock(return_value="prm123")
    get_prompt = mock.Mock(
        return_value={
            "submittedAt": "2021-08-18T20:00:00.000Z",
            "values": {},
            "cancelledAt": None,
        }
    )
    mocked_client.return_value = mock.Mock(
        create_prompt=create_prompt, get_prompt=get_prompt
    )

    values = prompt()
    assert values == {}

    create_prompt.assert_called_with(
        parameters=[],
        reviewers=None,
        confirm_text=None,
        cancel_text=None,
        description=None,
        notify=True,
    )
    get_prompt.assert_called_with("prm123")


@mock.patch("airplane.runtime.standard.api_client_from_env")
def test_prompt_with_parameters(mocked_client: mock.MagicMock) -> None:
    create_prompt = mock.Mock(return_value="prm123")
    get_prompt = mock.Mock(
        return_value={
            "submittedAt": "2021-08-18T20:00:00.000Z",
            "cancelledAt": None,
            "values": {
                "foo": "foo",
                "bar": 1,
                "baz": 2,
                "qux": "SELECT 1",
            },
        }
    )
    mocked_client.return_value = mock.Mock(
        create_prompt=create_prompt, get_prompt=get_prompt
    )

    values = prompt(
        {
            "foo": str,
            "bar": int,
            "baz": Annotated[
                int,
                ParamConfig(
                    options=[LabeledOption("label", 1), LabeledOption("label2", 2)],
                    default=2,
                ),
            ],
            "qux": SQL,
        }
    )
    assert values == {"bar": 1, "baz": 2, "foo": "foo", "qux": "SELECT 1"}

    create_prompt.assert_called_with(
        parameters=[
            SerializedParam(
                slug="foo",
                name="Foo",
                type="string",
                multi=False,
                constraints=Constraints(optional=False, regex=None, options=None),
            ),
            SerializedParam(
                slug="bar",
                name="Bar",
                type="integer",
                multi=False,
                constraints=Constraints(optional=False, regex=None, options=None),
            ),
            SerializedParam(
                slug="baz",
                name="Baz",
                type="integer",
                multi=False,
                constraints=Constraints(
                    optional=False,
                    regex=None,
                    options=[
                        LabeledOption("label", 1),
                        LabeledOption("label2", 2),
                    ],
                ),
                default=2,
            ),
            SerializedParam(
                slug="qux",
                name="Qux",
                type="string",
                multi=False,
                constraints=Constraints(optional=False, regex=None, options=None),
                component="editor-sql",
            ),
        ],
        reviewers=None,
        confirm_text=None,
        cancel_text=None,
        description=None,
        notify=True,
    )
    get_prompt.assert_called_with("prm123")


@mock.patch("airplane.runtime.standard.api_client_from_env")
def test_prompt_with_options(mocked_client: mock.MagicMock) -> None:
    create_prompt = mock.Mock(return_value="prm123")
    get_prompt = mock.Mock(
        return_value={
            "submittedAt": "2021-08-18T20:00:00.000Z",
            "values": {},
            "cancelledAt": None,
        }
    )
    mocked_client.return_value = mock.Mock(
        create_prompt=create_prompt, get_prompt=get_prompt
    )

    values = prompt(
        cancel_text="Cancel",
        confirm_text="Confirm",
        description="Description",
        reviewers=PromptReviewers(
            users=["user1", "user2"],
            groups=["group1", "group2"],
            allow_self_approvals=True,
        ),
        notify=True,
    )
    assert values == {}

    create_prompt.assert_called_with(
        parameters=[],
        reviewers=PromptReviewers(
            users=["user1", "user2"],
            groups=["group1", "group2"],
            allow_self_approvals=True,
        ),
        confirm_text="Confirm",
        cancel_text="Cancel",
        description="Description",
        notify=True,
    )
    get_prompt.assert_called_with("prm123")


@mock.patch("airplane.runtime.standard.api_client_from_env")
def test_prompt_cancelled(mocked_client: mock.MagicMock) -> None:
    create_prompt = mock.Mock(return_value="prm123")
    get_prompt = mock.Mock(
        return_value={
            "submittedAt": None,
            "cancelledAt": "2021-08-18T20:00:00.000Z",
            "values": {},
        }
    )
    mocked_client.return_value = mock.Mock(
        create_prompt=create_prompt, get_prompt=get_prompt
    )

    with pytest.raises(PromptCancelledError):
        prompt()
