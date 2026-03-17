from __future__ import annotations

import pytest

from src.core.formatter import (
    build_markdown_file,
    build_txt_file,
    chunk_text,
    format_brief_summary,
    format_demo_preview,
    format_pack_summary,
)


def test_format_demo_preview(sample_demo, sample_user_answers):
    result = format_demo_preview(sample_demo, sample_user_answers)
    assert "Демо-пакет готов" in result
    assert "Тема 1" in result
    assert "Тема 2" in result
    assert "Тема 3" in result
    assert "Молчание" in result
    assert "image_prompt" not in result  # field name shouldn't appear raw
    assert "<b>" in result  # HTML formatting present


def test_format_pack_summary_counts(sample_full_pack, sample_user_answers):
    result = format_pack_summary(sample_full_pack, sample_user_answers)
    assert "30 тем" in result
    assert "15" in result
    assert "Telegram" in result


def test_format_brief_summary_contains_all_fields(sample_user_answers):
    result = format_brief_summary(sample_user_answers)
    assert "психология отношений" in result
    assert "онлайн-консультация" in result
    assert "Telegram" in result
    assert "экспертност" in result  # goal label


def test_build_markdown_file_structure(sample_full_pack, sample_user_answers):
    md = build_markdown_file(sample_full_pack, sample_user_answers)
    assert "# Контент-пакет" in md
    assert "## 📅 Контент-календарь" in md
    assert "## 🪝 30 хуков" in md
    assert "## 📣 30 идей призывов" in md
    assert "## ✍️ 15 полных постов" in md
    assert "## 🎨 15 промптов" in md
    assert "## 💡 Советы" in md
    # All 30 days present
    assert "День 1" in md
    assert "День 30" in md


def test_build_markdown_contains_posts(sample_full_pack, sample_user_answers):
    md = build_markdown_file(sample_full_pack, sample_user_answers)
    assert "Молчание" in md  # from sample post hook
    assert "Напиши в комменты" in md  # from sample CTA


def test_build_txt_file_structure(sample_full_pack, sample_user_answers):
    txt = build_txt_file(sample_full_pack, sample_user_answers)
    assert "КОНТЕНТ-ПАКЕТ НА 30 ДНЕЙ" in txt
    assert "ХУКИ" in txt
    assert "ПРИЗЫВЫ К ДЕЙСТВИЮ" in txt
    assert "ПОЛНЫЕ ПОСТЫ" in txt
    assert "ПРОМПТЫ ДЛЯ ВИЗУАЛА" in txt


def test_build_txt_contains_niche(sample_full_pack, sample_user_answers):
    txt = build_txt_file(sample_full_pack, sample_user_answers)
    assert "психология отношений" in txt


def test_chunk_text_no_split_needed():
    text = "Короткий текст"
    chunks = chunk_text(text, max_len=4000)
    assert chunks == [text]


def test_chunk_text_splits_on_newline():
    part1 = "a" * 100
    part2 = "b" * 100
    text = part1 + "\n" + part2
    chunks = chunk_text(text, max_len=150)
    assert len(chunks) == 2
    assert part1 in chunks[0]
    assert part2 in chunks[1]


def test_chunk_text_handles_no_newline():
    text = "x" * 500
    chunks = chunk_text(text, max_len=200)
    assert len(chunks) == 3
    assert all(len(c) <= 200 for c in chunks)


def test_html_escaping_in_preview(sample_user_answers):
    from src.core.schemas import DemoContent, FullPost
    dangerous = DemoContent(
        topics=["<script>alert(1)</script>", "Тема 2", "Тема 3"],
        full_post=FullPost(
            day=1,
            topic="t",
            hook="hook & test",
            body="body",
            cta="cta",
            image_prompt="prompt",
        ),
        image_prompt="prompt",
    )
    result = format_demo_preview(dangerous, sample_user_answers)
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "&amp;" in result
