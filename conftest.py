from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
import aiosqlite

from src.storage.db import init_db
from src.storage.repo import PackRepo, PaymentRepo, SessionRepo, UserRepo


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_conn():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = await init_db(db_path)
    yield conn
    await conn.close()
    os.unlink(db_path)


@pytest_asyncio.fixture
async def user_repo(db_conn):
    return UserRepo(db_conn)


@pytest_asyncio.fixture
async def session_repo(db_conn):
    return SessionRepo(db_conn)


@pytest_asyncio.fixture
async def pack_repo(db_conn):
    return PackRepo(db_conn)


@pytest_asyncio.fixture
async def payment_repo(db_conn):
    return PaymentRepo(db_conn)


@pytest.fixture
def sample_user_answers():
    from src.core.enums import Goal, Platform, PostLength, Tone
    from src.core.schemas import UserAnswers
    return UserAnswers(
        platform=Platform.TELEGRAM,
        niche="психология отношений",
        product="онлайн-консультация",
        audience="женщины 25-40 лет в поиске гармонии",
        goal=Goal.EXPERTISE,
        tone=Tone.SIMPLE,
        length=PostLength.MEDIUM,
    )


@pytest.fixture
def sample_plan():
    from src.core.enums import PostFormat, VisualType
    from src.core.schemas import ContentPlan, PlanItem
    items = [
        PlanItem(
            day=i,
            topic=f"Тема {i}",
            format=PostFormat.EXPERT,
            goal="экспертность",
            cta_type="вопрос",
            visual_type=VisualType.PHOTO,
        )
        for i in range(1, 31)
    ]
    return ContentPlan(items=items)


@pytest.fixture
def sample_full_post():
    from src.core.schemas import FullPost
    return FullPost(
        day=1,
        topic="Почему клиент молчит",
        hook="Молчание — не знак согласия.",
        body="Три признака того, что клиент уходит, и как это остановить.",
        cta="Напиши в комменты свой случай",
        image_prompt="Minimalist desk with empty chair, soft light, editorial style",
    )


@pytest.fixture
def sample_demo(sample_full_post):
    from src.core.schemas import DemoContent
    return DemoContent(
        topics=["Тема 1", "Тема 2", "Тема 3"],
        full_post=sample_full_post,
        image_prompt="Clean workspace with notebook and coffee, natural light",
    )


@pytest.fixture
def sample_full_pack(sample_plan, sample_full_post):
    from src.core.schemas import FullPackContent
    return FullPackContent(
        plan=sample_plan.items,
        posts=[sample_full_post] * 15,
        hooks=[f"Хук {i}" for i in range(1, 31)],
        cta_ideas=[f"CTA {i}" for i in range(1, 31)],
        image_prompts=[f"Prompt {i}" for i in range(1, 16)],
        calendar_notes=[f"День {i}: публикуй утром" for i in range(1, 31)],
    )
