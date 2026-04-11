from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def api_request(client=None):
    if client is None:
        client = Anthropic()

    model = "claude-sonnet-4-0"

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": "What is quantum computing? Answer in one sentence",
            }
        ],
    )

    return response.content[0].text


if __name__ == "__main__":
    api_request()
