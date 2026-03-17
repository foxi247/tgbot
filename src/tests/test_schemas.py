from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.core.enums import Goal, Platform, PostLength, Tone
from src.core.schemas import DemoContent, FullPost, PlanItem, UserAnswers


def test_user_answers_valid():
    ua = UserAnswers(
        platform=Platform.TELEGRAM,
        niche="психология",
        product="курс",
        audience="женщины 30+",
        goal=Goal.SALES,
        tone=Tone.SIMPLE,
        length=PostLength.MEDIUM,
    )
    assert ua.platform == Platform.TELEGRAM
    assert ua.niche == "психология"


def test_user_answers_truncates_long_niche():
    ua = UserAnswers(
        platform=Platform.INSTAGRAM,
        niche="x" * 600,
        product="услуга",
        audience="все",
        goal=Goal.ENGAGEMENT,
        tone=Tone.LIVELY,
        length=PostLength.SHORT,
    )
    assert len(ua.niche) == 500


def test_user_answers_strips_whitespace():
    ua = UserAnswers(
        platform=Platform.VK,
        niche="  маркетинг  ",
        product="  консультация  ",
        audience="  малый бизнес  ",
        goal=Goal.EXPERTISE,
        tone=Tone.EXPERT,
        length=PostLength.LONG,
    )
    assert ua.niche == "маркетинг"
    assert ua.product == "консультация"


def test_plan_item_valid():
    from src.core.enums import PostFormat, VisualType
    item = PlanItem(
        day=1,
        topic="Тема",
        format=PostFormat.EXPERT,
        goal="цель",
        cta_type="вопрос",
        visual_type=VisualType.PHOTO,
    )
    assert item.day == 1


def test_plan_item_day_out_of_range():
    from src.core.enums import PostFormat, VisualType
    with pytest.raises(ValidationError):
        PlanItem(
            day=31,
            topic="Тема",
            format=PostFormat.EXPERT,
            goal="цель",
            cta_type="вопрос",
            visual_type=VisualType.PHOTO,
        )


def test_demo_content_requires_3_topics():
    with pytest.raises(ValidationError):
        DemoContent(
            topics=["только одна"],
            full_post=FullPost(
                day=1, topic="t", hook="h", body="b", cta="c", image_prompt="p"
            ),
            image_prompt="prompt",
        )
