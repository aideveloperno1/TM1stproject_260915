from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from ..paths import WEB_DIR
from ..plan.regions import region_label
from . import labels
from .session import COOKIE_NAME

templates = Jinja2Templates(directory=WEB_DIR / "templates")
templates.env.globals.update(labels=labels, region_label=region_label)

LAST_STEP = len(labels.STEP_LABELS)


def with_cookie(response: Response, session_id: str) -> Response:
    response.set_cookie(COOKIE_NAME, session_id, httponly=True, samesite="lax")
    return response


def redirect(url: str, session_id: str) -> Response:
    return with_cookie(RedirectResponse(url, status_code=303), session_id)
