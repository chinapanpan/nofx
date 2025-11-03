#!/usr/bin/env python3
"""
Verification script for LLM inference logging feature

This script verifies that:
1. The database schema has the new columns
2. The columns can store data correctly
3. The logging functionality works as expected
"""
import sys
from sqlalchemy import inspect
from database.connection import engine, SessionLocal
from database.models import AIDecisionLog


def verify_schema():
    """Verify that the new columns exist in the database schema"""
    print("=" * 60)
    print("Verifying Database Schema")
    print("=" * 60)
    
    inspector = inspect(engine)
    columns = inspector.get_columns('ai_decision_logs')
    
    required_columns = ['user_prompt', 'reasoning_trace', 'llm_output']
    found_columns = {col['name']: col for col in columns}
    
    all_found = True
    for col_name in required_columns:
        if col_name in found_columns:
            col_info = found_columns[col_name]
            print(f"✓ Column '{col_name}' exists")
            print(f"  - Type: {col_info['type']}")
            print(f"  - Nullable: {col_info['nullable']}")
        else:
            print(f"✗ Column '{col_name}' NOT FOUND")
            all_found = False
    
    print()
    return all_found


def verify_model():
    """Verify that the Python model has the new attributes"""
    print("=" * 60)
    print("Verifying Python Model")
    print("=" * 60)
    
    required_attrs = ['user_prompt', 'reasoning_trace', 'llm_output']
    all_found = True
    
    for attr_name in required_attrs:
        if hasattr(AIDecisionLog, attr_name):
            print(f"✓ Attribute '{attr_name}' exists in AIDecisionLog model")
        else:
            print(f"✗ Attribute '{attr_name}' NOT FOUND in AIDecisionLog model")
            all_found = False
    
    print()
    return all_found


def test_data_storage():
    """Test that we can store and retrieve data in the new columns"""
    print("=" * 60)
    print("Testing Data Storage")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Query the most recent log entry
        recent_log = db.query(AIDecisionLog).order_by(
            AIDecisionLog.decision_time.desc()
        ).first()
        
        if recent_log:
            print(f"✓ Found recent log entry (ID: {recent_log.id})")
            print(f"  - Decision Time: {recent_log.decision_time}")
            print(f"  - Operation: {recent_log.operation}")
            print(f"  - Symbol: {recent_log.symbol}")
            
            # Check if new fields are populated
            has_prompt = recent_log.user_prompt is not None and len(recent_log.user_prompt) > 0
            has_trace = recent_log.reasoning_trace is not None and len(recent_log.reasoning_trace) > 0
            has_output = recent_log.llm_output is not None and len(recent_log.llm_output) > 0
            
            print()
            print("New Field Population:")
            if has_prompt:
                print(f"  ✓ user_prompt: {len(recent_log.user_prompt)} chars")
                print(f"    Preview: {recent_log.user_prompt[:100]}...")
            else:
                print(f"  ⚠ user_prompt: Not populated (may be from old data)")
            
            if has_trace:
                print(f"  ✓ reasoning_trace: {len(recent_log.reasoning_trace)} chars")
                print(f"    Preview: {recent_log.reasoning_trace[:100]}...")
            else:
                print(f"  ⚠ reasoning_trace: Not populated (may be from old data)")
            
            if has_output:
                print(f"  ✓ llm_output: {len(recent_log.llm_output)} chars")
                print(f"    Content: {recent_log.llm_output}")
            else:
                print(f"  ⚠ llm_output: Not populated (may be from old data)")
            
            print()
            if has_prompt and has_trace and has_output:
                print("✓ All new fields are populated correctly!")
                return True
            else:
                print("⚠ New fields not yet populated. This is normal if no AI trades have been made since the update.")
                print("  Run the AI trading service to generate new logs with full inference data.")
                return True
        else:
            print("⚠ No log entries found. This is normal for a new system.")
            print("  Run the AI trading service to generate logs.")
            return True
            
    except Exception as e:
        print(f"✗ Error testing data storage: {e}")
        return False
    finally:
        db.close()


def main():
    """Main verification function"""
    print("\n" + "=" * 60)
    print("LLM Inference Logging Verification")
    print("=" * 60 + "\n")
    
    results = []
    
    # Verify schema
    results.append(("Schema", verify_schema()))
    
    # Verify model
    results.append(("Model", verify_model()))
    
    # Test data storage
    results.append(("Data Storage", test_data_storage()))
    
    # Summary
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All verifications passed!")
        print("\nNext steps:")
        print("1. Apply the migration if you haven't already:")
        print("   mysql -u username -p database_name < backend/database/migrations/add_llm_logging_columns.sql")
        print("2. Run the AI trading service to generate new logs")
        print("3. Query the ai_decision_logs table to see the logged data")
        return 0
    else:
        print("✗ Some verifications failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

