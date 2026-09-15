"""화면 시연용 합성 근거 파일을 만든다.

실행: uv run python scripts/build_demo_evidence.py
수치와 구간 설계 의도: 1근거계산계층계획.md 9장. 실제 카드 분석 수치를 쓰지 않는다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _evidence_builder import evidence_file, ok_month, record, status_month, write_json  # noqa: E402

from policy_signal_map.evidence.compare import compare_record  # noqa: E402
from policy_signal_map.evidence.loader import load_evidence  # noqa: E402
from policy_signal_map.evidence.summary import summarize_pairs  # noqa: E402
from policy_signal_map.paths import RESOURCES_DIR  # noqa: E402

OUT_PATH = RESOURCES_DIR / "evidence" / "review_evidence_demo_v1.json"
DATASET_VERSION = "demo-001"


def build() -> dict:
    national = record(
        "DEMO-R07-NATIONAL",
        [
            ok_month("2026-01", 820, 10000, 450),  # 01→02 금액 감소·비중 증가 (반대)
            ok_month("2026-02", 790, 9400, 520),  # 02→03 금액 증가·비중 감소 (반대)
            ok_month("2026-03", 860, 10300, 560),  # 03→04 같은 방향
            ok_month("2026-04", 905, 10600, 540),  # 04→05 같은 방향, 비중 변화 0.01%p 미만
            ok_month("2026-05", 930, 10890, 900),  # 05→06 같은 방향
            ok_month("2026-06", 880, 10700, 760),
        ],
    )
    sido_hold = record(
        "DEMO-R07-SIDO-HOLD",
        [
            ok_month("2026-01", 120, 1500, 90),
            ok_month("2026-02", 135, 1580, 100),
            status_month("2026-03", "no_data", warnings=("해당 월 관측 행 없음",)),
            ok_month("2026-04", 128, 1540, 95),
            status_month("2026-05", "invalid_denominator", F=0, T=0, U=0, C=0, warnings=("전체 금액 0으로 비중 계산 불가",)),
            ok_month("2026-06", 131, 1560, 98),
        ],
        geographic_scope="sido",
        region_key="DEMO-SIDO-A",
        applicability={
            "R07": {"status": "needs_review", "reason": "합성 보류 예시: 시도 자료의 누락 월이 많아 비교 결론 보류"},
            "R06": {"status": "blocked", "reason": "업종·월 보정 자료 없음"},
            "R02": {"status": "blocked", "reason": "지역 기준 미확인"},
        },
        limitations=["합성 자료", "가상 시도 예시이며 실제 지역이 아님", "누락 월을 0으로 해석하지 않음"],
    )
    return evidence_file([national, sido_hold], dataset_version=DATASET_VERSION)


def main() -> int:
    write_json(OUT_PATH, build())
    result = load_evidence(OUT_PATH)
    if result.warnings:
        print("경고가 있습니다:", *result.warnings, sep="\n  ")
        return 1
    for rec in result.file.records:
        s = summarize_pairs(compare_record(rec))
        print(
            f"{rec.evidence_id}: 구간 {s.pair_count}, 비교 가능 {s.comparable_count}, "
            f"비교 A 반대 {s.opposite_a_count}, 같음 {s.same_a_count}, 보류 {s.skipped_count}"
        )
    print(f"-> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
