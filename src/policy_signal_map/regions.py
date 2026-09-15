"""시도·시군구 선택 목록. scripts/build_regions.py가 만든 regions.json을 읽는다."""

import json
from functools import cache
from pathlib import Path

from .models import Region, RegionLevel

DATA_FILE = Path(__file__).parent / "data" / "regions.json"


@cache
def load_regions() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def sido_list() -> list[dict]:
    return load_regions()["sido"]


def find_sido(code: str) -> dict | None:
    return next((s for s in sido_list() if s["code"] == code), None)


def is_known_region(region: Region) -> bool:
    if region.level is RegionLevel.NATIONAL:
        return True
    sido = find_sido(region.sido_code)
    if sido is None:
        return False
    if region.level is RegionLevel.SIDO:
        return True
    return any(g["code"] == region.sigungu_code for g in sido["sigungu"])


def region_label(region: Region | None) -> str:
    if region is None:
        return ""
    if region.level is RegionLevel.NATIONAL:
        return "전국"
    sido = find_sido(region.sido_code)
    if sido is None:
        return ""
    if region.level is RegionLevel.SIDO:
        return sido["name"]
    sigungu = next((g for g in sido["sigungu"] if g["code"] == region.sigungu_code), None)
    return f"{sido['name']} {sigungu['name']}" if sigungu else sido["name"]
