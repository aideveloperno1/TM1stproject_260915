"""1단계: 기획 입력 (워크플로우 S01)"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse, Response

from ...plan.models import BudgetStatus, PlanInput, sample_plan
from ...plan.regions import load_regions, sido_list
from ...plan.validation import ValidationResult, validate_plan
from ...review.rules import load_rule_catalog
from ..forms import parse_plan_form
from ..session import COOKIE_NAME, WorkState, store
from ..templating import redirect, templates, with_cookie

router = APIRouter()
SessionCookie = Annotated[str | None, Cookie(alias=COOKIE_NAME)]


def _render(
    request: Request,
    session_id: str,
    state: WorkState,
    result: ValidationResult | None = None,
    status_code: int = 200,
) -> Response:
    plan = state.plan
    context = {
        "step": 1,
        "state": state,
        "plan": plan,
        # 제출 전에는 오류를 보여주지 않고, 요약만 현재 입력 기준으로 보여준다
        "errors": result.errors if result else {},
        "summary": result or validate_plan(plan),
        "sido_list": sido_list(),
        "regions_json": load_regions(),
        "rules": load_rule_catalog(),
        "budget_status": BudgetStatus,
    }
    response = templates.TemplateResponse(request, "steps/input.html", context, status_code=status_code)
    return with_cookie(response, session_id)


@router.get("/")
def index(session: SessionCookie = None) -> Response:
    session_id, _ = store.get_or_create(session)
    return redirect("/step/1", session_id)


@router.get("/step/1", response_class=HTMLResponse)
def show(request: Request, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    return _render(request, session_id, state)


@router.post("/step/1")
async def submit(request: Request, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    form = await request.form()
    action = form.get("action")

    if action == "sample":
        state.plan = sample_plan()
        return redirect("/step/1", session_id)
    if action == "clear":
        state.plan = PlanInput()
        return redirect("/step/1", session_id)

    single = {k: v for k, v in form.items() if isinstance(v, str)}
    multi = {k: [v for v in form.getlist(k) if isinstance(v, str)] for k in ("goals", "metrics")}
    state.plan = parse_plan_form(single, multi)

    result = validate_plan(state.plan)
    if not result.ok:
        return _render(request, session_id, state, result, status_code=422)

    state.start_review()
    return redirect("/step/2", session_id)


@router.post("/reset")
def reset(session: SessionCookie = None) -> Response:
    session_id, _ = store.get_or_create(session)
    store.reset(session_id)
    return redirect("/step/1", session_id)
