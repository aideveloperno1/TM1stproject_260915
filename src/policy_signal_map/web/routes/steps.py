"""2~5단계 임시 화면. 각 단계를 구현하면 evidence.py·questions.py·choices.py·draft.py로 옮긴다."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse, Response

from ..session import COOKIE_NAME, store
from ..templating import LAST_STEP, redirect, templates, with_cookie

router = APIRouter()
SessionCookie = Annotated[str | None, Cookie(alias=COOKIE_NAME)]


@router.get("/step/{step}", response_class=HTMLResponse)
def show(request: Request, step: int, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    # 원안을 보관하기 전에는 기획 입력만 열 수 있다
    if state.original is None or not 2 <= step <= LAST_STEP:
        return redirect("/step/1", session_id)
    context = {"step": step, "state": state, "original": state.original}
    return with_cookie(templates.TemplateResponse(request, "steps/placeholder.html", context), session_id)
