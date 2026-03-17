from __future__ import annotations

import asyncio
import logging
from typing import Any

import requests

from src.config import Config

logger = logging.getLogger(__name__)

API_URL = "https://api.mistral.ai/v1/chat/completions"


class MinimaxClientError(Exception):
    pass


class MinimaxClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._headers = {
            "Authorization": f"Bearer {config.mistral_api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        data = {
            "model": self._config.minimax_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(API_URL, headers=self._headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise MinimaxClientError(f"Unexpected response format: {result}") from e

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
                logger.debug("Mistral request attempt %d/%d", attempt, retries)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self._make_request(prompt, temperature, max_tokens),
                )
                logger.debug("Mistral response received (%d chars)", len(result))
                return result
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Rate limited. Waiting %ds before retry.", wait)
                    last_error = e
                    await asyncio.sleep(wait)
                else:
                    logger.error("HTTP error: %s", e)
                    last_error = e
                    if attempt < retries:
                        await asyncio.sleep(2**attempt)
            except requests.Timeout as e:
                wait = 2**attempt
                logger.warning("Timeout. Waiting %ds before retry.", wait)
                last_error = e
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error("Unexpected error calling Mistral: %s", e)
                last_error = e
                break

        raise MinimaxClientError(
            f"Не удалось получить ответ от модели после {retries} попыток. "
            f"Ошибка: {last_error}"
        ) from last_error
