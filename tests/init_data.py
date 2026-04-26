import sys
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from data.database import DatabaseManager


def init_test_data():
    db = DatabaseManager()
    
    print("Ajout des musiques de test...")
    
    # Exemples (Assurez-vous que les fichiers existent dans votre dossier "audio/")
    db.add_song(
        filename="assets/audio/Queen-WeWillRockYou.mp3",
        artist="Queen",
        title="We Will Rock You",
        phonetic_answers="Kouine, Queen, Wi wil rock you",
        kind="rock",
        difficulty=1
    )
    
    db.add_song(
        filename="assets/audio/MichaelJackson-BillieJean.mp3",
        artist="Michael Jackson",
        title="Billie Jean",
        phonetic_answers="Mickael Jackson, Billy Jean",
        kind="variety",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/DaftPunk-GetLucky.mp3",
        artist="Daft Punk",
        title="Get Lucky",
        phonetic_answers="Daf Punk, Get Luki",
        kind="electro",
        difficulty=1
    )
    
    print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_test_data()
