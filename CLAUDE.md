# voice_grill

> **Status: Skeleton — no implementation yet**
> See PLANNING.md for phases and design decisions.

Simple CLI audio-to-audio sessions with Gemini 3.1 Live Preview. No telephony, no web server, no bloat. Mic in, speakers out.

Primary use case: **elicitation** — the AI grills you about a topic. Think structured self-interview, requirements gathering, or thinking-out-loud facilitation.

## Architecture

```
CLI: uv run python main.py --topic "..."
    │
    ▼
Audio input (mic) ──► Gemini Live WebSocket ──► Audio output (speakers)
    │                        │
    └──► transcript saved ◄──┘
```

The entire session runs locally. There is no bridge server, no ngrok, no PSTN provider.

## Quick start

```bash
uv sync
cp .env.example .env
# add GEMINI_API_KEY
uv run python main.py --topic "Help me think through the architecture for X"
```

## Elicitation modes

```bash
# Free-form topic
uv run python main.py --topic "Why did the last project fail?"

# Structured grill mode (prompts defined in src/prompts.py)
uv run python main.py --grill-mode cv-review
uv run python main.py --grill-mode project-debrief
uv run python main.py --grill-mode requirements-gathering
```

## Environment

```bash
GEMINI_API_KEY=           # required
TRANSCRIPT_DIR=transcripts/
```

## Source layout

```
src/
  session.py     # Gemini Live WebSocket session lifecycle
  audio.py       # Mic capture + speaker playback (sounddevice)
  prompts.py     # Elicitation prompt templates and grill modes
main.py          # CLI entry point
```

## Design constraints

- **No telephony.** If we want a phone interface later, that is Phase 3 (web app).
- **No FastAPI / web framework.** This is a local process, not a server.
- **Minimal deps.** `google-genai`, `sounddevice`, `numpy`, `python-dotenv`. No Pipecat, no Twilio, no Daily.
- **Blocking CLI.** Run it, talk, hit Ctrl+C to stop. Save transcript on exit.
