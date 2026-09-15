"""테스트용 근거 파일 경계 사례 22개를 만든다.

실행: uv run python scripts/build_fixtures.py
사례 수치와 기대 결과: 1근거계산계층계획.md 6장. 모든 수치는 가상 규모다.
"""

from __future__ import annotations

import copy
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _evidence_builder import evidence_file, ok_month, record, status_month, write_json  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "evidence"
EVIDENCE_ID = "FX-01"


def _file(name: str, case: str, months: list[dict]) -> dict:
    return evidence_file([record(EVIDENCE_ID, months)], dataset_version=f"fixture-{name}", case=case)


# ---------------------------------------------------------------- 정상 사례 10개


def _valid_cases() -> dict[str, tuple[str, list[dict]]]:
    return {
        "amount_up_share_down": (
            "외국인 금액 증가, 전체 금액이 더 빠르게 증가 → 비교 A 반대 (8-5장 1행)",
            [ok_month("2026-01", 800, 10000, 1000), ok_month("2026-02", 900, 12000, 1200)],
        ),
        "amount_down_share_up": (
            "외국인 금액 감소, 전체 금액이 더 빠르게 감소 → 비교 A 반대 (8-5장 2행)",
            [ok_month("2026-01", 900, 12000, 1200), ok_month("2026-02", 800, 10000, 1000)],
        ),
        "same_direction": (
            "외국인 금액과 비중 모두 증가 → 반대 아님 (8-5장 3행)",
            [ok_month("2026-01", 800, 10000, 1000), ok_month("2026-02", 1000, 11000, 1100)],
        ),
        "flat_change": (
            "01→02 금액 변화 0, 02→03 비중 변화 0 → 반대 아님 (8-5장 4행)",
            [
                ok_month("2026-01", 800, 10000, 1000),
                ok_month("2026-02", 800, 11000, 1000),
                ok_month("2026-03", 1600, 22000, 2000),
            ],
        ),
        "prev_foreign_zero": (
            "이전 달 외국인 금액 0 → 증감률 계산 불가, 금액 차이는 유효 (8-5장 5행)",
            [
                ok_month("2026-01", 0, 10000, 1000, warnings=("외국인 집단 관측 행 없음 (실제 소비 0으로 단정하지 않음)",)),
                ok_month("2026-02", 500, 10000, 1000),
            ],
        ),
        "missing_month": (
            "02월 자료 없음 → 01→02, 02→03 보류, 01→03을 잇지 않음 (8-5장 6행)",
            [
                ok_month("2026-01", 800, 10000, 1000),
                status_month("2026-02", "no_data", warnings=("해당 월 관측 행 없음",)),
                ok_month("2026-03", 900, 12000, 1200),
            ],
        ),
        "tiny_change": (
            "비중 변화 −0.0004%p의 반대 방향 → 방향 유지, 표시는 0.01%p 미만",
            [ok_month("2026-01", 800, 10000, 1000), ok_month("2026-02", 801, 10013, 1000)],
        ),
        "known_only_differs": (
            "전체 분모 비중 감소, 미상 제외 비중 증가 → 비교 B만 반대",
            [ok_month("2026-01", 800, 10000, 1000), ok_month("2026-02", 790, 10500, 2000)],
        ),
        "large_amounts": (
            "소수점 계산은 비중 변화 없음, 정수 교차곱은 증가 → 교차곱 방식 필요",
            [
                ok_month("2026-01", 70_000_000_000_000, 1_000_000_000_000_000, 50_000_000_000_000),
                ok_month("2026-02", 70_000_000_000_004, 1_000_000_000_000_057, 50_000_000_000_000),
            ],
        ),
        "unknown_equals_total": (
            "02월 미상 금액 = 전체 금액 → 미상 제외 비중 null, 비교 B 계산 불가",
            [ok_month("2026-01", 800, 10000, 1000), ok_month("2026-02", 0, 5000, 5000)],
        ),
    }


# ---------------------------------------------------------------- 오류 사례 12개 (정상 ①에서 한 곳만 바꿈)


