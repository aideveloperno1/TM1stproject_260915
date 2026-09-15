from pathlib import Path
from typing import Annotated

from fastapi import Cookie, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import labels
from .forms import parse_plan_form
from .models import BudgetStatus, PlanInput, sample_plan
from .regions import load_regions, region_label, sido_list
from .session import COOKIE_NAME, WorkState, store
from .validation import ValidationResult, validate_plan

BASE = Path(__file__).parent

app = FastAPI(title="소비 시그널 정책맵")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
templates.env.globals.update(labels=labels, region_label=region_label)

SessionCookie = Annotated[str | None, Cookie(alias=COOKIE_NAME)]
LAST_STEP = len(labels.STEP_LABELS)


def _with_cookie(response: Response, session_id: str) -> Response:
    response.set_cookie(COOKIE_NAME, session_id, httponly=True, samesite="lax")
    return response


def _redirect(url: str, session_id: str) -> Response:
    return _with_cookie(RedirectResponse(url, status_code=303), session_id)


def _render_input(
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
        "budget_status": BudgetStatus,
    }
    response = templates.TemplateResponse(request, "step_input.html", context, status_code=status_code)
    return _with_cookie(response, session_id)


@app.get("/")
def index(session: SessionCookie = None) -> Response:
    session_id, _ = store.get_or_create(session)
    return _redirect("/step/1", session_id)


@app.get("/step/1", response_class=HTMLResponse)
def input_step(request: Request, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    return _render_input(request, session_id, state)


@app.post("/step/1")
async def submit_input(request: Request, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    form = await request.form()
    action = form.get("action")

    if action == "sample":
        state.plan = sample_plan()
        return _redirect("/step/1", session_id)
    if action == "clear":
        state.plan = PlanInput()
        return _redirect("/step/1", session_id)

    single = {k: v for k, v in form.items() if isinstance(v, str)}
    multi = {k: [v for v in form.getlist(k) if isinstance(v, str)] for k in ("goals", "metrics")}
    state.plan = parse_plan_form(single, multi)

    result = validate_plan(state.plan)
    if not result.ok:
        return _render_input(request, session_id, state, result, status_code=422)

    state.start_review()
    return _redirect("/step/2", session_id)


@app.get("/step/{step}", response_class=HTMLResponse)
def later_step(request: Request, step: int, session: SessionCookie = None) -> Response:
    session_id, state = store.get_or_create(session)
    # 원안을 보관하기 전에는 기획 입력만 열 수 있다
    if state.original is None or not 2 <= step <= LAST_STEP:
        return _redirect("/step/1", session_id)
    context = {"step": step, "state": state, "original": state.original}
    return _with_cookie(templates.TemplateResponse(request, "step_placeholder.html", context), session_id)


@app.post("/reset")
def reset(session: SessionCookie = None) -> Response:
    session_id, _ = store.get_or_create(session)
    store.reset(session_id)
    return _redirect("/step/1", session_id)
