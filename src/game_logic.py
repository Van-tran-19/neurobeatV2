"""
NeuroBeat — Game logic : vérification des réponses et lancement du STT.
"""

from __future__ import annotations
from thefuzz import fuzz
from vosk import Model # <-- On importe Model ici

from src.engine.stt_live import live_transcribe_optimized, MODEL_FR, MODEL_EN

class GameEngine:
    def __init__(self, db_manager) -> None:
        self.db = db_manager 
        
        # PRÉ-CHARGEMENT EN RAM (Prendra quelques secondes au lancement du jeu)
        print("[Système] Préchargement du modèle Français...")
        self.loaded_model_fr = Model(MODEL_FR)
        print("[Système] Préchargement du modèle Anglais...")
        self.loaded_model_en = Model(MODEL_EN)
        print("[Système] Moteur vocal prêt et chargé !")

    def recognize_speech(self, song_data: dict) -> str:
        # On choisit le modèle préchargé
        lang = song_data.get("language", "fr").lower()
        active_model = self.loaded_model_fr if lang == "fr" else self.loaded_model_en

        # On construit le vocabulaire
        expected_words = self.build_expected_words(song_data)

        # On envoie L'OBJET model (et non plus le chemin texte)
        return live_transcribe_optimized(active_model, expected_words)

    # ... La suite du fichier (check_answer et build_expected_words) ne change pas ! ...
    def check_answer(self, user_input: str, song_data: dict) -> bool:
        """
        Utilise thefuzz (token_set_ratio) pour tolérer le bruit et les phrases longues.
        """
        raw_answers  = song_data.get("phonetic_answers", "") or ""
        valid_answers = [a.strip().lower() for a in raw_answers.split(",") if a.strip()]
        
        # Ajout du titre, de l'artiste et des deux combinés dans les réponses valides
        title = song_data.get("title", "").lower()
        artist = song_data.get("artist", "").lower()
        if title: valid_answers.append(title)
        if artist: valid_answers.append(artist)
        if title and artist: valid_answers.append(f"{artist} {title}")

        user_clean = user_input.lower().strip()

        # token_set_ratio donne un score sur 100. 80 est un bon seuil pour la voix.
        for answer in valid_answers:
            if fuzz.token_set_ratio(user_clean, answer) > 80:
                return True
        return False

    def build_expected_words(self, song_data: dict) -> list[str]:
        """
        Prépare les mots que Vosk a le droit de comprendre.
        """
        raw = song_data.get("phonetic_answers", "") or ""
        words = [a.strip().lower() for a in raw.split(",") if a.strip()]
        
        title = song_data.get("title", "").lower()
        artist = song_data.get("artist", "").lower()
        if title: words.append(title)
        if artist: words.append(artist)
        
        return words
