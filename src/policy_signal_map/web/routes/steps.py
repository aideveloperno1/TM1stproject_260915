"""아직 구현하지 않은 단계의 임시 화면. 단계를 구현하면 해당 번호를 빼고 전용 라우트 파일로 옮긴다.

app.py에서 이 라우터는 전용 단계 라우터보다 뒤에 등록해야 한다 (/step/{step}이 먼저면 /step/2 등을 가로챈다).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response

from ..dependencies import evidence_state_dep, session_dep
from ..evidence_state import EvidenceState
from ..session import WorkState
from ..templating import LAST_STEP, redirect, render

router = APIRouter()
Session = Annotated[tuple[str, WorkState], Depends(session_dep)]
Evidence = Annotated[EvidenceState, Depends(evidence_state_dep)]

FIRST_PLACEHOLDER_STEP = 2


@router.get("/step/{step}", response_class=HTMLResponse)
def show(request: Request, step: int, session: Session, evidence: Evidence) -> Response:
    session_id, state = session
    # 원안을 보관하기 전에는 기획 입력만 열 수 있다
    if state.original is None or not FIRST_PLACEHOLDER_STEP <= step <= LAST_STEP:
        return redirect("/step/1", session_id)
    return render(
        request,
        "steps/placeholder.html",
        {"original": state.original},
        step=step,
        session_id=session_id,
        state=state,
        evidence=evidence,
    )
