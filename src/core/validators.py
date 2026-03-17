from __future__ import annotations

import json
import logging
import re

from pydantic import ValidationError

from src.core.schemas import ContentPlan, DemoContent, FullPackContent, FullPost, PlanItem

logger = logging.getLogger(__name__)


class JSONParseError(Exception):
    pass


def _extract_json(raw: str) -> str:
    """Strip markdown fences and extract JSON content."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
    if match:
        return match.group(1).strip()
    return raw


def _repair_json(raw: str, client: object | None = None) -> str:
    """Basic structural repair: truncated arrays, trailing commas."""
    raw = raw.strip()
    # Remove trailing commas before } or ]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    # If it's an array that seems truncated, close it
    if raw.startswith("[") and not raw.endswith("]"):
        # Try closing open objects
        open_braces = raw.count("{") - raw.count("}")
        raw += "}" * max(0, open_braces)
        raw += "]"
    return raw


def parse_plan(raw: str) -> ContentPlan:
    text = _extract_json(raw)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            items = [PlanItem.model_validate(item) for item in data]
        else:
            items = [PlanItem.model_validate(item) for item in data.get("items", [])]
        return ContentPlan(items=items)
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        logger.warning("First parse attempt failed for plan: %s", e)

    repaired = _repair_json(text)
    try:
        data = json.loads(repaired)
        if isinstance(data, list):
            items = [PlanItem.model_validate(item) for item in data]
        else:
            items = [PlanItem.model_validate(item) for item in data.get("items", [])]
        return ContentPlan(items=items)
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        logger.error("Second parse attempt failed for plan: %s", e)
        raise JSONParseError(
            "Не удалось разобрать план контента. Попробуйте сгенерировать заново."
        ) from e


def parse_demo(raw: str) -> DemoContent:
    text = _extract_json(raw)
    try:
        data = json.loads(text)
        return DemoContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("First parse attempt failed for demo: %s", e)

    repaired = _repair_json(text)
    try:
        data = json.loads(repaired)
        return DemoContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error("Second parse attempt failed for demo: %s", e)
        raise JSONParseError(
            "Не удалось разобрать демо-контент. Попробуйте сгенерировать заново."
        ) from e


def parse_full_pack(raw: str) -> FullPackContent:
    text = _extract_json(raw)
    try:
        data = json.loads(text)
        return FullPackContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("First parse attempt failed for full pack: %s", e)

    repaired = _repair_json(text)
    try:
        data = json.loads(repaired)
        return FullPackContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error("Second parse attempt failed for full pack: %s", e)
        raise JSONParseError(
            "Не удалось разобрать полный пакет контента. Попробуйте сгенерировать заново."
        ) from e
