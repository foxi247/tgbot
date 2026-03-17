from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PaymentResult:
    def __init__(self, success: bool, payment_id: str, message: str = "") -> None:
        self.success = success
        self.payment_id = payment_id
        self.message = message


class BasePaymentProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def create_payment(
        self,
        user_id: int,
        amount_rub: int,
        session_id: int,
        description: str,
    ) -> PaymentResult:
        ...

    @abstractmethod
    async def check_payment(self, payment_id: str) -> PaymentResult:
        ...


class DummyPaymentProvider(BasePaymentProvider):
    """Always succeeds. Used in dev mode / test unlock."""

    name = "dummy"

    async def create_payment(
        self,
        user_id: int,
        amount_rub: int,
        session_id: int,
        description: str,
    ) -> PaymentResult:
        payment_id = f"dummy_{uuid.uuid4().hex[:8]}"
        logger.info(
            "DummyPaymentProvider: created payment %s for user %d, %d RUB",
            payment_id,
            user_id,
            amount_rub,
        )
        return PaymentResult(success=True, payment_id=payment_id, message="Тестовый платёж")

    async def check_payment(self, payment_id: str) -> PaymentResult:
        return PaymentResult(success=True, payment_id=payment_id, message="Тестовый платёж")


class TelegramPaymentProvider(BasePaymentProvider):
    """
    Scaffold for real Telegram Payments (Stars or LiqPay/Stripe via Telegram invoice).
    Implement send_invoice + pre_checkout_query + successful_payment handlers
    in bot/handlers/payment_handler.py and wire them here.
    """

    name = "telegram"

    def __init__(self, provider_token: str) -> None:
        self._provider_token = provider_token

    async def create_payment(
        self,
        user_id: int,
        amount_rub: int,
        session_id: int,
        description: str,
    ) -> PaymentResult:
        # TODO: send invoice via bot.send_invoice
        # This requires access to the bot instance, pass it in __init__ when wiring.
        raise NotImplementedError(
            "TelegramPaymentProvider is not yet wired. "
            "Implement send_invoice in bot/handlers and call it here."
        )

    async def check_payment(self, payment_id: str) -> PaymentResult:
        raise NotImplementedError("TelegramPaymentProvider.check_payment not implemented.")


def get_payment_provider(config_obj: object) -> BasePaymentProvider:
    """Return the appropriate provider based on config."""
    from src.config import Config

    cfg: Config = config_obj  # type: ignore[assignment]
    if cfg.test_unlock_enabled:
        return DummyPaymentProvider()
    return DummyPaymentProvider()  # Switch to TelegramPaymentProvider in production
