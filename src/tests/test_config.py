from __future__ import annotations

import os
import pytest
from unittest.mock import patch


def test_config_loads_from_env():
    env = {
        "TELEGRAM_BOT_TOKEN": "test:token",
        "ANTHROPIC_API_KEY": "sk-test",
        "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
        "APP_ENV": "dev",
        "ENABLE_TEST_UNLOCK": "true",
        "FULL_PLAN_PRICE_RUB": "299",
        "DATABASE_PATH": "/tmp/test_bot.db",
        "MINIMAX_MODEL": "MiniMax-M2.5",
    }
    with patch.dict(os.environ, env, clear=True):
        from importlib import reload
        import src.config as cfg_module
        reload(cfg_module)
        config = cfg_module.load_config()
        assert config.telegram_bot_token == "test:token"
        assert config.is_dev is True
        assert config.test_unlock_enabled is True
        assert config.full_plan_price_rub == 299


def test_config_is_dev_false_in_prod():
    env = {
        "TELEGRAM_BOT_TOKEN": "test:token",
        "ANTHROPIC_API_KEY": "sk-test",
        "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
        "APP_ENV": "production",
        "ENABLE_TEST_UNLOCK": "false",
        "DATABASE_PATH": "/tmp/test_bot2.db",
    }
    with patch.dict(os.environ, env, clear=True):
        from importlib import reload
        import src.config as cfg_module
        reload(cfg_module)
        config = cfg_module.load_config()
        assert config.is_dev is False
        assert config.test_unlock_enabled is False
