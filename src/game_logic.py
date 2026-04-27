# s6-project/game_logic.py
import Levenshtein # Pour tolérer les petites fautes de frappe/prononciation
from audio_reco.stt_live_1.0 import live_transcribe_optimized

class GameEngine:
    def __init__(self):
        self.model_fr = "vosk-model-small-fr-0.22"
        self.model_en = "vosk-model-small-en-us-0.15"

    def recognize_speech(self, language='fr'):
        model = self.model_fr if language == 'fr' else self.model_en
        # Appelle ta fonction existante dans stt_live_1.0.py
        return live_transcribe_optimized(model)

    def check_answer(self, user_input, song_data):
        # On compare l'input avec les phonetic_answers stockées en DB
        valid_answers = [a.strip().lower() for a in song_data['phonetic_answers'].split(',')]
        user_input = user_input.lower()
        
        for answer in valid_answers:
            # Si la distance est faible (score > 0.8), c'est gagné
            if Levenshtein.ratio(user_input, answer) > 0.8:
                return True
        return False