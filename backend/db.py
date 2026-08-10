"""
Database abstraction layer supporting both SQLite and PostgreSQL
"""
import os
import sqlite3
from typing import Optional, List, Tuple, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite').lower()
DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'certificates.db')

# Try to import PostgreSQL driver
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    if DATABASE_TYPE == 'postgresql':
        print("WARNING: psycopg2 not installed. Install with: pip install psycopg2-binary")
        print("Falling back to SQLite")
        DATABASE_TYPE = 'sqlite'

COURSE_COLUMNS = [
    ("course_text_x", "REAL"),
    ("course_text_y", "REAL"),
    ("course_font", "TEXT"),
    ("course_font_size", "INTEGER"),
    ("course_alignment", "TEXT"),
    ("course_color", "TEXT"),
]


def _with_course_defaults(row_dict):
    name_y = row_dict["text_y"]
    if row_dict.get("course_text_x") is None:
        row_dict["course_text_x"] = row_dict["text_x"]
    if row_dict.get("course_text_y") is None:
        row_dict["course_text_y"] = name_y + 60
    if row_dict.get("course_font") is None:
        row_dict["course_font"] = row_dict["font"]
    if row_dict.get("course_font_size") is None:
        row_dict["course_font_size"] = row_dict["font_size"]
    if row_dict.get("course_alignment") is None:
        row_dict["course_alignment"] = row_dict["alignment"]
    if row_dict.get("course_color") is None:
        row_dict["course_color"] = row_dict["color"]
    return row_dict


