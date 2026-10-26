"""LLM provider abstract base."""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], stream: bool = False) -> str | AsyncIterator[str]:
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...
