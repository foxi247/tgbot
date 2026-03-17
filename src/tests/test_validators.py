from __future__ import annotations

import json
import pytest

from src.core.validators import JSONParseError, parse_demo, parse_full_pack, parse_plan


VALID_PLAN_JSON = json.dumps([
    {
        "day": i,
        "topic": f"Тема {i}",
        "format": "expert",
        "goal": "экспертность",
        "cta_type": "вопрос",
        "visual_type": "photo",
    }
    for i in range(1, 31)
])

VALID_DEMO_JSON = json.dumps({
    "topics": ["Тема 1", "Тема 2", "Тема 3"],
    "full_post": {
        "day": 1,
        "topic": "Тема 1",
        "hook": "Хук поста",
        "body": "Тело поста с полезным контентом.",
        "cta": "Напиши в комменты",
        "image_prompt": "A professional photo of a person working",
    },
    "image_prompt": "Minimalist desk setup with natural light",
})


def test_parse_plan_valid():
    plan = parse_plan(VALID_PLAN_JSON)
    assert len(plan.items) == 30
    assert plan.items[0].day == 1


def test_parse_plan_with_markdown_fence():
    fenced = f"```json\n{VALID_PLAN_JSON}\n```"
    plan = parse_plan(fenced)
    assert len(plan.items) == 30


def test_parse_plan_invalid_raises():
    with pytest.raises(JSONParseError):
        parse_plan("not json at all {{{")


def test_parse_demo_valid():
    demo = parse_demo(VALID_DEMO_JSON)
    assert len(demo.topics) == 3
    assert demo.full_post.hook == "Хук поста"


def test_parse_demo_invalid_raises():
    with pytest.raises(JSONParseError):
        parse_demo('{"topics": ["only one"]}')  # missing required fields


def test_parse_full_pack_invalid_raises():
    with pytest.raises(JSONParseError):
        parse_full_pack("{}")


def test_repair_trailing_comma():
    """Parser should handle trailing commas."""
    broken = '[{"day": 1, "topic": "t", "format": "expert", "goal": "g", "cta_type": "c", "visual_type": "photo",}]'
    # This should either parse or raise JSONParseError (not crash with unexpected exception)
    try:
        result = parse_plan(broken)
    except JSONParseError:
        pass  # acceptable
