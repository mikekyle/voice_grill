import pytest
from src.prompts import build_prompt, GRILL_MODES


def test_grill_mode_returns_base_prompt():
    for mode in GRILL_MODES:
        result = build_prompt(topic=None, grill_mode=mode)
        assert isinstance(result, str)
        assert len(result) > 20


def test_grill_mode_with_topic_appends_topic():
    result = build_prompt(topic="salary negotiation", grill_mode="cv-review")
    assert "salary negotiation" in result


def test_free_form_topic():
    result = build_prompt(topic="why did the project fail", grill_mode=None)
    assert "why did the project fail" in result
    assert isinstance(result, str)


def test_no_args_raises():
    with pytest.raises(ValueError):
        build_prompt(topic=None, grill_mode=None)


def test_unknown_grill_mode_falls_through_to_topic():
    result = build_prompt(topic="my topic", grill_mode="nonexistent-mode")
    assert "my topic" in result
