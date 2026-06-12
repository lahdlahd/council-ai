# STAGE 10 — AGENT MEMORY SYSTEM
## Council: Persistent Memory, Hybrid Ranking, & Vector Search

**Status**: Complete Agent Memory System  
**Database**: Supabase PostgreSQL + pgvector  
**Version**: 1.0  
**Date**: June 12, 2026

---

## 1. PERSISTENT MEMORY SCHEMA (SUPABASE)

The persistent memory is stored in the `agent_memory` table in Supabase. It uses the `pgvector` extension for storing vector embeddings and running high-speed semantic searches.

### 1.1 SQL Schema Setup

```sql
-- 1. Enable the pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the agent_memory table
CREATE TABLE IF NOT EXISTS agent_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  
  -- Memory Content
  memory_type VARCHAR(50) NOT NULL, -- 'past_trade', 'past_analysis', 'lesson_learned'
  content TEXT NOT NULL,
  
  -- Context
  symbol VARCHAR(20), -- BTC, ETH, etc (NULL if general/macro)
  market_conditions VARCHAR(100), -- 'bullish', 'bearish', 'volatile', 'stable'
  
  -- Relevance & Tracking
  relevance_score DECIMAL(3, 2) DEFAULT 0.50 CHECK (relevance_score BETWEEN 0 AND 1),
  last_retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  retrieval_count INT DEFAULT 0,
  
  -- Embedding (1536 dimensions for OpenAI text-embedding-ada-002)
  embedding vector(1536) DEFAULT NULL,
  
  -- Tagging
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent_id ON agent_memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_agent_memory_symbol ON agent_memory(symbol);
CREATE INDEX IF NOT EXISTS idx_agent_memory_tags ON agent_memory USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agent_memory_created_at ON agent_memory(created_at DESC);

-- 4. Create ivfflat index for fast vector search (Cosine Distance)
CREATE INDEX IF NOT EXISTS idx_agent_memory_embedding 
ON agent_memory USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 1.2 Supabase Vector Matching RPC Function

To perform semantic search directly inside PostgreSQL, we define a stored procedure `match_memories` that can be invoked via Supabase Client API:

```sql
CREATE OR REPLACE FUNCTION match_memories (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  filter_agent_id uuid,
  filter_symbol varchar DEFAULT NULL,
  filter_market_conditions varchar DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  agent_id uuid,
  memory_type varchar,
  content text,
  symbol varchar,
  market_conditions varchar,
  relevance_score decimal,
  tags text[],
  created_at timestamp with time zone,
  last_retrieved_at timestamp with time zone,
  retrieval_count int,
  similarity float
)
AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.id,
    m.agent_id,
    m.memory_type,
    m.content,
    m.symbol,
    m.market_conditions,
    m.relevance_score,
    m.tags,
    m.created_at,
    m.last_retrieved_at,
    m.retrieval_count,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM agent_memory m
  WHERE m.agent_id = filter_agent_id
    AND (filter_symbol IS NULL OR m.symbol = filter_symbol)
    AND (filter_market_conditions IS NULL OR m.market_conditions = filter_market_conditions)
    AND 1 - (m.embedding <=> query_embedding) > match_threshold
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

---

## 2. RETRIEVAL & UPDATE LOGIC

### 2.1 Embedding Generation

We generate 1536-dimensional text embeddings using OpenAI's `text-embedding-ada-002` API.
- **Fail-safe offline fallback**: If OpenAI credentials are not provided or if the network is down, the system dynamically shifts to a **Deterministic Hash-seeded RNG generator**. This outputs normalized unit vectors that behave predictably, preventing any run-time script crashes during local evaluation.

### 2.2 Local File Fallback

If connection to Supabase fails or credentials are omitted:
- Memories are stored locally in `agent_memory.json` inside the root or app data folders.
- Cosine similarity is computed in Python using NumPy:
  $$\text{Cosine Similarity} = \frac{\mathbf{q} \cdot \mathbf{m}}{\|\mathbf{q}\| \|\mathbf{m}\|}$$

---

## 3. HYBRID MEMORY RANKING STRATEGY

Retrieving information solely on semantic similarity can surface outdated or low-importance precedents. Council applies a **three-factor Hybrid Ranking Strategy**:

$$\text{Final Score} = 0.50 \cdot \text{CosineSimilarity} + 0.30 \cdot \text{RecencyDecay} + 0.20 \cdot \text{Importance}$$

### 3.1 Recency Decay
Memories decay exponentially over time to ensure the Council learns from the latest market dynamics:
$$\text{RecencyDecay} = e^{-\lambda \cdot t}$$
- $t$: Time elapsed since the memory was created (in days).
- $\lambda$: Decay rate ($0.05$), yielding a half-life of approximately 14 days. This keeps recent sessions prioritized.

### 3.2 Importance Score
- Represented by the `relevance_score` column (value between 0.0 and 1.0).
- High importance scores are assigned to critical events like **losses exceeding limits (-5.0%)**, **risk manager vetoes**, and **major disagreements (100% split votes)**.

---

## 4. EXAMPLE DATA STRUCTS

### 4.1 Stored Memory (JSON Schema representation)
```json
{
  "id": "e3b62f88-43d9-482d-8b01-3829adbf7b5b",
  "agent_id": "tech-analyst-uuid",
  "memory_type": "lesson_learned",
  "content": "RSI entered overbought territory (>75) under high volatility. Bullish momentum continued for 48 hours before a sharp 5% correction. Support held at $42,500.",
  "symbol": "BTC",
  "market_conditions": "volatile",
  "relevance_score": 0.80,
  "tags": ["rsi_overbought", "support_held", "failed_momentum"],
  "created_at": "2026-06-12T09:00:00Z"
}
```

### 4.2 Search Results (Ranked Output)
```json
[
  {
    "id": "e3b62f88-43d9-482d-8b01-3829adbf7b5b",
    "memory_type": "lesson_learned",
    "content": "RSI entered overbought territory (>75) under high volatility...",
    "symbol": "BTC",
    "market_conditions": "volatile",
    "relevance_score": 0.8,
    "tags": ["rsi_overbought", "support_held"],
    "created_at": "2026-06-12T09:00:00Z",
    "similarity": 0.9125,
    "hybrid_score": 0.8872,
    "age_days": 0.04,
    "recency_decay": 0.998
  }
]
```

---

## STAGE 10 COMPLETE
✅ 1. SQL schema for pgvector setup created.  
✅ 2. Supabase SQL RPC search function designed.  
✅ 3. Implement Python `AgentMemoryManager` (embedding, local fallback).  
✅ 4. Implement hybrid ranking math (similarity + recency decay + importance).  
✅ 5. Output retrieval stats updates logic.  
