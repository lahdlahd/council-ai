# STAGE 13 — COUNCIL REPLAY
## Council: Replaying AI Investment Committee Decisions

**Status**: Complete Council Replay Service  
**Implementation**: FastAPI Endpoints + Timeline Aggregation + Local Database Backup  
**Version**: 1.0  
**Date**: June 12, 2026

---

## 1. ARCHITECTURE OVERVIEW

Council Replay enables users (and frontend dashboard interfaces) to review and replay every single trading decision made by the AI Investment Committee. 

Rather than serving isolated pieces of data, the backend compiles a unified **Session Timeline** representing the chronological progression of a decision:

```
[Market Snapshot] ➔ [Round 1 Analyses] ➔ [Round 2+ Debates] ➔ [Weighted Votes Tally] ➔ [Risk Assessment] ➔ [Execution Decision] ➔ [Trade Outcome P&L]
```

To support local hackathon presentations and offline testability, the Replay Service employs a dual-layer data provider:
1. **Supabase PostgreSQL Layer**: Queries normalized postgres tables when connection credentials are active.
2. **Local JSON Database Layer** (`replay_fallback.json`): Provides pre-loaded investment committee replays (including successful trades and risk-vetoed decisions) if Supabase is offline.

---

## 2. API CONTRACT SPECIFICATIONS

### 2.1 GET /api/replay
Returns a list of all completed sessions available for replay.

**Response Schema (`List[ReplaySummary]`)**:
```json
[
  {
    "session_id": "d11b34a6-4be4-42f0-9a2c-e1f4864b22c0",
    "symbol": "BTC",
    "final_action": "BUY",
    "confidence_score": 88.65,
    "trade_status": "completed",
    "realized_pnl": 827.40,
    "created_at": "2026-06-10T10:00:00Z"
  }
]
```

### 2.2 GET /api/replay/{session_id}
Returns the detailed chronological timeline of a specific session.

**Response Schema (`ReplayTimeline`)**:
```json
{
  "session_id": "d11b34a6-4be4-42f0-9a2c-e1f4864b22c0",
  "symbol": "BTC",
  "created_at": "2026-06-10T10:00:00Z",
  "market_state": {
    "symbol": "BTC",
    "current_price": 43500.0,
    "price_24h_high": 44200.0,
    "price_24h_low": 42900.0,
    "volume_24h": 125000000.0,
    "volatility": 0.22,
    "trend_direction": "UP",
    "market_news_count": 14,
    "market_conditions": "bullish"
  },
  "initial_opinions": {
    "technical_analyst": {
      "recommendation": "BUY",
      "confidence": 80.0,
      "reasoning": "Golden cross on 4h chart with rising RSI indicators support breakout above resistance."
    },
    "news_analyst": {
      "recommendation": "BUY",
      "confidence": 75.0,
      "reasoning": "Sentiment is highly positive due to heavy ETF net inflows."
    },
    "quant_analyst": {
      "recommendation": "BUY",
      "confidence": 70.0,
      "reasoning": "Expected value calculations indicate positive momentum bounce likelihood."
    }
  },
  "debate_transcript": [
    {
      "agent_name": "Technical Analyst",
      "message_type": "ANALYSIS",
      "content": "Initial Analysis: BUY. Golden cross supports breakout.",
      "confidence": 0.8,
      "recommendation": "BUY"
    },
    {
      "agent_name": "News Analyst",
      "message_type": "CHALLENGE",
      "content": "I challenge Technical Analyst. SEC delay reports might cause volatility spike.",
      "confidence": 0.75,
      "recommendation": "HOLD"
    }
  ],
  "voting_tally": {
    "votes": {
      "technical_analyst": {"vote": "BUY", "weight": 1.2, "confidence": 80.0},
      "quant_analyst": {"vote": "BUY", "weight": 1.1, "confidence": 72.0},
      "news_analyst": {"vote": "BUY", "weight": 1.0, "confidence": 75.0}
    },
    "proposed_action": "BUY"
  },
  "veto_verification": {
    "risk_score": 25.0,
    "risk_level": "low",
    "position_size_recommendation": 15000.0,
    "max_position_allowed": 0.15,
    "approved": true,
    "veto_reason": "Approved"
  },
  "execution_decision": {
    "action": "BUY",
    "confidence_score": 84.85,
    "confidence_factors": {
      "raw_scores": {
        "agent_agreement": 100.0,
        "risk_score_factor": 75.0,
        "volatility_factor": 78.0,
        "sentiment_stability": 75.0,
        "historical_accuracy": 69.0
      },
      "weighted_contributions": {
        "agent_agreement": 40.0,
        "risk_score_factor": 15.0,
        "volatility_factor": 11.7,
        "sentiment_stability": 11.25,
        "historical_accuracy": 6.9
      },
      "total_score": 84.85
    },
    "position_size": {
      "percentage_of_portfolio": 12.0,
      "quantity": 0.2758,
      "entry_price": 43500.0,
      "target_price": 46500.0,
      "stop_loss": 41800.0
    },
    "reasoning": "The committee reached a unanimous agreement to BUY BTC...",
    "key_factors": ["Unanimous consensus", "ETF inflows breakout", "Low risk profile"]
  },
  "trade_result": {
    "status": "completed",
    "entry_price": 43500.0,
    "quantity": 0.2758,
    "exit_price": 46500.0,
    "exit_timestamp": "2026-06-11T14:30:00Z",
    "realized_pnl": 827.40,
    "notes": "Target hit. Exited automatically."
  }
}
```

### 2.3 POST /api/replay/{session_id}/mock-complete
Simulates trade completion with P&L exit data for demo presentations.

**Request Body**:
```json
{
  "exit_price": 46500.0
}
```

---

## 3. DATABASE DESIGN MAPPING

The timeline is aggregated by querying PostgreSQL tables sequentially:

1. **`council_sessions`**: Retrieves `symbol`, `created_at`, and `market_context`.
2. **`agent_debates`**: Retrieves the turn-by-turn messages.
   - Message rows with `message_type = 'analysis'` populate the `initial_opinions`.
   - Message rows with `message_type IN ('challenge', 'agreement', 'revision')` populate the `debate_transcript`.
3. **`votes`**: Aggregates weights and final voting positions.
4. **`council_decisions`**: Populates risk metrics, veto status, and execution synthesis targets.
5. **`trades`**: Retrieves execution prices and realized returns.

---

## STAGE 13 COMPLETE
✅ 1. Replay REST router endpoints (/api/replay, /api/replay/{session_id}) defined.  
✅ 2. Replay Pydantic API contract schemas completed.  
✅ 3. ReplayService database queries and local JSON fallback client implemented.  
✅ 4. Mock simulation completes enabled.  
✅ 5. Uvicorn/FastAPI main loop integrated.  
