"""Database migration script to add openapi_spec_json column

Run this script to update existing database with the new column.
"""

import sqlite3
import os

# Use absolute path to database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "data", "baqa.db")

print(f"Database path: {DB_PATH}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

def migrate_database():
    """Add openapi_spec_json column to stage_outputs table if it doesn't exist."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(stage_outputs)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'openapi_spec_json' not in columns:
        print("Adding openapi_spec_json column to stage_outputs table...")
        cursor.execute("""
            ALTER TABLE stage_outputs 
            ADD COLUMN openapi_spec_json TEXT DEFAULT NULL
        """)
        conn.commit()
        print("✅ Migration completed successfully!")
    else:
        print("✅ Column already exists, no migration needed.")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()
