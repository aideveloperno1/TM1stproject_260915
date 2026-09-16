"""문서 구조 → Markdown. 양식은 resources/documents/에 둔다.

사용자가 적은 문장은 Markdown 표·링크를 깨뜨리지 않게 이스케이프한다.
"""

from __future__ import annotations

import re

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..paths import RESOURCES_DIR
from .models import PlanDocument

TEMPLATE_DIR = RESOURCES_DIR / "documents"
_ESCAPE = re.compile(r"([|\[\]`])")


def md_escape(value: object) -> str:
    return _ESCAPE.sub(r"\\\1", str(value))


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["md_escape"] = md_escape
    return env


def render_markdown(document: PlanDocument) -> str:
    return _environment().get_template("plan.md.j2").render(doc=document)
