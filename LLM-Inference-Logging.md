# LLM Inference Logging

## Overview

This document describes the LLM inference logging feature that captures detailed information about each AI trading decision, including the full prompt, raw LLM response, and parsed output.

## Purpose

The LLM inference logging feature enables:

1. **Debugging**: Understand why the AI made specific trading decisions
2. **Analysis**: Evaluate prompt effectiveness and model performance
3. **Transparency**: Full visibility into the AI decision-making process
4. **Optimization**: Identify patterns and improve prompts over time
5. **Auditing**: Complete record of all AI trading decisions

## Architecture

### Database Schema

Three new columns were added to the `ai_decision_logs` table:

```sql
user_prompt VARCHAR(10000)      -- Full prompt sent to LLM
reasoning_trace VARCHAR(10000)  -- Raw LLM response before parsing
llm_output VARCHAR(2000)        -- Parsed JSON decision output
```

### Data Flow

```
1. Portfolio & Market Data → Build Prompt
2. Prompt → LLM API (OpenAI/Bedrock)
3. LLM Response → Parse JSON
4. Save to Database:
   - user_prompt: The complete prompt sent to the LLM
   - reasoning_trace: Raw response text from the LLM
   - llm_output: Parsed and validated decision JSON
```

## Implementation Details

### Modified Files

1. **`backend/database/models.py`**
   - Added three new columns to `AIDecisionLog` model
   - Columns are nullable to support backward compatibility

2. **`backend/services/ai_decision_service.py`**
   - Modified `call_ai_for_decision()` to return a dict containing:
     - `decision`: The parsed decision dict
     - `prompt`: The full prompt sent to LLM
     - `raw_response`: The raw LLM response before parsing
   - Updated `save_ai_decision()` to accept and save prompt and raw_response
   - Added field truncation to prevent database errors (10000 chars for prompt/trace, 2000 for output)

3. **`backend/services/trading_commands.py`**
   - Updated to extract prompt and raw_response from AI result
   - Pass these values to all `save_ai_decision()` calls

4. **`backend/database/migrations/add_llm_logging_columns.sql`**
   - SQL migration script to add the new columns

## Usage

### Automatic Logging

The logging happens automatically whenever an AI trading decision is made. No additional configuration is required.

### Querying Logged Data

#### View Recent Decisions with Full Details

```sql
SELECT 
    id,
    account_id,
    decision_time,
    operation,
    symbol,
    direction,
    target_portion,
    leverage,
    executed,
    reason,
    user_prompt,
    reasoning_trace,
    llm_output
FROM ai_decision_logs
ORDER BY decision_time DESC
LIMIT 10;
```

#### Analyze Prompt Effectiveness

```sql
-- Find decisions that were executed vs not executed
SELECT 
    executed,
    COUNT(*) as count,
    AVG(LENGTH(user_prompt)) as avg_prompt_length,
    AVG(LENGTH(reasoning_trace)) as avg_response_length
FROM ai_decision_logs
WHERE user_prompt IS NOT NULL
GROUP BY executed;
```

#### Debug Failed Decisions

```sql
-- Find decisions that failed to execute
SELECT 
    decision_time,
    operation,
    symbol,
    reason,
    user_prompt,
    reasoning_trace,
    llm_output
FROM ai_decision_logs
WHERE executed = 'false'
ORDER BY decision_time DESC
LIMIT 20;
```

#### Compare Different Models

```sql
-- Compare decisions across different AI accounts/models
SELECT 
    a.name as account_name,
    a.model,
    COUNT(*) as total_decisions,
    SUM(CASE WHEN d.executed = 'true' THEN 1 ELSE 0 END) as executed_count,
    AVG(LENGTH(d.reasoning_trace)) as avg_response_length
FROM ai_decision_logs d
JOIN accounts a ON d.account_id = a.id
WHERE d.user_prompt IS NOT NULL
GROUP BY a.id, a.name, a.model
ORDER BY total_decisions DESC;
```

## Data Retention

### Field Truncation

To prevent database errors and manage storage:
- `user_prompt`: Truncated to 9997 chars + "..." if exceeds 10000
- `reasoning_trace`: Truncated to 9997 chars + "..." if exceeds 10000
- `llm_output`: Truncated to 1997 chars + "..." if exceeds 2000

### Backward Compatibility

All three new columns are nullable, so:
- Existing records remain valid
- Old code continues to work
- New logging is opt-in via the updated service calls

## Example Data

### User Prompt Example

```
You are a cryptocurrency trading AI. Based on the following portfolio and market data, decide on a trading action.

Portfolio Data:
- Cash Available: $10000.00
- Frozen Cash: $0.00
- Total Assets: $10000.00
- Current Positions: {}

Current Market Prices:
{
  "BTC": 95234.50,
  "ETH": 3421.23,
  "SOL": 198.45
}

Latest Crypto News (CoinJournal):
Bitcoin reaches new all-time high...

Analyze the market and portfolio, then respond with ONLY a JSON object...
```

### Reasoning Trace Example

```json
{
  "operation": "open",
  "symbol": "BTC",
  "direction": "long",
  "target_portion_of_balance": 0.3,
  "leverage": 2,
  "reason": "Bitcoin showing strong bullish momentum with positive news sentiment. Opening 30% position with 2x leverage for moderate risk exposure."
}
```

### LLM Output Example

```json
{
  "operation": "open",
  "symbol": "BTC",
  "direction": "long",
  "target_portion_of_balance": 0.3,
  "leverage": 2,
  "reason": "Bitcoin showing strong bullish momentum with positive news sentiment."
}
```

## Benefits

1. **Full Transparency**: Every AI decision is fully logged with complete context
2. **Easy Debugging**: When something goes wrong, you can see exactly what was sent and received
3. **Performance Analysis**: Compare different prompts, models, and configurations
4. **Compliance**: Complete audit trail of all AI trading decisions
5. **Research**: Rich dataset for analyzing AI trading behavior

## Future Enhancements

Potential improvements:
- Add token usage tracking
- Include model temperature and other parameters
- Store intermediate parsing steps
- Add performance metrics (latency, success rate)
- Create visualization dashboard for logged data
- Implement automated prompt optimization based on logged results

## Migration

To apply the database migration:

```bash
# Using MySQL client
mysql -u username -p database_name < backend/database/migrations/add_llm_logging_columns.sql

# Or using docker-compose
docker-compose exec db mysql -u root -p nofx < backend/database/migrations/add_llm_logging_columns.sql
```

## Testing

The feature can be tested by:
1. Running the AI trading service
2. Checking the `ai_decision_logs` table for populated `user_prompt`, `reasoning_trace`, and `llm_output` columns
3. Verifying that the data is correctly truncated if it exceeds the column limits

## Support

For questions or issues related to LLM inference logging, please refer to:
- Database schema: `backend/database/models.py`
- Service implementation: `backend/services/ai_decision_service.py`
- Usage examples: `backend/services/trading_commands.py`

