-- Migration: Add LLM inference logging columns to ai_decision_logs table
-- Date: 2025-11-03
-- Description: Add user_prompt, reasoning_trace, and llm_output columns to track LLM inference details
-- Database: SQLite3

-- SQLite3 doesn't support adding multiple columns in one ALTER TABLE statement
-- SQLite3 doesn't support COMMENT clause
ALTER TABLE ai_decision_logs ADD COLUMN user_prompt TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN reasoning_trace TEXT;
ALTER TABLE ai_decision_logs ADD COLUMN llm_output TEXT;

