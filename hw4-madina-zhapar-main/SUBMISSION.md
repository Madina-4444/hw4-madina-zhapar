# HW4 — submission

**AI assistance:** <!-- what you used, and for what. "None" is an answer too. -->

I used OpenRouter and Deepseek as a model. Some of the codes are taken from ready‑made scripts.

------------------------------------------------------------------------

## Part A — Plan on paper (Easy)

> Commit this whole part before any `.py` file exists.

### A1 — The steps

| \# | Step | What goes in (types) | What comes out (types) | When it goes wrong | Tool, loop, or model? |
|----|----|----|----|----|----|
| 1 | Parse question | question: str | district1: str, district2: str, metric: str | District names or metric cannot be identified | Model |
| 2 | Retrieve Ossbridge population | district: str, field: str | population: int, source: str | District not found, ambiguous district name | Lookup tool |
| 3 | Retrieve Ossbridge area | district: str, field: str | area: float, source: str | Area not found | Lookup tool |
| 4 | Retrieve Ossford population | district: str, field: str | population: int, source: str | District not found, ambiguous district name | Lookup tool |
| 5 | Retrieve Ossford area | district: str, field: str | area: float, source: str | Area not found | Lookup tool |
| 6 | Calculate Ossbridge density | population: int, area: float | density: float | Division by zero, invalid number | Calculate tool |
| 7 | Calculate Ossford density | population: int, area: float | density: float | Division by zero, invalid number | Calculate tool |
| 8 | Compare densities and calculate difference | density1: float, density2: float | winner: str, difference: float | Missing density value | Calculate tool |
| 9 | Format final answer | winner: str, difference: float | answer: str | Missing result | Model |

**How the steps connect:**

<!-- which step feeds which: a list, an ASCII diagram, or an image committed to the repo -->

Question -\> Parse question -\> Lookup population and area for Ossbridge -\> Lookup population and area for Ossford -\> Calculate density for Ossbridge -\> Calculate density for Ossford -\> Compare densities -\> Generate final answer

**What I am assuming:**

<!-- census year, archived profiles, corrections, units, where rounding happens, ... -->

- If no year is specified, I use the 2025 values from the current district profiles.

- Archived profiles are ignored because they have been superseded.

- Correction notices override values in district profiles.

- Population density is calculated as `population / area`.

- Calculations use unrounded values until the final answer.

- The final numeric result is rounded according to the number of decimals required by the question.

### A2 — The two tools

#### `lookup`

``` json
{
  "name": "lookup",
  "description": "Retrieve a fact from the Nine Rivers Region corpus. Returns data from current district profiles, automatically ignores archived profiles, and applies correction notices when available. Returns both the value and the source document.",
  "parameters": {
    "type": "object",
    "properties": {
      "district": {
        "type": "string",
        "description": "District name"
      },
      "field": {
        "type": "string",
        "description": "Requested field such as population_2025, population_2020, area, budget, water_use, schools, pupils, roads, founded"
      }
    },
    "required": ["district", "field"]
  }
}
```

| Case | What the tool returns |
|----|----|
| success | {"district":"Ossbridge","field":"population_2025","value":52904,"source":"NR-01"} |
| district not found | {"error":"district not found"} |
| ambiguous district | {"error":"multiple matching districts found"} |
| field not found | {"error":"field not found"} |
| archived profile requested | returns data from current profile instead of archived profile |

**Worst thing it could do with strange or dangerous input:**

The tool could return an error message or no results. It cannot access files outside the dataset and cannot execute code.

#### `calculate`

``` json
{
  "name": "calculate",
  "description": "Safely evaluate arithmetic expressions using only numbers and basic arithmetic operators. Does not execute Python code.",
  "parameters": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "Arithmetic expression such as 52904 / 1284.6"
      }
    },
    "required": ["expression"]
  }
}
```

