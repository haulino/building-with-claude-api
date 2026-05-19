from unittest.mock import MagicMock, patch

from multi_turn_conversation import add_user_message, add_assistant_message, chat, chat_stream

# Add any global vars here
SYSTEM_PROMPT = "You are a helpful assistant."


def test_add_user_message():
    messages = []
    user_input = "Is tomato a fruit?"
    result = add_user_message(messages, user_input)

    assert result in messages


def test_add_assistant_message():
    messages = []
    input = "This would tipically be a text response from the api"
    result = add_assistant_message(messages, input)

    assert result in messages


def test_chat_includes_system_prompt():
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello! Claude here"

    with patch(
        "multi_turn_conversation.client.messages.create", return_value=mock_response
    ) as mock_create:
        messages = [{"role": "user", "content": "hi"}]
        chat(messages, system_prompt=SYSTEM_PROMPT)

        _, kwargs = mock_create.call_args
        assert kwargs.get("system") == SYSTEM_PROMPT


def test_chat_without_system_prompt():
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello! Claude here"

    with patch(
        "multi_turn_conversation.client.messages.create", return_value=mock_response
    ) as mock_create:
        messages = [{"role": "user", "content": "hi"}]
        chat(messages)
        _, kwargs = mock_create.call_args
        assert "system" not in kwargs


def test_chat_includes_temperature():
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello! Claude here"

    with patch(
        "multi_turn_conversation.client.messages.create", return_value=mock_response
    ) as mock_create:
        messages = [{"role": "user", "content": "hi"}]
        chat(messages, temperature=0.7)

        _, kwargs = mock_create.call_args
        assert kwargs.get("temperature") == 0.7


def test_chat_without_temperature():
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello! Claude here"

    with patch(
        "multi_turn_conversation.client.messages.create", return_value=mock_response
    ) as mock_create:
        messages = [{"role": "user", "content": "hi"}]
        chat(messages)

        _, kwargs = mock_create.call_args
        assert "temperature" not in kwargs


def test_chat_stream_returns_accumulated_text():
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Hello", ", ", "world!"])

    with patch(
        "multi_turn_conversation.client.messages.stream", return_value=mock_stream
    ):
        messages = [{"role": "user", "content": "hi"}]
        result = chat_stream(messages)

        assert result == "Hello, world!"
