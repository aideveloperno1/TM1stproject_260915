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


def has_real_records(file: EvidenceFile) -> bool:
    return any(record.data_kind == "real" for record in file.records)


def is_real_evidence(path: Path, file: EvidenceFile | None) -> bool:
    """실제 자료로 취급할지. 파일 안 표시가 잘못돼도 차단이 뚫리지 않게 경로·이름도 본다."""
    path = Path(path)
    in_private = any(part.lower() == "private" for part in path.parts)
    real_name = "_real_" in path.name.lower()
    return in_private or real_name or (file is not None and has_real_records(file))
