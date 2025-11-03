# SQLite3 数据库迁移指南

## 数据库信息

- **数据库类型**: SQLite3
- **数据库文件**: `backend/data.db`
- **连接字符串**: `sqlite:///./data.db`

## 快速迁移 (推荐方法)

### 方法 1: 使用 Python 迁移脚本 ✅

这是最简单和最安全的方法：

```bash
cd backend
python database/migrations/apply_migration.py apply
```

**优势**:
- ✅ 自动检测已存在的字段
- ✅ 提供详细的执行反馈
- ✅ 内置验证功能
- ✅ 不需要手动查找数据库文件

**验证迁移**:
```bash
python database/migrations/apply_migration.py check
```

### 方法 2: 直接使用 SQLite3 命令

如果你更喜欢直接使用 SQL：

```bash
cd backend
sqlite3 data.db < database/migrations/add_llm_logging_columns.sql
```

## 迁移脚本内容

```sql
-- SQLite3 doesn't support adding multiple columns in one ALTER TABLE statement
-- SQLite3 doesn't support COMMENT clause
ALTER TABLE ai_decision_logs ADD COLUMN user_prompt TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN reasoning_trace TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN llm_output TEXT;
```

## SQLite3 特性说明

### 1. TEXT 类型

SQLite3 使用 `TEXT` 类型存储可变长度字符串，没有固定的长度限制。应用层会自动截断：
- `user_prompt`: 最大 10,000 字符
- `reasoning_trace`: 最大 10,000 字符
- `llm_output`: 最大 2,000 字符

### 2. ALTER TABLE 限制

SQLite3 不支持在一个 `ALTER TABLE` 语句中添加多个字段，因此需要三个独立的语句。

### 3. COMMENT 不支持

SQLite3 不支持 `COMMENT` 子句，字段说明在代码注释中提供。

## 验证迁移

### 使用 Python 脚本

```bash
cd backend
python verify_llm_logging.py
```

### 使用 SQLite3 命令

```bash
cd backend
sqlite3 data.db "PRAGMA table_info(ai_decision_logs);"
```

应该看到新增的三个字段：
```
...
| user_prompt     | TEXT | 0 |     | 0 |
| reasoning_trace | TEXT | 0 |     | 0 |
| llm_output      | TEXT | 0 |     | 0 |
```

## 查询示例

### 查看最近的 AI 决策日志

```bash
cd backend
sqlite3 data.db "
SELECT 
    id,
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
LIMIT 5;
"
```

### 查看完整的推理过程

```bash
cd backend
sqlite3 data.db "
SELECT 
    decision_time,
    operation,
    symbol,
    user_prompt,
    reasoning_trace,
    llm_output
FROM ai_decision_logs
WHERE user_prompt IS NOT NULL
ORDER BY decision_time DESC
LIMIT 1;
"
```

### 使用 Python 查询

```python
from database.connection import SessionLocal
from database.models import AIDecisionLog

db = SessionLocal()
try:
    logs = db.query(AIDecisionLog).filter(
        AIDecisionLog.user_prompt.isnot(None)
    ).order_by(AIDecisionLog.decision_time.desc()).limit(5).all()
    
    for log in logs:
        print(f"Time: {log.decision_time}")
        print(f"Operation: {log.operation} {log.symbol}")
        print(f"Prompt length: {len(log.user_prompt) if log.user_prompt else 0}")
        print(f"Response length: {len(log.reasoning_trace) if log.reasoning_trace else 0}")
        print("-" * 60)
finally:
    db.close()
```

## 故障排除

### 问题: 找不到数据库文件

```bash
# 检查数据库文件是否存在
ls -la backend/data.db

# 如果不存在，可能需要先运行应用创建数据库
cd backend
python main.py
```

### 问题: 字段已存在

如果看到错误 "duplicate column name"，说明字段已经存在。可以使用检查命令：

```bash
cd backend
python database/migrations/apply_migration.py check
```

### 问题: 权限错误

```bash
# 确保有读写权限
chmod 644 backend/data.db
```

### 问题: 数据库被锁定

如果数据库被锁定，可能是因为其他进程正在使用：

```bash
# 停止后端服务
# 然后重试迁移
cd backend
python database/migrations/apply_migration.py apply
```

## 回滚迁移

SQLite3 不支持 `DROP COLUMN`，所以回滚比较复杂。如果确实需要回滚：

1. 创建新表（不包含新字段）
2. 复制旧数据
3. 删除旧表
4. 重命名新表

**建议**: 由于字段是 nullable 的，保留它们不会有任何问题。

## 备份建议

在应用迁移前，建议备份数据库：

```bash
# 备份数据库
cp backend/data.db backend/data.db.backup.$(date +%Y%m%d_%H%M%S)

# 应用迁移
cd backend
python database/migrations/apply_migration.py apply

# 如果有问题，可以恢复
# cp backend/data.db.backup.YYYYMMDD_HHMMSS backend/data.db
```

## 性能影响

- **存储**: 每条日志约增加 5-20KB（取决于提示词和响应长度）
- **查询**: 新字段有索引支持，查询性能不受影响
- **写入**: 略微增加（约 5-10%），可忽略不计

## SQLite3 工具推荐

### 命令行工具

```bash
# 安装 SQLite3 (如果未安装)
# macOS (通常已预装)
sqlite3 --version

# Ubuntu/Debian
sudo apt-get install sqlite3

# 交互式查询
cd backend
sqlite3 data.db
sqlite> .tables
sqlite> .schema ai_decision_logs
sqlite> SELECT COUNT(*) FROM ai_decision_logs;
sqlite> .quit
```

### GUI 工具

- **DB Browser for SQLite**: https://sqlitebrowser.org/
- **DBeaver**: https://dbeaver.io/
- **DataGrip**: https://www.jetbrains.com/datagrip/

## 下一步

1. ✅ 应用迁移
2. ✅ 验证迁移
3. ✅ 重启服务
4. ⏳ 运行 AI 交易
5. ⏳ 查询日志数据
6. ⏳ 分析 AI 决策

## 相关文档

- 完整功能文档: `LLM-Inference-Logging.md`
- 快速开始: `QUICK-START-LLM-LOGGING.md`
- 实现总结: `LLM-Logging-Implementation-Summary.md`
- 架构说明: `LLM-Logging-Architecture.md`

---

**数据库**: SQLite3 | **版本**: 1.0.0 | **日期**: 2025-11-03

