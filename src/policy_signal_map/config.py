"""환경변수 설정. 앱 시작 시 한 번 읽어 변경 불가 객체로 보관한다.

실행 예: uv run --env-file .env policy-signal-map
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, cast

from .paths import RESOURCES_DIR

DEFAULT_EVIDENCE_PATH = RESOURCES_DIR / "evidence" / "review_evidence_demo_v1.json"
LLM_PROVIDERS = ("none", "cloud", "local")

LlmProvider = Literal["none", "cloud", "local"]


class SettingsError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    evidence_path: Path
    llm_provider: LlmProvider
    llm_base_url: str | None
    llm_model: str | None
    # 로그·오류 출력에 키가 찍히지 않게 repr에서 뺀다
    llm_api_key: str | None = field(repr=False)


def _value(environ: Mapping[str, str], name: str) -> str | None:
    # 빈 문자열은 설정하지 않은 것으로 본다 (.env.example을 그대로 복사한 경우)
    raw = environ.get(name, "").strip()
    return raw or None


def load_settings(environ: Mapping[str, str] = os.environ) -> Settings:
    provider = _value(environ, "PSM_LLM_PROVIDER") or "none"
    if provider not in LLM_PROVIDERS:
        raise SettingsError(
            f'PSM_LLM_PROVIDER 값 "{provider}"는 사용할 수 없습니다. none, cloud, local 중 하나로 설정하세요.'
        )

    settings = Settings(
        evidence_path=Path(_value(environ, "PSM_EVIDENCE_PATH") or DEFAULT_EVIDENCE_PATH),
        llm_provider=cast(LlmProvider, provider),
        llm_base_url=_value(environ, "PSM_LLM_BASE_URL"),
        llm_model=_value(environ, "PSM_LLM_MODEL"),
        llm_api_key=_value(environ, "PSM_LLM_API_KEY"),
    )

    missing: list[str] = []
    if settings.llm_provider in ("cloud", "local") and not settings.llm_model:
        missing.append("PSM_LLM_MODEL")
    if settings.llm_provider == "cloud" and not settings.llm_api_key:
        missing.append("PSM_LLM_API_KEY")
    if settings.llm_provider == "local" and not settings.llm_base_url:
        missing.append("PSM_LLM_BASE_URL")
    if missing:
        raise SettingsError(
            f"PSM_LLM_PROVIDER={settings.llm_provider}에는 다음 설정이 필요합니다: {', '.join(missing)}"
        )
    return settings


def check_llm_data_combination(settings: Settings, is_real_evidence: bool) -> None:
    """실제 분석 근거와 클라우드 LLM의 조합을 막는다 (checks.md LLM 전달 자료).

    is_real_evidence는 evidence.loader.is_real_evidence()로 판단한 값을 넘긴다.
    로컬 LLM + 실제 자료는 데이터 담당 합의 전이라 여기서는 막지 않는다.
    앱 시작 시 연결(2-1)할 때 합의 결과에 따라 차단 여부를 정한다.
    """
    if is_real_evidence and settings.llm_provider == "cloud":
        raise SettingsError(
            "실제 분석 근거 파일과 클라우드 LLM은 함께 사용할 수 없습니다. "
            "PSM_LLM_PROVIDER를 none으로 바꾸거나 합성 근거 파일을 사용하세요."
        )
