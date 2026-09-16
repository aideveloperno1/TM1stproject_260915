from fastapi.testclient import TestClient
from helpers import VALID_FORM

from policy_signal_map.app import app


def client() -> TestClient:
    return TestClient(app)


def test_later_steps_locked_until_review_starts():
    response = client().get("/step/2", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/step/1"


def test_input_page_lists_rules_from_catalog():
    response = client().get("/step/1")
    assert response.status_code == 200
    assert "R07 · 검토 구현" in response.text
    assert "R02 · 향후 기능" in response.text


def test_static_files_are_served():
    c = client()
    assert c.get("/static/css/style.css").status_code == 200
    assert c.get("/static/js/input.js").status_code == 200


def test_empty_submit_shows_errors():
    response = client().post("/step/1", data={"action": "submit"})
    assert response.status_code == 422
    assert "필수 항목 7개를 확인해 주세요." in response.text
    assert "사업명을 입력해 주세요." in response.text


def test_valid_submit_keeps_original_and_opens_step_two():
    c = client()
    response = c.post("/step/1", data=VALID_FORM)
    assert response.status_code == 200
    assert str(response.url).endswith("/step/2")
    assert "선택한 강원특별자치도 강릉시의 소비를 진단한 결과가 아닙니다" in response.text

    # 보관한 원안은 다시 입력 화면을 열어도 그대로 남는다
    again = c.get("/step/1").text
    assert 'value="하반기 외국인 소비지원 쿠폰"' in again
    assert "51150" in again


def test_resubmitting_changed_plan_shows_recheck_notice():
    c = client()
    c.post("/step/1", data=VALID_FORM)
    c.post("/step/1", data={**VALID_FORM, "indicator_use": "reference"})
    assert "원안이 바뀌어 검토를 다시 실행했습니다" in c.get("/step/3").text


def test_recheck_notice_disappears_after_unchanged_resubmit():
    c = client()
    c.post("/step/1", data=VALID_FORM)
    c.post("/step/1", data={**VALID_FORM, "indicator_use": "reference"})
    c.post("/step/1", data={**VALID_FORM, "indicator_use": "reference"})  # 바뀐 것 없이 다시 제출
    assert "원안이 바뀌어 검토를 다시 실행했습니다" not in c.get("/step/3").text


def test_sample_button_fills_form():
    response = client().post("/step/1", data={"action": "sample"})
    assert 'value="하반기 외국인 소비지원 쿠폰"' in response.text


def test_reset_clears_work():
    c = client()
    c.post("/step/1", data=VALID_FORM)
    c.post("/reset")
    assert c.get("/step/2", follow_redirects=False).status_code == 303


def test_user_input_is_escaped():
    response = client().post("/step/1", data={**VALID_FORM, "name": "<script>alert(1)</script>", "target": ""})
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;" in response.text
