"""근거 레코드 선택과 지역 표시. 2단계 화면과 3단계 검토가 같은 기준을 쓰도록 한곳에 둔다.

입력 화면의 행정코드와 근거 파일 region_key의 연결 규칙(C-2)이 정해지기 전에는 전국만 사용한다.
"""

from __future__ import annotations

from ..evidence.loader import find_record
from ..evidence.schema import EvidenceFile, EvidenceRecord
from ..plan.models import PlanInput, RegionLevel
from ..plan.regions import region_label

NATIONAL_SCOPE_LABEL = "전국 참고 — 특정 지역의 진단이 아님"


def select_main_record(file: EvidenceFile) -> EvidenceRecord | None:
    return find_record(file, "national", "ALL")


def scope_label(record: EvidenceRecord | None) -> str | None:
    if record is None:
        return None
    if record.scope.geographic_scope == "national":
        return NATIONAL_SCOPE_LABEL
    return f"{record.scope.region_key} 범위 참고 — 선택 지역의 진단이 아님"


def region_note(plan: PlanInput) -> str | None:
    """입력 지역이 시도·시군구면 전국 자료를 지역 진단처럼 읽지 않도록 안내한다 (워크플로우 8-4)."""
    region = plan.region
    if region is None or region.level is RegionLevel.NATIONAL:
        return None
    return f"전국 참고 자료입니다. 선택한 {region_label(region)}의 소비를 진단한 결과가 아닙니다."
