from __future__ import annotations

import pytest

from src.core.enums import PackStatus, PaymentStatus
from src.storage.repo import PackRepo, PaymentRepo, SessionRepo, UserRepo


@pytest.mark.asyncio
async def test_user_upsert_creates_user(user_repo: UserRepo):
    uid = await user_repo.upsert(
        telegram_user_id=100001,
        username="testuser",
        first_name="Тест",
    )
    assert uid > 0


@pytest.mark.asyncio
async def test_user_upsert_returns_same_id_on_conflict(user_repo: UserRepo):
    id1 = await user_repo.upsert(100002, "alice", "Alice")
    id2 = await user_repo.upsert(100002, "alice_new", "Alice")
    assert id1 == id2


@pytest.mark.asyncio
async def test_user_get_by_telegram_id(user_repo: UserRepo):
    await user_repo.upsert(100003, "bob", "Bob")
    user = await user_repo.get_by_telegram_id(100003)
    assert user is not None
    assert user["username"] == "bob"
    assert user["first_name"] == "Bob"


@pytest.mark.asyncio
async def test_user_get_nonexistent(user_repo: UserRepo):
    user = await user_repo.get_by_telegram_id(999999)
    assert user is None


@pytest.mark.asyncio
async def test_session_create(user_repo: UserRepo, session_repo: SessionRepo):
    user_id = await user_repo.upsert(200001, "sess_user", "Sess")
    session_id = await session_repo.create(user_id)
    assert session_id > 0


@pytest.mark.asyncio
async def test_session_update_answers(user_repo: UserRepo, session_repo: SessionRepo):
    user_id = await user_repo.upsert(200002, "answers_user", "Ans")
    session_id = await session_repo.create(user_id)
    await session_repo.update_answers(
        session_id,
        platform="telegram",
        niche="психология",
        product="курс",
        audience="женщины",
        goal="sales",
        tone="simple",
        length="medium",
    )
    session = await session_repo.get(session_id)
    assert session is not None
    assert session["niche"] == "психология"
    assert session["platform"] == "telegram"


@pytest.mark.asyncio
async def test_session_update_status(user_repo: UserRepo, session_repo: SessionRepo):
    user_id = await user_repo.upsert(200003, "status_user", "St")
    session_id = await session_repo.create(user_id)
    await session_repo.update_status(session_id, PackStatus.DEMO_GENERATED)
    session = await session_repo.get(session_id)
    assert session["status"] == PackStatus.DEMO_GENERATED.value


@pytest.mark.asyncio
async def test_session_list_for_user(user_repo: UserRepo, session_repo: SessionRepo):
    user_id = await user_repo.upsert(200004, "list_user", "L")
    await session_repo.create(user_id)
    await session_repo.create(user_id)
    sessions = await session_repo.list_for_user(user_id)
    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_pack_create_and_list(
    user_repo: UserRepo, session_repo: SessionRepo, pack_repo: PackRepo
):
    user_id = await user_repo.upsert(300001, "pack_user", "P")
    session_id = await session_repo.create(user_id)
    pack_id = await pack_repo.create(
        session_id=session_id,
        user_id=user_id,
        is_demo=False,
        content={"posts": [], "hooks": []},
        md_path="/tmp/test.md",
        txt_path="/tmp/test.txt",
    )
    assert pack_id > 0
    packs = await pack_repo.list_for_user(user_id)
    assert len(packs) == 1
    assert packs[0]["md_path"] == "/tmp/test.md"


@pytest.mark.asyncio
async def test_demo_pack_not_in_list(
    user_repo: UserRepo, session_repo: SessionRepo, pack_repo: PackRepo
):
    user_id = await user_repo.upsert(300002, "demo_user", "D")
    session_id = await session_repo.create(user_id)
    # Demo pack — should NOT appear in list_for_user (is_demo=1)
    await pack_repo.create(
        session_id=session_id,
        user_id=user_id,
        is_demo=True,
        content={},
    )
    packs = await pack_repo.list_for_user(user_id)
    assert len(packs) == 0


@pytest.mark.asyncio
async def test_payment_create_and_check(
    user_repo: UserRepo, session_repo: SessionRepo, payment_repo: PaymentRepo
):
    user_id = await user_repo.upsert(400001, "pay_user", "Pay")
    session_id = await session_repo.create(user_id)
    payment_id = await payment_repo.create(
        user_id=user_id,
        session_id=session_id,
        amount_rub=299,
        provider="dummy",
    )
    assert payment_id > 0


@pytest.mark.asyncio
async def test_payment_update_status(
    user_repo: UserRepo, session_repo: SessionRepo, payment_repo: PaymentRepo
):
    user_id = await user_repo.upsert(400002, "pay_user2", "Pay2")
    session_id = await session_repo.create(user_id)
    payment_id = await payment_repo.create(user_id, session_id, 299, "dummy")
    await payment_repo.update_status(payment_id, PaymentStatus.SUCCESS, "dummy_abc")
    result = await payment_repo.get_successful_for_session(session_id)
    assert result is not None
    assert result["provider_payment_id"] == "dummy_abc"


@pytest.mark.asyncio
async def test_payment_no_success_returns_none(
    user_repo: UserRepo, session_repo: SessionRepo, payment_repo: PaymentRepo
):
    user_id = await user_repo.upsert(400003, "pay_user3", "Pay3")
    session_id = await session_repo.create(user_id)
    await payment_repo.create(user_id, session_id, 299, "dummy")
    # Status stays PENDING — no successful payment
    result = await payment_repo.get_successful_for_session(session_id)
    assert result is None
