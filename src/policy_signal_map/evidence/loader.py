"""분석 근거 파일 읽기. 형식 검증은 schema.py가 맡는다.

앱 시작 시 한 번 읽어 보관하는 것은 web 계층(2-1)의 몫이며, 여기서는 캐시하지 않는다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .schema import EvidenceFile, EvidenceRecord, parse_evidence


class EvidenceError(Exception):
    def __init__(self, messages: list[str], path: Path | None = None) -> None:
        super().__init__("\n".join(messages))
        self.messages = messages
        self.path = path


@dataclass(frozen=True)
class LoadResult:
    file: EvidenceFile
    warnings: tuple[str, ...]
    source_path: Path


def _reject_constant(name: str) -> None:
    raise ValueError(f"{name} 값은 사용할 수 없습니다")


def load_evidence(path: Path) -> LoadResult:
    path = Path(path)
    try:
        raw_bytes = path.read_bytes()
    except FileNotFoundError:
        raise EvidenceError([f"근거 파일을 찾을 수 없습니다: {path.resolve()}"], path) from None
    except OSError as exc:
        raise EvidenceError([f"근거 파일을 읽을 수 없습니다: {path.resolve()} ({exc.strerror})"], path) from None

    try:
        # 윈도우 편집기가 붙이는 BOM도 허용한다
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise EvidenceError(["근거 파일은 UTF-8이어야 합니다"], path) from None

    try:
        data = json.loads(text, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise EvidenceError([f"JSON 형식 오류: {exc.lineno}행 {exc.colno}열 ({exc.msg})"], path) from None
    except ValueError as exc:
        raise EvidenceError([f"JSON 형식 오류: {exc}"], path) from None

    result = parse_evidence(data)
    if result.file is None:
        raise EvidenceError(list(result.errors), path)
    return LoadResult(result.file, result.warnings, path)


def find_record(file: EvidenceFile, geographic_scope: str, region_key: str) -> EvidenceRecord | None:
    """요청한 범위의 레코드. 없으면 None이며 전국 레코드로 자동 대체하지 않는다 (9-3장).

    입력 화면의 행정코드와 region_key의 연결 규칙은 2-3 전에 정한다.
    """
    for record in file.records:
        if record.scope.geographic_scope == geographic_scope and record.scope.region_key == region_key:
            return record
    return None


SYNTHETIC_KIND = "synthetic"


def has_real_records(file: EvidenceFile) -> bool:
    return any(record.data_kind != SYNTHETIC_KIND for record in file.records)


def _data_kinds(data: object) -> set[str]:
    """JSON 안의 모든 data_kind 글자 값. 레코드 구조가 틀려도 찾는다."""
    if isinstance(data, dict):
        found = {data["data_kind"]} if isinstance(data.get("data_kind"), str) else set()
        for value in data.values():
            found |= _data_kinds(value)
        return found
    if isinstance(data, list):
        return set().union(*(_data_kinds(item) for item in data)) if data else set()
    return set()


def raw_marks_real(path: Path) -> bool:
    """검증에 실패한 파일도 원문의 data_kind로 실제 자료인지 본다.

    synthetic이 아니면 모두 실제로 본다. 분석 담당이 "actual_internal"처럼 약속과 다른 값을 적어
    검증에 실패하면, 예전에는 경로·이름 조건이 없을 때 실제 자료로 알아보지 못했다 (2026-09-17 임시본 점검).
    읽을 수 없는 파일은 판단하지 않는다 (경로·이름 조건은 따로 본다).
    """
    try:
        data = json.loads(Path(path).read_bytes().decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, ValueError):
        return False
    return any(kind != SYNTHETIC_KIND for kind in _data_kinds(data))


def is_real_evidence(path: Path, file: EvidenceFile | None) -> bool:
    """실제 자료로 취급할지. 파일 안 표시가 잘못돼도 차단이 뚫리지 않게 경로·이름·원문도 본다."""
    path = Path(path)
    in_private = any(part.lower() == "private" for part in path.parts)
    real_name = "_real_" in path.name.lower()
    if in_private or real_name:
        return True
    if file is not None:
        return has_real_records(file)
    return raw_marks_real(path)
