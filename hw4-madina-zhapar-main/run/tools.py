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

        # ==========================
        # POPULATION 2025
        # ==========================

        if field == "population_2025":

            patterns = [

                r"2025 census (?:recorded|counted)\s+([\d,]+)",

                r"Census population:\s*[\d,]+\s+in 2020 and\s+([\d,]+)\s+in 2025",

                r"([\d,]+)\s+in 2025"
            ]

            for pattern in patterns:

                m = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if m:
                    return int(
                        m.group(1).replace(",", "")
                    )

        # ==========================
        # POPULATION 2020
        # ==========================

        elif field == "population_2020":

            patterns = [

                r"2020 census (?:had recorded|recorded)\s+([\d,]+)",

                r"up from\s+([\d,]+)\s+at the 2020 census",

                r"([\d,]+)\s+at the 2020 census",

                r"Census population:\s*([\d,]+)\s+in 2020",

                r"([\d,]+)\s+in 2020"
            ]

            for pattern in patterns:

                m = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if m:
                    return int(
                        m.group(1).replace(",", "")
                    )

        # ==========================
        # AREA
        # ==========================

        elif field == "area":

            m = re.search(
                r"([\d,]+\.\d+)\s+square kilometres",
                text,
                re.IGNORECASE
            )

            if m:
                return float(
                    m.group(1).replace(",", "")
                )

        # ==========================
        # BUDGET
        # ==========================

        elif field == "budget":

            m = re.search(
                r"budget.*?([\d,]+\.\d+)\s+million tenge",
                text,
                re.IGNORECASE
            )

            if m:
                return float(
                    m.group(1).replace(",", "")
                )

        # ==========================
        # WATER USE
        # ==========================

        elif field == "water_use":

            if "cubic metres" in text:

                m = re.search(
                    r"([\d,]+)\s+cubic metres",
                    text,
                    re.IGNORECASE
                )

                if m:

                    cubic_metres = float(
                        m.group(1).replace(",", "")
                    )

                    return cubic_metres / 1000

            m = re.search(
                r"([\d,]+(?:\.\d+)?)\s+megalitres",
                text,
                re.IGNORECASE
            )

            if m:
                return float(
                    m.group(1).replace(",", "")
                )

        # ==========================
        # SCHOOLS
        # ==========================

        elif field == "schools":

            m = re.search(
                r"(\d+)\s+schools",
                text,
                re.IGNORECASE
            )

            if m:
                return int(m.group(1))

        # ==========================
        # PUPILS
        # ==========================

        elif field == "pupils":

            m = re.search(
                r"([\d,]+)\s+pupils",
                text,
                re.IGNORECASE
            )

            if m:
                return int(
                    m.group(1).replace(",", "")
                )

        # ==========================
        # ROADS
        # ==========================

        elif field == "roads":

            patterns = [

                r"road network is\s+([\d,]+\.\d+)\s+km",

                r"keeps\s+([\d,]+\.\d+)\s+km",

                r"maintains\s+([\d,]+\.\d+)\s+km"
            ]

            for pattern in patterns:

                m = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if m:
                    return float(
                        m.group(1).replace(",", "")
                    )

        # ==========================
        # FOUNDED
        # ==========================

        elif field == "founded":

            m = re.search(
                r"founded in (\d{4})",
                text,
                re.IGNORECASE
            )

            if m:
                return int(m.group(1))

        elif field == "water_tariff":
            for doc in DOCS:
                if doc["id"] == "NR-15":
                    m = re.search(
                        r"([\d.]+)\s+tenge per cubic metre",
                        doc["text"]
                    )
                    if m:
                        return float(m.group(1))

        return None

    except Exception:
        return None

# ======= LOOKUP TOOL ========

def lookup(district, field):

    FIELD_ALIASES = {
        "population": "population_2025",
        "water": "water_use",
        "water_usage": "water_use",
        "road_length": "roads",
        "road_network": "roads",
        "year_founded": "founded"
    }

    field = FIELD_ALIASES.get(field, field)

    try:
        # water tariff comes from NR-15
        if field == "water_tariff":
            for doc in DOCS:
                if doc["id"] == "NR-15":
                    m = re.search(
                        r"([\d.]+)\s+tenge per cubic metre",
                        doc["text"]
                    )
                    if m:
                        return {
                            "district": district,
                            "field": field,
                            "value": float(m.group(1)),
                            "source": "NR-15"
                        }

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
