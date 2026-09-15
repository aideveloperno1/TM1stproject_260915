import copy
import json
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "evidence"

VALID_FIXTURES = [
    "amount_up_share_down",
    "amount_down_share_up",
    "same_direction",
    "flat_change",
    "prev_foreign_zero",
    "missing_month",
    "tiny_change",
    "known_only_differs",
    "large_amounts",
    "unknown_equals_total",
    "denominator_zero",
]


def fixture_path(name: str) -> Path:
    return FIXTURE_DIR / f"{name}.json"


def fixture_data(name: str) -> dict:
    return json.loads(fixture_path(name).read_text(encoding="utf-8"))


def base_data() -> dict:
    return copy.deepcopy(fixture_data("amount_up_share_down"))
