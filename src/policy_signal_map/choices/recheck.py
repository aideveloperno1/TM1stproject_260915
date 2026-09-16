"""원안이 바뀌었을 때 선택을 재확인 대상으로 표시하고, 사라진 질문의 선택을 보관한다.

(워크플로우 11장: 목표·지역·지표가 바뀌면 영향받는 선택을 재확인 필요로 바꾸고 최종 문서 생성 전에 확인받는다)
"""

from __future__ import annotations

from dataclasses import replace

from ..review.outcome import ReviewResult
from ..review.rules import rules_by_id
from .models import ArchivedChoice, ChoiceSet


def mark_recheck(choice_set: ChoiceSet, changed_fields: frozenset[str]) -> tuple[str, ...]:
    """바뀐 입력 항목과 관련 있는 선택만 재확인 대상으로 바꾼다."""
    if not changed_fields:
        return ()
    rules = rules_by_id()
    marked = []
    for key, choice in list(choice_set.choices.items()):
        related = set(rules[choice.rule_id].related_fields)
        if related & changed_fields:
            choice_set.choices[key] = replace(choice, needs_recheck=True)
            marked.append(key)
    return tuple(marked)


def archive_missing(choice_set: ChoiceSet, result: ReviewResult) -> tuple[str, ...]:
    """다시 실행한 검토에 없는 질문의 선택을 보관함으로 옮긴다 (조용히 사라지지 않게)."""
    current = {outcome.question_key for outcome in result.outcomes}
    archived = []
    for key in list(choice_set.choices):
        if key not in current:
            choice = choice_set.remove(key)
            if choice is not None:
                choice_set.archived.append(ArchivedChoice(choice))
                archived.append(key)
    return tuple(archived)


def sync_after_review(choice_set: ChoiceSet, result: ReviewResult, changed_fields: frozenset[str]) -> None:
    archive_missing(choice_set, result)
    mark_recheck(choice_set, changed_fields)
