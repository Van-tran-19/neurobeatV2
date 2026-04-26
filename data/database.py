import sqlite3
import random
import os

class DatabaseManager:
    def __init__(self, db_name="blindtest.db"):
        # Localisation de la base de données dans le dossier 'data'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(base_dir, db_name)
        self.setup_database()

    def get_connection(self):
        """Établit une connexion avec SQLite et active le format dictionnaire."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des chansons : ajout de la colonne 'kind' (genre/thème)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    title TEXT NOT NULL,
                    phonetic_answers TEXT,
                    kind TEXT DEFAULT 'Général',
                    difficulty INTEGER DEFAULT 1
                )
            ''')
            
            # Table des sessions joueurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_score INTEGER DEFAULT 0
                )
            ''')
            
            # Table des logs de performance (Serious Game)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    song_id INTEGER,
                    reaction_time_ms REAL,
                    was_correct BOOLEAN,
                    FOREIGN KEY(session_id) REFERENCES sessions(id),
                    FOREIGN KEY(song_id) REFERENCES songs(id)
                )
            ''')
            conn.commit()

    # --- MÉTHODES POUR LES CHANSONS ---

    def add_song(self, filename, artist, title, phonetic_answers, kind='Général', difficulty=1):
        """Ajoute une chanson à la bibliothèque avec son genre."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO songs (filename, artist, title, phonetic_answers, kind, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, artist, title, phonetic_answers, kind, difficulty))
            conn.commit()

    def get_random_song(self, theme=None):
        """Récupère une chanson au hasard, optionnellement filtrée par thème."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if theme:
                cursor.execute('SELECT * FROM songs WHERE kind = ? ORDER BY RANDOM() LIMIT 1', (theme,))
            else:
                cursor.execute('SELECT * FROM songs ORDER BY RANDOM() LIMIT 1')
            
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_themes(self):
        """Récupère la liste unique des thèmes/genres disponibles en base."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT kind FROM songs')
            themes = [row['kind'] for row in cursor.fetchall()]
            
            # Retourne une liste par défaut si la base est vide pour éviter le crash de l'app
            return themes if themes else ["Général"]

    # --- MÉTHODES POUR LE SERIOUS GAME (STATS) ---

    def create_session(self, player_name):
        """Démarre une nouvelle session de jeu."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sessions (player_name) VALUES (?)', (player_name,))
            conn.commit()
            return cursor.lastrowid

    def log_reaction(self, session_id, song_id, reaction_time_ms, was_correct):
        """Enregistre les données de réaction pour analyse cognitive."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reaction_logs (session_id, song_id, reaction_time_ms, was_correct)
                VALUES (?, ?, ?, ?)
            ''', (session_id, song_id, reaction_time_ms, was_correct))
            conn.commit()