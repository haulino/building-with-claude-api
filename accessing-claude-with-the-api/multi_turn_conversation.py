from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-0"


# helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)
    return user_message


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)
    return assistant_message


def chat(messages, system_prompt=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    if system_prompt:
        params["system"] = system_prompt

    message = client.messages.create(**params)

    return message.content[0].text


if __name__ == "__main__":
    # conversation
    # Start with an empty message list
    messages = []

    system_prompt = """
    You are a patient math tutor.
    Do not directly answer a student's questions.
    Guide them to a solution step by step.
    """

    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break

        # Add user input to list of messages
        add_user_message(messages, user_input)

        # Get Claude's response
        answer = chat(messages)

        print(answer)

        # Add Claude's response to the conversation history
        add_assistant_message(messages, answer)