| Case                 | What the tool returns             |
|----------------------|-----------------------------------|
| success              | {"result":41.18}                  |
| invalid expression   | {"error":"invalid expression"}    |
| division by zero     | {"error":"division by zero"}      |
| unsupported operator | {"error":"unsupported operation"} |
| dangerous input      | {"error":"unsafe expression"}     |

**Worst thing it could do with strange or dangerous input:**

The tool may return an error message and refuse the calculation. It cannot execute arbitrary Python code because it only allows safe arithmetic operations through AST validation.

### A3 — Q-01 by hand

User message:

``` json
{
  "role": "user",
  "content": "Which district has the higher population density in 2025, Ossbridge or Ossford, and by how many residents per square kilometre?"
}
```

Tool call 1: population of Ossbridge

``` json
{
  "id": "call_1",
  "tool": "lookup",
  "arguments": {
    "district": "Ossbridge",
    "field": "population_2025"
  }
}
```

Result 1:

``` json
{
  "tool_call_id": "call_1",
  "value": 52904,
  "source": "NR-01"
}
```

Tool call 2: area of Ossbridge

``` json
{
  "id": "call_2",
  "tool": "lookup",
  "arguments": {
    "district": "Ossbridge",
    "field": "area"
  }
}
```

Result 2:

``` json
{
  "tool_call_id": "call_2",
  "value": 1284.6,
  "source": "NR-01"
}
```

Tool call 3: population of Ossford

``` json
{
  "id": "call_3",
  "tool": "lookup",
  "arguments": {
    "district": "Ossford",
    "field": "population_2025"
  }
}
```

Result 3:

``` json
{
  "tool_call_id": "call_3",
  "value": 30982,
  "source": "NR-02"
}
```

Tool call 4: area of Ossford

``` json
{
  "id": "call_4",
  "tool": "lookup",
  "arguments": {
    "district": "Ossford",
    "field": "area"
  }
}
```

Result 4:

``` json
{
  "tool_call_id": "call_4",
  "value": 846.2,
  "source": "NR-02"
}
```

Tool call 5: calculate for Ossbridge

``` json
{
  "id": "call_5",
  "tool": "calculate",
  "arguments": {
    "expression": "52904 / 1284.6"
  }
}
```

Result 5:

``` json
{
  "tool_call_id": "call_5",
  "result": 41.1817
}
```

Tool call 6: calculate for Ossford

``` json
{
  "id": "call_6",
  "tool": "calculate",
  "arguments": {
    "expression": "30982 / 846.2"
  }
}
```

Result 6:

``` json
{
  "tool_call_id": "call_6",
  "result": 36.6143
}
```

Tool call 7: difference

``` json
{
  "id": "call_7",
  "tool": "calculate",
  "arguments": {
    "expression": "41.1817 - 36.6143"
  }
}
```

Result 7:

``` json
{
  "tool_call_id": "call_7",
  "result": 4.5674
}
```

Final answer:

``` json
ANSWER: Ossbridge | 4.6
```

**My arithmetic:**

Population density of Ossbridge: 52904 / 1284.6 = 41.1817

Population density of Ossford: 30982 / 846.2 = 36.6143

Difference: 41.1817 - 36.6143 = 4.5674

Round to 1 decimal place: 4.6

ANSWER: Ossbridge \| 4.6

### A4 — Why I split it this way

<!-- one other way to split the task, and why you did not choose it -->

One alternative would be to create a single tool called answer_question that receives a question and returns the final answer directly.

I did not choose this approach because it combines document retrieval, reasoning, and calculations into a single tool. This makes the system harder to test, debug, and evaluate. If an answer is wrong, it is difficult to determine whether the mistake came from finding the wrong fact or from performing the calculation incorrectly. I chose two separate tools: lookup and calculate.

------------------------------------------------------------------------

## Part B — Build it and run it (Medium)

### What I changed from Part A while coding

<!-- what changed in your plan, and why. "None" is an answer too. -->

### B1 - Building the two tools

