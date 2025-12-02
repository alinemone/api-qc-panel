import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import get_settings

settings = get_settings()


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DATABASE,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            options=f'-c search_path={settings.POSTGRES_SCHEMA},public'
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection error: {e}")
        raise


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = None
    try:
        conn = get_db_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True):
    """Execute a SQL query and return results"""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)

            if fetch_one:
                return dict(cursor.fetchone()) if cursor.rowcount > 0 else None
            elif fetch_all:
                return [dict(row) for row in cursor.fetchall()]
            else:
                return cursor.rowcount


def execute_procedure(proc_name: str, params: tuple = ()):
    """Execute a stored procedure"""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.callproc(proc_name, params)
            try:
                return [dict(row) for row in cursor.fetchall()]
            except:
                return cursor.rowcount
