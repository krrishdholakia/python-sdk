import os
from unittest import mock

from typing_extensions import Annotated

from airplane import SQL, LabeledOption, ParamConfig, PromptReviewers, prompt
from airplane._version import __version__


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.get")
@mock.patch("requests.post")
def test_empty_prompt(mocked_post: mock.MagicMock, mocked_get: mock.MagicMock) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "prompt_id",
        },
    )

    mocked_get.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "prompt": {"submittedAt": "2021-08-18T20:00:00.000Z", "values": {}}
        },
    )

    values = prompt()

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/prompts/create",
        json={
            "schema": {"parameters": []},
            "reviewers": None,
            "confirmText": None,
            "cancelText": None,
            "description": None,
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )
    assert values == {}


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.get")
@mock.patch("requests.post")
def test_prompt_with_parameters(
    mocked_post: mock.MagicMock, mocked_get: mock.MagicMock
) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "prompt_id",
        },
    )

    mocked_get.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "prompt": {
                "submittedAt": "2021-08-18T20:00:00.000Z",
                "values": {
                    "foo": "foo",
                    "bar": 1,
                    "baz": 2,
                    "qux": "SELECT 1",
                },
            }
        },
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

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/prompts/create",
        json={
            "schema": {
                "parameters": [
                    {
                        "slug": "foo",
                        "name": "Foo",
                        "type": "string",
                        "constraints": {
                            "optional": False,
                            "regex": None,
                            "options": None,
                        },
                        "desc": None,
                        "component": None,
                        "default": None,
                    },
                    {
                        "slug": "bar",
                        "name": "Bar",
                        "type": "integer",
                        "constraints": {
                            "optional": False,
                            "regex": None,
                            "options": None,
                        },
                        "desc": None,
                        "component": None,
                        "default": None,
                    },
                    {
                        "slug": "baz",
                        "name": "Baz",
                        "type": "integer",
                        "constraints": {
                            "optional": False,
                            "regex": None,
                            "options": [
                                {"label": "label", "value": 1},
                                {"label": "label2", "value": 2},
                            ],
                        },
                        "desc": None,
                        "component": None,
                        "default": 2,
                    },
                    {
                        "slug": "qux",
                        "name": "Qux",
                        "type": "string",
                        "constraints": {
                            "optional": False,
                            "regex": None,
                            "options": None,
                        },
                        "desc": None,
                        "component": "editor-sql",
                        "default": None,
                    },
                ]
            },
            "reviewers": None,
            "confirmText": None,
            "cancelText": None,
            "description": None,
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )
    assert values == {"bar": 1, "baz": 2, "foo": "foo", "qux": "SELECT 1"}


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.get")
@mock.patch("requests.post")
def test_prompt_with_options(
    mocked_post: mock.MagicMock, mocked_get: mock.MagicMock
) -> None:
    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "id": "prompt_id",
        },
    )

    mocked_get.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "prompt": {
                "submittedAt": "2021-08-18T20:00:00.000Z",
                "values": {},
            }
        },
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
    )

    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/prompts/create",
        json={
            "schema": {"parameters": []},
            "reviewers": {
                "users": ["user1", "user2"],
                "groups": ["group1", "group2"],
                "allowSelfApproval": True,
            },
            "confirmText": "Confirm",
            "cancelText": "Cancel",
            "description": "Description",
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": __version__,
            "X-Airplane-Env-ID": "foo_env",
        },
    )
    assert values == {}
