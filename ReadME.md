# NeuroBeat V2

NeuroBeat V2 is an interactive musical application developed as a Semester 6 academic project. It features a custom game engine, audio playback capabilities, and real-time speech recognition (Speech-To-Text) to create an engaging cognitive training and blind-test experience.

## Features

* **Game Engine:** User interface and core application logic are built using pygame.
* **Live Speech Recognition (STT):** Real-time voice transcription supporting multiple languages (French and English) to handle user inputs.
* **Diverse Audio Library:** Includes a varied selection of tracks ranging from classical music (Beethoven) to electronic (Daft Punk) and modern rap (Gazo).
* **Modular Architecture:** Clean codebase separation between the graphical interface (app.py), game rules (game_logic.py), and the audio/voice engine (stt_live.py).

## System Requirements

Because the project relies on pyaudio for live microphone capture, specific system-level libraries are required before installing the Python packages. 

For Debian/Ubuntu-based systems, run the following commands:

    sudo apt-get update
    sudo apt-get install portaudio19-dev python3-dev

## Installation

1. Clone the repository:

    git clone https://github.com/goza/neurobeatV2.git
    cd neurobeatV2

2. Create and activate a virtual environment:

    python3 -m venv venv
    source venv/bin/activate

3. Install Python dependencies:

    pip install pygame pyaudio

*(Note: Ensure any additional packages required by the STT engine, such as Vosk or SpeechRecognition, are also installed).*

## Usage

Once the virtual environment is active and all dependencies are installed, you can launch the application from the root directory:

    python main.py

## Project Structure

    neurobeatV2/
    ├── .gitignore
    ├── main.py
    ├── assets/
    │   └── audio/
    └── src/
        ├── app.py
        ├── game_logic.py
        └── engine/
            └── stt_live.py