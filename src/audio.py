"""Local audio I/O: microphone capture and speaker playback."""

from __future__ import annotations

import queue
import threading
from typing import Callable

import numpy as np


# Gemini Live audio specs
INPUT_SAMPLE_RATE = 16_000   # Hz, PCM16
OUTPUT_SAMPLE_RATE = 24_000  # Hz, PCM16
CHUNK_DURATION_MS = 100      # ms per capture chunk


def input_chunk_size() -> int:
    return int(INPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


def output_chunk_size() -> int:
    return int(OUTPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


class AudioInput:
    """Capture microphone audio in a background thread."""

    def __init__(self, on_chunk: Callable[[bytes], None]) -> None:
        self.on_chunk = on_chunk
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Begin capturing."""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop capturing."""
        raise NotImplementedError


class AudioOutput:
    """Queue and play audio chunks through speakers."""

    def __init__(self) -> None:
        self._queue: queue.Queue[bytes | None] = queue.Queue()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Begin playback worker."""
        raise NotImplementedError

    def enqueue(self, pcm16_chunk: bytes) -> None:
        """Add a chunk to the playback queue."""
        self._queue.put(pcm16_chunk)

    def stop(self) -> None:
        """Drain queue and stop playback."""
        self._queue.put(None)
