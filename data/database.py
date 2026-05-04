# data/database.py
import sqlite3
import random
import sys
import os

DB_PATH = os.path.join(sys.path[0], "data", "blindtest.db")

class DatabaseManager:
    def __init__(self, db_name="blindtest.db"):
        # Localisation de la base de données dans le dossier 'data'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(base_dir, db_name)
        
        # 1. Establish connection FIRST
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        
        # 2. THEN setup database tables
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
            
            # Table des chansons
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

            # NEW: Table for User Profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    total_score INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    # --- MÉTHODES POUR LES CHANSONS ---

    def add_song(self, filename, artist, title, phonetic_answers, kind='Général', difficulty=1):
        """Ajoute une chanson uniquement si elle n'existe pas déjà, en normalisant le thème."""
        
        # 1. NETTOYAGE DU THÈME (enlève les espaces autour et met tout en majuscules)
        clean_kind = kind.strip().upper()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si le fichier existe déjà dans la base
            cursor.execute('SELECT id FROM songs WHERE filename = ?', (filename,))
            if cursor.fetchone():
                print(f"⏸ Ignoré : {title} (déjà dans la base)")
                return

            # Si elle n'existe pas, on l'ajoute avec le thème nettoyé (clean_kind)
            cursor.execute('''
                INSERT INTO songs (filename, artist, title, phonetic_answers, kind, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, artist, title, phonetic_answers, clean_kind, difficulty))
            conn.commit()
            print(f"✅ Ajouté : {title} dans le thème {clean_kind}")
            
    def normalize_existing_themes(self):
        """Met à jour tous les thèmes existants dans la DB pour qu'ils soient uniformes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # On met tout en majuscules (UPPER) et on enlève les espaces (TRIM)
            cursor.execute('''
                UPDATE songs 
                SET kind = UPPER(TRIM(kind))
            ''')
            conn.commit()
            print("🧹 Base de données nettoyée : Les thèmes sont maintenant fusionnés !")

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
        
    def remove_duplicates(self):
        """Supprime tous les doublons de la table songs (basé sur le nom du fichier)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Supprime les lignes dont l'ID n'est pas le plus petit ID pour ce nom de fichier
            cursor.execute('''
                DELETE FROM songs 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM songs 
                    GROUP BY filename
                )
            ''')
            doublons_supprimes = cursor.rowcount
            conn.commit()
            if doublons_supprimes > 0:
                print(f"🧹 Nettoyage : {doublons_supprimes} doublon(s) supprimé(s).")

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
            
    # --- MÉTHODES POUR LES PROFILS UTILISATEURS ---

    def save_score(self, username, score):
        """Update high score for a specific player or create them if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Try to insert the user if they don't exist
            cursor.execute("INSERT OR IGNORE INTO profiles (username, total_score) VALUES (?, 0)", (username,))
            # Update their score
            cursor.execute("UPDATE profiles SET total_score = total_score + ? WHERE username = ?", (score, username))
            conn.commit()

    def get_profile(self, username):
        """Retrieve user data to display in the Front End"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
            return cursor.fetchone()
        
    def get_random_song(self, theme=None, exclude_id=None):
        """Récupère une chanson au hasard, en excluant la précédente pour éviter les répétitions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM songs WHERE 1=1'
            params = []

            # Filtrer par thème si ce n'est pas "Tous" / "All"
            if theme and theme != "All" and theme != "Tous":
                query += ' AND kind = ?'
                params.append(theme)

            # Exclure la musique qui vient juste de passer
            if exclude_id is not None:
                query += ' AND id != ?'
                params.append(exclude_id)

            query += ' ORDER BY RANDOM() LIMIT 1'
            
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return dict(row) if row else None