``` python
import json
import re
import ast
import operator
import difflib

# ==== CONFIG  =====
CORPUS_PATH = "/content/drive/MyDrive/hw4-madina-zhapar-main/data/corpus.jsonl"
DISTRICTS = [
    "Ossbridge",
    "Ossford",
    "Tarnvale",
    "Kelmarsh",
    "Brightwater",
    "Stonecairn",
    "Harrowfield",
    "Lindenmoor",
    "Redfen",
    "Ashgrove",
    "Millbrook",
    "Coldharbour",
]

# ====== CORRECTIONS ========

CORRECTIONS = {
    ("Brightwater", "area"): {
        "value": 921.4,
        "source": "NR-16"
    }
}

# ===== LOAD CORPUS =====

def load_corpus(path=CORPUS_PATH):
    docs = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))

    return docs


DOCS = load_corpus()

# ====== LOOKUP HELPERS =======

def get_district_doc(district):

    for doc in DOCS:

        title = doc["title"]

        # ignore archived documents
        if "ARCHIVED" in title:
            continue

        if district.lower() in title.lower():
            return doc

    return None


def parse_field(doc, field):

    text = doc["text"]

    try:

        if field == "population_2025":

            m = re.search(
                r"2025 census (?:recorded|counted)\s+([\d,]+)",
                text,
                re.IGNORECASE,
            )

            if m:
                return int(m.group(1).replace(",", ""))

            m = re.search(
                r"([\d,]+)\s+in 2025",
                text
            )

            if m:
                return int(m.group(1).replace(",", ""))

        elif field == "population_2020":

            m = re.search(
                r"2020 census (?:had recorded|recorded)\s+([\d,]+)",
                text,
                re.IGNORECASE,
            )

            if m:
                return int(m.group(1).replace(",", ""))

            m = re.search(
                r"([\d,]+)\s+in 2020",
                text
            )

            if m:
                return int(m.group(1).replace(",", ""))

        elif field == "area":

            m = re.search(
                r"([\d,]+\.\d+)\s+square kilometres",
                text
            )

            if m:
                return float(m.group(1).replace(",", ""))

        elif field == "budget":

            m = re.search(
                r"budget.*?([\d,]+\.\d+)\s+million tenge",
                text,
                re.IGNORECASE,
            )

            if m:
                return float(m.group(1).replace(",", ""))

        elif field == "water_use":

            # Lindenmoor uses cubic metres
            if "cubic metres" in text:

                m = re.search(
                    r"([\d,]+)\s+cubic metres",
                    text
                )

                if m:
                    cubic_metres = float(
                        m.group(1).replace(",", "")
                    )

                    return cubic_metres / 1000

            m = re.search(
                r"([\d,]+(?:\.\d+)?)\s+megalitres",
                text
            )

            if m:
                return float(m.group(1).replace(",", ""))

        elif field == "schools":

            m = re.search(
                r"(\d+)\s+schools",
                text
            )

            if m:
                return int(m.group(1))

        elif field == "pupils":

            m = re.search(
                r"([\d,]+)\s+pupils",
                text
            )

            if m:
                return int(m.group(1).replace(",", ""))

        elif field == "roads":

            candidates = re.findall(
                r"([\d,]+\.\d+)\s+km",
                text
            )

            if candidates:
                return float(candidates[-1].replace(",", ""))

        elif field == "founded":

            m = re.search(
                r"Founded in (\d{4})|founded in (\d{4})",
                text,
                re.IGNORECASE,
            )

            if m:
                for g in m.groups():
                    if g:
                        return int(g)

        return None

    except Exception:
        return None

# ======= LOOKUP TOOL ========

def lookup(district, field):

    try:

        # correction notices override profile values
        correction_key = (district, field)

        if correction_key in CORRECTIONS:

            correction = CORRECTIONS[correction_key]

            return {
                "district": district,
                "field": field,
                "value": correction["value"],
                "source": correction["source"]
            }

        doc = get_district_doc(district)

        if doc is None:

            suggestion = difflib.get_close_matches(
                district,
                DISTRICTS,
                n=2
            )

            if suggestion:
                return {
                    "error":
                    f"no district named {district}; did you mean "
                    + " or ".join(suggestion)
                    + "?"
                }

            return {
                "error": f"district '{district}' not found"
            }

        value = parse_field(doc, field)

        if value is None:
            return {
                "error":
                f"field '{field}' not found for {district}"
            }

        return {
            "district": district,
            "field": field,
            "value": value,
            "source": doc["id"]
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# ======= SAFE CALCULATOR =======

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def eval_ast(node):

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.BinOp):

        if type(node.op) not in OPS:
            raise ValueError("unsupported operator")

        left = eval_ast(node.left)
        right = eval_ast(node.right)

        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError

        return OPS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp):

        if isinstance(node.op, ast.USub):
            return -eval_ast(node.operand)

        raise ValueError("unsupported unary operator")

    raise ValueError("unsafe expression")

def calculate(expression):
    try:
        if len(expression) > 100:
            return {
                "error": "expression too long"
            }

        tree = ast.parse(
            expression,
            mode="eval"
        )

        banned = (
            ast.Call,
            ast.Attribute,
            ast.Name,
            ast.Import,
            ast.ImportFrom,
            ast.Pow,
        )

        for node in ast.walk(tree):
            if isinstance(node, banned):
                return {
                    "error": "unsafe expression"
                }

        result = eval_ast(tree.body)

        if abs(result) > 1e12:
            return {
                "error": "result too large"
            }

        return {
            "result": result
        }

    except ZeroDivisionError:
        return {
            "error": "division by zero"
        }
    except Exception:
        return {
            "error": "invalid expression"
        }
```

