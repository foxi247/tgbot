from __future__ import annotations

from src.core.enums import Goal, Platform, PostLength, Tone
from src.core.prompt_builder import GOAL_LABELS, LENGTH_LABELS, PLATFORM_LABELS, TONE_LABELS
from src.core.schemas import DemoContent, FullPackContent, UserAnswers


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_demo_preview(demo: DemoContent, answers: UserAnswers) -> str:
    topics_list = "\n".join(f"• {_escape_html(t)}" for t in demo.topics)
    post = demo.full_post
    return (
        f"<b>🔍 Демо-пакет готов</b>\n\n"
        f"<b>3 темы для твоей ниши:</b>\n{topics_list}\n\n"
        f"<b>Пример поста (день 1):</b>\n"
        f"<i>{_escape_html(post.hook)}</i>\n\n"
        f"{_escape_html(post.body)}\n\n"
        f"<b>Призыв:</b> {_escape_html(post.cta)}\n\n"
        f"<b>🖼 Визуал (промпт для ИИ):</b>\n<code>{_escape_html(demo.image_prompt)}</code>"
    )


def format_pack_summary(pack: FullPackContent, answers: UserAnswers) -> str:
    post_count = len(pack.posts)
    hook_count = len(pack.hooks)
    cta_count = len(pack.cta_ideas)
    prompt_count = len(pack.image_prompts)
    return (
        f"<b>📦 Полный контент-пакет готов!</b>\n\n"
        f"<b>Платформа:</b> {PLATFORM_LABELS[answers.platform]}\n"
        f"<b>Ниша:</b> {_escape_html(answers.niche)}\n\n"
        f"✅ 30 тем по дням\n"
        f"✅ {hook_count} хуков\n"
        f"✅ {cta_count} идей CTA\n"
        f"✅ {post_count} полных постов\n"
        f"✅ {prompt_count} промптов для визуала\n"
        f"✅ Календарь на 30 дней\n\n"
        f"Скачай файлы ниже 👇"
    )


def format_brief_summary(answers: UserAnswers) -> str:
    return (
        f"<b>📋 Твой бриф:</b>\n\n"
        f"<b>Платформа:</b> {PLATFORM_LABELS[answers.platform]}\n"
        f"<b>Ниша:</b> {_escape_html(answers.niche)}\n"
        f"<b>Продукт/услуга:</b> {_escape_html(answers.product)}\n"
        f"<b>Аудитория:</b> {_escape_html(answers.audience)}\n"
        f"<b>Цель:</b> {GOAL_LABELS[answers.goal]}\n"
        f"<b>Тон:</b> {answers.tone.value}\n"
        f"<b>Длина:</b> {LENGTH_LABELS[answers.length]}\n"
    )


def build_markdown_file(pack: FullPackContent, answers: UserAnswers) -> str:
    lines: list[str] = []
    lines.append(f"# Контент-пакет на 30 дней")
    lines.append(f"**Платформа:** {PLATFORM_LABELS[answers.platform]}")
    lines.append(f"**Ниша:** {answers.niche}")
    lines.append(f"**Продукт/услуга:** {answers.product}")
    lines.append(f"**Аудитория:** {answers.audience}")
    lines.append(f"**Цель:** {GOAL_LABELS[answers.goal]}")
    lines.append(f"**Тон:** {answers.tone.value}")
    lines.append(f"**Длина постов:** {LENGTH_LABELS[answers.length]}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 📅 Контент-календарь на 30 дней")
    lines.append("")
    for item in pack.plan:
        note = pack.calendar_notes[item.day - 1] if item.day - 1 < len(pack.calendar_notes) else ""
        lines.append(
            f"**День {item.day}** | {item.topic} | `{item.format}` | {item.visual_type}"
        )
        if note:
            lines.append(f"> {note}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 🪝 30 хуков")
    lines.append("")
    for i, hook in enumerate(pack.hooks, 1):
        lines.append(f"**{i}.** {hook}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 📣 30 идей призывов к действию (CTA)")
    lines.append("")
    for i, cta in enumerate(pack.cta_ideas, 1):
        lines.append(f"**{i}.** {cta}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## ✍️ 15 полных постов")
    lines.append("")
    for post in pack.posts:
        lines.append(f"### День {post.day}: {post.topic}")
        lines.append("")
        lines.append(f"**Хук:** {post.hook}")
        lines.append("")
        lines.append(post.body)
        lines.append("")
        lines.append(f"**Призыв:** {post.cta}")
        lines.append("")
        lines.append(f"🖼 **Визуал:** `{post.image_prompt}`")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## 🎨 15 промптов для визуала")
    lines.append("")
    for i, prompt in enumerate(pack.image_prompts, 1):
        lines.append(f"**{i}.** {prompt}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 💡 Советы по использованию")
    lines.append("")
    lines.append("- Публикуй в одно и то же время — это повышает охваты.")
    lines.append("- Чередуй форматы: не ставь два продающих поста подряд.")
    lines.append("- Промпты для визуала используй в Midjourney, DALL-E или Stable Diffusion.")
    lines.append("- Адаптируй хуки под актуальные события в нише.")
    lines.append("- Фиксируй, какие темы дают больше реакций — это основа следующего пакета.")
    lines.append("")

    return "\n".join(lines)


def build_txt_file(pack: FullPackContent, answers: UserAnswers) -> str:
    lines: list[str] = []
    lines.append("КОНТЕНТ-ПАКЕТ НА 30 ДНЕЙ")
    lines.append("=" * 40)
    lines.append(f"Платформа: {PLATFORM_LABELS[answers.platform]}")
    lines.append(f"Ниша: {answers.niche}")
    lines.append(f"Продукт: {answers.product}")
    lines.append(f"Аудитория: {answers.audience}")
    lines.append(f"Цель: {GOAL_LABELS[answers.goal]}")
    lines.append("")

    lines.append("КОНТЕНТ-ПЛАН")
    lines.append("-" * 40)
    for item in pack.plan:
        lines.append(f"День {item.day}: {item.topic} [{item.format}]")
    lines.append("")

    lines.append("ХУКИ (30 штук)")
    lines.append("-" * 40)
    for i, hook in enumerate(pack.hooks, 1):
        lines.append(f"{i}. {hook}")
    lines.append("")

    lines.append("ПРИЗЫВЫ К ДЕЙСТВИЮ (30 штук)")
    lines.append("-" * 40)
    for i, cta in enumerate(pack.cta_ideas, 1):
        lines.append(f"{i}. {cta}")
    lines.append("")

    lines.append("ПОЛНЫЕ ПОСТЫ (15 штук)")
    lines.append("-" * 40)
    for post in pack.posts:
        lines.append(f"\nДень {post.day}: {post.topic}")
        lines.append(f"Хук: {post.hook}")
        lines.append(post.body)
        lines.append(f"CTA: {post.cta}")
        lines.append(f"Визуал: {post.image_prompt}")
        lines.append("-" * 20)
    lines.append("")

    lines.append("ПРОМПТЫ ДЛЯ ВИЗУАЛА (15 штук)")
    lines.append("-" * 40)
    for i, prompt in enumerate(pack.image_prompts, 1):
        lines.append(f"{i}. {prompt}")

    return "\n".join(lines)


def chunk_text(text: str, max_len: int = 4000) -> list[str]:
    """Split text into safe Telegram message chunks."""
    chunks: list[str] = []
    while len(text) > max_len:
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks
