from __future__ import annotations

from src.core.enums import Goal, Platform, PostLength, Tone
from src.core.schemas import ContentPlan, UserAnswers

# ── Label maps ────────────────────────────────────────────────────────────────

PLATFORM_LABELS: dict[Platform, str] = {
    Platform.TELEGRAM: "Telegram",
    Platform.INSTAGRAM: "Instagram",
    Platform.VK: "ВКонтакте",
}

GOAL_LABELS: dict[Goal, str] = {
    Goal.SALES: "продажи",
    Goal.EXPERTISE: "демонстрация экспертности",
    Goal.ENGAGEMENT: "вовлечение аудитории",
    Goal.PERSONAL_BRAND: "личный бренд",
}

TONE_LABELS: dict[Tone, str] = {
    Tone.EXPERT: "экспертный — авторитетный, с фактами и кейсами",
    Tone.SIMPLE: "простой — понятный, без терминов",
    Tone.LIVELY: "живой — разговорный, с историями",
    Tone.BOLD: "дерзкий — провокационный, острый",
    Tone.PREMIUM: "премиум — сдержанный, статусный",
}

LENGTH_LABELS: dict[PostLength, str] = {
    PostLength.SHORT: "короткий (до 500 знаков)",
    PostLength.MEDIUM: "средний (500–1200 знаков)",
    PostLength.LONG: "длинный (1200–2500 знаков)",
}

PLATFORM_NOTES: dict[Platform, str] = {
    Platform.TELEGRAM: (
        "Пиши немного длиннее и глубже. Минимум хэштегов (не больше 3). "
        "Структурируй через абзацы, а не буллеты. Читатель вдумчивый."
    ),
    Platform.INSTAGRAM: (
        "Первые 2 строки — сильный хук, с него начинается пост. "
        "Абзацы короткие. Визуал важен. До 5 хэштегов в конце."
    ),
    Platform.VK: (
        "Нейтральный стиль. Чёткий призыв к действию в конце. "
        "Длина умеренная. Форматируй через абзацы."
    ),
}

RUSSIAN_WRITING_RULES = (
    "Правила русского текста:\n"
    "— Не используй клише: «в современном мире», «важно понимать», «каждый знает», «не секрет, что».\n"
    "— Не пиши как корпоративный документ. Пиши как живой человек.\n"
    "— Первая строка должна захватить внимание — конкретно, без воды.\n"
    "— Пиши конкретно: цифры, кейсы, детали лучше абстракций.\n"
    "— Минимум эмодзи — только там, где они уместны.\n"
    "— Избегай пустых фраз типа «это очень важно» без объяснения почему.\n"
)


def _brief(answers: UserAnswers) -> str:
    return (
        f"Платформа: {PLATFORM_LABELS[answers.platform]}\n"
        f"Ниша: {answers.niche}\n"
        f"Продукт/услуга: {answers.product}\n"
        f"Целевая аудитория: {answers.audience}\n"
        f"Цель контента: {GOAL_LABELS[answers.goal]}\n"
        f"Тон: {TONE_LABELS[answers.tone]}\n"
        f"Длина постов: {LENGTH_LABELS[answers.length]}\n"
    )


def build_plan_prompt(answers: UserAnswers) -> str:
    return (
        "Ты — опытный контент-стратег для малого бизнеса и экспертов в России.\n"
        f"{RUSSIAN_WRITING_RULES}\n"
        "Создай контент-план на 30 дней на основе брифа ниже.\n\n"
        f"БРИФ:\n{_brief(answers)}\n"
        f"Особенности платформы: {PLATFORM_NOTES[answers.platform]}\n\n"
        "Верни ТОЛЬКО валидный JSON-массив из 30 объектов. Никакого другого текста.\n"
        "Каждый объект:\n"
        "{\n"
        '  "day": <число 1-30>,\n'
        '  "topic": "<конкретная тема поста>",\n'
        '  "format": "<expert|engagement|sales|case|faq|personal>",\n'
        '  "goal": "<цель этого поста одной фразой>",\n'
        '  "cta_type": "<тип призыва к действию>",\n'
        '  "visual_type": "<photo|carousel|quote|infographic|story>"\n'
        "}\n\n"
        "Темы должны быть разнообразными: кейсы, советы, личное, ответы на возражения, "
        "полезные факты, продающие посты. Не повторяй форматы подряд больше 2 раз.\n"
        "JSON:"
    )