class Database:
    """Database abstraction layer"""

    def __init__(self):
        self.db_type = DATABASE_TYPE
        self.conn = None

        if self.db_type == 'postgresql' and POSTGRES_AVAILABLE and DATABASE_URL:
            try:
                self.conn = psycopg2.connect(DATABASE_URL)
                # ponytail: one long-lived conn; without autocommit, health-check
                # SELECTs stay idle-in-transaction and block ALTER/DDL. Upgrade: pool.
                self.conn.autocommit = True
                print(f"[OK] Connected to PostgreSQL database")
            except Exception as e:
                print(f"ERROR: Failed to connect to PostgreSQL: {e}")
                print("Falling back to SQLite")
                self.db_type = 'sqlite'
                self.conn = None

        if self.db_type == 'sqlite':
            self.db_path = DATABASE_PATH
            print(f"[OK] Using SQLite database: {self.db_path}")

    def get_connection(self):
        """Get database connection"""
        if self.db_type == 'postgresql':
            if not self.conn or self.conn.closed:
                self.conn = psycopg2.connect(DATABASE_URL)
                self.conn.autocommit = True
            return self.conn
        else:
            return sqlite3.connect(self.db_path)

    def execute(self, query: str, params: Tuple = ()) -> Any:
        """Execute a query and return cursor"""
        conn = self.get_connection()

        # Convert query for PostgreSQL
        if self.db_type == 'postgresql':
            query = query.replace('?', '%s')
            cursor = conn.cursor()
        else:
            cursor = conn.cursor()

        try:
            cursor.execute(query, params)
        except Exception:
            # ponytail: one shared psycopg2 connection — a failed ALTER aborts the
            # txn and every later query 500s until rollback. Upgrade: pool + retry.
            if self.db_type == "postgresql":
                conn.rollback()
            raise
        return cursor, conn

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """Execute query and fetch one result"""
        cursor, conn = self.execute(query, params)
        result = cursor.fetchone()
        if self.db_type == 'sqlite':
            conn.close()
        return result

    def fetchall(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute query and fetch all results"""
        cursor, conn = self.execute(query, params)
        results = cursor.fetchall()
        if self.db_type == 'sqlite':
            conn.close()
        return results

    def insert(self, query: str, params: Tuple = ()) -> int:
        """Execute insert query and return last inserted ID"""
        cursor, conn = self.execute(query, params)

        if self.db_type == 'postgresql':
            # PostgreSQL needs RETURNING clause for getting last ID
            # We'll handle this in the calling code
            last_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        else:
            last_id = cursor.lastrowid

        conn.commit()
        if self.db_type == 'sqlite':
            conn.close()

        return last_id

    def commit_query(self, query: str, params: Tuple = ()) -> None:
        """Execute query and commit (for UPDATE, DELETE)"""
        cursor, conn = self.execute(query, params)
        conn.commit()
        if self.db_type == 'sqlite':
            conn.close()

    def init_database(self):
        """Initialize database tables"""
        if self.db_type == 'postgresql':
            create_table_sql = '''
                CREATE TABLE IF NOT EXISTS templates (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    image_base64 TEXT NOT NULL,
                    text_x REAL NOT NULL,
                    text_y REAL NOT NULL,
                    font TEXT NOT NULL,
                    font_size INTEGER NOT NULL,
                    alignment TEXT NOT NULL,
                    color TEXT NOT NULL,
                    language TEXT NOT NULL,
                    course_text_x REAL,
                    course_text_y REAL,
                    course_font TEXT,
                    course_font_size INTEGER,
                    course_alignment TEXT,
                    course_color TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        else:
            create_table_sql = '''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    image_base64 TEXT NOT NULL,
                    text_x REAL NOT NULL,
                    text_y REAL NOT NULL,
                    font TEXT NOT NULL,
                    font_size INTEGER NOT NULL,
                    alignment TEXT NOT NULL,
                    color TEXT NOT NULL,
                    language TEXT NOT NULL,
                    course_text_x REAL,
                    course_text_y REAL,
                    course_font TEXT,
                    course_font_size INTEGER,
                    course_alignment TEXT,
                    course_color TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''

        try:
            self.commit_query(create_table_sql)
            self._ensure_course_columns()
            print(f"[OK] Database initialized ({self.db_type})")
        except Exception as e:
            if self.db_type == "postgresql" and self.conn and not self.conn.closed:
                self.conn.rollback()
            print(f"ERROR: Failed to initialize database: {e}")

    def _ensure_course_columns(self):
        existing = set()
        if self.db_type == "postgresql":
            rows = self.fetchall(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = current_schema() AND table_name = 'templates'"
            )
            existing = {r[0] for r in rows}
        else:
            rows = self.fetchall("PRAGMA table_info(templates)")
            existing = {r[1] for r in rows}
        for col, typ in COURSE_COLUMNS:
            if col not in existing:
                if self.db_type == "postgresql":
                    self.commit_query(f"ALTER TABLE templates ADD COLUMN IF NOT EXISTS {col} {typ}")
                else:
                    self.commit_query(f"ALTER TABLE templates ADD COLUMN {col} {typ}")

    def get_database_info(self) -> dict:
        """Get information about current database"""
        return {
            "type": self.db_type,
            "postgresql_available": POSTGRES_AVAILABLE,
            "connection": "active" if (self.db_type == 'postgresql' and self.conn and not self.conn.closed) else "sqlite"
        }

    def close(self):
        """Close database connection"""
        if self.db_type == 'postgresql' and self.conn and not self.conn.closed:
            self.conn.close()
            print("[OK] PostgreSQL connection closed")


# Template-specific database operations
class TemplateDB:
    """Template database operations"""

    def __init__(self, db: Database):
        self.db = db

    def create_template(self, name: str, image_base64: str, text_x: float, text_y: float,
                       font: str, font_size: int, alignment: str, color: str, language: str,
                       course_text_x: float = None, course_text_y: float = None,
                       course_font: str = None, course_font_size: int = None,
                       course_alignment: str = None, course_color: str = None) -> int:
        """Create a new template"""
        params = (name, image_base64, text_x, text_y, font, font_size, alignment, color, language,
                  course_text_x, course_text_y, course_font, course_font_size, course_alignment, course_color)
        if self.db.db_type == 'postgresql':
            query = '''
                INSERT INTO templates (name, image_base64, text_x, text_y, font, font_size, alignment, color, language,
                                       course_text_x, course_text_y, course_font, course_font_size, course_alignment, course_color)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            '''
            cursor, conn = self.db.execute(query, params)
            template_id = cursor.fetchone()[0]
            conn.commit()
            return template_id
        else:
            query = '''
                INSERT INTO templates (name, image_base64, text_x, text_y, font, font_size, alignment, color, language,
                                       course_text_x, course_text_y, course_font, course_font_size, course_alignment, course_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            return self.db.insert(query, params)

    def get_template_count(self) -> int:
        """Get total number of templates"""
        result = self.db.fetchone('SELECT COUNT(*) FROM templates')
        return result[0] if result else 0

    def list_templates(self) -> List[dict]:
        """List all templates (basic info)"""
        results = self.db.fetchall('SELECT id, name, language, created_at FROM templates')
        return [{"id": r[0], "name": r[1], "language": r[2], "created_at": r[3]} for r in results]

    def get_template(self, template_id: int) -> Optional[dict]:
        """Get full template details"""
        result = self.db.fetchone(
            '''SELECT id, name, image_base64, text_x, text_y, font, font_size, alignment, color, language,
                      course_text_x, course_text_y, course_font, course_font_size, course_alignment, course_color
               FROM templates WHERE id = ?''',
            (template_id,),
        )
        if not result:
            return None
        row_dict = {
            "id": result[0],
            "name": result[1],
            "image_base64": result[2],
            "text_x": result[3],
            "text_y": result[4],
            "font": result[5],
            "font_size": result[6],
            "alignment": result[7],
            "color": result[8],
            "language": result[9],
            "course_text_x": result[10],
            "course_text_y": result[11],
            "course_font": result[12],
            "course_font_size": result[13],
            "course_alignment": result[14],
            "course_color": result[15],
        }
        return _with_course_defaults(row_dict)

    def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        try:
            self.db.commit_query('DELETE FROM templates WHERE id = ?', (template_id,))
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False

    def update_template(self, template_id: int, **kwargs) -> bool:
        """Update template fields"""
        if not kwargs:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = tuple(kwargs.values()) + (template_id,)
        query = f"UPDATE templates SET {set_clause} WHERE id = ?"

        try:
            self.db.commit_query(query, values)
            return True
        except Exception as e:
            print(f"Error updating template: {e}")
            return False


# Global database instance
db = Database()
template_db = TemplateDB(db)

# Initialize database on import
db.init_database()
