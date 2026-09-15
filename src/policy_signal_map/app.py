from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .paths import WEB_DIR
from .web.routes import input as input_routes
from .web.routes import steps as step_routes

app = FastAPI(title="소비 시그널 정책맵")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.include_router(input_routes.router)
app.include_router(step_routes.router)
