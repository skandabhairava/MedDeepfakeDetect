"""Database models and setup."""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from ..core.logging import get_logger

logger = get_logger("models.database")


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = "medical_deepfake.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_name TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    name TEXT NOT NULL,
                    image_base64 TEXT,
                    results TEXT NOT NULL,
                    confidence REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Add new columns if they don't exist (for existing databases)
            cursor.execute("PRAGMA table_info(analysis_history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'name' not in columns:
                cursor.execute("ALTER TABLE analysis_history ADD COLUMN name TEXT NOT NULL DEFAULT ''")
            if 'image_base64' not in columns:
                cursor.execute("ALTER TABLE analysis_history ADD COLUMN image_base64 TEXT")
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON analysis_history(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON analysis_history(timestamp)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_user(self, account_name: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """Create a new user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (account_name, email, password_hash, is_admin)
                VALUES (?, ?, ?, ?)
                """,
                (account_name, email, password_hash, is_admin)
            )
            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"Created user: {email} (ID: {user_id})")
            return user_id
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_user_password(self, user_id: int, new_password_hash: str) -> bool:
        """Update user password."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_password_hash, user_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated password for user ID: {user_id}")
            return updated
    
    def add_analysis_history(self, user_id: int, analysis_type: str, filename: str, name: str,
                           image_base64: Optional[str], results: Dict[str, Any], confidence: Optional[float] = None) -> int:
        """Add analysis history entry."""
        utc_now = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_history (user_id, analysis_type, filename, name, image_base64, results, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, analysis_type, filename, name, image_base64, json.dumps(results), confidence, utc_now)
            )
            conn.commit()
            history_id = cursor.lastrowid
            logger.info(f"Added analysis history for user {user_id}: {analysis_type}")
            return history_id
    
    def delete_analysis_history(self, user_id: int, history_id: int) -> bool:
        """Delete a specific analysis history entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM analysis_history WHERE id = ? AND user_id = ?",
                (history_id, user_id)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted analysis history {history_id} for user {user_id}")
            return deleted
    
    def get_user_history(self, user_id: int, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get user analysis history with pagination."""
        offset = (page - 1) * page_size
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM analysis_history WHERE user_id = ?", (user_id,))
            total = cursor.fetchone()[0]
            
            # Get paginated results
            cursor.execute(
                """
                SELECT * FROM analysis_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
                """,
                (user_id, page_size, offset)
            )
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                entry = dict(row)
                entry['results'] = json.loads(entry['results'])
                history.append(entry)
            
            has_more = (offset + len(history)) < total
            
            return {
                "history": history,
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": has_more
            }


# Global database instance
db = Database()