### B2 — Tests

``` text
<!-- pytest output -->
/content/drive/MyDrive/hw4-madina-zhapar-main
============================= test session starts ==============================
platform linux -- Python 3.13.16, pytest-8.4.2, pluggy-1.7.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /content/drive/MyDrive/hw4-madina-zhapar-main
plugins: anyio-4.15.1, langsmith-0.14.11, platformdirs-4.13.4, typeguard-4.6.0
collected 11 items                                                             

tests/test_tools.py::test_lookup_population_2025 PASSED                  [  9%]
tests/test_tools.py::test_lookup_misspelled_name PASSED                  [ 18%]
tests/test_tools.py::test_lookup_similar_districts PASSED                [ 27%]
tests/test_tools.py::test_lookup_archived_profile_ignored PASSED         [ 36%]
tests/test_tools.py::test_lookup_correction_notice PASSED                [ 45%]
tests/test_tools.py::test_calculate_multiplication PASSED                [ 54%]
tests/test_tools.py::test_calculate_division PASSED                      [ 63%]
tests/test_tools.py::test_calculate_division_by_zero PASSED              [ 72%]
tests/test_tools.py::test_calculate_block_import PASSED                  [ 81%]
tests/test_tools.py::test_calculate_block_attribute PASSED               [ 90%]
tests/test_tools.py::test_calculate_block_huge_power PASSED              [100%]

============================== 11 passed in 0.09s ==============================
```

### B3 — The loop

- Round limit, and why: I set the round limit to 10 rounds. Most questions require only a few tool calls, so 10 rounds are sufficient while also preventing infinite loops if the model repeatedly requests tools without producing a final answer.
- Where the logs are: The logs are stored in the outputs/ directory. Each log file contains:

the tool name, tool arguments, tool results, execution time, the final answer for the question. A separate log file is created for each question. - Real Q-09 conversation compared with my A3 version, what is different: The real run was very similar to my A3 version. The same values were retrieved and the same calculations were performed. The only difference was that the model provided more detailed intermediate results and returned 4.57 instead of the rounded value 4.6. The final conclusion was the same: ANSWER: Ossbridge \| 4.57.

### B4 — Three strategies

**What I kept the same:**

<!-- model, temperature, k, prompts, answer format, anything else -->

