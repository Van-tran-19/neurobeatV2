import sys
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# --- Configuration ---
MODEL_PATH = "vosk-model-small-fr-0.22"         #French model of vosk to recognize french song
SAMPLE_RATE = 16000
RECORD_SECONDS = 5
CHUNK_SIZE = 4000

# OPTIMIZATION: Restrict the vocabulary. 
# Only include the exact artists and songs in your game.
# Important: "[unk]" must always be included at the end for unknown sounds/noise.
EXPECTED_WORDS = '["bohemian rhapsody", "queen", "michael jackson", "thriller","ninho","zipette" "[unk]"]'

def live_transcribe_optimized(model_path):
    # 1. Load the model
    print("Loading model...")
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # 2. Initialize recognizer with restricted grammar for massive speed boost
    recognizer = KaldiRecognizer(model, SAMPLE_RATE, EXPECTED_WORDS)

    # 3. Initialize PyAudio for live microphone streaming
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=SAMPLE_RATE, 
                        input=True, 
                        frames_per_buffer=CHUNK_SIZE)
    except Exception as e:
        print(f"Error opening microphone: {e}")
        p.terminate()
        sys.exit(1)

    print(f"Listening live for {RECORD_SECONDS} seconds...")
    stream.start_stream()

    # Calculate how many chunks of audio equal 5 seconds
    num_chunks = int((SAMPLE_RATE / CHUNK_SIZE) * RECORD_SECONDS)
    transcription = []

    # 4. Process the audio stream in real-time
    for _ in range(num_chunks):
        # Read a tiny chunk of audio from the microphone
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        
        # Feed it to Vosk immediately
        if recognizer.AcceptWaveform(data):
            result_dict = json.loads(recognizer.Result())
            text = result_dict.get("text", "")
            if text and text != "[unk]":
                transcription.append(text)

    # 5. The 5 seconds are up. Catch the very last words spoken.
    final_dict = json.loads(recognizer.FinalResult())
    final_text = final_dict.get("text", "")
    if final_text and final_text != "[unk]":
        transcription.append(final_text)

    # 6. Clean up the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Join the detected words
    return " ".join(transcription).strip()

if __name__ == "__main__":
    result = live_transcribe_optimized(MODEL_PATH)
    
    print("\n" + "-" * 50)
    print("RESULT:")
    print("-" * 50)
    # If the user mumbled or said something not in the list, it might be empty
    if not result:
        print("No match found in the expected vocabulary.")
    else:
        print(result)
    print("-" * 50 + "\n")
