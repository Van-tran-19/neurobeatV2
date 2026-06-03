"""
NeuroBeat — Entry point.
Run from the project root:  python main.py
"""


# We import the app from the src folder
from src.app import App 
import os
os.environ["SDL_VIDEODRIVER"] = "x11" #use x11 when using the Raspberry Pi or "cocoa" elsewhere
if __name__ == "__main__":
    App().run()
