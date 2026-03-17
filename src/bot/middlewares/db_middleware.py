from __future__ import annotations

from typing import Any, Awaitable, Callable

import aiosqlite
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.storage.repo import PackRepo, PaymentRepo, SessionRepo, UserRepo


class DbMiddleware(BaseMiddleware):
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["conn"] = self._conn
        data["user_repo"] = UserRepo(self._conn)
        data["session_repo"] = SessionRepo(self._conn)
        data["pack_repo"] = PackRepo(self._conn)
        data["payment_repo"] = PaymentRepo(self._conn)
        return await handler(event, data)
