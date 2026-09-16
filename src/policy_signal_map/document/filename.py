"""저장 파일 이름 (checks.md 결정: 보완기획안_{사업명}_{날짜}.md)."""

from __future__ import annotations

import re
from datetime import date

FORBIDDEN = re.compile(r'[\\/:*?"<>|\r\n\t]')
MAX_NAME = 60


def document_filename(plan_name: str, today: date) -> str:
    cleaned = FORBIDDEN.sub("", plan_name).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)[:MAX_NAME].strip("_")
    cleaned = cleaned.rstrip(". ")  # 윈도에서 마침표·공백으로 끝나는 이름은 저장이 막힌다
    stamp = today.strftime("%Y%m%d")
    return f"보완기획안_{cleaned}_{stamp}.md" if cleaned else f"보완기획안_{stamp}.md"
