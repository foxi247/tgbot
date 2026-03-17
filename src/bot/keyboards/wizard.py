from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def platform_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", callback_data="platform:telegram")],
        [InlineKeyboardButton(text="Instagram", callback_data="platform:instagram")],
        [InlineKeyboardButton(text="ВКонтакте", callback_data="platform:vk")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")],
    ])


def goal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Продажи", callback_data="goal:sales")],
        [InlineKeyboardButton(text="🎓 Экспертность", callback_data="goal:expertise")],
        [InlineKeyboardButton(text="💬 Вовлечение", callback_data="goal:engagement")],
        [InlineKeyboardButton(text="🌟 Личный бренд", callback_data="goal:personal_brand")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")],
    ])


def tone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Экспертный", callback_data="tone:expert")],
        [InlineKeyboardButton(text="😊 Простой", callback_data="tone:simple")],
        [InlineKeyboardButton(text="🔥 Живой", callback_data="tone:lively")],
        [InlineKeyboardButton(text="⚡️ Дерзкий", callback_data="tone:bold")],
        [InlineKeyboardButton(text="💎 Премиум", callback_data="tone:premium")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")],
    ])


def length_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Коротко", callback_data="length:short")],
        [InlineKeyboardButton(text="📝 Средне", callback_data="length:medium")],
        [InlineKeyboardButton(text="📖 Подробно", callback_data="length:long")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")],
    ])


def summary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сгенерировать демо", callback_data="wizard:generate_demo")],
        [InlineKeyboardButton(text="✏️ Изменить ответы", callback_data="wizard:restart")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")],
    ])


def demo_result_keyboard(test_unlock: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    if test_unlock:
        buttons.append([InlineKeyboardButton(
            text="🧪 Тестовый доступ", callback_data="payment:test_unlock"
        )])
    buttons.append([InlineKeyboardButton(
        text=f"💳 Открыть полный пакет — 299 ₽", callback_data="payment:pay"
    )])
    buttons.append([InlineKeyboardButton(text="🔁 Другой стиль", callback_data="wizard:restart")])
    buttons.append([InlineKeyboardButton(text="✏️ Исправить ответы", callback_data="wizard:restart")])
    buttons.append([InlineKeyboardButton(text="🏠 В меню", callback_data="wizard:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def full_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Скачать .md", callback_data="result:download_md")],
        [InlineKeyboardButton(text="📄 Скачать .txt", callback_data="result:download_txt")],
        [InlineKeyboardButton(text="🔄 Сгенерировать заново", callback_data="result:regenerate")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="wizard:cancel")],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ В меню", callback_data="wizard:cancel")]
    ])
