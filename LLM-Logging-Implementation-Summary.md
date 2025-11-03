# LLM Inference Logging - Implementation Summary

## 概述 (Overview)

本次更新为 AI 交易决策系统添加了完整的 LLM 推理日志记录功能，能够记录每次 LLM 推理的：
- **User Prompt** (用户提示词): 发送给 LLM 的完整提示
- **Reasoning Trace** (推理轨迹): LLM 返回的原始响应
- **Output** (输出结果): 解析后的 JSON 决策结果

This update adds comprehensive LLM inference logging to the AI trading decision system, recording:
- **User Prompt**: The complete prompt sent to the LLM
- **Reasoning Trace**: The raw response from the LLM
- **Output**: The parsed JSON decision result

## 修改的文件 (Modified Files)

### 1. Database Schema
**文件**: `backend/database/models.py`

添加了三个新字段到 `AIDecisionLog` 模型:
```python
# LLM Inference Logging
user_prompt = Column(String(10000), nullable=True)      # Full prompt sent to LLM
reasoning_trace = Column(String(10000), nullable=True)  # Raw LLM response before parsing
llm_output = Column(String(2000), nullable=True)        # Parsed JSON decision output
```

### 2. AI Decision Service
**文件**: `backend/services/ai_decision_service.py`

**主要修改**:

1. **`call_ai_for_decision()` 函数返回值变更**:
   ```python
   # 旧返回格式 (Old format)
   return decision  # Dict
   
   # 新返回格式 (New format)
   return {
       "decision": decision,      # 解析后的决策 (Parsed decision)
       "prompt": prompt,          # 完整提示词 (Full prompt)
       "raw_response": raw_response  # 原始响应 (Raw response)
   }
   ```

2. **`save_ai_decision()` 函数参数增加**:
   ```python
   def save_ai_decision(
       db: Session, 
       account: Account, 
       decision: Dict, 
       portfolio: Dict, 
       executed: bool = False, 
       order_id: Optional[int] = None,
       prompt: Optional[str] = None,        # 新增 (New)
       raw_response: Optional[str] = None   # 新增 (New)
   ) -> None:
   ```

3. **自动截断功能**:
   - `user_prompt`: 超过 10000 字符自动截断
   - `reasoning_trace`: 超过 10000 字符自动截断
   - `llm_output`: 超过 2000 字符自动截断

### 3. Trading Commands Service
**文件**: `backend/services/trading_commands.py`

**主要修改**:

1. **处理新的返回格式**:
   ```python
   # 调用 AI 获取决策 (Call AI for decision)
   ai_result = call_ai_for_decision(account, portfolio, prices)
   
   # 提取数据 (Extract data)
   decision = ai_result.get("decision", {})
   prompt = ai_result.get("prompt", "")
   raw_response = ai_result.get("raw_response", "")
   ```

2. **更新所有 `save_ai_decision()` 调用**:
   ```python
   # 所有调用都传递 prompt 和 raw_response (All calls pass prompt and raw_response)
   save_ai_decision(
       db, account, decision, portfolio, 
       executed=executed, 
       order_id=order_id,
       prompt=prompt,           # 新增 (New)
       raw_response=raw_response  # 新增 (New)
   )
   ```

### 4. Database Migration
**文件**: `backend/database/migrations/add_llm_logging_columns.sql`

SQL 迁移脚本 (SQLite3):
```sql
-- SQLite3 doesn't support adding multiple columns in one ALTER TABLE statement
-- SQLite3 doesn't support COMMENT clause
ALTER TABLE ai_decision_logs ADD COLUMN user_prompt TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN reasoning_trace TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN llm_output TEXT;
```

**注意**: SQLite3 使用 TEXT 类型存储可变长度字符串，应用层负责截断以防止过度存储。

## 新增文件 (New Files)

1. **`LLM-Inference-Logging.md`**: 完整的功能文档
2. **`LLM-Logging-Implementation-Summary.md`**: 本文档
3. **`backend/database/migrations/add_llm_logging_columns.sql`**: 数据库迁移脚本 (SQLite3)
4. **`backend/database/migrations/apply_migration.py`**: Python 迁移脚本 (推荐使用)
5. **`backend/database/migrations/README.md`**: 迁移说明文档
6. **`backend/verify_llm_logging.py`**: 验证脚本
7. **`QUICK-START-LLM-LOGGING.md`**: 快速开始指南
8. **`LLM-Logging-Architecture.md`**: 架构图和数据流

## 部署步骤 (Deployment Steps)

### 1. 应用数据库迁移 (Apply Database Migration)

```bash
# 方法 1: 使用 Python 迁移脚本 (推荐) (Method 1: Use Python migration script - Recommended)
cd backend
python database/migrations/apply_migration.py apply

# 方法 2: 直接使用 SQLite3 (Method 2: Direct SQLite3)
# 数据库文件位于: backend/data.db
cd backend
sqlite3 data.db < database/migrations/add_llm_logging_columns.sql

# 检查迁移状态 (Check migration status)
cd backend
python database/migrations/apply_migration.py check
```

