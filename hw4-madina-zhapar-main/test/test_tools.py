import sys
import pytest

sys.path.append("/content/drive/MyDrive/hw4-madina-zhapar-main")

from tools import lookup, calculate

# =====================================================
# LOOKUP TESTS
# =====================================================

def test_lookup_population_2025():
    result = lookup("Ossbridge", "population_2025")

    assert result["value"] == 52904
    assert result["source"] == "NR-01"


def test_lookup_misspelled_name():
    result = lookup("Ossbrige", "population_2025")

    assert "error" in result
    assert "Ossbridge" in result["error"]


def test_lookup_similar_districts():
    ossbridge = lookup("Ossbridge", "population_2025")
    ossford = lookup("Ossford", "population_2025")

    assert ossbridge["value"] != ossford["value"]


def test_lookup_archived_profile_ignored():
    result = lookup("Tarnvale", "population_2025")

    assert result["source"] == "NR-03"
    assert result["value"] == 71388


def test_lookup_correction_notice():
    result = lookup("Brightwater", "area")

    assert result["value"] == 921.4
    assert result["source"] == "NR-16"


# =====================================================
# CALCULATE TESTS
# =====================================================

def test_calculate_multiplication():
    result = calculate("48317 * 1.0947")

    assert result["result"] == pytest.approx(
        52892.6199
    )


def test_calculate_division():
    result = calculate("52904 / 1284.6")

    assert result["result"] == pytest.approx(
        41.183247703565314
    )


def test_calculate_division_by_zero():
    result = calculate("10 / 0")

    assert result["error"] == "division by zero"


def test_calculate_block_import():
    result = calculate(
        "__import__('os').system('echo hi')"
    )

    assert "error" in result


def test_calculate_block_attribute():
    result = calculate("(1).__class__")

    assert "error" in result


def test_calculate_block_huge_power():
    result = calculate("9**9**9")

    assert "error" in result