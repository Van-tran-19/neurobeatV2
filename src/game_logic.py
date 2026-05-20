"""
NeuroBeat — Game logic : vérification des réponses et lancement du STT.
"""
from __future__ import annotations
import unicodedata
import re
import os
import Levenshtein
from src.engine.stt_live import live_transcribe_optimized, MODEL_FR, MODEL_EN

# Seuil de similarité (0.0 → 1.0)
MATCH_THRESHOLD = 0.72


def _normalize(text: str) -> str:
    """
    Nettoie un texte pour la comparaison :
    - Minuscules
    - Supprime les accents        (michaël → michael)
    - Supprime la ponctuation
    - Supprime les mots vides     (feat, ft, the, le, la…)
    """
    text = text.lower().strip()

    # Supprime les accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Supprime la ponctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Mots vides
    stopwords = {"feat", "ft", "the", "les", "de", "du", "la", "le", "un", "une"}
    words = [w for w in text.split() if w not in stopwords]

    return " ".join(words)


def _fuzzy_match(a: str, b: str) -> float:
    """
    Retourne le meilleur score de similarité entre deux chaînes (0.0 → 1.0).
    Combine trois stratégies pour couvrir un maximum de cas.
    """
    a, b = _normalize(a), _normalize(b)
    if not a or not b:
        return 0.0

    # 1. Ratio global  ("michael jackson" vs "mickael jackson")
    score_full = Levenshtein.ratio(a, b)

    # 2. Ratio partiel — a contenu dans b ou inversement
    #    ("jackson" vs "michael jackson")
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    best_partial = 0.0
    for i in range(len(long) - len(short) + 1):
        window = long[i: i + len(short)]
        s = Levenshtein.ratio(short, window)
        if s > best_partial:
            best_partial = s

    # 3. Ratio par tokens triés — insensible à l'ordre des mots
    #    ("jackson michael" vs "michael jackson")
    tokens_a = " ".join(sorted(a.split()))
    tokens_b = " ".join(sorted(b.split()))
    score_tokens = Levenshtein.ratio(tokens_a, tokens_b)

    return max(score_full, best_partial, score_tokens)


class GameEngine:
    """
    Encapsule la logique de reconnaissance vocale et de validation des réponses.
    Instanciée une seule fois dans App et partagée entre les screens.
    """

    def __init__(self, language: str = "fr") -> None:
        self.language   = language
        self.model_path = MODEL_FR if language == "fr" else MODEL_EN

    def recognize_speech(self, expected_words: list[str] | None = None) -> str:
        """
        Lance la transcription live et retourne le texte reconnu.
        Args:
            expected_words: Liste de réponses valides pour restreindre le vocabulaire Vosk.
                            Passer None pour un vocabulaire ouvert (plus lent).
        """
        return live_transcribe_optimized(self.model_path, expected_words)

    def check_answer(self, user_input: str, song_data: dict) -> tuple[bool, float]:
        if not user_input:
            return False, 0.0

        # Construit toutes les réponses acceptables
        raw = song_data.get("phonetic_answers", "") or ""
        valid_answers = [a.strip() for a in raw.split(",") if a.strip()]

        if song_data.get("artist"):
            valid_answers.append(song_data["artist"])
        if song_data.get("title"):
            valid_answers.append(song_data["title"])
        # Artiste + titre ensemble
        if song_data.get("artist") and song_data.get("title"):
            valid_answers.append(f"{song_data['artist']} {song_data['title']}")

        best_score = 0.0
        for answer in valid_answers:
            score = _fuzzy_match(user_input, answer)
            if score > best_score:
                best_score = score

        is_correct = best_score >= MATCH_THRESHOLD
        print(f"[CHECK] '{user_input}' → {best_score:.2f} → {'✅' if is_correct else '❌'}")
        return is_correct, best_score

    def build_expected_words(self, song_data: dict) -> list[str]:
        raw = song_data.get("phonetic_answers", "") or ""
        words = [a.strip().lower() for a in raw.split(",") if a.strip()]

        # Ajoute artiste et titre directement
        if song_data.get("artist"):
            words.append(song_data["artist"].lower())
        if song_data.get("title"):
            words.append(song_data["title"].lower())

        words.append("[unk]")
        return words
    def set_language(self, language: str) -> None:
        self.language   = language
        self.model_path = MODEL_FR if language == "fr" else MODEL_EN