def _base() -> dict:
    case, months = _valid_cases()["amount_up_share_down"]
    return _file("base", case, months)


def _month(data: dict, index: int) -> dict:
    return data["records"][0]["months"][index]


def _set_no_data_with_zero(data: dict) -> None:
    m = _month(data, 1)
    m.update(
        calculation_status="no_data",
        foreign_amount=0,
        total_amount=0,
        unknown_amount=0,
        transaction_count=None,
        foreign_share_pct=None,
        known_only_share_pct=None,
        unknown_share_pct=None,
    )


def _set_mixed_data_kind(data: dict) -> None:
    real = copy.deepcopy(data["records"][0])
    real["evidence_id"] = "FX-02-REAL-LABEL-ONLY"
    real["data_kind"] = "real"  # 수치는 가짜이며 이름표만 real이다
    data["records"].append(real)


def _set_denominator_zero(data: dict) -> None:
    _month(data, 1).update(
        calculation_status="invalid_denominator",
        foreign_amount=0,
        total_amount=0,
        unknown_amount=0,
        transaction_count=0,
        foreign_share_pct=None,
        known_only_share_pct=None,
        unknown_share_pct=None,
        warnings=["전체 금액 0으로 비중 계산 불가"],
    )


def _invalid_cases() -> dict[str, tuple[str, Callable[[dict], None]]]:
    return {
        "invalid_status_value": (
            "02월 calculation_status가 목록에 없는 값",
            lambda d: _month(d, 1).update(calculation_status="okay"),
        ),
        "invalid_applicability": (
            "R07 applicability status가 목록에 없는 값",
            lambda d: d["records"][0]["applicability"]["R07"].update(status="maybe"),
        ),
        "missing_reason": (
            "R06 applicability reason이 빈 문자열",
            lambda d: d["records"][0]["applicability"]["R06"].update(reason=""),
        ),
        "relation_broken": (
            "02월 외국인+미상 금액이 전체 금액보다 큼",
            lambda d: _month(d, 1).update(unknown_amount=11200),
        ),
        "negative_amount": (
            "01월 외국인 금액 음수",
            lambda d: _month(d, 0).update(foreign_amount=-800),
        ),
        "decimal_amount": (
            "01월 외국인 금액이 소수",
            lambda d: _month(d, 0).update(foreign_amount=800.5),
        ),
        "no_data_with_zero": (
            "02월 자료 없음인데 금액을 0으로 적음 (비중·건수는 null)",
            _set_no_data_with_zero,
        ),
        "month_omitted": (
            "기간은 03월까지인데 03월 항목이 없음",
            lambda d: d["records"][0]["scope"].update(period_end="2026-03"),
        ),
        "schema_version_unsupported": (
            "지원하지 않는 형식 버전",
            lambda d: d.update(schema_version="1.0"),
        ),
        "mixed_data_kind": (
            "합성 레코드와 실제 표시 레코드가 한 파일에 섞임 (실제 레코드 수치도 가짜)",
            _set_mixed_data_kind,
        ),
        "denominator_zero": (
            "02월 전체 금액 0, invalid_denominator → 로드 성공, 비교는 보류",
            _set_denominator_zero,
        ),
        "national_region_key_wrong": (
            "전국 범위인데 region_key가 ALL이 아님",
            lambda d: d["records"][0]["scope"].update(region_key="11"),
        ),
    }


def build_all() -> dict[str, dict]:
    files: dict[str, dict] = {}
    for name, (case, months) in _valid_cases().items():
        files[f"{name}.json"] = _file(name, case, months)
    for name, (case, mutate) in _invalid_cases().items():
        data = _base()
        data["_case"] = case
        data["dataset_version"] = f"fixture-{name}"
        mutate(data)
        files[f"{name}.json"] = data
    return files


def main() -> int:
    files = build_all()
    for name, data in files.items():
        write_json(OUT_DIR / name, data)
    stale = sorted(p.name for p in OUT_DIR.glob("*.json") if p.name not in files)
    print(f"경계 사례 {len(files)}개 -> {OUT_DIR}")
    if stale:
        print("생성 목록에 없는 파일 (확인 후 삭제):", ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
