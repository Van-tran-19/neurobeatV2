# data/database.py
import sqlite3
import random
import sys
import os

DB_PATH = os.path.join(sys.path[0], "data", "blindtest.db")

class DatabaseManager:
    def __init__(self, db_name="blindtest.db"):
        # Locate the database
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(base_dir, db_name)
        
        # Establish connection FIRST
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        
        # THEN setup database tables
        self.setup_database()

    def get_connection(self):
        """Establish the connection with SQLite and activate the dictionary format."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self):
        """Create the necessary tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Song Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    title TEXT NOT NULL,
                    phonetic_answers TEXT,
                    kind TEXT DEFAULT 'Général',
                    difficulty INTEGER DEFAULT 1,
                    anecdote TEXT DEFAULT '',
                    language TEXT DEFAULT 'fr' --
                )
            ''')
            
            # Players sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_score INTEGER DEFAULT 0
                )
            ''')
            
            # Logs of performances tables (serious game)
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

            # Table for User Profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    total_score INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    # --- Methods for songs ---

    # Add attribute "fr"
    def add_song(self, filename, artist, title, phonetic_answers, kind='Général', difficulty=1, anecdote="", language="fr"):
        """Adds a song only if it does not already exist, normalizing the theme."""
        clean_kind = kind.strip().upper()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM songs WHERE filename = ?', (filename,))
            if cursor.fetchone():
                print(f"⏸ Ignoré : {title} (déjà dans la base)")
                return

            # Adds "language" in the INSERT INTO and an extra "?"
            cursor.execute('''
                INSERT INTO songs (filename, artist, title, phonetic_answers, kind, difficulty, anecdote, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (filename, artist, title, phonetic_answers, clean_kind, difficulty, anecdote, language))
            conn.commit()
            print(f"Ajouté : {title} dans le thème {clean_kind} (Langue: {language})")
            
    def normalize_existing_themes(self):
        """Updates all existing themes in the DB to make them uniform."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Convert everything to uppercase (UPPER) and remove spaces (TRIM)
            cursor.execute('''
                UPDATE songs 
                SET kind = UPPER(TRIM(kind))
            ''')
            conn.commit()
            print("🧹 Base de données nettoyée : Les thèmes sont maintenant fusionnés !")

    def get_random_song(self, theme=None):
        """Fetches a random song, optionally filtered by theme."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if theme:
                cursor.execute('SELECT * FROM songs WHERE kind = ? ORDER BY RANDOM() LIMIT 1', (theme,))
            else:
                cursor.execute('SELECT * FROM songs ORDER BY RANDOM() LIMIT 1')
            
            row = cursor.fetchone()
            return dict(row) if row else None
        
    def remove_duplicates(self):
        """Removes all duplicates from the songs table (based on the filename)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Removes rows where the ID is not the smallest ID for this filename
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
        """Retrieves the unique list of themes/genres available in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT kind FROM songs')
            themes = [row['kind'] for row in cursor.fetchall()]
            
            # Returns a default list if the database is empty to prevent the app from crashing
            return themes if themes else ["Général"]

    # --- METHODS FOR THE SERIOUS GAME (STATS) ---

    def create_session(self, player_name):
        """Starts a new game session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sessions (player_name) VALUES (?)', (player_name,))
            conn.commit()
            return cursor.lastrowid

    def log_reaction(self, session_id, song_id, reaction_time_ms, was_correct):
        """Logs reaction data (with strict integer conversion for SQLite)."""
        # Force the value to integer: 1 if True, 0 if False
        is_correct_int = 1 if was_correct else 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reaction_logs (session_id, song_id, reaction_time_ms, was_correct)
                VALUES (?, ?, ?, ?)
            ''', (session_id, song_id, reaction_time_ms, is_correct_int))
            conn.commit()
            
    # --- METHODS FOR USER PROFILES ---

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
        """Fetches a random song, excluding the previous one to avoid repetitions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM songs WHERE 1=1'
            params = []

            # Filter by theme if it is not "Tous" / "All"
            if theme and theme != "ALL" and theme != "Tous":
                query += ' AND kind = ?'
                params.append(theme)

            # Exclude the song that just played
            if exclude_id is not None:
                query += ' AND id != ?'
                params.append(exclude_id)

            query += ' ORDER BY RANDOM() LIMIT 1'
            
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return dict(row) if row else None
        
    def get_top_profiles(self, limit=5):
        """Fetch the top players ordered by total score."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, total_score 
                FROM profiles 
                ORDER BY total_score DESC 
                LIMIT ?
            ''', (limit,))
            # Convert rows to dictionaries so they are easy to use in the UI
            return [dict(row) for row in cursor.fetchall()]
        
    def clean_duplicate_profiles(self):
        """Removes duplicate usernames and only keeps the one with the highest score."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # This SQL query finds the best score for each username 
            # and deletes all other corresponding rows.
            cursor.execute('''
                DELETE FROM profiles 
                WHERE user_id NOT IN (
                    SELECT user_id 
                    FROM (
                        SELECT user_id, MAX(total_score) 
                        FROM profiles 
                        GROUP BY username
                    )
                )
            ''')
            
            doublons_supprimes = cursor.rowcount
            conn.commit()
            
            if doublons_supprimes > 0:
                print(f"🧹 Nettoyage : {doublons_supprimes} profil(s) fantôme(s) supprimé(s).")
                
                
    def get_user_stats(self, username):
        """Calculates and retrieves global cognitive statistics for a player."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(r.id) as total_played,
                    AVG(CASE WHEN r.was_correct IN (1, '1', 'True', 'true') THEN r.reaction_time_ms END) as avg_reaction_correct,
                    AVG(r.reaction_time_ms) as avg_reaction_total,
                    SUM(CASE WHEN r.was_correct IN (1, '1', 'True', 'true') THEN 1 ELSE 0 END) as total_correct
                FROM reaction_logs r
                JOIN sessions s ON r.session_id = s.id
                WHERE s.player_name = ?
            ''', (username,))
            row = cursor.fetchone()
            
            # If no games have been played, return None
            if not row or row['total_played'] == 0:
                return None
                
            stats = dict(row)
            # Additional safety to prevent the ratio calculation from crashing if total_correct is empty
            stats['total_correct'] = stats['total_correct'] or 0
            return stats