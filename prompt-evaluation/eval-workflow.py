from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os
import uuid

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


def run_prompt(test_case):
    """Merges the prompt and test case input, then returns the result"""
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""
    messages = []
    add_user_message(messages, prompt)
    output = chat(messages)
    return output


def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)

    # TODO - grading
    score = 10
    return {"output": output, "test_case": test_case, "score": score}


def run_eval(dataset):
    """Loads the dataset and calls run_test_case with each case"""
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    return results


if __name__ == "__main__":
    run_id = uuid.uuid4().hex[:8]
    dataset = generate_dataset()

    dataset_output_path = os.path.join(
        os.path.dirname(__file__), f"dataset_{run_id}.json"
    )
    with open(dataset_output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    results = run_eval(dataset)

    eval_output_path = os.path.join(
        os.path.dirname(__file__), f"eval_output_{run_id}.json"
    )
    with open(eval_output_path, "w") as f:
        json.dump(results, f, indent=2)