### 2. 验证安装 (Verify Installation)

```bash
cd backend
python verify_llm_logging.py
```

验证脚本会检查:
- ✓ 数据库 schema 是否包含新字段
- ✓ Python 模型是否包含新属性
- ✓ 数据存储是否正常工作

### 3. 重启服务 (Restart Services)

```bash
# 重启后端服务 (Restart backend service)
docker-compose restart backend

# 或使用重启脚本 (Or use restart script)
./restart.sh
```

## 使用示例 (Usage Examples)

### 查询最近的 AI 决策及完整推理信息 (Query Recent AI Decisions with Full Inference)

```sql
SELECT 
    id,
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
WHERE user_prompt IS NOT NULL
ORDER BY decision_time DESC
LIMIT 5;
```

### 分析提示词效果 (Analyze Prompt Effectiveness)

```sql
SELECT 
    executed,
    COUNT(*) as count,
    AVG(LENGTH(user_prompt)) as avg_prompt_length,
    AVG(LENGTH(reasoning_trace)) as avg_response_length
FROM ai_decision_logs
WHERE user_prompt IS NOT NULL
GROUP BY executed;
```

### 调试失败的决策 (Debug Failed Decisions)

```sql
SELECT 
    decision_time,
    operation,
    symbol,
    reason,
    user_prompt,
    reasoning_trace,
    llm_output
FROM ai_decision_logs
WHERE executed = 'false' AND user_prompt IS NOT NULL
ORDER BY decision_time DESC
LIMIT 10;
```

## 数据示例 (Data Examples)

### User Prompt 示例

```text
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

Analyze the market and portfolio, then respond with ONLY a JSON object in this exact format:
{
  "operation": "open" or "close" or "hold",
  "symbol": "BTC" or "ETH" or "SOL" or "BNB" or "XRP" or "DOGE",
  "direction": "long" or "short",
  "target_portion_of_balance": 0.2,
  "leverage": 3,
  "reason": "Brief explanation of your decision"
}
...
```

### Reasoning Trace 示例

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

### LLM Output 示例

```json
{"operation": "open", "symbol": "BTC", "direction": "long", "target_portion_of_balance": 0.3, "leverage": 2, "reason": "Bitcoin showing strong bullish momentum with positive news sentiment."}
```

## 技术细节 (Technical Details)

### 字段类型 (Field Types)

**SQLite3 数据库**:
- `user_prompt`: TEXT - 无固定长度限制
- `reasoning_trace`: TEXT - 无固定长度限制
- `llm_output`: TEXT - 无固定长度限制

**应用层截断** (Application Layer Truncation):
- `user_prompt`: 截断到 10000 字符
- `reasoning_trace`: 截断到 10000 字符
- `llm_output`: 截断到 2000 字符

### 自动截断 (Automatic Truncation)

如果内容超过字段长度限制，会自动截断并添加 "..." 后缀:

```python
if prompt and len(prompt) > 10000:
    prompt = prompt[:9997] + "..."
if raw_response and len(raw_response) > 10000:
    raw_response = raw_response[:9997] + "..."
if llm_output_str and len(llm_output_str) > 2000:
    llm_output_str = llm_output_str[:1997] + "..."
```

### 向后兼容性 (Backward Compatibility)

- 所有新字段都是 `nullable=True`
- 旧数据不受影响
- 旧代码继续工作
- 新功能自动启用

## 优势 (Benefits)

1. **完全透明** (Full Transparency): 每个 AI 决策都有完整的上下文记录
2. **易于调试** (Easy Debugging): 出问题时可以看到完整的输入输出
3. **性能分析** (Performance Analysis): 可以比较不同提示词、模型和配置
4. **合规审计** (Compliance): 完整的 AI 交易决策审计轨迹
5. **研究价值** (Research): 丰富的数据集用于分析 AI 交易行为

## 测试清单 (Testing Checklist)

- [x] 数据库 schema 更新
- [x] Python 模型更新
- [x] AI 决策服务更新
- [x] 交易命令服务更新
- [x] 创建迁移脚本
- [x] 创建验证脚本
- [x] 编写文档
- [ ] 应用数据库迁移
- [ ] 运行验证脚本
- [ ] 运行 AI 交易服务
- [ ] 查询数据库验证日志记录

## 后续改进 (Future Enhancements)

可能的改进方向:
- 添加 token 使用量跟踪
- 记录模型参数 (temperature, max_tokens 等)
- 存储中间解析步骤
- 添加性能指标 (延迟、成功率)
- 创建可视化仪表板
- 基于日志数据自动优化提示词

## 支持 (Support)

如有问题，请参考:
- 功能文档: `LLM-Inference-Logging.md`
- 数据库模型: `backend/database/models.py`
- 服务实现: `backend/services/ai_decision_service.py`
- 使用示例: `backend/services/trading_commands.py`
- 验证脚本: `backend/verify_llm_logging.py`

## 版本信息 (Version Info)

- **实现日期** (Implementation Date): 2025-11-03
- **版本** (Version): 1.0.0
- **兼容性** (Compatibility): 向后兼容 (Backward compatible)

