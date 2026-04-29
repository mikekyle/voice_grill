# voice_grill — Planning

## Goal

A dead-simple local CLI that opens a bidirectional audio session with Gemini 3.1 Live Preview. You speak into your mic; Gemini speaks back through your speakers. Transcripts are saved automatically.

The "killer feature" is **elicitation**: structured prompt templates that turn Gemini into a relentless interviewer / grill master on a specific topic.

## Why this instead of phone_me

phone_me got bogged down in telephony plumbing: Twilio accounts, PSTN numbers, WebSocket bridge servers, audio codec conversion (mulaw ↔ PCM16), ngrok tunnels, trial account limitations. The ratio of setup friction to actual utility was too high.

voice_grill strips all that away. If we want a phone interface later, we can add a web app that uses the same core session code. But the daily-use version is just a command you run on your laptop.

## Audio stack

- **Capture:** `sounddevice` (PortAudio wrapper, simpler than PyAudio on Windows/macOS/Linux)
- **Playback:** `sounddevice`
- **Buffer format:** `numpy` int16 arrays
- **Gemini Live expects:** PCM16, 16 kHz input; outputs PCM16 at 24 kHz

## Dependencies

```
google-genai>=1.0.0      # Gemini Live WebSocket client
python-dotenv>=1.0.0     # env loading
sounddevice>=0.5.0       # audio I/O
numpy>=1.26.0            # audio buffers
rich>=14.0.0             # pretty CLI output (optional)
```

## Phases

### Phase 1 — Core audio loop
- [ ] `src/session.py`: open `google.genai.live` connection with audio modality
- [ ] `src/audio.py`: capture mic chunks in a background thread, feed into session
- [ ] `src/audio.py`: receive audio chunks from Gemini, queue for speaker playback
- [ ] `main.py`: wire it together; Ctrl+C saves transcript and exits cleanly
- [ ] `.env` + basic error handling (no mic, no API key, etc.)

### Phase 2 — Elicitation modes
- [ ] `src/prompts.py`: prompt template registry
- [ ] Grill modes:
  - `cv-review` — "You are a ruthless CV reviewer. Find every weak claim."
  - `project-debrief` — "You are a post-mortem facilitator. Keep asking why."
  - `requirements-gathering` — "You are a product manager extracting specs."
  - `free-form` — pass raw topic string
- [ ] CLI: `--grill-mode` and `--topic` args
- [ ] Transcript saved as markdown with timestamp, mode, and topic header

### Phase 3 — Web app (optional, future)
- [ ] FastAPI or similar serves a simple web UI
- [ ] Browser captures mic via WebRTC / getUserMedia
- [ ] Server relays audio to Gemini Live (similar to phone_me's bridge, but simpler because no telephony)
- [ ] Enables phone/mobile use without installing anything

## Open questions

- Does `google-genai` live API expose audio output as raw PCM chunks we can feed to `sounddevice`?
- Latency: will local audio loop feel snappy enough for natural conversation?
- `sounddevice` default device selection on Windows — may need a `--device` flag.
