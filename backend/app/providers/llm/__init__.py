"""OpenAI-compatible LLM provider (works with Ollama, vLLM, LM Studio, etc.)."""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator

import httpx

from app.core.config import settings
from app.providers.llm.base import LLMProvider

log = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self) -> None:
        self._base_url = settings.LLM_BASE_URL.rstrip("/")
        self._api_key = settings.LLM_API_KEY or "none"
        self._model = settings.LLM_MODEL

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, messages: list[dict], stream: bool = False) -> str | AsyncIterator[str]:
        payload = {"model": self._model, "messages": messages, "stream": stream}
        if stream:
            return self._stream(payload)
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _stream(self, payload: dict) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{self._base_url}/models",
                    headers=self._headers(),
                )
                return resp.status_code == 200
        except Exception:
            return False

    def get_provider_name(self) -> str:
        return f"OpenAI-compatible ({self._base_url}, model={self._model})"


class MockLLMProvider(LLMProvider):
    """Deterministic mock for development and testing."""

    async def chat(self, messages: list[dict], stream: bool = False) -> str | AsyncIterator[str]:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        response = (
            f"[Mock AI Coach] I received your question: \"{last_user[:100]}\"\n\n"
            "This is the mock LLM provider. To enable real AI coaching:\n"
            "1. Install Ollama: https://ollama.com\n"
            "2. Run: `ollama pull llama3.2`\n"
            "3. Set LLM_PROVIDER=ollama in your .env file\n\n"
            "Your training data is available — the AI coach will analyse it once an LLM is configured."
        )
        if stream:
            async def _gen():
                for word in response.split(" "):
                    yield word + " "
            return _gen()
        return response

    async def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return "Mock LLM (Demo Mode)"


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER in ("ollama", "openai_compatible"):
        return OpenAICompatibleProvider()
    return MockLLMProvider()
