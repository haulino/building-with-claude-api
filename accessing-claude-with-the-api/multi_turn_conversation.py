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


def chat(messages, system_prompt=None, temperature=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    if system_prompt:
        params["system"] = system_prompt

    if temperature is not None:
        params["temperature"] = temperature

    message = client.messages.create(**params)

    return message.content[0].text


def chat_stream(messages, system_prompt=None, temperature=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    if system_prompt:
        params["system"] = system_prompt

    if temperature is not None:
        params["temperature"] = temperature

    with client.messages.stream(**params) as stream:
        full_text = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text
    print()

    return full_text


if __name__ == "__main__":
    # conversation
    use_streaming = True

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
        if use_streaming:
            answer = chat_stream(messages, system_prompt)
        else:
            answer = chat(messages, system_prompt)
            print(answer)

        # Add Claude's response to the conversation history
        add_assistant_message(messages, answer)
