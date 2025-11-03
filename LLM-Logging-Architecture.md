# LLM Inference Logging - Architecture Diagram

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Trading Decision Flow                     │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Trading Trigger │  (Scheduled or Manual)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    trading_commands.py                                │
│  place_ai_driven_crypto_order()                                      │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         │ 1. Get portfolio & market data
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ai_decision_service.py                             │
│  call_ai_for_decision(account, portfolio, prices)                    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ 1. Build Prompt                                          │        │
│  │    - Portfolio data (cash, positions, leverage)          │        │
│  │    - Market prices (BTC, ETH, SOL, etc.)                │        │
│  │    - Latest crypto news                                  │        │
│  │    - Trading rules & constraints                         │        │
│  └────────────────┬────────────────────────────────────────┘        │
│                   │                                                   │
│                   │ user_prompt (String, max 10000 chars)            │
│                   ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ 2. Call LLM API                                          │        │
│  │    - OpenAI-compatible API (GPT, Claude, etc.)           │        │
│  │    - AWS Bedrock (Claude Sonnet 4.5, Qwen, DeepSeek)   │        │
│  └────────────────┬────────────────────────────────────────┘        │
│                   │                                                   │
│                   │ raw_response (String, max 10000 chars)           │
│                   ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ 3. Parse Response                                        │        │
│  │    - Extract JSON from response                          │        │
│  │    - Clean markdown code blocks                          │        │
│  │    - Validate decision structure                         │        │
│  │    - Normalize direction & leverage                      │        │
│  └────────────────┬────────────────────────────────────────┘        │
│                   │                                                   │
│                   │ decision (Dict)                                  │
│                   ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ 4. Return Result                                         │        │
│  │    {                                                     │        │
│  │      "decision": {...},      # Parsed decision           │        │
│  │      "prompt": "...",        # Full prompt               │        │
│  │      "raw_response": "..."   # Raw LLM response          │        │
│  │    }                                                     │        │
│  └────────────────┬────────────────────────────────────────┘        │
└──────────────────┬┘                                                  │
                   │                                                    │
                   ▼                                                    │
┌──────────────────────────────────────────────────────────────────────┐
│                    trading_commands.py                                │
│  Extract: decision, prompt, raw_response                             │
│                                                                       │
│  Validate decision:                                                  │
│  - operation in ["open", "close", "hold"]                           │
│  - symbol in SUPPORTED_SYMBOLS                                       │
│  - direction in ["long", "short"]                                    │
│  - target_portion in (0, 1]                                          │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         │ 2. Execute order (if valid)
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    order_executor_leverage.py                         │
│  place_and_execute_crypto()                                          │
│  - Create order                                                      │
│  - Execute trade                                                     │
│  - Update positions                                                  │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         │ 3. Save decision log
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ai_decision_service.py                             │
│  save_ai_decision(db, account, decision, portfolio,                  │
│                   executed, order_id,                                │
│                   prompt, raw_response)  ← NEW PARAMS                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ Serialize & Truncate                                     │        │
│  │ - llm_output = json.dumps(decision)                      │        │
│  │ - Truncate prompt to 10000 chars                         │        │
│  │ - Truncate raw_response to 10000 chars                  │        │
│  │ - Truncate llm_output to 2000 chars                     │        │
│  └────────────────┬────────────────────────────────────────┘        │
│                   ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ Create AIDecisionLog                                     │        │
│  │ - account_id, decision_time                              │        │
│  │ - operation, symbol, direction                           │        │
│  │ - target_portion, leverage                               │        │
│  │ - executed, order_id                                     │        │
│  │ - user_prompt          ← NEW                             │        │
│  │ - reasoning_trace      ← NEW                             │        │
│  │ - llm_output           ← NEW                             │        │
│  └────────────────┬────────────────────────────────────────┘        │
└──────────────────┬┘                                                  │
                   │                                                    │
                   ▼                                                    │
