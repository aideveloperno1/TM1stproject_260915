"""검토 규칙 원본(resources/rules/review_rules.json)을 읽는다."""

import json
from dataclasses import dataclass
from functools import cache
from typing import Literal

from ..paths import RESOURCES_DIR

RULES_FILE = RESOURCES_DIR / "rules" / "review_rules.json"

RuleScope = Literal["implement", "basic", "example", "future"]

SCOPE_LABELS: dict[RuleScope, str] = {
    "implement": "검토 구현",
    "basic": "기본 검토",
    "example": "분석 예시",
    "future": "향후 기능",
}


@dataclass(frozen=True)
class RuleInfo:
    id: str
    title: str
    scope: RuleScope
    summary: str

    @property
    def scope_label(self) -> str:
        return SCOPE_LABELS[self.scope]


@cache
def load_rule_catalog() -> tuple[RuleInfo, ...]:
    data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
    rules = []
    for item in data["rules"]:
        if item["scope"] not in SCOPE_LABELS:
            raise ValueError(f"알 수 없는 규칙 범위: {item['id']} {item['scope']}")
        rules.append(RuleInfo(item["id"], item["title"], item["scope"], item["summary"]))
    return tuple(rules)
