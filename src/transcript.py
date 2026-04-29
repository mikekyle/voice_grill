"""Save session transcripts as markdown files."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def save(
    transcript: list[str],
    topic: str | None,
    grill_mode: str | None,
    transcript_dir: str = "transcripts",
) -> Path:
    Path(transcript_dir).mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = (grill_mode or topic or "session").replace(" ", "-")[:40]
    filename = Path(transcript_dir) / f"{ts}_{slug}.md"

    mode_line = f"**Mode:** {grill_mode}" if grill_mode else f"**Topic:** {topic}"
    header = (
        f"# voice_grill session\n\n"
        f"{mode_line}  \n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n"
    )

    filename.write_text(header + "\n".join(transcript), encoding="utf-8")
    return filename
