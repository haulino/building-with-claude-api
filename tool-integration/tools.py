import datetime

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"

get_current_datetime_schema = {
    "name": "get_current_datetime",
    "description": "Returns the current date and time in the specified format.",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": (
                    "Python strftime format string. Defaults to '%Y-%m-%d %H:%M:%S'."
                ),
            }
        },
        "required": ["date_format"],
    },
}


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.datetime.now().strftime(date_format)


get_days_until_date_schema = {
    "name": "get_days_until_date",
    "description": "Returns the number of days from today until a given target date.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target_date": {
                "type": "string",
                "description": "Target date in YYYY-MM-DD format (e.g. '2026-12-25').",
            }
        },
        "required": ["target_date"],
    },
}


def get_days_until_date(target_date):
    target = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    today = datetime.date.today()
    return str((target - today).days)


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)
    return user_message


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)
    return assistant_message


def chat(messages, system_prompt=None, temperature=None, tools=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    if system_prompt:
        params["system"] = system_prompt

    if temperature is not None:
        params["temperature"] = temperature

    if tools is not None:
        params["tools"] = tools

    message = client.messages.create(**params)

    return message


if __name__ == "__main__":
    messages = []

    system_prompt = """
    You're a meteorologist. Help users with wheather related questions.
    """

    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break

        # Add user input to list of messages
        add_user_message(messages, user_input)

        # Get Claude's response
        response = chat(
            messages,
            system_prompt,
            tools=[get_current_datetime_schema, get_days_until_date_schema],
        )

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Tool call: {block.name}({block.input})]")

                    if block.name == "get_current_datetime":
                        result = get_current_datetime(**block.input)
                    elif block.name == "get_days_until_date":
                        result = get_days_until_date(**block.input)

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Get final response
            follow_up = chat(
                messages,
                system_prompt,
                tools=[get_current_datetime_schema, get_days_until_date_schema],
            )
            text = follow_up.content[0].text
            print(text)
            add_assistant_message(messages, text)
        else:
            text = response.content[0].text
            print(text)
            add_assistant_message(messages, text)
