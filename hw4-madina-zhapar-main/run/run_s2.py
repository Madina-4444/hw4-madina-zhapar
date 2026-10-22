import json
import os
import re
import time
from collections import Counter
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

MODEL = "deepseek/deepseek-v4-flash-0731"


def load_questions():
    with open(
        "data/questions.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def load_corpus():

    docs = []

    with open(
        "data/corpus.jsonl",
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            doc = json.loads(line)

            docs.append(
                f"{doc['id']}\n"
                f"{doc['title']}\n"
                f"{doc['text']}\n"
            )

    return "\n".join(docs)


def extract_answer(text):

    match = re.search(
        r"ANSWER:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return "NO ANSWER"


corpus = load_corpus()

questions = load_questions()

for q in questions:

    print(f"\nRunning {q['id']}")

    votes = []

    total_input = 0
    total_output = 0
    total_seconds = 0

    for i in range(3):

        start = time.time()

        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": """
Think step by step.

Answer using the supplied documents.

End every answer with:

ANSWER: <name or yes/no> | <number>
"""
                },
                {
                    "role": "user",
                    "content":
                    f"{corpus}\n\nQUESTION:\n{q['question']}"
                }
            ]
        )

        elapsed = time.time() - start

        answer = (
            response.choices[0]
            .message.content
        )

        votes.append(
            extract_answer(answer)
        )

        total_input += (
            response.usage.prompt_tokens
        )

        total_output += (
            response.usage.completion_tokens
        )

        total_seconds += elapsed

    winner = Counter(votes).most_common(1)[0][0]

    print("Votes:")
    print(votes)

    print("\nWinner:")
    print(winner)

    print(
        f"\nInput tokens: "
        f"{total_input}"
    )

    print(
        f"Output tokens: "
        f"{total_output}"
    )

    print(
        f"Total seconds: "
        f"{round(total_seconds, 2)}"
    )
