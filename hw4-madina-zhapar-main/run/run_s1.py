import json
import os
import time
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


corpus = load_corpus()

questions = load_questions()

for q in questions:

    print(f"\nRunning {q['id']}")

    start = time.time()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
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

    elapsed = round(
        time.time() - start,
        3
    )

    print(
        response.choices[0]
        .message.content
    )

    print(
        f"Input tokens: "
        f"{response.usage.prompt_tokens}"
    )

    print(
        f"Output tokens: "
        f"{response.usage.completion_tokens}"
    )

    print(
        f"Seconds: {elapsed}"
    )