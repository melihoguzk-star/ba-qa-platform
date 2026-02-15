"""
Migration script for Phase 3: Document Lineage & Adaptation tracking
Adds fields to track document ancestry and adaptation notes.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "baqa.db")


def migrate_phase3():
    """Add Phase 3 columns to documents table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]

    migrations = []

    if 'source_document_id' not in columns:
        migrations.append(
            "ALTER TABLE documents ADD COLUMN source_document_id INTEGER DEFAULT NULL "
            "REFERENCES documents(id) ON DELETE SET NULL"
        )
        print("➕ Adding source_document_id column...")

    if 'adaptation_notes' not in columns:
        migrations.append(
            "ALTER TABLE documents ADD COLUMN adaptation_notes TEXT DEFAULT ''"
        )
        print("➕ Adding adaptation_notes column...")

    if migrations:
        for migration in migrations:
            cursor.execute(migration)
            print(f"   ✅ Executed: {migration[:50]}...")

        conn.commit()
        print("\n✅ Phase 3 migration completed successfully!")
    else:
        print("✅ Database already up to date. No migration needed.")

    conn.close()


if __name__ == "__main__":
    print("🔄 Running Phase 3 Migration\n")
    migrate_phase3()
