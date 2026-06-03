from __future__ import annotations
import sys
import json
import os
import pyaudio
from vosk import Model, KaldiRecognizer

SAMPLE_RATE    = 48000
RECORD_SECONDS = 5
CHUNK_SIZE     = 4000

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FR    = os.path.join(_ENGINE_DIR, "vosk-model-small-fr-0.22")
MODEL_EN    = os.path.join(_ENGINE_DIR, "vosk-model-small-en-us-0.15")


def live_transcribe_optimized(model: Model, expected_words: list[str] | None = None) -> str:
    if expected_words:
        grammar = json.dumps(expected_words + ["[unk]"])
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, grammar)
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=1,
            frames_per_buffer=CHUNK_SIZE,
        )
    except Exception as e:
        print(f"[STT] Error opening microphone: {e}")
        p.terminate()
        return ""

    print(f"[STT] Listening for {RECORD_SECONDS} seconds...")
    stream.start_stream()

    num_chunks    = int((SAMPLE_RATE / CHUNK_SIZE) * RECORD_SECONDS)
    transcription = []

    for _ in range(num_chunks):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text   = result.get("text", "").strip()
            if text and text != "[unk]":
                transcription.append(text)

    final = json.loads(recognizer.FinalResult())
    text  = final.get("text", "").strip()
    if text and text != "[unk]":
        transcription.append(text)

    stream.stop_stream()
    stream.close()
    p.terminate()

    result_text = " ".join(transcription).strip()
    print(f"[STT] Result: '{result_text}'")
    return result_text