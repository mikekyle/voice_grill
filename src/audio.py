"""Local audio I/O: microphone capture and speaker playback."""

from __future__ import annotations

import queue
import threading
from typing import Callable

import numpy as np
import sounddevice


# Gemini Live audio specs
INPUT_SAMPLE_RATE = 16_000   # Hz, PCM16
OUTPUT_SAMPLE_RATE = 24_000  # Hz, PCM16
CHUNK_DURATION_MS = 20       # ms per capture chunk


def input_chunk_size() -> int:
    return int(INPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


def output_chunk_size() -> int:
    return int(OUTPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


class AudioInput:
    """Capture microphone audio in a background thread."""

    def __init__(self, on_chunk: Callable[[bytes], None], device: int | None = None) -> None:
        self.on_chunk = on_chunk
        self._device = device
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _capture_loop(self) -> None:
        chunk_size = input_chunk_size()
        try:
            with sounddevice.InputStream(
                samplerate=INPUT_SAMPLE_RATE,
                channels=1,
                dtype="int16",
                blocksize=chunk_size,
                device=self._device,
            ) as stream:
                while not self._stop_event.is_set():
                    data, _ = stream.read(chunk_size)
                    self.on_chunk(data.tobytes())
        except sounddevice.PortAudioError as e:
            print(f"\nMicrophone error: {e}")
            self._stop_event.set()


class AudioOutput:
    """Queue and play audio chunks through speakers."""

    def __init__(self, device: int | None = None) -> None:
        self._device = device
        self._queue: queue.Queue[bytes | None] = queue.Queue()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._playback_loop, daemon=True)
        self._thread.start()

    def enqueue(self, pcm16_chunk: bytes) -> None:
        self._queue.put(pcm16_chunk)

    def stop(self) -> None:
        self._queue.put(None)
        if self._thread:
            self._thread.join(timeout=5.0)

    def _playback_loop(self) -> None:
        try:
            with sounddevice.OutputStream(
                samplerate=OUTPUT_SAMPLE_RATE,
                channels=1,
                dtype="int16",
                device=self._device,
            ) as stream:
                while True:
                    chunk = self._queue.get()
                    if chunk is None:
                        break
                    array = np.frombuffer(chunk, dtype=np.int16).reshape(-1, 1)
                    stream.write(array)
        except sounddevice.PortAudioError as e:
            print(f"\nAudio output error: {e}")