def build_demo_prompt(answers: UserAnswers, plan: ContentPlan) -> str:
    plan_preview = "\n".join(
        f"День {item.day}: {item.topic} [{item.format}]"
        for item in plan.items[:5]
    )
    return (
        "Ты — профессиональный копирайтер для экспертов и малого бизнеса в России.\n"
        f"{RUSSIAN_WRITING_RULES}\n"
        f"БРИФ:\n{_brief(answers)}\n"
        f"Особенности платформы: {PLATFORM_NOTES[answers.platform]}\n\n"
        f"Первые 5 тем из плана:\n{plan_preview}\n\n"
        "Создай демо-контент. Верни ТОЛЬКО валидный JSON без других слов.\n"
        "Структура JSON:\n"
        "{\n"
        '  "topics": ["<тема 1>", "<тема 2>", "<тема 3>"],\n'
        '  "full_post": {\n'
        '    "day": 1,\n'
        '    "topic": "<тема>",\n'
        '    "hook": "<первые 1-2 предложения, сильный зацеп>",\n'
        '    "body": "<основная часть поста>",\n'
        '    "cta": "<призыв к действию>",\n'
        '    "image_prompt": "<описание визуала на английском для нейросети>"\n'
        "  },\n"
        '  "image_prompt": "<описание визуала для второго поста на английском>"\n'
        "}\n\n"
        f"Длина поста: {LENGTH_LABELS[answers.length]}.\n"
        "Пиши живо, конкретно, без воды. image_prompt — на английском, подробный.\n"
        "JSON:"
    )


def build_full_pack_prompt(answers: UserAnswers, plan: ContentPlan) -> str:
    plan_json = "\n".join(
        f"День {item.day}: {item.topic} [{item.format}] | CTA: {item.cta_type}"
        for item in plan.items
    )
    return (
        "Ты — профессиональный копирайтер для экспертов и малого бизнеса в России.\n"
        f"{RUSSIAN_WRITING_RULES}\n"
        f"БРИФ:\n{_brief(answers)}\n"
        f"Особенности платформы: {PLATFORM_NOTES[answers.platform]}\n\n"
        f"Полный контент-план на 30 дней:\n{plan_json}\n\n"
        "Создай полный контент-пакет. Верни ТОЛЬКО валидный JSON.\n"
        "Структура:\n"
        "{\n"
        '  "plan": [/* 30 объектов плана, те же что выше */],\n'
        '  "posts": [/* 15 полных постов */\n'
        "    {\n"
        '      "day": <число>,\n'
        '      "topic": "<тема>",\n'
        '      "hook": "<зацеп>",\n'
        '      "body": "<основной текст>",\n'
        '      "cta": "<призыв к действию>",\n'
        '      "image_prompt": "<промпт на английском>"\n'
        "    }\n"
        "  ],\n"
        '  "hooks": [/* 30 хуков — по одному на каждый день */],\n'
        '  "cta_ideas": [/* 30 идей CTA */],\n'
        '  "image_prompts": [/* 15 промптов для визуала на английском */],\n'
        '  "calendar_notes": [/* 30 коротких заметок по дням: что публиковать и когда */]\n'
        "}\n\n"
        f"Длина постов: {LENGTH_LABELS[answers.length]}.\n"
        "Посты выбирай для дней 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29.\n"
        "Текст живой, конкретный, не корпоративный. image_prompts — на английском.\n"
        "JSON:"
    )
