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
                    last_analysis TIMESTAMP,
                    encryption_salt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    study_consent_accepted_at TIMESTAMP,
                    study_consent_ip_addr TEXT,
                    study_consent_user_agent TEXT
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
                    status TEXT DEFAULT 'pending',
                    queue_position INTEGER,
                    processing_started TIMESTAMP,
                    processing_completed TIMESTAMP,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    consent_confirmed BOOLEAN DEFAULT FALSE,
                    consent_timestamp TIMESTAMP,
                    consent_ip_addr TEXT,
                    consent_usr_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Add new columns if they don't exist (for existing databases)
            # cursor.execute("PRAGMA table_info(analysis_history)")
            # columns = [column[1] for column in cursor.fetchall()]
            
            # if 'name' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN name TEXT NOT NULL DEFAULT ''")
            # if 'image_base64' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN image_base64 TEXT")
            # if 'status' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN status TEXT DEFAULT 'pending'")
            # if 'queue_position' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN queue_position INTEGER")
            # if 'processing_started' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN processing_started TIMESTAMP")
            # if 'processing_completed' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN processing_completed TIMESTAMP")
            # if 'consent_confirmed' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN consent_confirmed BOOLEAN DEFAULT TRUE")
            # if 'consent_timestamp' not in columns:
            #     cursor.execute("ALTER TABLE analysis_history ADD COLUMN consent_timestamp TIMESTAMP")
            
            # Add last_analysis column to users table if it doesn't exist
            # cursor.execute("PRAGMA table_info(users)")
            # user_columns = [column[1] for column in cursor.fetchall()]
            # if 'last_analysis' not in user_columns:
            #     cursor.execute("ALTER TABLE users ADD COLUMN last_analysis TIMESTAMP")
            # if 'encryption_salt' not in user_columns:
            #     cursor.execute("ALTER TABLE users ADD COLUMN encryption_salt TEXT")
            # if 'study_consent_accepted_at' not in user_columns:
            #     cursor.execute("ALTER TABLE users ADD COLUMN study_consent_accepted_at TIMESTAMP")
            # if 'study_consent_ip_addr' not in user_columns:
            #     cursor.execute("ALTER TABLE users ADD COLUMN study_consent_ip_addr TEXT")
            # if 'study_consent_user_agent' not in user_columns:
            #     cursor.execute("ALTER TABLE users ADD COLUMN study_consent_user_agent TEXT")

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
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users with their analysis counts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    u.id, 
                    u.account_name, 
                    u.email, 
                    u.is_admin, 
                    u.created_at,
                    COUNT(a.id) AS analyses_count
                FROM users u
                LEFT JOIN analysis_history a ON a.user_id = u.id
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_user(self, user_id: int) -> bool:
        """Delete a user and their associated analysis history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analysis_history WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted user ID: {user_id}")
            return deleted
    
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
    
    def update_user_last_analysis(self, user_id: int) -> bool:
        """Update user's last analysis time."""
        utc_now = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_analysis = ? WHERE id = ?",
                (utc_now, user_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated last analysis time for user ID: {user_id}")
            return updated
    
    def get_user_last_analysis(self, user_id: int) -> Optional[str]:
        """Get user's last analysis time."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_analysis FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else None

    def get_user_encryption_salt(self, user_id: int) -> Optional[str]:
        """Return the hex-encoded Argon2 salt for *user_id*, or None if unset."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT encryption_salt FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else None

    def set_user_encryption_salt(self, user_id: int, salt_hex: str) -> None:
        """Persist the hex-encoded Argon2 salt for *user_id*."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET encryption_salt = ? WHERE id = ?",
                (salt_hex, user_id)
            )
            conn.commit()
            logger.debug(f"Set encryption salt for user ID: {user_id}")

    def set_study_consent(self, user_id: int, accepted_at: str, ip_addr, user_agent) -> None:
        """Record a user's study consent and associated audit metadata."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET study_consent_accepted_at = ?,
                    study_consent_ip_addr = ?,
                    study_consent_user_agent = ?
                WHERE id = ?
                """,
                (
                    accepted_at,
                    ip_addr,
                    user_agent,
                    user_id,
                ),
            )
            conn.commit()

            logger.info(
                "Study consent recorded for user ID %s at %s",
                user_id,
                accepted_at,
            )

    def get_study_consent(self, user_id: int) -> Optional[str]:
        """Return the ISO-8601 UTC study-consent timestamp for *user_id*, or None if not yet accepted."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT study_consent_accepted_at FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else None

    def get_user_history_for_reencrypt(self, user_id: int) -> list:
        """Return all history rows (id, image_base64, results, filename, name) for re-encryption
        during a password change.  Intentionally returns *all* rows — no pagination.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, image_base64, results, filename, name
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY id ASC
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


    def update_analysis_images(self, history_id: int,
                               image_base64: Optional[str],
                               results_json: str,
                               filename: Optional[str] = None,
                               name: Optional[str] = None) -> None:
        """Atomically overwrite the image, results, filename and name columns for one history row.
        Used exclusively by the password-change re-encryption flow.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE analysis_history SET image_base64 = ?, results = ?, filename = ?, name = ? WHERE id = ?",
                (image_base64, results_json, filename, name, history_id)
            )
            conn.commit()

    
    def can_user_analyze(self, user_id: int, rate_limit_seconds: int) -> tuple[bool, Optional[int]]:
        """Check if user can submit analysis based on rate limit.
        
        Returns:
            Tuple of (can_analyze: bool, wait_time_seconds: Optional[int])
        """
        last_analysis = self.get_user_last_analysis(user_id)
        if not last_analysis:
            return True, None
        
        try:
            last_time = datetime.fromisoformat(last_analysis.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff >= rate_limit_seconds:
                return True, None
            else:
                wait_time = int(rate_limit_seconds - time_diff) + 1
                return False, wait_time
        except Exception as e:
            logger.error(f"Error checking rate limit for user {user_id}: {str(e)}")
            return True, None
    
    def add_analysis_history(self, user_id: int, analysis_type: str, filename: str, name: str,
                           image_base64: Optional[str], results: Dict[str, Any],
                           status: str = 'pending', queue_position: Optional[int] = None,
                           consent_confirmed: bool = True, consent_timestamp: Optional[str] = None, consent_ip_addr: Optional[str]=None, consent_usr_agent: Optional[str]=None) -> int:
        """Add analysis history entry with mandatory consent audit metadata."""
        utc_now = datetime.now(timezone.utc).isoformat()
        if consent_timestamp is None and consent_confirmed:
            consent_timestamp = utc_now
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_history (user_id, analysis_type, filename, name, image_base64, results, status, queue_position, consent_confirmed, consent_timestamp, consent_ip_addr, consent_usr_agent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, analysis_type, filename, name, image_base64, json.dumps(results), status, queue_position, consent_confirmed, consent_timestamp, consent_ip_addr, consent_usr_agent, utc_now)
            )
            conn.commit()
            history_id = cursor.lastrowid
            logger.info(f"Added analysis history for user {user_id}: {analysis_type} (status: {status}, consent: {consent_confirmed})")
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
    
    def update_analysis_status(self, history_id: int, status: str, results: Optional[Dict[str, Any]] = None,
                              processing_started: Optional[str] = None,
                              processing_completed: Optional[str] = None) -> bool:
        """Update analysis status and results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = ["status = ?"]
            update_values = [status]
            
            if results is not None:
                update_fields.append("results = ?")
                update_values.append(json.dumps(results))
            
            if processing_started is not None:
                update_fields.append("processing_started = ?")
                update_values.append(processing_started)
            
            if processing_completed is not None:
                update_fields.append("processing_completed = ?")
                update_values.append(processing_completed)
            
            update_values.append(history_id)
            
            cursor.execute(
                f"UPDATE analysis_history SET {', '.join(update_fields)} WHERE id = ?",
                update_values
            )
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated analysis {history_id} status to {status}")
            return updated
    
    def get_analysis_status(self, history_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis status by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, status, queue_position, processing_started, processing_completed FROM analysis_history WHERE id = ?",
                (history_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_pending_analyses(self) -> List[Dict[str, Any]]:
        """Get all pending analyses ordered by queue position."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, analysis_type, filename, name, image_base64, queue_position
                FROM analysis_history 
                WHERE status = 'pending' 
                ORDER BY queue_position ASC, timestamp ASC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_queue_position(self, history_id: int) -> Optional[int]:
        """Get queue position for a specific analysis."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT queue_position FROM analysis_history WHERE id = ? AND status = 'pending'",
                (history_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def update_queue_positions(self) -> None:
        """Update queue positions for all pending analyses."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE analysis_history 
                SET queue_position = (
                    SELECT COUNT(*) + 1 
                    FROM analysis_history a2 
                    WHERE a2.status = 'pending' 
                    AND (a2.timestamp < analysis_history.timestamp OR 
                         (a2.timestamp = analysis_history.timestamp AND a2.id < analysis_history.id))
                )
                WHERE status = 'pending'
                """
            )
            conn.commit()
            logger.info("Updated queue positions for pending analyses")


# Global database instance
db = Database()
