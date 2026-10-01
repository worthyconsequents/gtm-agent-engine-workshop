import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import (
    _build_scoring_payload,
    build_prospect_profile,
    get_prospect,
)
from gtm_agent.gtm_records import PROSPECTS


SENSITIVE_KEYS = {
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
}


def assert_no_sensitive_keys(value):
    if isinstance(value, dict):
        assert SENSITIVE_KEYS.isdisjoint(value)
        for item in value.values():
            assert_no_sensitive_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_sensitive_keys(item)


@pytest.fixture(autouse=True)
def clear_profile_cache():
    data_service._PROFILES.clear()
    yield
    data_service._PROFILES.clear()


@pytest.mark.parametrize("prospect_id", PROSPECTS)
def test_get_prospect_excludes_sensitive_fields(prospect_id):
    result = get_prospect.invoke({"prospect_id": prospect_id})

    assert_no_sensitive_keys(result)


@pytest.mark.parametrize("prospect_id", PROSPECTS)
def test_build_prospect_profile_excludes_sensitive_fields(prospect_id):
    data_service._PROFILES[prospect_id] = {
        **PROSPECTS[prospect_id],
        "prospect_id": prospect_id,
    }

    result = build_prospect_profile.invoke({"prospect_id": prospect_id})

    assert_no_sensitive_keys(result)
    assert_no_sensitive_keys(data_service._PROFILES[prospect_id])


@pytest.mark.parametrize("prospect_id", PROSPECTS)
def test_scoring_payload_excludes_sensitive_fields(prospect_id):
    profile = {
        **PROSPECTS[prospect_id],
        "prospect_id": prospect_id,
        "engagement_history": data_service.fetch_engagement_history(prospect_id),
        "account_details": data_service.fetch_account_details(prospect_id),
        "tech_stack": data_service.fetch_tech_stack(prospect_id),
    }

    result = _build_scoring_payload(profile)

    assert_no_sensitive_keys(result)
