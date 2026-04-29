"""CLI entry point for voice_grill."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audio-to-audio Gemini Live elicitation")
    parser.add_argument("--topic", type=str, help="Free-form topic to discuss")
    parser.add_argument(
        "--grill-mode",
        choices=["cv-review", "project-debrief", "requirements-gathering"],
        help="Structured elicitation mode",
    )
    parser.add_argument(
        "--transcript-dir",
        type=str,
        default="transcripts",
        help="Directory to save transcripts",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    # TODO: load env, pick prompt, open Gemini session, start audio loop
    raise NotImplementedError("Phase 1 not yet implemented — see PLANNING.md")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
