"""
Gestionnaire de base de données SQLite pour le questionnaire EORTC QLQ-C30
"""

import sqlite3
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DatabaseManager:
    """Gestionnaire de base de données SQLite"""

    def __init__(self, db_path: str = "data/responses.db"):
        """Initialise le gestionnaire de base de données"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        # Créer le dossier data s'il n'existe pas
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Table des sessions
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    initials TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    today_date TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    audio_enabled BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL
                )
            """
            )

            # Table des réponses
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_num INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    response_text TEXT NOT NULL,
                    transcript TEXT,
                    response_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """
            )

            # Index pour améliorer les performances
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_id ON responses(session_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_question_num ON responses(question_num)"
            )

            conn.commit()

    def create_session(self, personal_info: Dict) -> str:
        """Crée une nouvelle session"""
        session_id = str(uuid.uuid4())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sessions (id, initials, birth_date, today_date, mode, audio_enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    personal_info["initials"],
                    personal_info["birth_date"],
                    personal_info["today_date"],
                    personal_info.get("mode", "Standard"),
                    personal_info.get("audio_enabled", True),
                ),
            )
            conn.commit()

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Récupère une session par son ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def save_response(
        self,
        session_id: str,
        question_num: int,
        question_text: str,
        score: int,
        response_text: str,
        transcript: str = None,
        response_type: str = "manual",
    ) -> bool:
        """Sauvegarde une réponse"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO responses (session_id, question_num, question_text, 
                                        score, response_text, transcript, response_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        question_num,
                        question_text,
                        score,
                        response_text,
                        transcript,
                        response_type,
                    ),
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Erreur sauvegarde réponse: {e}")
            return False

    def get_responses(self, session_id: str) -> List[Dict]:
        """Récupère toutes les réponses d'une session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM responses 
                WHERE session_id = ? 
                ORDER BY question_num
            """,
                (session_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_session_completion(self, session_id: str):
        """Marque une session comme terminée"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions 
                SET completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """,
                (session_id,),
            )
            conn.commit()

    def get_session_statistics(self, session_id: str) -> Dict:
        """Calcule les statistiques d'une session"""
        responses = self.get_responses(session_id)

        # ✅ FILTRER pour exclure la question 0
        responses = [r for r in responses if r.get("question_num", 0) != 0]

        if not responses:
            return {
                "total_questions": 30,
                "answered": 0,
                "missed": 30,
                "completion_rate": 0.0,
                "average_score": 0.0,
            }

        valid_responses = [r for r in responses if r.get("score") is not None]
        scores = [
            r["score"]
            for r in valid_responses
            if isinstance(r.get("score"), (int, float))
        ]

        stats = {
            "total_questions": 30,
            "answered": len(valid_responses),
            "missed": 30 - len(valid_responses),
            "completion_rate": (len(valid_responses) / 30) * 100,
            "average_score": sum(scores) / len(scores) if scores else 0.0,
        }

        return stats

    def export_session_data(self, session_id: str) -> Dict:
        """Exporte toutes les données d'une session"""
        session = self.get_session(session_id)
        responses = self.get_responses(session_id)
        statistics = self.get_session_statistics(session_id)

        return {
            "session": session,
            "responses": responses,
            "statistics": statistics,
            "metadata": {
                "questionnaire": "EORTC QLQ-C30",
                "version": "3.0",
                "exported_at": datetime.datetime.now().isoformat(),
            },
        }

    def delete_session(self, session_id: str) -> bool:
        """Supprime une session et ses réponses"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM responses WHERE session_id = ?", (session_id,)
                )
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Erreur suppression session: {e}")
            return False

    def get_all_sessions(self) -> List[Dict]:
        """Récupère toutes les sessions (pour administration)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.*, 
                       COUNT(r.id) as response_count,
                       MAX(r.timestamp) as last_response
                FROM sessions s
                LEFT JOIN responses r ON s.id = r.session_id
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Nettoie les sessions anciennes"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM responses 
                WHERE session_id IN (
                    SELECT id FROM sessions 
                    WHERE created_at < ?
                )
            """,
                (cutoff_date,),
            )

            cursor.execute(
                """
                DELETE FROM sessions 
                WHERE created_at < ?
            """,
                (cutoff_date,),
            )

            conn.commit()
            return cursor.rowcount
