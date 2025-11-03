#!/usr/bin/env python3
"""
Apply database migration for LLM inference logging
Works with SQLite3 database
"""
import sys
import os

# Add parent directory to path to import database modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy import text
from database.connection import engine, SessionLocal


def check_columns_exist():
    """Check if the new columns already exist"""
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(ai_decision_logs)"))
        columns = [row[1] for row in result]
        
        required_columns = ['user_prompt', 'reasoning_trace', 'llm_output']
        existing = [col for col in required_columns if col in columns]
        missing = [col for col in required_columns if col not in columns]
        
        return existing, missing
    finally:
        db.close()


def apply_migration():
    """Apply the migration to add LLM logging columns"""
    print("=" * 60)
    print("Applying LLM Inference Logging Migration")
    print("=" * 60)
    print()
    
    # Check current state
    existing, missing = check_columns_exist()
    
    if existing:
        print(f"✓ Already exists: {', '.join(existing)}")
    
    if not missing:
        print("\n✓ All columns already exist. Migration not needed.")
        return True
    
    print(f"⚠ Missing columns: {', '.join(missing)}")
    print("\nApplying migration...")
    print()
    
    # Read and execute migration SQL
    migration_file = os.path.join(os.path.dirname(__file__), 'add_llm_logging_columns.sql')
    
    try:
        with open(migration_file, 'r') as f:
            sql_content = f.read()
        
        # Execute each statement
        with engine.begin() as conn:
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    print(f"Executing: {statement[:50]}...")
                    conn.execute(text(statement))
        
        print("\n✓ Migration applied successfully!")
        print()
        
        # Verify
        existing, missing = check_columns_exist()
        if not missing:
            print("✓ Verification passed: All columns now exist")
            print(f"  - {', '.join(['user_prompt', 'reasoning_trace', 'llm_output'])}")
            return True
        else:
            print(f"✗ Verification failed: Still missing {', '.join(missing)}")
            return False
            
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration():
    """Rollback the migration (remove added columns)"""
    print("=" * 60)
    print("Rolling Back LLM Inference Logging Migration")
    print("=" * 60)
    print()
    
    existing, missing = check_columns_exist()
    
    if not existing:
        print("✓ No columns to remove. Already rolled back.")
        return True
    
    print(f"⚠ Will remove columns: {', '.join(existing)}")
    print()
    
    # SQLite doesn't support DROP COLUMN directly
    # We need to recreate the table without these columns
    print("Note: SQLite doesn't support DROP COLUMN.")
    print("To rollback, you would need to:")
    print("1. Create a new table without these columns")
    print("2. Copy data from old table to new table")
    print("3. Drop old table and rename new table")
    print()
    print("This is complex and risky. Consider keeping the columns (they're nullable).")
    
    return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply or rollback LLM logging migration')
    parser.add_argument('action', choices=['apply', 'rollback', 'check'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        print("=" * 60)
        print("Checking Migration Status")
        print("=" * 60)
        print()
        
        existing, missing = check_columns_exist()
        
        if existing:
            print(f"✓ Existing columns: {', '.join(existing)}")
        if missing:
            print(f"⚠ Missing columns: {', '.join(missing)}")
        
        if not missing:
            print("\n✓ Migration is complete")
            return 0
        else:
            print("\n⚠ Migration is incomplete")
            return 1
    
    elif args.action == 'apply':
        success = apply_migration()
        return 0 if success else 1
    
    elif args.action == 'rollback':
        success = rollback_migration()
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

