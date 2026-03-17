from __future__ import annotations

import pytest

from src.integrations.payments import DummyPaymentProvider, get_payment_provider


@pytest.mark.asyncio
async def test_dummy_provider_always_succeeds():
    provider = DummyPaymentProvider()
    result = await provider.create_payment(
        user_id=123,
        amount_rub=299,
        session_id=1,
        description="Тест",
    )
    assert result.success is True
    assert result.payment_id.startswith("dummy_")


@pytest.mark.asyncio
async def test_dummy_provider_check_payment():
    provider = DummyPaymentProvider()
    result = await provider.check_payment("dummy_abc123")
    assert result.success is True
    assert result.payment_id == "dummy_abc123"


@pytest.mark.asyncio
async def test_dummy_provider_unique_ids():
    provider = DummyPaymentProvider()
    r1 = await provider.create_payment(1, 299, 1, "test")
    r2 = await provider.create_payment(1, 299, 2, "test")
    assert r1.payment_id != r2.payment_id


def test_dummy_provider_name():
    provider = DummyPaymentProvider()
    assert provider.name == "dummy"


def test_get_payment_provider_dev_returns_dummy():
    import os
    from unittest.mock import patch

    env = {
        "TELEGRAM_BOT_TOKEN": "test:token",
        "ANTHROPIC_API_KEY": "sk-test",
        "ANTHROPIC_BASE_URL": "https://example.com",
        "APP_ENV": "dev",
        "ENABLE_TEST_UNLOCK": "true",
        "DATABASE_PATH": "/tmp/test.db",
    }
    with patch.dict(os.environ, env, clear=True):
        from importlib import reload
        import src.config as cfg_module
        reload(cfg_module)
        config = cfg_module.load_config()
        provider = get_payment_provider(config)
        assert isinstance(provider, DummyPaymentProvider)


def test_telegram_payment_provider_raises_not_implemented():
    from src.integrations.payments import TelegramPaymentProvider
    import pytest

    provider = TelegramPaymentProvider(provider_token="test_token")
    with pytest.raises(NotImplementedError):
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            provider.create_payment(1, 299, 1, "test")
        )
