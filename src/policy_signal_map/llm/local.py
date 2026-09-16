"""로컬 LLM 호출 (Ollama·LM Studio 등 OpenAI 호환 서버).

표준 라이브러리만 쓴다. 실행 의존성을 늘리지 않기 위해서다 (6LLM참고의견계획.md 결정 ⑤).
요청 본문은 로그에 남기지 않는다. 남기면 사용자의 기획 내용이 로그 파일에 쌓인다.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

from .base import LLMError, Message

log = logging.getLogger(__name__)


@dataclass
class LocalProvider:
    base_url: str
    model: str
    name: str = "local"

    @property
    def endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    def generate(self, messages: list[Message], *, max_tokens: int, timeout_s: float) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens,
                "temperature": 0.2,
                "stream": False,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_s) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            log.warning("로컬 LLM 호출 실패: %s (%s)", type(exc).__name__, self.model)
            raise LLMError("로컬 LLM을 부르지 못했습니다") from exc
        except json.JSONDecodeError as exc:
            log.warning("로컬 LLM 응답을 읽지 못함: %s", self.model)
            raise LLMError("로컬 LLM 응답 형식이 올바르지 않습니다") from exc

        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            log.warning("로컬 LLM 응답에 내용이 없음: %s", self.model)
            raise LLMError("로컬 LLM 응답에 내용이 없습니다") from exc
