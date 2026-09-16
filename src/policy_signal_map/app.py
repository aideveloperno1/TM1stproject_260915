from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .paths import WEB_DIR
from .web.routes import choices as choice_routes
from .web.routes import draft as draft_routes
from .web.routes import evidence as evidence_routes
from .web.routes import input as input_routes
from .web.routes import questions as question_routes

app = FastAPI(title="소비 시그널 정책맵")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.include_router(input_routes.router)
app.include_router(evidence_routes.router)
app.include_router(question_routes.router)
app.include_router(choice_routes.router)
app.include_router(draft_routes.router)
