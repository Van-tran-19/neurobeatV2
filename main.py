"""
NeuroBeat — Entry point.
Run from the project root:  python main.py
"""


# On importe la classe App depuis le dossier src
from src.app import App 
import os
os.environ["SDL_VIDEODRIVER"] = "cocoa"#mettre x11 lors du portage
if __name__ == "__main__":
    App().run()
