# Database Migrations

This directory contains SQL migration scripts for the database schema.

## How to Apply Migrations

To apply a migration, run the SQL file against your SQLite3 database:

```bash
# For SQLite3 (direct file access)
# Database file is located at: backend/data.db
cd backend
sqlite3 data.db < database/migrations/add_llm_logging_columns.sql

# Or using Python
cd backend
python -c "
from database.connection import engine
with open('database/migrations/add_llm_logging_columns.sql', 'r') as f:
    sql = f.read()
    with engine.begin() as conn:
        for statement in sql.split(';'):
            if statement.strip():
                conn.execute(statement)
print('Migration applied successfully!')
"
```

## Migration History

### 2025-11-03: Add LLM Logging Columns

**File:** `add_llm_logging_columns.sql`

**Description:** Adds three new columns to the `ai_decision_logs` table to capture LLM inference details:
- `user_prompt` (TEXT): Full prompt sent to the LLM
- `reasoning_trace` (TEXT): Raw LLM response before parsing
- `llm_output` (TEXT): Parsed JSON decision output

**Note:** SQLite3 uses TEXT type for variable-length strings. The application layer handles truncation to prevent excessive storage.

**Purpose:** Enable comprehensive logging of AI decision-making process for debugging, analysis, and model performance evaluation.

**Usage:** These fields are automatically populated when AI trading decisions are made. You can query them to:
- Debug AI decision issues
- Analyze prompt effectiveness
- Compare model responses
- Track decision quality over time

**Example Query:**
```sql
-- View recent AI decisions with full inference details
SELECT 
    decision_time,
    operation,
    symbol,
    reason,
    executed,
    user_prompt,
    reasoning_trace,
    llm_output
FROM ai_decision_logs
ORDER BY decision_time DESC
LIMIT 10;
```

