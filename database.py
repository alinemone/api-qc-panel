import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


def get_db_connection():
    """Create and return a database connection"""
    try:
        logger.debug(f"Attempting to connect to database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}")

        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DATABASE,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            options=f'-c search_path={settings.POSTGRES_SCHEMA},public',
            connect_timeout=10
        )

        logger.info(f"Database connection established: {settings.POSTGRES_HOST}/{settings.POSTGRES_DATABASE}")
        return conn

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed (OperationalError): {str(e)}")
        raise
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected database connection error: {str(e)}")
        raise


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = None
    try:
        logger.debug("Getting database connection from context manager")
        conn = get_db_connection()
        yield conn
        conn.commit()
        logger.debug("Database transaction committed")
    except Exception as e:
        logger.error(f"Database transaction error: {str(e)}")
        if conn:
            conn.rollback()
            logger.warning("Database transaction rolled back")
        raise e
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True):
    """Execute a SQL query and return results"""
    logger.debug(f"Executing query: {query[:100]}... with params: {params}")

    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)

                if fetch_one:
                    result = dict(cursor.fetchone()) if cursor.rowcount > 0 else None
                    logger.debug(f"Query returned 1 row: {result is not None}")
                    return result
                elif fetch_all:
                    results = [dict(row) for row in cursor.fetchall()]
                    logger.debug(f"Query returned {len(results)} rows")
                    return results
                else:
                    logger.debug(f"Query affected {cursor.rowcount} rows")
                    return cursor.rowcount

    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise


def execute_procedure(proc_name: str, params: tuple = ()):
    """Execute a stored procedure"""
    logger.debug(f"Executing procedure: {proc_name} with params: {params}")

    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.callproc(proc_name, params)
                try:
                    results = [dict(row) for row in cursor.fetchall()]
                    logger.debug(f"Procedure returned {len(results)} rows")
                    return results
                except:
                    logger.debug(f"Procedure affected {cursor.rowcount} rows")
                    return cursor.rowcount

    except Exception as e:
        logger.error(f"Procedure execution failed: {str(e)}")
        raise