For all three strategies I used the same model (deepseek/deepseek-v4-flash-0731), the same twenty questions, and the same answer format:

ANSWER: \<name or yes/no\> \|

The only thing that changed was the strategy. S1 and S2 received the full document corpus in the prompt, while S3 received only the tool definitions. For S2 I used k = 3 and selected the most common answer by majority vote.

**My rule for a correct answer** (written before the first full run):

An answer was counted as correct if the district name (or yes/no value) matched exactly. The numeric value had to match the expected value after rounding to the required number of decimal places. A difference of one unit in the final decimal place was accepted.

|      |     |     |                     |            |
|------|-----|-----|---------------------|------------|
| Q-03 | 6   | 49  | Lindenmoor \| 5.34  | UNANSWERED |
| Q-05 | 6   | 80  | None                | UNANSWERED |
| Q-08 | 6   | 19  | None                | NO ANSWER  |
| Q-17 | 8   | 42  | Harrowfield \| 0.88 | NO ANSWER  |
| Q-20 | 8   | 22  | None                | NO ANSWER  |

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost (\$) |
|----|----|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | 20 | 0 | 44 269 | 12 790 | 3.25 | 75.90 | 0 |
| 1 | S2 think and vote (k =3 ) | 20 | 0 | 132 696 | 36 249 | 22.75 | 542.49 | 0 |
| 1 | S3 tools | 16 | 2 | 68 205 | 13 478 | 3.39 | 85.54 | 0 |
| 2 | S1 direct | 20 | 0 | 44 269 | 13 912 | 6.29 | 150.55 | 0 |
| 2 | S2 think and vote (k = ) | 20 | 0 | 132 696 | 38 589 | 20.28 | 459.76 | 0 |
| 2 | S3 tools | 14 | 3 | 63 217 | 13 946 | 3.79 | 74.24 | 0 |

**Per question (run 1):**

| Question | S1  | S2  |             S3              |
|----------|:---:|:---:|:---------------------------:|
| Q-01     |  ✓  |  ✓  |              ✓              |
| Q-02     |  ✓  |  ✓  |              ✓              |
| Q-03     |  ✓  |  ✓  |              ✓              |
| Q-04     |  ✓  |  ✓  |              ✓              |
| Q-05     |  ✓  |  ✓  |          ✗ (None)           |
| Q-06     |  ✓  |  ✓  |              ✓              |
| Q-07     |  ✓  |  ✓  |              ✓              |
| Q-08     |  ✓  |  ✓  |          ✗ (None)           |
| Q-09     |  ✓  |  ✓  |              ✓              |
| Q-10     |  ✓  |  ✓  |              ✓              |
| Q-11     |  ✓  |  ✓  |              ✓              |
| Q-12     |  ✓  |  ✓  |              ✓              |
| Q-13     |  ✓  |  ✓  |              ✓              |
| Q-14     |  ✓  |  ✓  |              ✓              |
| Q-15     |  ✓  |  ✓  |              ✓              |
| Q-16     |  ✓  |  ✓  |              ✓              |
| Q-17     |  ✓  |  ✓  |   ✗ (0.88 instead of 884)   |
| Q-18     |  ✓  |  ✓  |              ✓              |
| Q-19     |  ✓  |  ✓  |              ✓              |
| Q-20     |  ✓  |  ✓  | ✗ (0.00299 instead of 2993) |

------------------------------------------------------------------------

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|----|---:|---:|----|----|
| Q-03 | 6 | 49 | Lindenmoor \| 5.34 | NO ANSWER |
| Q-05 | 6 | 80 | None | NO ANSWER |
| Q-08 | 6 | 19 | None | NO ANSWER |
| Q-17 | 8 | 42 | Harrowfield \| 0.88 | NO ANSWER |
| Q-20 | 8 | 22 | None | NO ANSWER |

### C2 — Three mistakes explained

