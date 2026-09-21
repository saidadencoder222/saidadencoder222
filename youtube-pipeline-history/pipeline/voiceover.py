"""Synthesizes narration to speech. Default provider is edge-tts (free, no
API key). Also captures word-boundary timings so video_builder.py can time
image changes and captions to the actual narration instead of guessing
from a words-per-minute average.
"""
import asyncio
from dataclasses import dataclass

import edge_tts
import requests


@dataclass
class WordTiming:
    text: str
    start_s: float
    duration_s: float


@dataclass
class Voiceover:
    audio_path: str
    word_timings: list[WordTiming]
    duration_s: float


async def _synthesize_edge(text: str, voice: str, audio_path: str) -> list[WordTiming]:
    # edge-tts >=7 defaults to boundary="SentenceBoundary"; we need word-level
    # timing for caption sync, so request it explicitly.
    communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    timings: list[WordTiming] = []
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timings.append(
                    WordTiming(
                        text=chunk["text"],
                        start_s=chunk["offset"] / 1e7,
                        duration_s=chunk["duration"] / 1e7,
                    )
                )
    return timings


def _synthesize_elevenlabs(text: str, voice_id: str, api_key: str, audio_path: str) -> None:
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2"},
        timeout=180,
    )
    resp.raise_for_status()
    with open(audio_path, "wb") as f:
        f.write(resp.content)


def generate_voiceover(cfg: dict, narration: str, audio_path: str, elevenlabs_api_key: str | None) -> Voiceover:
    provider = cfg["tts"]["provider"]

    if provider == "edge":
        timings = asyncio.run(_synthesize_edge(narration, cfg["tts"]["edge_voice"], audio_path))
        duration = (timings[-1].start_s + timings[-1].duration_s) if timings else 0.0
        if duration <= 0:
            raise RuntimeError(
                "edge-tts returned no audio (0 seconds) — this usually means the connection "
                "to Microsoft's speech service failed or was interrupted silently. Check your "
                "internet connection and try again."
            )
        return Voiceover(audio_path=audio_path, word_timings=timings, duration_s=duration)

    if provider == "elevenlabs":
        if not elevenlabs_api_key:
            raise RuntimeError("tts.provider is 'elevenlabs' but ELEVENLABS_API_KEY is not set.")
        _synthesize_elevenlabs(narration, cfg["tts"]["elevenlabs_voice_id"], elevenlabs_api_key, audio_path)
        return Voiceover(audio_path=audio_path, word_timings=[], duration_s=0.0)

    raise ValueError(f"Unknown tts.provider: {provider}")
