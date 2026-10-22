import json
import time
import os

from google.colab import userdata
from openai import OpenAI

from tools import lookup, calculate

# =====================================================
# OPENROUTER
# =====================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

MODEL = "deepseek/deepseek-v4-flash-0731"

# =====================================================
# SETTINGS
# =====================================================

MAX_ROUNDS = 15
MAX_TOKENS = 500

OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# =====================================================
# TOOL DEFINITIONS
# =====================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup",
            "description": (
                "Retrieve a fact from the Nine Rivers Region corpus. "
                "Returns data from current district profiles, "
                "ignores archived profiles, and applies correction notices. "
                "Valid fields are: population_2025, population_2020, "
                "area, budget, water_use, schools, pupils, "
                "roads, founded, water_tariff."
            ),

            "parameters": {
                "type": "object",
                "properties": {
                    "district": {
                        "type": "string"
                    },
                    "field": {
                        "type": "string"
                    }
                },
                "required": [
                    "district",
                    "field"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description":
            "Safely evaluate arithmetic expressions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string"
                    }
                },
                "required": [
                    "expression"
                ]
            }
        }
    }
]

# =====================================================
# LOOP
# =====================================================
def run_question(question_id, question):
    question_start = time.time()
    messages = [
        {
            "role": "system",
            "content": """
Use the available tools to answer questions.

Rules:
1. Use lookup to retrieve facts.
2. Use calculate for arithmetic.
3. Do not invent numbers.
4. Use calculate whenever arithmetic is required.
5. End every answer with:

ANSWER: <name or yes/no> | <number>
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    logs = []

    total_input = 0
    total_output = 0

    for round_num in range(MAX_ROUNDS):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=MAX_TOKENS
        )

        total_input += response.usage.prompt_tokens
        total_output += response.usage.completion_tokens

        message = response.choices[0].message

        # ===============================================
        # FINAL ANSWER
        # ===============================================

        if not message.tool_calls:

            with open(
                f"{OUTPUT_DIR}/{question_id}.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    logs,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print(f"Input tokens: {total_input}")
            print(f"Output tokens: {total_output}")
            print(
                f"Total seconds: "
                f"{round(time.time() - question_start, 2)}")

            return message.content

        messages.append(message)

        # ===============================================
        # PROCESS TOOLS
        # ===============================================

        for tool_call in message.tool_calls:

            start = time.time()

            tool_name = tool_call.function.name

            try:

                args = json.loads(
                    tool_call.function.arguments
                )

            except Exception:

                result = {
                    "error": "invalid JSON arguments"
                }

                args = None

            else:

                if tool_name == "lookup":

                    if (
                        "district" not in args
                        or
                        "field" not in args
                    ):
                        result = {
                            "error": "missing arguments"
                        }
                    else:
                        result = lookup(
                            args["district"],
                            args["field"]
                        )

                elif tool_name == "calculate":

                    if "expression" not in args:
                        result = {
                            "error": "missing arguments"
                        }
                    else:
                        result = calculate(
                            args["expression"]
                        )

                else:

                    result = {
                        "error": "unknown tool"
                    }

            elapsed = round(
                time.time() - start,
                6
            )

            logs.append(
                {
                    "round": round_num + 1,
                    "tool": tool_name,
                    "arguments": args,
                    "result": result,
                    "seconds": elapsed,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
            )

    print(f"Input tokens: {total_input}")
    print(f"Output tokens: {total_output}")
    print(
        f"Total seconds: "
        f"{round(time.time() - question_start, 2)}")

    return "UNANSWERED"

def load_questions():

    with open(
        "data/questions.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

if __name__ == "__main__":

    questions = load_questions()

    for q in questions:

        print(f"\nRunning {q['id']}")

        answer = run_question(
            question_id=q["id"],
            question=q["question"]
        )

        print(answer)