from pathlib import Path

import pytest

from policy_signal_map.config import (
    DEFAULT_EVIDENCE_PATH,
    SettingsError,
    check_llm_data_combination,
    load_settings,
)


def test_defaults_use_demo_evidence_and_no_llm():
    settings = load_settings({})
    assert settings.evidence_path == DEFAULT_EVIDENCE_PATH
    assert settings.llm_provider == "none"


def test_empty_values_are_treated_as_unset():
    settings = load_settings({"PSM_EVIDENCE_PATH": "  ", "PSM_LLM_PROVIDER": ""})
    assert settings.evidence_path == DEFAULT_EVIDENCE_PATH
    assert settings.llm_provider == "none"


def test_evidence_path_can_be_overridden():
    settings = load_settings({"PSM_EVIDENCE_PATH": "private/review_evidence_real_v1.json"})
    assert settings.evidence_path == Path("private/review_evidence_real_v1.json")


def test_unknown_provider_is_rejected():
    with pytest.raises(SettingsError, match="gpt"):
        load_settings({"PSM_LLM_PROVIDER": "gpt"})


def test_cloud_requires_model_and_key():
    with pytest.raises(SettingsError, match="PSM_LLM_MODEL, PSM_LLM_API_KEY"):
        load_settings({"PSM_LLM_PROVIDER": "cloud"})


def test_local_requires_base_url_and_model():
    with pytest.raises(SettingsError, match="PSM_LLM_MODEL, PSM_LLM_BASE_URL"):
        load_settings({"PSM_LLM_PROVIDER": "local"})


def test_api_key_not_in_repr():
    settings = load_settings(
        {"PSM_LLM_PROVIDER": "cloud", "PSM_LLM_MODEL": "some-model", "PSM_LLM_API_KEY": "secret-key-123"}
    )
    assert "secret-key-123" not in repr(settings)


def test_real_evidence_with_cloud_is_blocked():
    settings = load_settings(
        {"PSM_LLM_PROVIDER": "cloud", "PSM_LLM_MODEL": "some-model", "PSM_LLM_API_KEY": "k"}
    )
    with pytest.raises(SettingsError, match="클라우드 LLM"):
        check_llm_data_combination(settings, is_real_evidence=True)


def test_synthetic_evidence_with_cloud_is_allowed():
    settings = load_settings(
        {"PSM_LLM_PROVIDER": "cloud", "PSM_LLM_MODEL": "some-model", "PSM_LLM_API_KEY": "k"}
    )
    check_llm_data_combination(settings, is_real_evidence=False)


def test_real_evidence_without_llm_is_allowed():
    check_llm_data_combination(load_settings({}), is_real_evidence=True)
