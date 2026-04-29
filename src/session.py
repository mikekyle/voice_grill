"""Gemini Live audio session lifecycle."""

from __future__ import annotations

import os
from typing import AsyncIterator


def build_system_prompt(topic: str | None = None, grill_mode: str | None = None) -> str:
    """Return the system prompt for a session."""
    # TODO: integrate prompt templates from prompts.py
    raise NotImplementedError


class GeminiLiveSession:
    """Manages the WebSocket connection to Gemini Live."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

    async def connect(self, system_prompt: str) -> None:
        """Open the live connection."""
        raise NotImplementedError

    async def send_audio(self, pcm16_chunk: bytes) -> None:
        """Stream an audio chunk to Gemini."""
        raise NotImplementedError

    async def receive_audio(self) -> AsyncIterator[bytes]:
        """Yield PCM16 audio chunks from Gemini."""
        raise NotImplementedError

    async def close(self) -> None:
        """Clean shutdown."""
        raise NotImplementedError
