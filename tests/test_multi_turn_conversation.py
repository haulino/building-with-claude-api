from multi_turn_conversation import add_user_message, add_assistant_message


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
