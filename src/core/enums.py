from enum import Enum


class Platform(str, Enum):
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    VK = "vk"


class Goal(str, Enum):
    SALES = "sales"
    EXPERTISE = "expertise"
    ENGAGEMENT = "engagement"
    PERSONAL_BRAND = "personal_brand"


class Tone(str, Enum):
    EXPERT = "expert"
    SIMPLE = "simple"
    LIVELY = "lively"
    BOLD = "bold"
    PREMIUM = "premium"


class PostLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class PostFormat(str, Enum):
    EXPERT = "expert"
    ENGAGEMENT = "engagement"
    SALES = "sales"
    CASE = "case"
    FAQ = "faq"
    PERSONAL = "personal"


class VisualType(str, Enum):
    PHOTO = "photo"
    CAROUSEL = "carousel"
    QUOTE = "quote"
    INFOGRAPHIC = "infographic"
    STORY = "story"


class PackStatus(str, Enum):
    DRAFT = "draft"
    DEMO_GENERATED = "demo_generated"
    PAID = "paid"
    FULL_GENERATED = "full_generated"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
