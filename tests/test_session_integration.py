import pytest


@pytest.mark.skip(reason="Requires live GEMINI_API_KEY and audio hardware")
async def test_session_connects_and_receives_audio():
    """Smoke test: open a session, send silence, receive at least one audio chunk."""
    import os
    from src.session import GeminiLiveSession

    session = GeminiLiveSession(api_key=os.environ["GEMINI_API_KEY"])
    await session.connect("Say hello.")
    silence = b"\x00" * 3200  # 100ms of silence at 16kHz
    await session.send_audio(silence)

    chunks = []
    async for chunk in session.receive_audio():
        chunks.append(chunk)
        if len(chunks) >= 1:
            break

    assert chunks
    await session.close()
