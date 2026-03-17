from __future__ import annotations

import json
from typing import Any

import aiosqlite

from src.core.enums import PackStatus, PaymentStatus


class UserRepo:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def upsert(
        self,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
    ) -> int:
        cursor = await self._conn.execute(
            """
            INSERT INTO users (telegram_user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            RETURNING id
            """,
            (telegram_user_id, username, first_name),
        )
        row = await cursor.fetchone()
        await self._conn.commit()
        return row["id"]

    async def get_by_telegram_id(self, telegram_user_id: int) -> dict[str, Any] | None:
        cursor = await self._conn.execute(
            "SELECT * FROM users WHERE telegram_user_id = ?",
            (telegram_user_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


class SessionRepo:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def create(self, user_id: int) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO generation_sessions (user_id, status) VALUES (?, ?) RETURNING id",
            (user_id, PackStatus.DRAFT.value),
        )
        row = await cursor.fetchone()
        await self._conn.commit()
        return row["id"]

    async def update_answers(
        self,
        session_id: int,
        platform: str,
        niche: str,
        product: str,
        audience: str,
        goal: str,
        tone: str,
        length: str,
    ) -> None:
        await self._conn.execute(
            """
            UPDATE generation_sessions SET
                platform=?, niche=?, product=?, audience=?,
                goal=?, tone=?, length=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (platform, niche, product, audience, goal, tone, length, session_id),
        )
        await self._conn.commit()

    async def update_status(self, session_id: int, status: PackStatus) -> None:
        await self._conn.execute(
            "UPDATE generation_sessions SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status.value, session_id),
        )
        await self._conn.commit()

    async def get(self, session_id: int) -> dict[str, Any] | None:
        cursor = await self._conn.execute(
            "SELECT * FROM generation_sessions WHERE id=?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def list_for_user(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        cursor = await self._conn.execute(
            "SELECT * FROM generation_sessions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


class PackRepo:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def create(
        self,
        session_id: int,
        user_id: int,
        is_demo: bool,
        content: dict[str, Any],
        md_path: str | None = None,
        txt_path: str | None = None,
    ) -> int:
        cursor = await self._conn.execute(
            """
            INSERT INTO content_packs (session_id, user_id, is_demo, content_json, md_path, txt_path)
            VALUES (?, ?, ?, ?, ?, ?) RETURNING id
            """,
            (session_id, user_id, int(is_demo), json.dumps(content, ensure_ascii=False), md_path, txt_path),
        )
        row = await cursor.fetchone()
        await self._conn.commit()
        return row["id"]

    async def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        cursor = await self._conn.execute(
            """
            SELECT cp.*, gs.niche, gs.platform, gs.created_at as session_created
            FROM content_packs cp
            JOIN generation_sessions gs ON gs.id = cp.session_id
            WHERE cp.user_id=? AND cp.is_demo=0
            ORDER BY cp.created_at DESC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


class PaymentRepo:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def create(
        self,
        user_id: int,
        session_id: int,
        amount_rub: int,
        provider: str,
    ) -> int:
        cursor = await self._conn.execute(
            """
            INSERT INTO payments (user_id, session_id, amount_rub, provider, status)
            VALUES (?, ?, ?, ?, ?) RETURNING id
            """,
            (user_id, session_id, amount_rub, provider, PaymentStatus.PENDING.value),
        )
        row = await cursor.fetchone()
        await self._conn.commit()
        return row["id"]

    async def update_status(
        self,
        payment_id: int,
        status: PaymentStatus,
        provider_payment_id: str | None = None,
    ) -> None:
        await self._conn.execute(
            "UPDATE payments SET status=?, provider_payment_id=? WHERE id=?",
            (status.value, provider_payment_id, payment_id),
        )
        await self._conn.commit()

    async def get_successful_for_session(self, session_id: int) -> dict[str, Any] | None:
        cursor = await self._conn.execute(
            "SELECT * FROM payments WHERE session_id=? AND status=?",
            (session_id, PaymentStatus.SUCCESS.value),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
