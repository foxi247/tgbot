from __future__ import annotations

import asyncio
import logging
from typing import Any

import anthropic

from src.config import Config

logger = logging.getLogger(__name__)


class MinimaxClientError(Exception):
    pass


class MinimaxClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = anthropic.Anthropic(
            api_key=config.anthropic_api_key,
            base_url=config.anthropic_base_url,
        )

    def _make_request(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        response = self._client.messages.create(
            model=self._config.minimax_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract text from the response
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        raise MinimaxClientError("Empty response from model")

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.75,
        max_tokens: int = 4096,
        retries: int = 3,
    ) -> str:
        """Call the model with exponential backoff retries."""
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                logger.debug("MiniMax request attempt %d/%d", attempt, retries)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self._make_request(prompt, temperature, max_tokens),
                )
                logger.debug("MiniMax response received (%d chars)", len(result))
                return result
            except anthropic.RateLimitError as e:
                wait = 2**attempt
                logger.warning("Rate limited. Waiting %ds before retry.", wait)
                last_error = e
                await asyncio.sleep(wait)
            except anthropic.APITimeoutError as e:
                wait = 2**attempt
                logger.warning("Timeout. Waiting %ds before retry.", wait)
                last_error = e
                await asyncio.sleep(wait)
            except anthropic.APIError as e:
                logger.error("API error: %s", e)
                last_error = e
                if attempt < retries:
                    await asyncio.sleep(2**attempt)
            except Exception as e:
                logger.error("Unexpected error calling MiniMax: %s", e)
                last_error = e
                break

        raise MinimaxClientError(
            f"Не удалось получить ответ от модели после {retries} попыток. "
            f"Ошибка: {last_error}"
        ) from last_error
