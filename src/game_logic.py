# game_logic.py
"""
NeuroBeat — Game logic: answer verification and STT launch.
"""

from __future__ import annotations
from thefuzz import fuzz
from vosk import Model 

from src.engine.stt_live import live_transcribe_optimized, MODEL_FR, MODEL_EN

class GameEngine:
    def __init__(self, db_manager) -> None:
        self.db = db_manager 
        
        # PRE-LOADING IN RAM 
        print("French model is pre-loading..")
        self.loaded_model_fr = Model(MODEL_FR)
        print("English model is pre-loading..")
        self.loaded_model_en = Model(MODEL_EN)
        print("Model ready and loaded ! ")

    def recognize_speech(self, song_data: dict) -> str:
        # We choose the preloaded model
        lang = song_data.get("language", "fr").lower()
        active_model = self.loaded_model_fr if lang == "fr" else self.loaded_model_en

        # We build the vocabulary
        expected_words = self.build_expected_words(song_data)

        # We send the model OBJECT (and no longer the text path)
        return live_transcribe_optimized(active_model, expected_words)

    # ... The rest of the file (check_answer and build_expected_words) remains unchanged! ...
    def check_answer(self, user_input: str, song_data: dict) -> bool:
        """
        Uses thefuzz (token_set_ratio) to tolerate noise and long sentences.
        """
        raw_answers  = song_data.get("phonetic_answers", "") or ""
        valid_answers = [a.strip().lower() for a in raw_answers.split(",") if a.strip()]
        
        # Adding the title, the artist, and both combined to valid answers
        title = song_data.get("title", "").lower()
        artist = song_data.get("artist", "").lower()
        if title: valid_answers.append(title)
        if artist: valid_answers.append(artist)
        if title and artist: valid_answers.append(f"{artist} {title}")

        user_clean = user_input.lower().strip()

        # token_set_ratio gives a score out of 100. 80 is a good threshold for voice.
        for answer in valid_answers:
            if fuzz.token_set_ratio(user_clean, answer) > 80:
                return True
        return False

    def build_expected_words(self, song_data: dict) -> list[str]:
        """
        Prepares the words that Vosk is allowed to understand.
        """
        raw = song_data.get("phonetic_answers", "") or ""
        words = [a.strip().lower() for a in raw.split(",") if a.strip()]
        
        title = song_data.get("title", "").lower()
        artist = song_data.get("artist", "").lower()
        if title: words.append(title)
        if artist: words.append(artist)
        
        return words