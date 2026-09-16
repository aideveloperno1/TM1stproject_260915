"""3단계 AI 참고 의견 (6LLM참고의견계획.md C-5).

화면과 따로 부른다. 로컬 모델은 느릴 수 있어 이 요청이 3단계 화면을 붙잡으면 안 된다.
근거 파일에 문제가 있거나 설정 조합이 막힌 상태면 부르지 않는다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from ...llm.base import LLMError, get_provider
from ...llm.opinions import safe_collect
from ...review.engine import run_review
from ..dependencies import evidence_state_dep, session_dep
from ..evidence_state import EvidenceState
from ..session import WorkState

router = APIRouter()
Session = Annotated[tuple[str, WorkState], Depends(session_dep)]
Evidence = Annotated[EvidenceState, Depends(evidence_state_dep)]

FAILED = {"state": "failed", "message": "AI 의견을 불러오지 못했습니다"}
OFF = {"state": "off", "opinions": []}


@router.get("/step/3/opinions")
def opinions(session: Session, evidence: Evidence) -> Response:
    _, state = session
    if state.original is None or evidence.blocked or not evidence.ok or evidence.result is None:
        return JSONResponse(OFF)

    settings = evidence.settings
    if settings is None or settings.llm_provider == "none":
        return JSONResponse(OFF)

    cached = state.cached_opinions()
    if cached is None:
        try:
            provider = get_provider(settings)
        except LLMError:
            return JSONResponse(FAILED)
        if provider is None:
            return JSONResponse(OFF)

        result = run_review(state.original, evidence.result)
        cached = safe_collect(
            provider,
            result,
            state.original,
            timeout_s=settings.llm_timeout_s,
            model=settings.llm_model or "",
        )
        if cached is None:
            return JSONResponse(FAILED)
        state.remember_opinions(cached)

    return JSONResponse(
        {
            "state": "ok",
            "opinions": [
                {"text": opinion.text, "rule_ids": list(opinion.cited_rule_ids)} for opinion in cached.opinions
            ],
            "model": cached.model,
            "created_at": cached.created_at,
            "dropped_count": cached.dropped_count,
        }
    )
