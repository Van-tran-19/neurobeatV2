"""
NeuroBeat — Live Speech-to-Text engine (Vosk).
Appelé depuis game_logic.py avec le chemin du modèle et une liste de mots attendus.
"""

import sys
import json
import os
import pyaudio
from vosk import Model, KaldiRecognizer

# --- Configuration par défaut ---
SAMPLE_RATE    = 16000
RECORD_SECONDS = 5
CHUNK_SIZE     = 4000

# Chemin vers les modèles (relatif à ce fichier)
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FR    = os.path.join(_ENGINE_DIR, "vosk-model-small-fr-0.22")
MODEL_EN    = os.path.join(_ENGINE_DIR, "vosk-model-small-en-us-0.15")


def live_transcribe_optimized(model_path: str, expected_words: list[str] | None = None) -> str:
    """
    Écoute le micro pendant RECORD_SECONDS secondes et retourne le texte reconnu.

    Args:
        model_path:     Chemin absolu vers le dossier du modèle Vosk.
        expected_words: Liste de mots/phrases attendus pour restreindre le vocabulaire
                        (accélère fortement la reconnaissance). Si None, pas de restriction.

    Returns:
        Le texte reconnu (str), éventuellement vide si rien n'a été détecté.
    """
    # 1. Chargement du modèle
    print(f"[STT] Chargement du modèle : {model_path}")
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"[STT] Erreur chargement modèle : {e}")
        return ""

    # 2. Initialisation du recognizer
    if expected_words:
        # Grammaire restreinte : on ajoute toujours "[unk]" pour le bruit
        grammar = json.dumps(expected_words + ["[unk]"])
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, grammar)
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    # 3. Ouverture du micro
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
    except Exception as e:
        print(f"[STT] Erreur ouverture micro : {e}")
        p.terminate()
        return ""

    print(f"[STT] Écoute pendant {RECORD_SECONDS} secondes...")
    stream.start_stream()

    num_chunks    = int((SAMPLE_RATE / CHUNK_SIZE) * RECORD_SECONDS)
    transcription = []

    # 4. Traitement en temps réel
    for _ in range(num_chunks):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text   = result.get("text", "").strip()
            if text and text != "[unk]":
                transcription.append(text)

    # 5. Récupération des derniers mots
    final = json.loads(recognizer.FinalResult())
    text  = final.get("text", "").strip()
    if text and text != "[unk]":
        transcription.append(text)

    # 6. Nettoyage
    stream.stop_stream()
    stream.close()
    p.terminate()

    result_text = " ".join(transcription).strip()
    print(f"[STT] Résultat : '{result_text}'")
    return result_text
