"""Extract AWS CLI commands using message prefilling and stop sequences."""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def get_aws_commands(client=None):
    if client is None:
        client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "List 3 AWS CLI commands for managing S3 buckets. "
                    "Output only the commands, one per line, no numbering, "
                    "no explanations. After the last command, write END."
                ),
            },
            {
                "role": "assistant",
                "content": "aws",
            },
        ],
        stop_sequences=["END"],
    )

    return "aws" + response.content[0].text


if __name__ == "__main__":
    print(get_aws_commands())
