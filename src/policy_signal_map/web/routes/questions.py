"""3단계: 검토 질문 (워크플로우 S02·11장, 3검토질문계획.md)"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response

from ...review.engine import run_review
from ..dependencies import evidence_state_dep, session_dep
from ..evidence_state import EvidenceState
from ..session import WorkState
from ..templating import redirect, render

router = APIRouter()
Session = Annotated[tuple[str, WorkState], Depends(session_dep)]
Evidence = Annotated[EvidenceState, Depends(evidence_state_dep)]

KIND_LABELS = {
    "question": "질문",
    "notice": "안내",
    "pending": "추가 확정 필요",
    "held": "보류",
    "not_reviewed": "검토하지 않음",
}


@router.get("/step/3", response_class=HTMLResponse)
def show(request: Request, session: Session, evidence: Evidence) -> Response:
    session_id, state = session
    common = {"step": 3, "session_id": session_id, "state": state, "evidence": evidence}

    if state.original is None:
        return redirect("/step/1", session_id)
    if not evidence.ok or evidence.result is None:
        return render(request, "error.html", {}, status_code=503, **common)

    # 검토 결과는 저장하지 않고 요청마다 다시 계산한다 (같은 입력이면 같은 결과)
    result = run_review(state.original, evidence.result)
    # AI 의견은 화면을 그린 뒤 /step/3/opinions로 따로 받는다 (로컬 모델이 느려도 화면이 기다리지 않게)
    ai_enabled = evidence.settings is not None and evidence.settings.llm_provider != "none"
    context = {"result": result, "kind_labels": KIND_LABELS, "ai_enabled": ai_enabled}
    return render(request, "steps/questions.html", context, **common)
