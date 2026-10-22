import json
import re
import time
from collections import Counter

MODEL = "deepseek/deepseek-v4-flash-0731"


def load_corpus_text():
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

    if not text:
        return "NO ANSWER"

    m = re.search(
        r"ANSWER:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if m:
        return m.group(1).strip()

    return "NO ANSWER"


# =====================================================
# S1 DIRECT
# =====================================================

def strategy_s1(client, question):

    corpus = load_corpus_text()

    start = time.time()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Answer the question using the supplied documents.

End every answer with:

ANSWER: <name or yes/no> | <number>
"""
            },
            {
                "role": "user",
                "content":
                f"{corpus}\n\nQUESTION:\n{question}"
            }
        ]
    )

    elapsed = time.time() - start

    return {
        "answer":
        response.choices[0].message.content,

        "input_tokens":
        response.usage.prompt_tokens,

        "output_tokens":
        response.usage.completion_tokens,

        "seconds":
        round(elapsed, 3)
    }


# =====================================================
# S2 THINK + VOTE (k = 5)
# =====================================================

def strategy_s2(client, question):

    corpus = load_corpus_text()

    answers = []

    total_input = 0
    total_output = 0

    times = []

    raw_answers = []

    for _ in range(5):

        start = time.time()

        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": """
Think step by step.

Answer using the documents.

End every answer with:

ANSWER: <name or yes/no> | <number>
"""
                },
                {
                    "role": "user",
                    "content":
                    f"{corpus}\n\nQUESTION:\n{question}"
                }
            ]
        )

        elapsed = time.time() - start

        text = response.choices[0].message.content

        raw_answers.append(text)

        answer = extract_answer(text)

        answers.append(answer)

        total_input += response.usage.prompt_tokens

        total_output += response.usage.completion_tokens

        times.append(elapsed)

    winner = Counter(answers).most_common(1)[0][0]

    return {
        "answer": winner,
        "votes": answers,
        "raw_answers": raw_answers,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "seconds": round(sum(times), 3)
    }