┌──────────────────────────────────────────────────────────────────────┐
│                         Database                                      │
│  ai_decision_logs table                                              │
│                                                                       │
│  Columns:                                                            │
│  - id, account_id, decision_time                                     │
│  - operation, symbol, direction                                      │
│  - prev_portion, target_portion, total_balance                       │
│  - leverage, executed, order_id                                      │
│  - reason                                                            │
│  - user_prompt (VARCHAR 10000)          ← NEW                        │
│  - reasoning_trace (VARCHAR 10000)      ← NEW                        │
│  - llm_output (VARCHAR 2000)            ← NEW                        │
└──────────────────────────────────────────────────────────────────────┘
```

## Database Schema

```sql
CREATE TABLE ai_decision_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    decision_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Decision details
    reason VARCHAR(1000) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    symbol VARCHAR(20),
    prev_portion DECIMAL(10,6) DEFAULT 0,
    target_portion DECIMAL(10,6) NOT NULL,
    total_balance DECIMAL(18,2) NOT NULL,
    leverage INT DEFAULT 1,
    
    -- Execution status
    executed VARCHAR(10) DEFAULT 'false',
    order_id INT,
    
    -- LLM Inference Logging (NEW)
    user_prompt VARCHAR(10000),
    reasoning_trace VARCHAR(10000),
    llm_output VARCHAR(2000),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                    Component Diagram                             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Scheduler      │  (APScheduler)
│   - Every 5 min  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│  Trading Commands Service                                     │
│  - Get active AI accounts                                    │
│  - Fetch market data                                         │
│  - Loop through accounts                                     │
└────────┬─────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────┐
         │                                          │
         ▼                                          ▼
┌──────────────────────┐              ┌──────────────────────┐
│  AI Decision Service │              │  Market Data Service │
│  - Build prompt      │              │  - Get prices        │
│  - Call LLM API      │              │  - Get news          │
│  - Parse response    │              └──────────────────────┘
│  - Return decision   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│  Order Executor Service                                       │
│  - Validate decision                                         │
│  - Calculate quantity                                        │
│  - Create & execute order                                    │
│  - Update positions                                          │
└────────┬─────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│  AI Decision Service (save_ai_decision)                      │
│  - Serialize decision                                        │
│  - Truncate long fields                                      │
│  - Save to database                                          │
└────────┬─────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│  Database (MySQL)                                            │
│  - ai_decision_logs table                                    │
│  - Stores all decision data + LLM inference logs             │
└──────────────────────────────────────────────────────────────┘
```

## Data Examples

### 1. User Prompt (Input to LLM)

```text
You are a cryptocurrency trading AI. Based on the following portfolio 
and market data, decide on a trading action.

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
Bitcoin reaches new all-time high amid institutional adoption...

Analyze the market and portfolio, then respond with ONLY a JSON object...
```

### 2. Reasoning Trace (Raw LLM Response)

```json
{
  "operation": "open",
  "symbol": "BTC",
  "direction": "long",
  "target_portion_of_balance": 0.3,
  "leverage": 2,
  "reason": "Bitcoin showing strong bullish momentum with positive news 
            sentiment and institutional adoption. Opening 30% position 
            with 2x leverage for moderate risk exposure."
}
```

### 3. LLM Output (Parsed Decision)

```json
{
  "operation": "open",
  "symbol": "BTC",
  "direction": "long",
  "target_portion_of_balance": 0.3,
  "leverage": 2,
  "reason": "Bitcoin showing strong bullish momentum..."
}
```

## Key Features

1. **Complete Transparency**: Every AI decision is fully logged
2. **Debugging Support**: See exact input/output for failed decisions
3. **Performance Analysis**: Compare prompts and model responses
4. **Audit Trail**: Complete record for compliance
5. **Research Data**: Rich dataset for AI trading analysis

## Security Considerations

- API keys are NOT logged (stored separately in accounts table)
- Prompts may contain portfolio values (consider data retention policies)
- Raw responses are stored as-is (ensure database access controls)
- Truncation prevents excessive storage usage

## Performance Impact

- **Minimal**: Only string operations and one additional DB write
- **Storage**: ~20KB per decision (with full logs)
- **Query Performance**: Indexed by decision_time and account_id
- **Scalability**: Suitable for thousands of decisions per day

---

**Version**: 1.0.0 | **Date**: 2025-11-03

