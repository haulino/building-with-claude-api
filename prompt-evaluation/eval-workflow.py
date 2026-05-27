import concurrent.futures
import json
import os
import re
import uuid
from html import escape as html_escape
from statistics import mean
from textwrap import dedent

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(messages, system=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
    }

    if system:
        params["system"] = system

    if stop_sequences is not None:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)
    return response.content[0].text


def generate_prompt_evaluation_report(evaluation_results):
    total_tests = len(evaluation_results)
    scores = [result["score"] for result in evaluation_results]
    avg_score = mean(scores) if scores else 0
    pass_rate = (
        100 * len([s for s in scores if s >= 7]) / total_tests if total_tests else 0
    )

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Evaluation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .header {{
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary-stats {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .stat-box {{
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex-basis: 30%;
            min-width: 200px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #4a4a4a;
            color: white;
            text-align: left;
            padding: 12px;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            vertical-align: top;
            width: 20%;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .output pre {{
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin: 0;
            font-family: 'Consolas', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .score {{
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }}
        .score-high {{
            background-color: #c8e6c9;
            color: #2e7d32;
        }}
        .score-medium {{
            background-color: #fff9c4;
            color: #f57f17;
        }}
        .score-low {{
            background-color: #ffcdd2;
            color: #c62828;
        }}
        .score-col {{
            width: 80px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Prompt Evaluation Report</h1>
        <div class="summary-stats">
            <div class="stat-box">
                <div>Total Test Cases</div>
                <div class="stat-value">{total_tests}</div>
            </div>
            <div class="stat-box">
                <div>Average Score</div>
                <div class="stat-value">{avg_score:.1f} / 10</div>
            </div>
            <div class="stat-box">
                <div>Pass Rate (&ge;7)</div>
                <div class="stat-value">{pass_rate:.1f}%</div>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Scenario</th>
                <th>Prompt Inputs</th>
                <th>Solution Criteria</th>
                <th>Output</th>
                <th>Score</th>
                <th>Reasoning</th>
            </tr>
        </thead>
        <tbody>
"""

    for result in evaluation_results:
        esc = html_escape
        prompt_inputs_html = "<br>".join(
            [
                f"<strong>{esc(key)}:</strong> {esc(str(value))}"
                for key, value in result["test_case"]["prompt_inputs"].items()
            ]
        )

        criteria_string = "<br>• ".join(
            esc(c) for c in result["test_case"]["solution_criteria"]
        )

        score = result["score"]
        if score >= 8:
            score_class = "score-high"
        elif score <= 5:
            score_class = "score-low"
        else:
            score_class = "score-medium"

        scenario = esc(result["test_case"]["scenario"])
        output = esc(result["output"])
        reasoning = esc(result["reasoning"])

        html += f"""\
            <tr>
                <td>{scenario}</td>
                <td>{prompt_inputs_html}</td>
                <td>• {criteria_string}</td>
                <td class="output"><pre>{output}</pre></td>
                <td class="score-col">\
<span class="score {score_class}">{score}</span></td>
                <td>{reasoning}</td>
            </tr>
"""

    html += """\
        </tbody>
    </table>
</body>
</html>
"""

    return html


class PromptEvaluator:
    def __init__(self, max_concurrent_tasks=2):
        self.max_concurrent_tasks = max_concurrent_tasks

    def render(self, template_string, variables):
        placeholders = re.findall(r"{([^{}]+)}", template_string)

        result = template_string
        for placeholder in placeholders:
            if placeholder in variables:
                result = result.replace(
                    "{" + placeholder + "}", str(variables[placeholder])
                )

        return result.replace("{{", "{").replace("}}", "}")

    def generate_unique_ideas(self, task_description, prompt_inputs_spec, num_cases):
        prompt = """\
        Generate {num_cases} unique, diverse ideas for testing a prompt \
        that accomplishes this task:

        <task_description>
        {task_description}
        </task_description>

        The prompt will receive the following inputs:
        <prompt_inputs>
        {prompt_inputs_spec}
        </prompt_inputs>

        Each idea should represent a distinct scenario or example that \
        tests different aspects of the task.

        Output Format:
        Provide your response as a structured JSON array where each \
        item is a brief description of the idea.

        Example:
        ```json
        [
            "Testing with technical computer science terminology",
            "Testing with medical research findings",
            "Testing with complex mathematical concepts"
        ]
        ```

        Ensure each idea is:
        - Clearly distinct from the others
        - Relevant to the task description
        - Specific enough to guide generation of a full test case
        - Quick to solve without requiring extensive computation
        - Solvable with no more than 400 tokens of output

        Remember, only generate {num_cases} unique ideas"""

        system_prompt = (
            "You are a test scenario designer specialized in "
            "creating diverse, unique testing scenarios."
        )

        example_prompt_inputs = ""
        for key, value in prompt_inputs_spec.items():
            val = value.replace("\n", "\\n")
            example_prompt_inputs += f'"{key}": str # {val},'

        rendered_prompt = self.render(
            dedent(prompt),
            {
                "task_description": task_description,
                "num_cases": num_cases,
                "prompt_inputs_spec": example_prompt_inputs,
            },
        )

        messages = []
        add_user_message(messages, rendered_prompt)
        add_assistant_message(messages, "```json")
        text = chat(
            messages,
            stop_sequences=["```"],
            system=system_prompt,
            temperature=1.0,
        )

        return json.loads(text)

    def generate_test_case(self, task_description, idea, prompt_inputs_spec=None):
        if prompt_inputs_spec is None:
            prompt_inputs_spec = {}

        example_prompt_inputs = ""
        for key, value in prompt_inputs_spec.items():
            val = value.replace("\n", "\\n")
            example_prompt_inputs += f'"{key}": "EXAMPLE_VALUE", // {val}\n'

        allowed_keys = ", ".join([f'"{key}"' for key in prompt_inputs_spec.keys()])

        prompt = """\
        Generate a single detailed test case for a prompt evaluation \
        based on:

        <task_description>
        {task_description}
        </task_description>

        <specific_idea>
        {idea}
        </specific_idea>

        <allowed_input_keys>
        {allowed_keys}
        </allowed_input_keys>

        Output Format:
        ```json
        {{{{
            "prompt_inputs": {{{{
            {example_prompt_inputs}
            }}}},
            "solution_criteria": ["criterion 1", "criterion 2", ...]
        }}}}
        ```

        IMPORTANT REQUIREMENTS:
        - You MUST ONLY use these exact input keys: {allowed_keys}
        - Do NOT add any additional keys to prompt_inputs
        - All keys listed in allowed_input_keys must be included
        - Make the test case realistic and practically useful
        - Include measurable, concise solution criteria (1-4 items)
        - Keep solution criteria simple and directly tied to the task
        - The test case should be tailored to the specific idea
        - Quick to solve without extensive computation
        - Solvable with no more than 400 tokens of output
        - DO NOT include fields beyond those in the output format"""

        system_prompt = (
            "You are a test case creator specializing in "
            "designing evaluation scenarios."
        )

        rendered_prompt = self.render(
            dedent(prompt),
            {
                "allowed_keys": allowed_keys,
                "task_description": task_description,
                "idea": idea,
                "example_prompt_inputs": example_prompt_inputs,
            },
        )

        messages = []
        add_user_message(messages, rendered_prompt)
        add_assistant_message(messages, "```json")
        text = chat(
            messages,
            stop_sequences=["```"],
            system=system_prompt,
            temperature=0.7,
        )

        test_case = json.loads(text)
        test_case["task_description"] = task_description
        test_case["scenario"] = idea

        return test_case

    def generate_dataset(
        self,
        task_description,
        prompt_inputs_spec=None,
        num_cases=1,
        output_file="dataset.json",
    ):
        if prompt_inputs_spec is None:
            prompt_inputs_spec = {}

        ideas = self.generate_unique_ideas(
            task_description, prompt_inputs_spec, num_cases
        )

        dataset = []
        completed = 0
        total = len(ideas)
        last_reported_percentage = 0

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent_tasks
        ) as executor:
            future_to_idea = {
                executor.submit(
                    self.generate_test_case,
                    task_description,
                    idea,
                    prompt_inputs_spec,
                ): idea
                for idea in ideas
            }

            for future in concurrent.futures.as_completed(future_to_idea):
                try:
                    result = future.result()
                    completed += 1
                    current_percentage = int((completed / total) * 100)
                    milestone = (current_percentage // 20) * 20

                    if milestone > last_reported_percentage:
                        print(f"Generated {completed}/{total} test cases")
                        last_reported_percentage = milestone

                    dataset.append(result)
                except Exception as e:
                    print(f"Error generating test case: {e}")

        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=2)

        return dataset

    def grade_output(self, test_case, output, extra_criteria):
        prompt_inputs = ""
        for key, value in test_case["prompt_inputs"].items():
            val = value.replace("\n", "\\n")
            prompt_inputs += f'"{key}":"{val}",\n'

        extra_criteria_section = ""
        if extra_criteria:
            extra_criteria_template = """\
            Mandatory Requirements - ANY VIOLATION MEANS AUTOMATIC \
            FAILURE (score of 3 or lower):
            <extra_important_criteria>
            {extra_criteria}
            </extra_important_criteria>"""
            extra_criteria_section = self.render(
                dedent(extra_criteria_template),
                {"extra_criteria": extra_criteria},
            )

        eval_template = """\
        Your task is to evaluate the following AI-generated solution \
        with EXTREME RIGOR.

        Original task description:
        <task_description>
        {task_description}
        </task_description>

        Original task inputs:
        <task_inputs>
        {{{{ {prompt_inputs} }}}}
        </task_inputs>

        Solution to Evaluate:
        <solution>
        {output}
        </solution>

        Criteria you should use to evaluate the solution:
        <criteria>
        {solution_criteria}
        </criteria>

        {extra_criteria_section}

        Scoring Guidelines:
        * Score 1-3: Solution fails to meet one or more MANDATORY \
        requirements
        * Score 4-6: Solution meets all mandatory requirements but \
        has significant deficiencies in secondary criteria
        * Score 7-8: Solution meets all mandatory requirements and \
        most secondary criteria, with minor issues
        * Score 9-10: Solution meets all mandatory and secondary \
        criteria

        IMPORTANT SCORING INSTRUCTIONS:
        * Grade the output based ONLY on the listed criteria
        * If a solution meets all mandatory and secondary criteria \
        give it a 10
        * Do not add your own extra requirements beyond the listed \
        criteria
        * ANY violation of a mandatory requirement MUST result in a \
        score of 3 or lower
        * The full 1-10 scale should be utilized

        Output Format:
        Provide your evaluation as a structured JSON object with:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement
        - "reasoning": A concise explanation of your assessment
        - "score": A number between 1-10

        Respond with JSON only. Example response shape:
        {{{{
            "strengths": ["..."],
            "weaknesses": ["..."],
            "reasoning": "...",
            "score": 8
        }}}}"""

        eval_prompt = self.render(
            dedent(eval_template),
            {
                "task_description": test_case["task_description"],
                "prompt_inputs": prompt_inputs,
                "output": output,
                "solution_criteria": "\n".join(test_case["solution_criteria"]),
                "extra_criteria_section": extra_criteria_section,
            },
        )

        messages = []
        add_user_message(messages, eval_prompt)
        add_assistant_message(messages, "```json")
        eval_text = chat(
            messages,
            stop_sequences=["```"],
            temperature=0.0,
        )
        return json.loads(eval_text)

    def run_test_case(self, test_case, run_prompt_function, extra_criteria=None):
        output = run_prompt_function(test_case["prompt_inputs"])
        model_grade = self.grade_output(test_case, output, extra_criteria)

        return {
            "output": output,
            "test_case": test_case,
            "score": model_grade["score"],
            "reasoning": model_grade["reasoning"],
        }

    def run_evaluation(
        self,
        run_prompt_function,
        dataset_file,
        extra_criteria=None,
        json_output_file="output.json",
        html_output_file="output.html",
    ):
        with open(dataset_file, "r") as f:
            dataset = json.load(f)

        results = []
        completed = 0
        total = len(dataset)
        last_reported_percentage = 0

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent_tasks
        ) as executor:
            future_to_case = {
                executor.submit(
                    self.run_test_case,
                    test_case,
                    run_prompt_function,
                    extra_criteria,
                ): test_case
                for test_case in dataset
            }

            for future in concurrent.futures.as_completed(future_to_case):
                result = future.result()
                completed += 1
                current_percentage = int((completed / total) * 100)
                milestone = (current_percentage // 20) * 20

                if milestone > last_reported_percentage:
                    print(f"Graded {completed}/{total} test cases")
                    last_reported_percentage = milestone

                results.append(result)

        average_score = mean([result["score"] for result in results])
        print(f"Average score: {average_score}")

        with open(json_output_file, "w") as f:
            json.dump(results, f, indent=2)

        html = generate_prompt_evaluation_report(results)
        with open(html_output_file, "w", encoding="utf-8") as f:
            f.write(html)

        return results


if __name__ == "__main__":
    run_id = uuid.uuid4().hex[:8]
    evaluator = PromptEvaluator(max_concurrent_tasks=1)

    dataset = evaluator.generate_dataset(
        task_description="Generate a solution for a given coding task",
        prompt_inputs_spec={"task": "Description of the coding task"},
        output_file=os.path.join(os.path.dirname(__file__), f"dataset_{run_id}.json"),
        num_cases=3,
    )

    def run_prompt(prompt_inputs):
        prompt = "Solve this task:\n"
        for key, value in prompt_inputs.items():
            prompt += f"{key}: {value}\n"
        prompt += "\nRespond only with the solution code."
        messages = []
        add_user_message(messages, prompt)
        add_assistant_message(messages, "```code")
        return chat(messages, stop_sequences=["```"])

    results = evaluator.run_evaluation(
        run_prompt_function=run_prompt,
        dataset_file=os.path.join(os.path.dirname(__file__), f"dataset_{run_id}.json"),
        json_output_file=os.path.join(
            os.path.dirname(__file__), f"eval_output_{run_id}.json"
        ),
        html_output_file=os.path.join(
            os.path.dirname(__file__), f"eval_report_{run_id}.html"
        ),
    )
