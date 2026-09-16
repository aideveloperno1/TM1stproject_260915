"""검토 규칙 원본(resources/rules/review_rules.json)을 읽는다.

문구·대안·문서 반영 위치는 JSON이 원본이고, 조건 판단은 규칙 ID별 파이썬 함수가 맡는다.
사람이 읽는 설명은 docs/review_rules.md이며 규칙 ID가 서로 같아야 한다.
"""

import json
from dataclasses import dataclass
from functools import cache
from typing import Literal

from ..paths import RESOURCES_DIR

RULES_FILE = RESOURCES_DIR / "rules" / "review_rules.json"
SUPPORTED_VERSIONS = frozenset({"1.0"})

RuleScope = Literal["implement", "basic", "example", "future"]

SCOPE_LABELS: dict[RuleScope, str] = {
    "implement": "검토 구현",
    "basic": "기본 검토",
    "example": "분석 예시",
    "future": "향후 기능",
}

# 문구에 쓰지 않는 단어 (판정·단정 표현). docs/review_rules.md 공통 원칙
FORBIDDEN_WORDS = ("문제", "오류", "위험", "실패", "성공", "잘못")


SECTION_NUMBERS = range(1, 9)
DOCUMENT_MODES = ("append", "replace")


@dataclass(frozen=True)
class OptionDocument:
    """대안을 채택했을 때 보완 기획안에 들어갈 문장 (5보완기획안계획.md 3장)."""

    section: int
    mode: str
    lines: tuple[str, ...]
    replace_key: str | None = None
    appendix: str | None = None


@dataclass(frozen=True)
class OptionSpec:
    id: str
    title: str
    where: str
    need: str
    load: str
    execution_fields: tuple[str, ...]
    document: OptionDocument | None = None


@dataclass(frozen=True)
class RuleInfo:
    id: str
    title: str
    scope: RuleScope
    summary: str
    messages: dict[str, str]
    options: tuple[OptionSpec, ...]
    related_fields: tuple[str, ...]
    document_targets: tuple[str, ...]
    merge_group: str | None

    @property
    def scope_label(self) -> str:
        return SCOPE_LABELS[self.scope]

    def message(self, key: str, **values: object) -> str:
        """JSON 문구에 값을 채운다. 없는 키는 파일 오류로 본다."""
        try:
            template = self.messages[key]
        except KeyError:
            raise KeyError(f"{self.id} 규칙에 '{key}' 문구가 없습니다 (review_rules.json)") from None
        return template.format(**values) if values else template

    def option(self, option_id: str) -> OptionSpec | None:
        return next((o for o in self.options if o.id == option_id), None)


@cache
def _rules_file() -> dict:
    data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
    if data.get("version") not in SUPPORTED_VERSIONS:
        raise ValueError(f"지원하지 않는 규칙 파일 버전: {data.get('version')}")
    return data


def _parse_document(rule_id: str, option: dict) -> OptionDocument | None:
    data = option.get("document")
    if data is None:
        raise ValueError(f"{rule_id} {option['id']} 대안에 문서 문장(document)이 없습니다 (review_rules.json)")
    if data["section"] not in SECTION_NUMBERS:
        raise ValueError(f"{rule_id} {option['id']}: 알 수 없는 장 번호 {data['section']}")
    if data["mode"] not in DOCUMENT_MODES:
        raise ValueError(f"{rule_id} {option['id']}: 알 수 없는 반영 방식 {data['mode']}")
    if data["mode"] == "replace" and not data.get("replace_key"):
        raise ValueError(f"{rule_id} {option['id']}: 교체 방식에는 replace_key가 필요합니다")
    return OptionDocument(
        section=data["section"],
        mode=data["mode"],
        lines=tuple(data["lines"]),
        replace_key=data.get("replace_key"),
        appendix=data.get("appendix"),
    )


@cache
def load_rule_catalog() -> tuple[RuleInfo, ...]:
    data = _rules_file()
    groups = data.get("merge_groups", {})

    rules = []
    for item in data["rules"]:
        if item["scope"] not in SCOPE_LABELS:
            raise ValueError(f"알 수 없는 규칙 범위: {item['id']} {item['scope']}")
        if item.get("merge_group") and item["merge_group"] not in groups:
            # 묶음 이름은 보완 기획안에 그대로 실린다. 내부 키가 사용자에게 보이지 않게 막는다
            raise ValueError(f"{item['id']}: 묶음 {item['merge_group']}의 한글 이름이 없습니다 (merge_groups)")
        options = tuple(
            OptionSpec(
                id=o["id"],
                title=o["title"],
                where=o["where"],
                need=o["need"],
                load=o["load"],
                execution_fields=tuple(o.get("execution_fields", ())),
                document=_parse_document(item["id"], o),
            )
            for o in item.get("options", ())
        )
        rules.append(
            RuleInfo(
                id=item["id"],
                title=item["title"],
                scope=item["scope"],
                summary=item["summary"],
                messages=dict(item.get("messages", {})),
                options=options,
                related_fields=tuple(item.get("related_fields", ())),
                document_targets=tuple(item.get("document_targets", ())),
                merge_group=item.get("merge_group"),
            )
        )
    return tuple(rules)


@cache
def merge_group_labels() -> dict[str, str]:
    """묶음 키 → 사람이 읽는 이름. 화면과 보완 기획안이 함께 쓴다."""
    load_rule_catalog()  # 이름이 빠진 묶음은 여기서 걸러진다
    return dict(_rules_file().get("merge_groups", {}))


def merge_group_label(group: str) -> str:
    return merge_group_labels().get(group, group)


@cache
def rules_by_id() -> dict[str, RuleInfo]:
    return {rule.id: rule for rule in load_rule_catalog()}


def get_rule(rule_id: str) -> RuleInfo:
    return rules_by_id()[rule_id]
