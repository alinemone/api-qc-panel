import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

def run_migration():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Read the migration SQL file
        with open('migrations/add_completed_to_review_status.sql', 'r') as f:
            migration_sql = f.read()

        # Execute the migration
        cursor.execute(migration_sql)
        conn.commit()

        print("[SUCCESS] Migration completed successfully!")
        print("[SUCCESS] 'completed' has been added to analysis_review_status enum")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
