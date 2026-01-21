"""Utility helpers for converting text files to speech audio outputs."""

from __future__ import annotations

import os
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk


def _resolve_scripts_root() -> Path:
    override = os.environ.get("TEXT_DIRECTORY") or os.environ.get("SCRIPTS_ROOT")
    base = Path(override) if override else Path("scripts")
    if not base.is_absolute():
        base = Path.cwd() / base
    return base.resolve()


SCRIPTS_ROOT = _resolve_scripts_root()
AUDIO_ROOT = Path("audio")

speech_key = os.environ.get("SPEECH_KEY")
if not speech_key:
    raise ValueError("Please set the SPEECH_KEY environment variable.")

endpoint_url = os.environ.get("ENDPOINT_URL")
if not endpoint_url:
    raise ValueError("Please set the ENDPOINT_URL environment variable.")

_speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=endpoint_url)


def synthesize_text_file(text_file: str | os.PathLike[str], voice_name: str) -> Path:
    """Generate an audio file for the supplied text file using the provided voice."""
    if not voice_name:
        raise ValueError("Voice name must be provided for speech synthesis.")

    text_path = Path(text_file)
    if not text_path.exists():
        raise FileNotFoundError(f"Text file not found: {text_path}")

    try:
        relative_path = text_path.relative_to(SCRIPTS_ROOT)
    except ValueError as exc:  # pragma: no cover - guardrail
        raise ValueError(
            f"Text file {text_path} must be located under the {SCRIPTS_ROOT} directory."
        ) from exc

    destination = (AUDIO_ROOT / relative_path).with_suffix(".wav")
    destination.parent.mkdir(parents=True, exist_ok=True)

    text_content = text_path.read_text(encoding="utf-8")

    _speech_config.speech_synthesis_voice_name = voice_name
    audio_output = speechsdk.audio.AudioOutputConfig(filename=str(destination))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=_speech_config,
        audio_config=audio_output,
    )

    result = synthesizer.speak_text_async(text_content).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        error = getattr(result, "error_details", "Unknown error")
        raise RuntimeError(f"Speech synthesis failed for {text_path}: {error}")

    return destination
