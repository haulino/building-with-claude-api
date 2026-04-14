from multi_turn_conversation import add_user_message


def test_add_user_message():
    messages = []
    user_input = "Is tomato a fruit?"
    result = add_user_message(messages, user_input)

    assert result in messages
