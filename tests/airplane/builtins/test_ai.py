import os
from typing import Any
from unittest import mock

import pytest

import airplane
from airplane.exceptions import InvalidEnvironmentException


def test_invalid_env() -> None:
    with pytest.raises(InvalidEnvironmentException):
        airplane.ai.chat("foo")


@mock.patch.dict(
    os.environ,
    {"OPENAI_API_KEY": "baz"},
)
@mock.patch("airplane.ai._chat", return_value="Hello!")
def test_chat(mock_chat: Any) -> None:
    assert airplane.ai.chat("foo") == "Hello!"


@mock.patch.dict(
    os.environ,
    {"OPENAI_API_KEY": "baz"},
)
@mock.patch("airplane.ai._chat", side_effect=["response1", "response2"])
def test_chat_bot(mock_chat: Any) -> None:
    bot = airplane.ai.ChatBot()
    assert bot.chat("foo1") == "response1"
    assert bot.chat("foo2") == "response2"

    assert len(bot.history) == 5
    assert bot.history[0].role == "system"
    assert bot.history[1].role == "user"
    assert bot.history[1].content == "foo1"
    assert bot.history[2].role == "assistant"
    assert bot.history[2].content == "response1"
    assert bot.history[3].role == "user"
    assert bot.history[3].content == "foo2"
    assert bot.history[4].role == "assistant"
    assert bot.history[4].content == "response2"


@mock.patch.dict(
    os.environ,
    {"OPENAI_API_KEY": "baz"},
)
@mock.patch("airplane.ai._chat", return_value='"kiwi"||["strawberry", "banana"]||0.7')
def test_function(mock_chat: Any) -> None:
    fruits = airplane.ai.Func(
        "return related fruits",
        [("orange", ["tangerine", "mandarin"])],
    )
    assert fruits("kiwi") == (["strawberry", "banana"], 0.7)
