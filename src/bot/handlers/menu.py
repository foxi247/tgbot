from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot import texts
from src.bot.keyboards.main_menu import main_menu_keyboard
from src.storage.repo import PackRepo, UserRepo

logger = logging.getLogger(__name__)
router = Router(name="menu")


async def _upsert_user(message: Message, user_repo: UserRepo) -> int:
    user = message.from_user
    return await user_repo.upsert(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    user_repo: UserRepo,
) -> None:
    await state.clear()
    await _upsert_user(message, user_repo)
    await message.answer(texts.WELCOME, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(Command("menu"))
@router.message(lambda m: m.text in ("🏠 В меню", "↩️ В меню"))
async def cmd_menu(message: Message, state: FSMContext, user_repo: UserRepo) -> None:
    await state.clear()
    await _upsert_user(message, user_repo)
    await message.answer("Главное меню 👇", reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(lambda m: m.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(texts.HELP, parse_mode="HTML")


@router.message(lambda m: m.text == "💳 Цена")
async def cmd_price(message: Message) -> None:
    await message.answer(texts.PRICE_INFO, parse_mode="HTML")


@router.message(lambda m: m.text == "📁 Мои пакеты")
async def cmd_my_packs(message: Message, user_repo: UserRepo, pack_repo: PackRepo) -> None:
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала создай свой первый пакет!", parse_mode="HTML")
        return

    packs = await pack_repo.list_for_user(user["id"])
    if not packs:
        await message.answer(texts.NO_PACKS, parse_mode="HTML")
        return

    lines = ["<b>📁 Твои контент-пакеты:</b>\n"]
    for i, pack in enumerate(packs, 1):
        created = pack.get("created_at", "")[:10]
        niche = pack.get("niche") or "—"
        platform = pack.get("platform") or "—"
        lines.append(f"{i}. <b>{niche}</b> | {platform} | {created}")

    lines.append("\nДля скачивания файлов открой последний пакет через <b>✨ Создать пакет</b>.")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(lambda m: m.text == "🧪 Пример")
async def cmd_example(message: Message) -> None:
    example = (
        "<b>🧪 Пример поста из контент-пакета</b>\n\n"
        "<b>Тема:</b> Почему клиент ушёл молча\n\n"
        "<i>Молчание — не знак согласия. Иногда это последнее, что человек делает перед уходом.</i>\n\n"
        "Три года назад я потерял клиента. Он просто перестал отвечать. "
        "Я думал: «ну и ладно, сам виноват». Потом узнал, что он ушёл к конкуренту, "
        "который просто позвонил и спросил: «Как дела?»\n\n"
        "Люди не уходят от плохого сервиса. Они уходят от ощущения, что их не замечают.\n\n"
        "Что я теперь делаю иначе:\n"
        "— звоню через 2 недели после завершения работы\n"
        "— спрашиваю конкретно, а не «как дела?»\n"
        "— фиксирую обратную связь письменно\n\n"
        "<b>Призыв:</b> Когда ты последний раз сам выходил на связь с клиентом?\n\n"
        "🖼 <b>Промпт для визуала:</b>\n"
        "<code>Minimalist illustration of an empty chair at a table, soft natural light, "
        "muted tones, metaphor for absence and reflection, editorial style</code>"
    )
    await message.answer(example, parse_mode="HTML")
