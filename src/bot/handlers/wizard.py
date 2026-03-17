from __future__ import annotations

import json
import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from src.bot import texts
from src.bot.keyboards.main_menu import main_menu_keyboard
from src.bot.keyboards.wizard import (
    cancel_keyboard,
    demo_result_keyboard,
    full_result_keyboard,
    goal_keyboard,
    length_keyboard,
    platform_keyboard,
    summary_keyboard,
    tone_keyboard,
)
from src.bot.states import WizardStates
from src.config import Config
from src.core.content_service import ContentGenerationError, ContentService
from src.core.enums import PackStatus
from src.core.formatter import (
    chunk_text,
    format_brief_summary,
    format_demo_preview,
    format_pack_summary,
)
from src.core.schemas import UserAnswers
from src.integrations.payments import BasePaymentProvider
from src.storage.repo import PackRepo, PaymentRepo, SessionRepo, UserRepo

logger = logging.getLogger(__name__)
router = Router(name="wizard")


# ── helpers ────────────────────────────────────────────────────────────────────

async def _get_or_create_session(
    state: FSMContext,
    user_id: int,
    session_repo: SessionRepo,
) -> int:
    data = await state.get_data()
    session_id = data.get("session_id")
    if not session_id:
        session_id = await session_repo.create(user_id)
        await state.update_data(session_id=session_id)
    return session_id


async def _send_progress(
    message: Message,
    step: int,
    total: int,
    text: str,
    msg_id_key: str,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    existing_id = data.get(msg_id_key)
    try:
        if existing_id:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=existing_id,
                text=text,
                parse_mode="HTML",
            )
        else:
            sent = await message.answer(text, parse_mode="HTML")
            await state.update_data(**{msg_id_key: sent.message_id})
    except Exception:
        sent = await message.answer(text, parse_mode="HTML")
        await state.update_data(**{msg_id_key: sent.message_id})


# ── entry point ────────────────────────────────────────────────────────────────

@router.message(lambda m: m.text == "✨ Создать пакет")
async def start_wizard(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WizardStates.platform)
    await message.answer(texts.ASK_PLATFORM, reply_markup=platform_keyboard(), parse_mode="HTML")


# ── cancel / back to menu ──────────────────────────────────────────────────────

