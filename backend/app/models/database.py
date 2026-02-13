"""Database models and setup."""

import sqlite3
import json
from datetime import datetime
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    results TEXT NOT NULL,
                    confidence REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
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
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user last login timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def add_analysis_history(self, user_id: int, analysis_type: str, filename: str, 
                           results: Dict[str, Any], confidence: Optional[float] = None) -> int:
        """Add analysis history entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_history (user_id, analysis_type, filename, results, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, analysis_type, filename, json.dumps(results), confidence)
            )
            conn.commit()
            history_id = cursor.lastrowid
            logger.info(f"Added analysis history for user {user_id}: {analysis_type}")
            return history_id
    
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
