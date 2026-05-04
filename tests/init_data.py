import sys
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from data.database import DatabaseManager


def init_test_data():
    db = DatabaseManager()
    
    print("Ajout des musiques de test...")
    
    db.add_song(
        filename="assets/audio/Queen-WeWillRockYou.mp3",
        artist="Queen",
        title="We Will Rock You",
        phonetic_answers="Kouine, Queen, Wi wil rock you",
        kind="ROCK",
        difficulty=1
    )
    
    db.add_song(
        filename="assets/audio/MichaelJackson-BillieJean.mp3",
        artist="Michael Jackson",
        title="Billie Jean",
        phonetic_answers="Mickael Jackson, Billy Jean",
        kind="VARIETY",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/DaftPunk-GetLucky.mp3",
        artist="Daft Punk",
        title="Get Lucky",
        phonetic_answers="Daf Punk, Get Luki",
        kind="HOUSE",
        difficulty=1
    )
    
    db.add_song(
        filename="assets/audio/6IX9INE-GOOBA.mp3",
        artist="6IX9INE",
        title="GOOBA",
        phonetic_answers="six nine, gouba",
        kind="RAP",
        difficulty=2
    )
    
    db.add_song(
        filename="assets/audio/DontMakeMeWait.mp3",
        artist="Geods sored",
        title="Don't make me wait",
        phonetic_answers="music de Henri, don't make me wait",
        kind="HOUSE",
        difficulty=3
    )
    
    
    db.add_song(
        filename="assets/audio/Beethoven-MoonlightSonata.mp3",
        artist="Beethoven",
        title="Moonlight Sonata",
        phonetic_answers="beethoven, moonlight sonata, sonate au clair de lune",
        kind="CLASSIC",
        difficulty=1
    )

    db.add_song(
        filename="assets/audio/ÉlocutionGazo.mp3",
        artist="Gazo",
        title="Élocution",
        phonetic_answers="gazo, elocution, élocution",
        kind="REF",
        difficulty=3
    )

    db.add_song(
        filename="assets/audio/Fredagain-Marea.mp3",
        artist="Fred again",
        title="Marea",
        phonetic_answers="fred again, marea, we've lost dancing",
        kind="HOUSE",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/Gazoexpliquesesparoles.mp3",
        artist="Gazo",
        title="Explique ses paroles",
        phonetic_answers="gazo, explique ses paroles, interview gazo",
        kind="REF",
        difficulty=4
    )

    db.add_song(
        filename="assets/audio/GAZO-KATfeat.Rvfleuze.mp3",
        artist="Gazo feat. Rvfleuze",
        title="K.A.T",
        phonetic_answers="gazo, kat, k a t, rvfleuze, rafaleuse",
        kind="RAP",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/GIMS&LaMano1.9-PARISIENNE.mp3",
        artist="GIMS & La Mano 1.9",
        title="PARISIENNE",
        phonetic_answers="gims, maitre gims, la mano, parisienne",
        kind="RAP",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/Guy2Bezbar-Monaco.mp3",
        artist="Guy2Bezbar",
        title="Monaco",
        phonetic_answers="guy de bezbar, guy2bezbar, monaco",
        kind="RAP",
        difficulty=2
    )

    db.add_song(
        filename="assets/audio/InterstellarMainTheme.mp3",
        artist="Hans Zimmer",
        title="Interstellar Main Theme",
        phonetic_answers="hans zimmer, interstellar, theme principal interstellar, film interstellar",
        kind="OST",
        difficulty=1
    )
    
    print("Base de données initialisée avec succès !")
    db.remove_duplicates()
    db.normalize_existing_themes()
    
    
    print("Success! All songs have been injected and duplicates removed.")

if __name__ == "__main__":
    init_test_data()
