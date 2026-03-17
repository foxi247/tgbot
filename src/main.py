from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import menu, wizard
from src.bot.middlewares.db_middleware import DbMiddleware
from src.config import load_config
from src.core.content_service import ContentService
from src.integrations.minimax_client import MinimaxClient
from src.integrations.payments import get_payment_provider
from src.storage.db import init_db
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging("INFO")
    config = load_config()

    logger.info("Starting content_pack_bot (env=%s)", config.app_env)

    # DB
    conn = await init_db(config.database_path)

    # Services
    minimax = MinimaxClient(config)
    packs_dir = Path("data/packs")
    packs_dir.mkdir(parents=True, exist_ok=True)
    content_service = ContentService(minimax, packs_dir)
    payment_provider = get_payment_provider(config)

    # Bot
    bot = Bot(
        token=config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    db_mw = DbMiddleware(conn)
    dp.message.middleware(db_mw)
    dp.callback_query.middleware(db_mw)

    # Inject dependencies via workflow_data
    dp["content_service"] = content_service
    dp["payment_provider"] = payment_provider
    dp["config"] = config

    # Routers
    dp.include_router(menu.router)
    dp.include_router(wizard.router)

    logger.info("Bot started. Polling...")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await conn.close()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
