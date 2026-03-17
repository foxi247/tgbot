from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.core.enums import (
    Goal,
    PackStatus,
    PaymentStatus,
    Platform,
    PostFormat,
    PostLength,
    Tone,
    VisualType,
)


class UserAnswers(BaseModel):
    platform: Platform
    niche: str
    product: str
    audience: str
    goal: Goal
    tone: Tone
    length: PostLength

    @field_validator("niche", "product", "audience", mode="before")
    @classmethod
    def strip_and_limit(cls, v: str) -> str:
        v = str(v).strip()
        if len(v) > 500:
            v = v[:500]
        return v


class PlanItem(BaseModel):
    day: int = Field(ge=1, le=30)
    topic: str
    format: PostFormat
    goal: str
    cta_type: str
    visual_type: VisualType


class ContentPlan(BaseModel):
    items: list[PlanItem] = Field(min_length=1, max_length=30)


class FullPost(BaseModel):
    day: int
    topic: str
    hook: str
    body: str
    cta: str
    image_prompt: str


class DemoContent(BaseModel):
    topics: list[str] = Field(min_length=3, max_length=3)
    full_post: FullPost
    image_prompt: str


class FullPackContent(BaseModel):
    plan: list[PlanItem]
    posts: list[FullPost] = Field(min_length=1, max_length=15)
    hooks: list[str]
    cta_ideas: list[str]
    image_prompts: list[str]
    calendar_notes: list[str]


class User(BaseModel):
    id: int
    telegram_user_id: int
    username: str | None
    first_name: str | None
    created_at: datetime


class GenerationSession(BaseModel):
    id: int
    user_id: int
    platform: str | None
    niche: str | None
    product: str | None
    audience: str | None
    goal: str | None
    tone: str | None
    length: str | None
    status: PackStatus
    created_at: datetime
    updated_at: datetime


class ContentPack(BaseModel):
    id: int
    session_id: int
    user_id: int
    is_demo: bool
    content_json: dict[str, Any]
    md_path: str | None
    txt_path: str | None
    created_at: datetime


class Payment(BaseModel):
    id: int
    user_id: int
    session_id: int
    amount_rub: int
    status: PaymentStatus
    provider: str
    provider_payment_id: str | None
    created_at: datetime
