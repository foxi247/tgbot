from __future__ import annotations

import logging
from pathlib import Path

from src.core.formatter import build_markdown_file, build_txt_file
from src.core.prompt_builder import build_demo_prompt, build_full_pack_prompt, build_plan_prompt
from src.core.schemas import DemoContent, FullPackContent, UserAnswers
from src.core.validators import JSONParseError, parse_demo, parse_full_pack, parse_plan
from src.integrations.minimax_client import MinimaxClient

logger = logging.getLogger(__name__)


class ContentGenerationError(Exception):
    """User-facing generation error."""


class ContentService:
    def __init__(self, client: MinimaxClient, packs_dir: Path) -> None:
        self.client = client
        self.packs_dir = packs_dir

    async def generate_demo(self, answers: UserAnswers) -> DemoContent:
        # Stage 1: plan
        plan_prompt = build_plan_prompt(answers)
        logger.info("Generating content plan...")
        plan_raw = await self.client.generate_json(plan_prompt)
        try:
            plan = parse_plan(plan_raw)
        except JSONParseError as e:
            raise ContentGenerationError(str(e)) from e

        # Stage 2: demo
        demo_prompt = build_demo_prompt(answers, plan)
        logger.info("Generating demo content...")
        demo_raw = await self.client.generate_json(demo_prompt)
        try:
            return parse_demo(demo_raw)
        except JSONParseError as e:
            raise ContentGenerationError(str(e)) from e

    async def generate_full_pack(
        self, answers: UserAnswers, user_id: int
    ) -> tuple[FullPackContent, Path, Path]:
        # Stage 1: plan
        plan_prompt = build_plan_prompt(answers)
        logger.info("Generating content plan for full pack...")
        plan_raw = await self.client.generate_json(plan_prompt, temperature=0.85)
        try:
            plan = parse_plan(plan_raw)
        except JSONParseError as e:
            raise ContentGenerationError(str(e)) from e

        # Stage 2: full pack
        pack_prompt = build_full_pack_prompt(answers, plan)
        logger.info("Generating full pack content...")
        pack_raw = await self.client.generate_json(pack_prompt, temperature=0.85, max_tokens=6000)
        try:
            pack = parse_full_pack(pack_raw)
        except JSONParseError as e:
            raise ContentGenerationError(str(e)) from e

        # Save files
        user_dir = self.packs_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        md_content = build_markdown_file(pack, answers)
        txt_content = build_txt_file(pack, answers)

        md_path = user_dir / "content_pack.md"
        txt_path = user_dir / "content_pack.txt"

        md_path.write_text(md_content, encoding="utf-8")
        txt_path.write_text(txt_content, encoding="utf-8")

        logger.info("Files saved: %s, %s", md_path, txt_path)
        return pack, md_path, txt_path