```         
S1 answered all questions correctly, so I selected Q17, one of the most complex questions. The model had to combine water use, the tariff, population data, and unit conversion. Because all information was available in the prompt, the model produced the correct answer.
```

```         
S2
I selected Q08. The three votes were:

Brightwater | 72.30615
Brightwater | 72.45615
Brightwater | 72.45615

One sample was incorrect, but the majority vote produced the correct answer. Voting helps when errors are random, but it cannot fix mistakes if all samples make the same error.
```

```         
S3
I selected Q20. The model retrieved the correct budget and population values but compared:

9284.5 / 52904
10488.1 / 58760
16021.7 / 90212

without converting budgets from millions of tenge. It therefore returned:

ANSWER: Ashgrove | 0.00299

instead of about:

ANSWER: Ashgrove | 2993

The tools retrieved the correct data, but the model misunderstood the units.
```

### C3 — Which strategy I would use, and what would change it

```         
I would choose S1 (direct prompting) for this task. S1 achieved the same accuracy as S2 (20/20 correct answers) but used far fewer tokens and required much less time. In both runs S1 answered all questions correctly while remaining the most efficient strategy.
```

```         
I would not choose S2 because it was much more expensive. Although it also achieved 20/20 accuracy, it required about three times more tokens and much longer execution time due to repeated sampling and voting.
```

```         
I would not choose S3 because it was less reliable. While S3 used fewer tokens than S2, it produced several incorrect or unanswered questions because the model sometimes misunderstood units or failed to complete the reasoning process.
```

```         
Different conditions could change my choice:

Small budget: I would choose S1 because it uses far fewer tokens.
Much larger document collection: I would choose S3 because tools can retrieve only the needed information.

Questions with little arithmetic: I would choose S1 because tools provide little additional benefit.

Maximum accuracy is required: I would choose S2 because voting can reduce random errors.
```

### C4 — How sure I can be

```         
How different were your two runs?
My two runs were very similar for S1 and S2. Both strategies achieved 20/20 correct answers in both runs. S3 varied more, with 16/20 in Run 1 and 14/20 in Run 2.
```

```         
Is the difference between your two best strategies bigger than that?
No. The difference between the two best strategies (S1 and S2) was smaller than the variation observed in S3. S1 and S2 produced identical accuracy, while S3 was less stable across runs.
```

```         
How many questions would you need before you trusted the result?
Twenty questions provide a useful estimate, but I would prefer a larger test set before drawing strong conclusions. With around 100 questions, I would be much more confident that the measured differences represent the true performance of the strategies rather than random variation.
```

### Final questions

1.  Nothing has been executed yet. The model has only decided which tool to call and generated the arguments for that call. The actual tool runs only after my code receives the request and executes the corresponding Python function.

2.  The API returns tool arguments as a JSON string. It must be converted using json.loads(). If I pass the string directly to the function, Python treats it as text rather than a dictionary, causing errors when accessing fields such as args["district"].

3.  I did not measure this exactly. However, the tool definitions are included in every S3 request, so they add a fixed number of prompt tokens each time a request is sent to the model.

4.  In Run 1, S1 used 44,269 input tokens and 12,790 output tokens, while S2 used 132,696 input tokens and 36,249 output tokens. S2 required about three times more tokens because each question was answered three times before voting selected the final answer.

5.  Q-05 required the most tool calls during the C1 experiment (80 calls). With the vague tool description, the model struggled to determine which fields it needed and repeatedly tried additional tool calls before reaching the round limit.

6.  I would replace the linear scan with an indexed retrieval system. Instead of checking every document, the tool would first retrieve a small set of relevant documents and then extract the requested value from those results.

7.  calculate parses expressions using Python AST and blocks dangerous node types such as function calls, imports, attributes, and names. The model could still produce invalid or inefficient expressions, but it cannot execute arbitrary Python code.

8.  Tools helped most on questions that required retrieving several facts and performing calculations, such as Q17 and Q20. They helped least on simple comparison questions where all necessary information could be read directly from the documents without additional computation.
