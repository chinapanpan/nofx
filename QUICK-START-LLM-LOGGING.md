# LLM Inference Logging - Quick Start Guide

## 🚀 快速开始 (Quick Start)

### 1️⃣ 应用数据库迁移 (Apply Database Migration)

```bash
# 进入项目目录 (Enter project directory)
cd /Users/chris/Documents/codes/alapha-arena/nofx

# 方法 1: 使用 Python 迁移脚本 (推荐) (Method 1: Use Python migration script - Recommended)
cd backend
python database/migrations/apply_migration.py apply

# 方法 2: 直接使用 SQLite3 (Method 2: Direct SQLite3)
# 数据库文件位于: backend/data.db
cd backend
sqlite3 data.db < database/migrations/add_llm_logging_columns.sql
```

### 2️⃣ 验证安装 (Verify Installation)

```bash
cd backend
python verify_llm_logging.py
```

### 3️⃣ 重启服务 (Restart Services)

```bash
./restart.sh
```

## 📊 查看日志数据 (View Logged Data)

### 最简单的查询 (Simplest Query)

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
ORDER BY decision_time DESC
LIMIT 5;
```

### 使用 SQLite3 查询 (Query with SQLite3)

```bash
# 数据库文件位于: backend/data.db
cd backend
sqlite3 data.db "
SELECT 
    decision_time,
    operation,
    symbol,
    executed,
    LENGTH(user_prompt) as prompt_len,
    LENGTH(reasoning_trace) as trace_len,
    LENGTH(llm_output) as output_len
FROM ai_decision_logs
WHERE user_prompt IS NOT NULL
ORDER BY decision_time DESC
LIMIT 10;
"

# 或者使用 Python
cd backend
python -c "
from database.connection import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('''
    SELECT decision_time, operation, symbol, executed
    FROM ai_decision_logs 
    WHERE user_prompt IS NOT NULL 
    ORDER BY decision_time DESC 
    LIMIT 5
'''))
for row in result:
    print(row)
db.close()
"
```

## 📁 重要文件 (Important Files)

| 文件 | 说明 |
|------|------|
| `LLM-Logging-Implementation-Summary.md` | 完整实现总结 (中英文) |
| `LLM-Inference-Logging.md` | 详细功能文档 |
| `backend/database/migrations/add_llm_logging_columns.sql` | 数据库迁移脚本 |
| `backend/verify_llm_logging.py` | 验证脚本 |

## 🔍 记录的内容 (What's Logged)

每次 AI 交易决策都会记录:

1. **User Prompt** (用户提示词)
   - 完整的提示词，包括投资组合数据、市场价格、新闻等
   - 最大 10,000 字符

2. **Reasoning Trace** (推理轨迹)
   - LLM 返回的原始响应文本
   - 最大 10,000 字符

3. **LLM Output** (输出结果)
   - 解析后的 JSON 决策对象
   - 最大 2,000 字符

## ✅ 验证成功标志 (Success Indicators)

运行验证脚本后，应该看到:

```
✓ PASS: Schema
✓ PASS: Model
✓ PASS: Data Storage

✓ All verifications passed!
```

## 🐛 故障排除 (Troubleshooting)

### 问题: 迁移失败 (Migration Failed)

```bash
# 检查迁移状态 (Check migration status)
cd backend
python database/migrations/apply_migration.py check

# 或直接查看表结构 (Or view table structure directly)
cd backend
sqlite3 data.db "PRAGMA table_info(ai_decision_logs);"
```

### 问题: 日志字段为空 (Log Fields Empty)

这是正常的！新字段只会在迁移后的新决策中填充。

运行 AI 交易服务生成新的决策:
```bash
# 服务会自动运行，或手动触发
docker-compose logs -f backend
```

### 问题: 验证脚本失败 (Verification Script Failed)

```bash
# 确保在正确的目录 (Ensure in correct directory)
cd backend

# 检查数据库连接 (Check database connection)
python -c "from database.connection import engine; print(engine)"
```

## 📈 使用场景 (Use Cases)

1. **调试 AI 决策** (Debug AI Decisions)
   - 查看完整的输入输出
   - 理解 AI 为什么做出某个决策

2. **优化提示词** (Optimize Prompts)
   - 分析不同提示词的效果
   - 比较成功和失败的决策

3. **模型比较** (Compare Models)
   - 对比不同 AI 模型的表现
   - 评估响应质量

4. **合规审计** (Compliance Audit)
   - 完整的决策历史记录
   - 可追溯的交易理由

## 🎯 下一步 (Next Steps)

1. ✅ 应用数据库迁移
2. ✅ 运行验证脚本
3. ✅ 重启服务
4. ⏳ 等待 AI 交易服务运行
5. ⏳ 查询数据库查看日志
6. ⏳ 分析 AI 决策数据

## 📞 获取帮助 (Get Help)

- 查看完整文档: `LLM-Inference-Logging.md`
- 查看实现总结: `LLM-Logging-Implementation-Summary.md`
- 检查代码: `backend/services/ai_decision_service.py`

---

**版本**: 1.0.0 | **日期**: 2025-11-03

