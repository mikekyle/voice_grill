"""Gemini Live audio session lifecycle."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncIterator

from google import genai
from google.genai import types
from google.genai.live import AsyncSession

from src.prompts import build_prompt


def build_system_prompt(topic: str | None = None, grill_mode: str | None = None) -> str:
    return build_prompt(topic=topic, grill_mode=grill_mode)


class GeminiLiveSession:
    """Manages the WebSocket connection to Gemini Live.

    Use as an async context manager — matches the docs pattern:
        async with GeminiLiveSession(api_key, system_prompt) as session:
            await asyncio.gather(send_loop(), recv_loop())
    """

    MODEL = "gemini-3.1-flash-live-preview"
    API_VERSION = "v1alpha"

    def __init__(self, api_key: str | None = None, system_prompt: str = "") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self.system_prompt = system_prompt
        self._session: AsyncSession | None = None
        self._cm = None
        # Set when the server signals the model was interrupted mid-turn.
        # Caller should flush the audio playback queue when this is set.
        self.interrupted = asyncio.Event()

    async def __aenter__(self) -> GeminiLiveSession:
        client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(api_version=self.API_VERSION),
        )
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=self.system_prompt,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            ),
        )
        self._cm = client.aio.live.connect(model=self.MODEL, config=config)
        self._session = await self._cm.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        if self._cm is not None:
            await self._cm.__aexit__(*args)
            self._cm = None
            self._session = None

    async def send_audio(self, pcm16_chunk: bytes) -> None:
        await self._session.send_realtime_input(
            audio=types.Blob(data=pcm16_chunk, mime_type="audio/pcm;rate=16000")
        )

    async def receive_audio(self, debug: bool = False) -> AsyncIterator[bytes]:
        try:
            while True:
                async for response in self._session.receive():
                    if response.server_content and response.server_content.interrupted:
                        self.interrupted.set()
                        if debug:
                            print("[debug] model interrupted by user")
                    if response.data:
                        if debug:
                            print(f"[debug] audio chunk: {len(response.data)} bytes")
                        yield response.data
                    elif debug and response.text:
                        print(f"[debug] text: {response.text!r}")
        except Exception as e:
            print(f"\nSession interrupted: {e}")
            return
