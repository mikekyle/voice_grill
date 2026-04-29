"""CLI entry point for voice_grill."""

from __future__ import annotations

import argparse
import asyncio
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audio-to-audio Gemini Live elicitation")
    parser.add_argument("--topic", type=str, help="Free-form topic to discuss")
    parser.add_argument(
        "--grill-mode",
        choices=["cv-review", "project-debrief", "requirements-gathering", "cheese-jokes"],
        help="Structured elicitation mode",
    )
    parser.add_argument(
        "--transcript-dir",
        type=str,
        default="transcripts",
        help="Directory to save transcripts",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="sounddevice device index (see --list-devices)",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Print available audio devices and exit",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print audio chunk sizes and interruption signals for debugging",
    )
    return parser.parse_args()


async def main() -> None:
    from dotenv import load_dotenv
    load_dotenv()

    args = parse_args()

    if args.list_devices:
        import sounddevice
        print(sounddevice.query_devices())
        return

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        raise SystemExit(1)

    if args.device is not None:
        import sounddevice
        try:
            sounddevice.query_devices(args.device)
        except sounddevice.PortAudioError as e:
            print(f"Error: audio device {args.device} not available — {e}")
            print("Run with --list-devices to see available devices.")
            raise SystemExit(1)

    if not args.topic and not args.grill_mode:
        print("Error: provide --topic or --grill-mode (or both).")
        raise SystemExit(1)

    from src.prompts import build_prompt
    from src.session import GeminiLiveSession
    from src.audio import AudioInput, AudioOutput
    from src.transcript import save as save_transcript

    system_prompt = build_prompt(topic=args.topic, grill_mode=args.grill_mode)
    transcript: list[str] = []

    try:
        async with GeminiLiveSession(api_key=api_key, system_prompt=system_prompt) as session:
            audio_out = AudioOutput(device=args.device)
            audio_out.start()
            print("Session started. Speak into your mic. Press Ctrl+C to stop.")

            async def mic_to_session() -> None:
                loop = asyncio.get_event_loop()
                chunk_queue: asyncio.Queue[bytes] = asyncio.Queue()

                def on_chunk(data: bytes) -> None:
                    loop.call_soon_threadsafe(chunk_queue.put_nowait, data)

                audio_in = AudioInput(on_chunk=on_chunk, device=args.device)
                audio_in.start()
                try:
                    while not audio_in._stop_event.is_set():
                        try:
                            chunk = await asyncio.wait_for(chunk_queue.get(), timeout=1.0)
                        except asyncio.TimeoutError:
                            continue
                        await session.send_audio(chunk)
                finally:
                    audio_in.stop()

            async def session_to_speaker() -> None:
                async for chunk in session.receive_audio(debug=args.debug):
                    if session.interrupted.is_set():
                        # Model was interrupted — discard buffered audio so it
                        # stops playing immediately and the user's new input is heard.
                        audio_out.clear()
                        session.interrupted.clear()
                        if args.debug:
                            print("[debug] audio queue flushed")
                    audio_out.enqueue(chunk)

            try:
                await asyncio.gather(mic_to_session(), session_to_speaker())
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass
            finally:
                audio_out.stop()
                if transcript:
                    path = save_transcript(transcript, args.topic, args.grill_mode, args.transcript_dir)
                    print(f"Transcript saved: {path}")
                else:
                    print("\nSession ended.")

    except Exception as e:
        msg = str(e).lower()
        if "api_key" in msg or "permission" in msg or "credential" in msg or "401" in msg or "403" in msg:
            print(f"Error: Gemini API authentication failed — check your GEMINI_API_KEY")
        else:
            print(f"Error: could not connect to Gemini Live — {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
