import sys
import wave
import json
from vosk import Model, KaldiRecognizer
import time



#This script is designed to take an wav file already existing and processing it with vosk


# --- Configuration ---
start = time.time()
MODEL_PATH = "vosk-model-small-en-us-0.15"
AUDIO_PATH = "audio.wav"

def transcribe_audio(model_path, audio_path):
    # 1. Load the Vosk model
    print("Loading model...")
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # 2. Open the audio file using a context manager for safe handling
    try:
        with wave.open(audio_path, "rb") as wf:
            
            # 3. Validate audio format (Vosk requires Mono, PCM)
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                print("Error: Audio file must be WAV format, Mono, and PCM.")
                sys.exit(1)

            # 4. Initialize the recognizer with the audio's frame rate
            recognizer = KaldiRecognizer(model, wf.getframerate())
            print("Transcribing audio...")
            
            transcription = []

            # 5. Read and process the audio in chunks
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                # If a phrase is completed, extract the text
                if recognizer.AcceptWaveform(data):
                    result_dict = json.loads(recognizer.Result())
                    text = result_dict.get("text", "")
                    if text:
                        transcription.append(text)

            # 6. Extract any remaining words at the end of the file
            final_dict = json.loads(recognizer.FinalResult())
            final_text = final_dict.get("text", "")
            if final_text:
                transcription.append(final_text)

            # 7. Join all extracted phrases into a single string
            return " ".join(transcription)

    except FileNotFoundError:
        print(f"Error: The file {audio_path} was not found. Please convert your MP3 to WAV first.")
        sys.exit(1)

if __name__ == "__main__":
    # Execute the transcription
    result = transcribe_audio(MODEL_PATH, AUDIO_PATH)
    end = time.time()

    run = end - start
    # Display the final output cleanly
    print("\n" + "-" * 50)
    print("TRANSCRIPTION RESULT:")
    print("-" * 50)
    print(result)
    print("-" * 50 + "\n")
    print(f"{run} secondes to do it")