@router.callback_query(F.data == "wizard:cancel")
async def wizard_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        texts.CANCEL_TO_MENU, reply_markup=main_menu_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "wizard:restart")
async def wizard_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WizardStates.platform)
    await callback.message.answer(
        texts.ASK_PLATFORM, reply_markup=platform_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


# ── step 1: platform ───────────────────────────────────────────────────────────

@router.callback_query(WizardStates.platform, F.data.startswith("platform:"))
async def step_platform(callback: CallbackQuery, state: FSMContext) -> None:
    platform = callback.data.split(":")[1]
    await state.update_data(platform=platform)
    await state.set_state(WizardStates.niche)
    await callback.message.answer(
        texts.ASK_NICHE, reply_markup=cancel_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


# ── step 2: niche ──────────────────────────────────────────────────────────────

@router.message(WizardStates.niche)
async def step_niche(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer(texts.NICHE_TOO_SHORT, reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
    await state.update_data(niche=text)
    await state.set_state(WizardStates.product)
    await message.answer(texts.ASK_PRODUCT, reply_markup=cancel_keyboard(), parse_mode="HTML")


# ── step 3: product ────────────────────────────────────────────────────────────

@router.message(WizardStates.product)
async def step_product(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer(texts.PRODUCT_TOO_SHORT, reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
    await state.update_data(product=text)
    await state.set_state(WizardStates.audience)
    await message.answer(texts.ASK_AUDIENCE, reply_markup=cancel_keyboard(), parse_mode="HTML")


# ── step 4: audience ───────────────────────────────────────────────────────────

@router.message(WizardStates.audience)
async def step_audience(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 5:
        await message.answer(texts.AUDIENCE_TOO_SHORT, reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
    await state.update_data(audience=text)
    await state.set_state(WizardStates.goal)
    await message.answer(texts.ASK_GOAL, reply_markup=goal_keyboard(), parse_mode="HTML")


# ── step 5: goal ───────────────────────────────────────────────────────────────

@router.callback_query(WizardStates.goal, F.data.startswith("goal:"))
async def step_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await state.set_state(WizardStates.tone)
    await callback.message.answer(texts.ASK_TONE, reply_markup=tone_keyboard(), parse_mode="HTML")
    await callback.answer()


# ── step 6: tone ───────────────────────────────────────────────────────────────

@router.callback_query(WizardStates.tone, F.data.startswith("tone:"))
async def step_tone(callback: CallbackQuery, state: FSMContext) -> None:
    tone = callback.data.split(":")[1]
    await state.update_data(tone=tone)
    await state.set_state(WizardStates.length)
    await callback.message.answer(texts.ASK_LENGTH, reply_markup=length_keyboard(), parse_mode="HTML")
    await callback.answer()


# ── step 7: length ─────────────────────────────────────────────────────────────

@router.callback_query(WizardStates.length, F.data.startswith("length:"))
async def step_length(callback: CallbackQuery, state: FSMContext) -> None:
    length = callback.data.split(":")[1]
    await state.update_data(length=length)
    await state.set_state(WizardStates.summary)

    data = await state.get_data()
    answers = _build_answers(data)
    summary_text = format_brief_summary(answers)
    await callback.message.answer(
        summary_text, reply_markup=summary_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


# ── summary: generate demo ─────────────────────────────────────────────────────

@router.callback_query(WizardStates.summary, F.data == "wizard:generate_demo")
async def generate_demo(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UserRepo,
    session_repo: SessionRepo,
    pack_repo: PackRepo,
    content_service: ContentService,
    config: Config,
) -> None:
    await callback.answer()
    await state.set_state(WizardStates.generating_demo)

    data = await state.get_data()
    answers = _build_answers(data)

    tg_user = callback.from_user
    user_id = await user_repo.upsert(tg_user.id, tg_user.username, tg_user.first_name)
    session_id = await _get_or_create_session(state, user_id, session_repo)

    await session_repo.update_answers(
        session_id,
        platform=answers.platform.value,
        niche=answers.niche,
        product=answers.product,
        audience=answers.audience,
        goal=answers.goal.value,
        tone=answers.tone.value,
        length=answers.length.value,
    )

    # Progress messages
    prog_msg = await callback.message.answer(texts.GENERATING_STEP_1, parse_mode="HTML")
    await state.update_data(prog_msg_id=prog_msg.message_id)

    try:
        await callback.message.bot.send_chat_action(callback.message.chat.id, "typing")

        await prog_msg.edit_text(texts.GENERATING_STEP_2, parse_mode="HTML")
        demo = await content_service.generate_demo(answers)

        await prog_msg.edit_text(texts.GENERATING_STEP_3, parse_mode="HTML")

        # Save demo pack
        await pack_repo.create(
            session_id=session_id,
            user_id=user_id,
            is_demo=True,
            content=demo.model_dump(),
        )
        await session_repo.update_status(session_id, PackStatus.DEMO_GENERATED)

        await state.update_data(user_id=user_id, session_id=session_id)

        # Send preview
        preview = format_demo_preview(demo, answers)
        for chunk in chunk_text(preview, 4000):
            await callback.message.answer(chunk, parse_mode="HTML")

        await prog_msg.delete()

        await callback.message.answer(
            texts.UNLOCK_PROMPT,
            reply_markup=demo_result_keyboard(test_unlock=config.test_unlock_enabled),
            parse_mode="HTML",
        )
        await state.set_state(WizardStates.demo_shown)

    except (ContentGenerationError, Exception) as e:
        logger.error("Demo generation error: %s", e)
        await prog_msg.edit_text(texts.ERROR_GENERATION, parse_mode="HTML")
        await session_repo.update_status(session_id, PackStatus.FAILED)
        await callback.message.answer(
            "Вернуться в меню?", reply_markup=cancel_keyboard(), parse_mode="HTML"
        )


# ── payment: test unlock ────────────────────────────────────────────────────────

@router.callback_query(WizardStates.demo_shown, F.data == "payment:test_unlock")
async def payment_test_unlock(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UserRepo,
    session_repo: SessionRepo,
    pack_repo: PackRepo,
    payment_repo: PaymentRepo,
    payment_provider: BasePaymentProvider,
    content_service: ContentService,
    config: Config,
) -> None:
    await callback.answer("🧪 Тестовый доступ активирован!")
    await _do_generate_full(
        callback=callback,
        state=state,
        session_repo=session_repo,
        pack_repo=pack_repo,
        payment_repo=payment_repo,
        payment_provider=payment_provider,
        content_service=content_service,
        config=config,
    )


@router.callback_query(WizardStates.demo_shown, F.data == "payment:pay")
async def payment_pay(
    callback: CallbackQuery,
    state: FSMContext,
    session_repo: SessionRepo,
    pack_repo: PackRepo,
    payment_repo: PaymentRepo,
    payment_provider: BasePaymentProvider,
    content_service: ContentService,
    config: Config,
) -> None:
    await callback.answer()
    if config.test_unlock_enabled:
        await _do_generate_full(
            callback=callback,
            state=state,
            session_repo=session_repo,
            pack_repo=pack_repo,
            payment_repo=payment_repo,
            payment_provider=payment_provider,
            content_service=content_service,
            config=config,
        )
    else:
        await callback.message.answer(
            "Оплата через Telegram Payments пока в разработке. "
            "Используй тестовый режим или напиши в поддержку.",
            parse_mode="HTML",
        )


async def _do_generate_full(
    callback: CallbackQuery,
    state: FSMContext,
    session_repo: SessionRepo,
    pack_repo: PackRepo,
    payment_repo: PaymentRepo,
    payment_provider: BasePaymentProvider,
    content_service: ContentService,
    config: Config,
) -> None:
    data = await state.get_data()
    answers = _build_answers(data)
    user_id: int = data["user_id"]
    session_id: int = data["session_id"]

    # Record payment
    payment_id = await payment_repo.create(
        user_id=user_id,
        session_id=session_id,
        amount_rub=config.full_plan_price_rub,
        provider=payment_provider.name,
    )
    result = await payment_provider.create_payment(
        user_id=user_id,
        amount_rub=config.full_plan_price_rub,
        session_id=session_id,
        description="Контент-пакет на 30 дней",
    )

    from src.core.enums import PaymentStatus
    from src.storage.repo import PaymentRepo as PR
    await payment_repo.update_status(
        payment_id=payment_id,
        status=PaymentStatus.SUCCESS if result.success else PaymentStatus.FAILED,
        provider_payment_id=result.payment_id,
    )

    if not result.success:
        await callback.message.answer("Ошибка оплаты. Попробуй ещё раз.", parse_mode="HTML")
        return

    await state.set_state(WizardStates.generating_full)
    prog_msg = await callback.message.answer(texts.FULL_GENERATING, parse_mode="HTML")

    try:
        await callback.message.bot.send_chat_action(callback.message.chat.id, "typing")

        await prog_msg.edit_text(texts.GENERATING_STEP_1, parse_mode="HTML")
        pack, md_path, txt_path = await content_service.generate_full_pack(answers, user_id)

        await prog_msg.edit_text(texts.GENERATING_STEP_3, parse_mode="HTML")

        await pack_repo.create(
            session_id=session_id,
            user_id=user_id,
            is_demo=False,
            content=pack.model_dump(),
            md_path=str(md_path),
            txt_path=str(txt_path),
        )
        await session_repo.update_status(session_id, PackStatus.FULL_GENERATED)

        await state.update_data(md_path=str(md_path), txt_path=str(txt_path))

        summary = format_pack_summary(pack, answers)
        await prog_msg.delete()
        await callback.message.answer(summary, parse_mode="HTML")
        await callback.message.answer(
            "Выбери действие:",
            reply_markup=full_result_keyboard(),
            parse_mode="HTML",
        )

    except (ContentGenerationError, Exception) as e:
        logger.error("Full pack generation error: %s", e)
        await prog_msg.edit_text(texts.ERROR_GENERATION, parse_mode="HTML")
        await session_repo.update_status(session_id, PackStatus.FAILED)


# ── result: download ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "result:download_md")
async def download_md(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    md_path = data.get("md_path")
    if not md_path or not Path(md_path).exists():
        await callback.message.answer("Файл не найден. Сгенерируй пакет заново.", parse_mode="HTML")
        return
    await callback.message.answer_document(
        FSInputFile(md_path, filename="content_pack.md"),
        caption="📄 Твой контент-пакет в формате Markdown",
    )


@router.callback_query(F.data == "result:download_txt")
async def download_txt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    txt_path = data.get("txt_path")
    if not txt_path or not Path(txt_path).exists():
        await callback.message.answer("Файл не найден. Сгенерируй пакет заново.", parse_mode="HTML")
        return
    await callback.message.answer_document(
        FSInputFile(txt_path, filename="content_pack.txt"),
        caption="📄 Твой контент-пакет в формате TXT",
    )


@router.callback_query(F.data == "result:regenerate")
async def regenerate(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    # Keep answers, reset to summary state
    data = await state.get_data()
    # Clear file paths and session so new generation happens
    data.pop("md_path", None)
    data.pop("txt_path", None)
    data.pop("session_id", None)
    await state.set_data(data)
    await state.set_state(WizardStates.demo_shown)

    await callback.message.answer(
        "Хочешь сгенерировать заново с теми же ответами?",
        reply_markup=demo_result_keyboard(test_unlock=True),
        parse_mode="HTML",
    )


# ── helper ─────────────────────────────────────────────────────────────────────

def _build_answers(data: dict) -> UserAnswers:
    from src.core.enums import Goal, Platform, PostLength, Tone

    return UserAnswers(
        platform=Platform(data.get("platform", "telegram")),
        niche=data.get("niche", ""),
        product=data.get("product", ""),
        audience=data.get("audience", ""),
        goal=Goal(data.get("goal", "sales")),
        tone=Tone(data.get("tone", "simple")),
        length=PostLength(data.get("length", "medium")),
    )
