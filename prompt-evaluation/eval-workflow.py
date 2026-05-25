from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-0"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(messages, stop_sequences=None):
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": messages,
    }

    if stop_sequences is not None:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)
    return response.content[0].text


def generate_dataset():
    prompt = """
Generate an evaluation dataset for a prompt evaluation. The dataset will be
used to evaluate prompts that generate Python, JSON, or Regex specifically
for AWS-related tasks. Generate an array of JSON objects, each representing
task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {
    "task": "Description of task",
  },
  ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function,
a single JSON object, or a single regex
* Focus on tasks solvable with mininum coding.

Generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequences=["```"])
    return json.loads(text)


if __name__ == "__main__":
    dataset = generate_dataset()
    print(dataset)
    output_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
