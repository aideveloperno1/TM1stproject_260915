"""3단계 AI 참고 의견 화면·주소 (6LLM참고의견계획.md C-5). 실제 모델을 부르지 않는다."""

import pytest
from evidence_helpers import fixture_path
from fastapi.testclient import TestClient
from helpers import VALID_FORM

from policy_signal_map.app import app
from policy_signal_map.llm.base import FakeProvider, LLMError
from policy_signal_map.web.routes import opinions as opinion_routes

CLEAN = "- 참여자 확인 자료를 어디서 모을지 정해 두세요 [R07]\n- 사용처 범위를 적어 두세요 [R07]"


@pytest.fixture
def local_llm(use_evidence):
    """설정만 local로 바꾼다. 실제 호출은 가짜 제공자가 대신한다."""

    def _use(provider: FakeProvider | None = None, **env: str):
        use_evidence(
            None,
            PSM_LLM_PROVIDER="local",
            PSM_LLM_MODEL="시험모델",
            PSM_LLM_BASE_URL="http://127.0.0.1:11434/v1",
            **env,
        )
        fake = provider or FakeProvider(reply=CLEAN)
        return fake

    return _use


def reviewed_client() -> TestClient:
    client = TestClient(app)
    client.post("/step/1", data=VALID_FORM)
    return client


def use_provider(monkeypatch: pytest.MonkeyPatch, fake: FakeProvider) -> None:
    monkeypatch.setattr(opinion_routes, "get_provider", lambda settings: fake)


def test_ai_area_is_absent_when_provider_is_none():
    html = reviewed_client().get("/step/3").text
    assert "AI 참고 의견" not in html
    assert "js/opinions.js" not in html


def test_ai_area_appears_when_provider_is_set(local_llm):
    local_llm()
    html = reviewed_client().get("/step/3").text
    assert "AI 참고 의견" in html
    assert "js/opinions.js" in html
    assert "결정하지 않습니다" in html


def test_opinions_are_off_without_provider():
    client = reviewed_client()
    assert client.get("/step/3/opinions").json() == {"state": "off", "opinions": []}


def test_opinions_are_off_before_review_starts(local_llm):
    local_llm()
    assert TestClient(app).get("/step/3/opinions").json()["state"] == "off"


def test_opinions_are_returned_with_rule_ids(local_llm, monkeypatch):
    fake = local_llm()
    use_provider(monkeypatch, fake)
    data = reviewed_client().get("/step/3/opinions").json()

    assert data["state"] == "ok"
    assert [o["text"] for o in data["opinions"]] == [
        "참여자 확인 자료를 어디서 모을지 정해 두세요 [R07]",
        "사용처 범위를 적어 두세요 [R07]",
    ]
    assert data["opinions"][0]["rule_ids"] == ["R07"]
    assert data["model"] == "시험모델"


def test_prompt_gets_no_numbers(local_llm, monkeypatch):
    fake = local_llm()
    use_provider(monkeypatch, fake)
    reviewed_client().get("/step/3/opinions")

    sent = fake.calls[0][1].content
    assert "비교 가능한" not in sent
    assert "금액과 비중의 변화 방향이 서로 달랐던" in sent


def test_same_plan_is_not_asked_twice(local_llm, monkeypatch):
    fake = local_llm()
    use_provider(monkeypatch, fake)
    client = reviewed_client()
    client.get("/step/3/opinions")
    client.get("/step/3/opinions")
    assert len(fake.calls) == 1


def test_changed_plan_asks_again(local_llm, monkeypatch):
    fake = local_llm()
    use_provider(monkeypatch, fake)
    client = reviewed_client()
    client.get("/step/3/opinions")
    client.post("/step/1", data={**VALID_FORM, "indicator_use": "reference"})
    client.get("/step/3/opinions")
    assert len(fake.calls) == 2


def test_failure_does_not_break_step_three(local_llm, monkeypatch):
    fake = local_llm(FakeProvider(error=LLMError("연결 실패")))
    use_provider(monkeypatch, fake)
    client = reviewed_client()

    data = client.get("/step/3/opinions").json()
    assert data == {"state": "failed", "message": "AI 의견을 불러오지 못했습니다"}
    assert "연결 실패" not in str(data)
    assert "검토 질문" in client.get("/step/3").text


def test_dropped_lines_are_not_shown(local_llm, monkeypatch):
    fake = local_llm(FakeProvider(reply="- 3개 구간에서 방향이 달랐습니다 [R07]\n- 성공합니다 [R07]"))
    use_provider(monkeypatch, fake)
    data = reviewed_client().get("/step/3/opinions").json()
    assert data["state"] == "ok" and data["opinions"] == []
    assert data["dropped_count"] == 2


def test_evidence_error_stops_the_call(local_llm, monkeypatch, use_evidence):
    fake = local_llm()
    use_provider(monkeypatch, fake)
    client = reviewed_client()
    use_evidence(
        fixture_path("relation_broken"),
        PSM_LLM_PROVIDER="local",
        PSM_LLM_MODEL="시험모델",
        PSM_LLM_BASE_URL="http://127.0.0.1:11434/v1",
    )
    assert client.get("/step/3/opinions").json()["state"] == "off"
    assert fake.calls == []
