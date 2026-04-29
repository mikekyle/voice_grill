"""Gemini Live audio session lifecycle."""

from __future__ import annotations

import os
from typing import AsyncIterator

from google import genai
from google.genai import types
from google.genai.live import AsyncSession

from src.prompts import build_prompt


def build_system_prompt(topic: str | None = None, grill_mode: str | None = None) -> str:
    return build_prompt(topic=topic, grill_mode=grill_mode)


class GeminiLiveSession:
    """Manages the WebSocket connection to Gemini Live."""

    # Preview models live on v1alpha, not v1beta (the SDK default)
    MODEL = "gemini-3.1-flash-live-preview"
    API_VERSION = "v1alpha"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._session: AsyncSession | None = None
        self._cm = None

    async def connect(self, system_prompt: str) -> None:
        client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(api_version=self.API_VERSION),
        )
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=system_prompt,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            ),
        )
        self._cm = client.aio.live.connect(model=self.MODEL, config=config)
        self._session = await self._cm.__aenter__()

    async def send_audio(self, pcm16_chunk: bytes) -> None:
        await self._session.send_realtime_input(
            media=types.Blob(data=pcm16_chunk, mime_type="audio/pcm;rate=16000")
        )

    async def receive_audio(self) -> AsyncIterator[bytes]:
        try:
            async for response in self._session.receive():
                if response.data:
                    yield response.data
        except Exception as e:
            print(f"\nSession interrupted: {e}")
            return

    async def close(self) -> None:
        if self._cm is not None:
            await self._cm.__aexit__(None, None, None)
            self._cm = None
            self._session = None
