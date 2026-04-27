"""
NeuroBeat — Game logic : vérification des réponses et lancement du STT.
"""

from __future__ import annotations
import Levenshtein
import os

from src.engine.stt_live import live_transcribe_optimized, MODEL_FR, MODEL_EN


class GameEngine:
    """
    Encapsule la logique de reconnaissance vocale et de validation des réponses.
    Instanciée une seule fois dans App et partagée entre les screens.
    """

    def __init__(self, language: str = "fr") -> None:
        self.language  = language
        self.model_path = MODEL_FR if language == "fr" else MODEL_EN

    def recognize_speech(self, expected_words: list[str] | None = None) -> str:
        """
        Lance la transcription live et retourne le texte reconnu.

        Args:
            expected_words: Liste de réponses valides pour restreindre le vocabulaire Vosk.
                            Passer None pour un vocabulaire ouvert (plus lent).
        """
        return live_transcribe_optimized(self.model_path, expected_words)

    def check_answer(self, user_input: str, song_data: dict) -> bool:
        """
        Compare l'input utilisateur aux réponses phonétiques acceptées (stockées en DB).
        Tolère les petites fautes grâce à la distance de Levenshtein (seuil 0.75).

        Returns:
            True si une réponse correspond, False sinon.
        """
        raw_answers  = song_data.get("phonetic_answers", "") or ""
        valid_answers = [a.strip().lower() for a in raw_answers.split(",") if a.strip()]
        user_clean   = user_input.lower().strip()

        for answer in valid_answers:
            if Levenshtein.ratio(user_clean, answer) > 0.75:
                return True
        return False

    def build_expected_words(self, song_data: dict) -> list[str]:
        """
        Construit la liste des mots attendus pour la grammaire Vosk à partir d'une chanson.
        Permet d'accélérer massivement la reconnaissance.
        """
        raw = song_data.get("phonetic_answers", "") or ""
        return [a.strip().lower() for a in raw.split(",") if a.strip()]
