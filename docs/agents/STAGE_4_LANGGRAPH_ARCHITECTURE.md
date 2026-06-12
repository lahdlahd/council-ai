# STAGE 4 — LANGGRAPH AGENTS
## Council: Multi-Agent Architecture & Orchestration

**Status**: LangGraph Architecture Design (No Code)  
**Framework**: LangGraph + LangChain  
**Version**: 1.0  
**Date**: June 12, 2026

---

## 1. LANGGRAPH SYSTEM OVERVIEW

### 1.1 Architecture Philosophy

Council uses **LangGraph** as the orchestration layer for multi-agent coordination:

**Key Principles:**
- **Deterministic Execution**: Graph flow is reproducible for replay
- **State Threading**: Single shared state passed through all nodes
- **Conditional Routing**: Risk checks can block trade execution
- **Message Immutability**: Debate messages append-only
- **Tool Composition**: Agents access specialized tools via registry
- **Error Resilience**: Single agent failure doesn't stop council
- **Audit Trail**: Every decision step is logged and traceable

### 1.2 LangGraph Component Hierarchy

```
LangGraph Application
├── GraphBuilder (Define nodes and edges)
├── StateSchema (AgentState definition)
├── Nodes (5 Agent + 7 Support Nodes)
├── Edges (Routing logic)
├── Compiled Graph (Executable workflow)
└── Checkpointer (For replay/persistence)
```

### 1.3 Node Types

```
Agent Nodes (Active Decision-Making):
├── TechnicalAnalystNode
├── NewsAnalystNode
├── QuantAnalystNode
├── RiskManagerNode
└── ExecutionAgentNode

Support Nodes (Orchestration):
├── DataPreparationNode
├── DebateCoordinatorNode
├── VotingCoordinatorNode
├── RiskValidationNode
├── DecisionMakingNode
├── TradeExecutionNode
└── MemoryUpdateNode
```

---

## 2. STATE DEFINITION (AgentState)

### 2.1 AgentState Structure

The **AgentState** is the single source of truth passed through all nodes:

```
AgentState (Shared Mutable State)
├── Session Metadata
│   ├── session_id: UUID
│   ├── user_id: UUID
│   ├── start_timestamp: ISO8601
│   ├── market_conditions: str (bullish/bearish/volatile/stable)
│   └── debate_max_rounds: int
│
├── Market Data
│   ├── symbol: str (BTC, ETH, etc)
│   ├── current_price: float
│   ├── price_24h_high: float
│   ├── price_24h_low: float
│   ├── volume_24h: float
│   ├── volatility: float (0-1, 1=highly volatile)
│   ├── historical_candles: list[OHLCV]
│   │   └── Each: {timestamp, open, high, low, close, volume}
│   ├── current_rsi: float
│   ├── current_macd: dict (value, signal, histogram)
│   ├── current_ema_50: float
│   ├── current_ema_200: float
│   ├── support_levels: list[float]
│   ├── resistance_levels: list[float]
│   ├── trend_direction: str (UP/DOWN/SIDEWAYS)
│   └── market_news_count: int
│
├── Agent Analyses (Collected from each agent)
│   ├── technical_analysis: TechnicalAnalysis object
│   │   ├── bullish_score: float (0-100)
│   │   ├── bearish_score: float (0-100)
│   │   ├── confidence: float (0-100)
│   │   ├── reasoning: str
│   │   ├── recommendation: str (BUY/SELL/HOLD)
│   │   ├── key_findings: list[str]
│   │   └── supporting_data: dict
│   │
│   ├── news_analysis: NewsAnalysis object
│   │   ├── sentiment_score: float (-1 to 1, -1=bearish)
│   │   ├── confidence: float (0-100)
│   │   ├── reasoning: str
│   │   ├── recommendation: str (BUY/SELL/HOLD)
│   │   ├── key_events: list[str]
│   │   ├── whale_activity: str (BUYING/SELLING/NEUTRAL)
│   │   └── macro_impact: str
│   │
│   ├── quant_analysis: QuantAnalysis object
│   │   ├── probability_score: float (0-100)
│   │   ├── confidence: float (0-100)
│   │   ├── reasoning: str
│   │   ├── recommendation: str (BUY/SELL/HOLD)
│   │   ├── historical_pattern: str
│   │   ├── expected_value: float
│   │   └── correlation_analysis: dict
│   │
│   ├── risk_assessment: RiskAssessment object
│   │   ├── volatility_score: float (0-100)
│   │   ├── drawdown_risk: float (0-100)
│   │   ├── position_size_recommendation: float (% of portfolio)
│   │   ├── overall_risk_score: float (0-100)
│   │   ├── exposure_level: str (LOW/MEDIUM/HIGH)
│   │   ├── approved: bool
│   │   ├── veto_reason: str or null
│   │   └── alternative_suggestions: list[str]
│   │
│   └── execution_synthesis: ExecutionSynthesis object
│       ├── aggregated_recommendation: str
│       ├── weighted_consensus: float (0-100)
│       ├── confidence_score: float (0-100)
│       └── reasoning: str
│
├── Debate Messages
│   ├── messages: list[AgentMessage]
│   │   └── Each message:
│   │       ├── agent_id: UUID
│   │       ├── agent_name: str
│   │       ├── timestamp: ISO8601
│   │       ├── message_type: str (ANALYSIS|CHALLENGE|AGREEMENT|REVISION|VOTE|FINAL)
│   │       ├── content: str (natural language)
│   │       ├── confidence: float (0-1)
│   │       ├── recommendation: str (BUY/SELL/HOLD)
│   │       ├── reasoning: dict {key_points, supporting_data, risk_factors}
│   │       ├── reply_to: UUID or null
│   │       └── metadata: dict {processing_time_ms, tokens_used}
│   │
│   ├── current_round: int (1-indexed)
│   ├── max_rounds: int
│   ├── debate_started_at: ISO8601
│   ├── total_debate_turns: int
│   └── consensus_building: bool
│
├── Voting State
│   ├── votes: dict[agent_id, Vote]
│   │   └── Each vote:
│   │       ├── agent_id: UUID
│   │       ├── agent_name: str
│   │       ├── vote: str (BUY/SELL/HOLD/ABSTAIN)
│   │       ├── confidence: float (0-100)
│   │       ├── weight: float (1.0 = equal, RiskManager weight = 2.0)
│   │       ├── reasoning: str
│   │       └── timestamp: ISO8601
│   │
│   ├── voting_started_at: ISO8601
│   ├── all_votes_received: bool
│   ├── buy_votes: int
│   ├── sell_votes: int
│   ├── hold_votes: int
│   ├── abstain_votes: int
│   ├── weighted_consensus: float (0-100)
│   └── consensus_action: str (BUY/SELL/HOLD)
│
├── Risk Validation
│   ├── risk_validation_passed: bool
│   ├── risk_score: float (0-100)
│   ├── veto_applied: bool
│   ├── veto_reason: str or null
│   ├── approval_timestamp: ISO8601
│   └── risk_assessment_details: dict
│
├── Final Decision
│   ├── final_action: str (BUY/SELL/HOLD)
│   ├── final_confidence_score: float (0-100)
│   ├── position_size: float (% of portfolio)
│   ├── target_price: float or null
│   ├── stop_loss: float or null
│   ├── reasoning: str
│   ├── key_factors: list[str]
│   ├── decision_made_at: ISO8601
│   └── decision_reasoning_full: str (comprehensive explanation)
│
├── Trade Execution
│   ├── trade_approved: bool
│   ├── trade_id: UUID or null
│   ├── execution_timestamp: ISO8601 or null
│   ├── execution_price: float or null
│   ├── execution_status: str (PENDING/EXECUTED/FAILED/CANCELLED)
│   ├── execution_notes: str or null
│   └── trade_quantity: float or null
│
└── Metadata & Tracking
    ├── session_status: str (IN_PROGRESS/COMPLETED/FAILED/CANCELLED)
    ├── error_log: list[str]
    ├── warnings: list[str]
    ├── nodes_executed: list[str]
    ├── total_duration_ms: int
    └── memory_update_count: int
```

### 2.2 State Type Definitions (Pydantic Models)

```
Key TypedDicts/Pydantic Models:

TechnicalAnalysis:
  - bullish_score: float
  - bearish_score: float
  - confidence: float
  - reasoning: str
  - recommendation: str
  - key_findings: list[str]
  - supporting_data: dict

NewsAnalysis:
  - sentiment_score: float
  - confidence: float
  - reasoning: str
  - recommendation: str
  - key_events: list[str]
  - whale_activity: str
  - macro_impact: str

QuantAnalysis:
  - probability_score: float
  - confidence: float
  - reasoning: str
  - recommendation: str
  - historical_pattern: str
  - expected_value: float
  - correlation_analysis: dict

RiskAssessment:
  - volatility_score: float
  - drawdown_risk: float
  - position_size_recommendation: float
  - overall_risk_score: float
  - exposure_level: str
  - approved: bool
  - veto_reason: str | None
  - alternative_suggestions: list[str]

AgentMessage:
  - agent_id: UUID
  - agent_name: str
  - timestamp: ISO8601
  - message_type: str
  - content: str
  - confidence: float
  - recommendation: str
  - reasoning: dict
  - reply_to: UUID | None
  - metadata: dict

Vote:
  - agent_id: UUID
  - agent_name: str
  - vote: str
  - confidence: float
  - weight: float
  - reasoning: str
  - timestamp: ISO8601
```

---

## 3. MESSAGE STRUCTURE

### 3.1 AgentMessage Format

Every message in the debate uses a consistent structure:

```
AgentMessage {
  # Identity
  agent_id: "uuid-technical-analyst",
  agent_name: "Technical Analyst",
  
  # Timing
  timestamp: "2026-06-12T14:32:45.123Z",
  message_sequence: 5,  # Order in round
  
  # Message Classification
  message_type: "ANALYSIS" | "CHALLENGE" | "AGREEMENT" | "REVISION" | "VOTE" | "FINAL",
  
  # Content
  content: "Bitcoin is showing strong bullish signals with RSI above 70...",
  
  # Confidence Metrics
  confidence: 0.92,  # 0-1 scale
  
  # Recommendation
  recommendation: "BUY" | "SELL" | "HOLD",
  
  # Detailed Reasoning
  reasoning: {
    key_points: [
      "RSI is at 78 (overbought but can continue trending)",
      "MACD histogram is positive and widening",
      "Price above EMA-200, strong uptrend"
    ],
    supporting_data: {
      rsi: 78,
      macd_histogram: 0.45,
      ema_50_position: "above price (support)",
      volume_trend: "increasing"
    },
    risk_factors: [
      "Extended rally may face profit taking",
      "Support at $42,000 is key level"
    ]
  },
  
  # Context
  reply_to: "uuid-news-analyst-message" | null,  # If replying to another agent
  
  # Processing Info
  metadata: {
    processing_time_ms: 1234,
    tokens_used: 847,
    model_used: "gpt-4",
    temperature: 0.7
  }
}
```

### 3.2 Message Types & Semantics

```
ANALYSIS:
├── Use: Initial agent analysis
├── When: First message in round, or after being asked
├── Must Include: Full reasoning, confidence, recommendation
└── Follow-up: Can be challenged or agreed with

CHALLENGE:
├── Use: Disagreement with another agent
├── Format: Points out specific issues with prior analysis
├── Must Include: Alternative reasoning, counter-evidence
└── Target: Specific prior message (reply_to set)

AGREEMENT:
├── Use: Support for another agent's analysis
├── Format: Concise, reinforces their reasoning
├── Must Include: Why you agree, additional supporting points
└── Target: Specific prior message (reply_to set)

REVISION:
├── Use: Agent changes their opinion mid-debate
├── Trigger: After being challenged with good evidence
├── Must Include: New recommendation, why they changed, confidence
└── Type: Major state change in debate

VOTE:
├── Use: Final voting phase
├── When: After debate rounds complete
├── Must Include: vote (BUY/SELL/HOLD), confidence, reasoning
└── Immutable: Vote cannot change once cast

FINAL:
├── Use: Execution agent synthesizes decision
├── When: After all votes collected & risk check passes
├── Must Include: Final action, confidence score, key factors
└── Timestamp: Marks decision point
```

### 3.3 Debate Message Protocol

```
Round 1: Initial Analyses
├─ Agent 1 (Technical): Sends ANALYSIS
├─ Agent 2 (News): Sends ANALYSIS
├─ Agent 3 (Quant): Sends ANALYSIS
├─ Agent 4 (Risk): Sends ANALYSIS
└─ Agent 5 (Execution): Observes (no message yet)

Round 2: Debate & Challenges
├─ Agent 2: Sends CHALLENGE to Agent 1
├─ Agent 1: Sends REVISION or clarifies position
├─ Agent 3: Sends AGREEMENT with Agent 1
├─ Agent 4: Flags potential issues
└─ Message flow: Any agent can respond to any prior message

Round 3: Consensus Building
├─ Agents coalesce around strongest thesis
├─ AGREEMENT messages increase
├─ Consensus level rising
└─ Debate coordinator signals end

Voting Phase:
├─ All agents (including Execution) vote
├─ VOTE message type used
├─ Voting immutable once received
└─ Results immediately tallied

Decision Phase:
├─ Execution agent synthesizes
├─ FINAL message issued
├─ Decision recorded to state
└─ Risk validation triggered
```

---

## 4. NODE DEFINITIONS

### 4.1 DataPreparationNode

**Purpose**: Fetch and prepare all market data before agent analysis

```
Input: session_id, symbol, user_id
Output: Updated state with:
  - current_price
  - volatility
  - historical_candles
  - current_rsi, MACD, EMAs
  - support/resistance levels
  - trend_direction
  - market_news_count

Processing:
├── 1. Fetch current price from data service
├── 2. Get 7-day historical candles
├── 3. Calculate technical indicators (RSI, MACD, EMAs)
├── 4. Identify support/resistance (via algorithm)
├── 5. Determine trend (via analysis)
├── 6. Count recent news items
├── 7. Calculate volatility score
└── 8. Return complete market state

Error Handling:
├── If price fetch fails: Use cached price + warning
├── If indicators fail: Notify, continue with available data
├── If news fetch fails: Set news_count to 0
└── All warnings appended to state.warnings
```

### 4.2 TechnicalAnalystNode

**Purpose**: Technical analysis (RSI, MACD, EMA, trends, support/resistance)

```
Input State:
├── Market data (prices, candles, indicators)
├── Historical performance
└── Previous trades

Output: state.technical_analysis updated with:
  - bullish_score (0-100)
  - bearish_score (0-100)
  - confidence (0-100)
  - reasoning
  - recommendation (BUY/SELL/HOLD)
  - key_findings
  - supporting_data

Agent Responsibilities:
├── 1. Analyze RSI (oversold/overbought context)
├── 2. Analyze MACD (trend confirmation)
├── 3. Analyze EMA crossovers (trend strength)
├── 4. Analyze volume trends (confirm moves)
├── 5. Identify key support/resistance
├── 6. Determine overall trend direction
└── 7. Generate recommendation with confidence

Scoring Logic:
├── RSI > 70: Bullish (but watch for reversal)
├── RSI < 30: Bearish (watch for bounce)
├── MACD positive & histogram widening: Bullish
├── Price above EMA-50 above EMA-200: Strong bullish
└── Combine all into 0-100 score

Confidence Factors:
├── How clear is the signal? (30-100%)
├── How many indicators agree? (multiplier 0.8-1.2)
├── How extreme is the move? (affects confidence)
└── Final: bullish_score + bearish_score <= 100
```

### 4.3 NewsAnalystNode

**Purpose**: News sentiment, macro events, whale activity

```
Input State:
├── Market data
├── Recent news items
├── Social sentiment
└── Whale movement data

Output: state.news_analysis updated with:
  - sentiment_score (-1 to +1, -1=bearish)
  - confidence (0-100)
  - reasoning
  - recommendation (BUY/SELL/HOLD)
  - key_events (list of important news)
  - whale_activity (BUYING/SELLING/NEUTRAL)
  - macro_impact (str)

Agent Responsibilities:
├── 1. Analyze recent news sentiment
├── 2. Identify major news items (ETF approvals, etc)
├── 3. Assess whale activity (large movements)
├── 4. Evaluate macro economic factors
├── 5. Check social media sentiment
├── 6. Gauge regulatory environment
└── 7. Generate recommendation with confidence

Sentiment Calculation:
├── Positive events: +0.3 each (capped at 1.0)
├── Negative events: -0.3 each (floored at -1.0)
├── Whale buying: +0.2 sentiment boost
├── Whale selling: -0.2 sentiment boost
├── Scale to 0-100 confidence
└── Final recommendation based on magnitude

Key News Types:
├── Regulatory approvals/denials
├── Major partnerships
├── Exchange hacks/issues
├── Macro economic shifts
├── Large institutional movements
└── Social media sentiment shifts
```

### 4.4 QuantAnalystNode

**Purpose**: Statistical analysis, historical patterns, expected value

```
Input State:
├── Historical price data
├── Past trades & outcomes
├── Historical patterns
└── Portfolio correlations

Output: state.quant_analysis updated with:
  - probability_score (0-100)
  - confidence (0-100)
  - reasoning
  - recommendation (BUY/SELL/HOLD)
  - historical_pattern (str)
  - expected_value (float)
  - correlation_analysis (dict)

Agent Responsibilities:
├── 1. Identify similar historical patterns
├── 2. Calculate probability of success
├── 3. Calculate expected value (EV)
├── 4. Perform correlation analysis
├── 5. Analyze win rate patterns
├── 6. Assess portfolio diversification impact
└── 7. Generate recommendation

Statistical Methods:
├── Pattern Recognition:
│  └── Find similar price action in history
├── Probability Calculation:
│  └── Win rate of similar setups historically
├── Expected Value:
│  └── (probability_of_win × avg_gain) - (probability_of_loss × avg_loss)
├── Correlation:
│  └── How does this move affect other holdings?
└── Confidence:
   └── Based on statistical sample size & consistency

Recommendation Logic:
├── If EV > 0 and probability > 50%: BUY (if bullish)
├── If EV < 0 or probability < 40%: SELL
├── If EV near 0 or mixed signals: HOLD
└── Scale confidence 0-100 based on statistical strength
```

### 4.5 RiskManagerNode

**Purpose**: Risk assessment with veto power

```
Input State:
├── Portfolio data
├── Proposed trade size
├── Market volatility
├── Position exposure
└── Drawdown risk

Output: state.risk_assessment updated with:
  - volatility_score (0-100)
  - drawdown_risk (0-100)
  - position_size_recommendation (% of portfolio)
  - overall_risk_score (0-100)
  - exposure_level (LOW/MEDIUM/HIGH)
  - approved (bool) ⭐ VETO POWER
  - veto_reason (str or null)
  - alternative_suggestions (list)

Agent Responsibilities:
├── 1. Calculate portfolio volatility
├── 2. Assess potential drawdown
├── 3. Check position sizing rules
├── 4. Verify exposure limits
├── 5. Analyze correlation risks
├── 6. Make VETO decision
└── 7. Suggest alternatives if rejecting

Risk Scoring:
├── Volatility: 0-100 (higher = more risky)
├── Drawdown potential: % of portfolio at risk
├── Position sizing: Validate against limits
├── Total exposure: Sum of all open positions
└── Overall risk = weighted average

Veto Criteria (VETO if ANY triggered):
├── Portfolio exposure would exceed 50%
├── Volatility too extreme (>80%)
├── Max daily loss limit would be breached
├── Position size > max_position_size setting
├── High correlation with existing positions
├── Drawdown risk exceeds tolerance
└── User-configured risk limits

Approval:
├── If all checks pass: approved = true
├── If any fail: approved = false, veto_reason populated
├── Alternative suggestions: Reduce size, HOLD, etc
└── Cannot be overridden by other agents ⭐
```

### 4.6 ExecutionAgentNode

**Purpose**: Synthesize all analyses into final decision

```
Input State:
├── All 4 agent analyses (technical, news, quant, risk)
├── Debate messages
├── Market state
└── Risk approval

Output: state.execution_synthesis updated with:
  - aggregated_recommendation (str: BUY/SELL/HOLD)
  - weighted_consensus (0-100)
  - confidence_score (0-100)
  - reasoning (comprehensive explanation)

Agent Responsibilities:
├── 1. Read all prior agent analyses
├── 2. Read all debate messages
├── 3. Calculate weighted consensus
├── 4. Assess agreement level
├── 5. Weight by agent credibility
├── 6. Generate synthesis reasoning
└── 7. Prepare for voting

Consensus Calculation:
├── Collect all agent recommendations
├── Weight by agent credibility/accuracy
├── Technical weight: 1.2x (historical accuracy)
├── News weight: 1.0x (standard)
├── Quant weight: 1.1x (data-driven)
├── Risk weight: 2.0x (veto power)
├── Calculate: (Σ votes × weights) / Σ weights
└── Result: 0-100 consensus score

Confidence Score Components:
├── Agent agreement (40%): How much do agents agree?
├── Historical accuracy (25%): How accurate are agents?
├── Volatility factor (15%): Lower vol = higher confidence
├── Risk approval (20%): Risk manager blessing
└── Final: Weighted sum (0-100 scale)

Output Recommendation:
├── Synthesize all analyses
├── Explain consensus
├── Note any disagreements
├── Reference key debate points
└── Set confidence_score
```

### 4.7 DebateCoordinatorNode

**Purpose**: Manage debate rounds and transitions

```
Input: state with analyses
Output: Orchestrates debate, updates messages list

Responsibilities:
├── 1. Start debate round
├── 2. Set speaking order (consistent each round)
├── 3. Trigger each agent to speak
├── 4. Collect responses into messages list
├── 5. Detect new challenges/agreements
├── 6. Track consensus level
├── 7. Decide: Continue debate or move to voting?

Speaking Order (Consistent):
├── Round 1: Technical → News → Quant → Risk
├── Round 2+: Same order, but agents respond to challenges
├── Execution Agent: Observes (votes later)

Debate Continuation Logic:
├── Check: Are agents still challenging?
├── Check: Is consensus forming?
├── Check: Any major revisions?
├── If round < max_rounds AND consensus < 80%:
│  └── Continue debate
├── Else:
│  └── End debate, move to voting
└── Track total debate turns

Message Handling:
├── ANALYSIS messages: Append to messages list
├── CHALLENGE messages: Link to challenged message
├── AGREEMENT messages: Append, track support
├── REVISION messages: Record opinion change
└── All timestamped, sequenced, immutable once added
```

### 4.8 VotingCoordinatorNode

**Purpose**: Collect votes from all agents

```
Input: debate_messages, analyses
Output: state.votes dictionary populated

Voting Process:
├── 1. Request vote from each agent
├── 2. Collect vote + confidence + reasoning
├── 3. Record vote with timestamp
├── 4. Wait for all agents (timeout: 30s)
├── 5. Calculate voting statistics
└── 6. Determine consensus action

Vote Collection:
├── Technical Analyst vote (weight: 1.2x)
├── News Analyst vote (weight: 1.0x)
├── Quant Analyst vote (weight: 1.1x)
├── Risk Manager vote (weight: 2.0x)
└── Execution Agent vote (weight: 1.0x, tiebreaker)

Vote Weighting:
├── Multiply vote confidence by agent weight
├── Sum all weighted votes
├── Divide by sum of weights
├── Scale to 0-100 consensus score

Consensus Determination:
├── BUY votes: Count and sum weights
├── SELL votes: Count and sum weights
├── HOLD votes: Count and sum weights
├── ABSTAIN: Handled but not counted
├── Majority wins (weighted)
└── consensus_action = BUY/SELL/HOLD with highest score

Result Recording:
├── All votes immutable in state.votes dict
├── Timestamps recorded
├── Consensus level calculated
└── Ready for risk validation
```

### 4.9 RiskValidationNode

**Purpose**: Final risk check before execution

```
Input: state with final decision, risk_assessment
Output: Trade approved or vetoed

Final Check:
├── 1. Verify risk_manager.approved = true
├── 2. Check: risk_score < risk_threshold
├── 3. Verify: position_size valid
├── 4. Confirm: exposure limits OK
└── 5. Decision: Execute or VETO

Routing Logic:
├── If risk_approved == true:
│  └── → Proceed to TradeExecutionNode
├── Else (VETO):
│  ├── Set: veto_applied = true
│  ├── Set: final_action = null
│  ├── Log: veto_reason
│  ├── Notify: User
│  └── → Skip to MemoryUpdateNode (no trade)
└── All decision attempts logged to audit_log
```

### 4.10 TradeExecutionNode

**Purpose**: Execute the approved trade

```
Input: final_decision (BUY/SELL/HOLD), position_size
Output: Trade record created, portfolio updated

Execution Flow:
├── 1. If action = HOLD:
│  └── Skip execution, mark as such
├── 2. Create trade record
├── 3. Calculate execution parameters
├── 4. Execute trade (simulated or real)
├── 5. Record execution details
├── 6. Update portfolio
└── 7. Broadcast to frontend via WebSocket

Trade Creation:
├── Trade ID: Generated UUID
├── Symbol: From state
├── Action: From final_decision
├── Quantity: Calculated from position_size
├── Entry Price: Current market price
├── Status: PENDING → EXECUTED
├── Timestamp: Current time
└── All recorded to trades table

Portfolio Update:
├── Add/modify position in portfolio_holdings
├── Update user_portfolios totals
├── Recalculate allocation percentages
├── Update portfolio_tracking
└── Emit WebSocket event

Broadcasting:
├── WebSocket event: trade_executed
├── Payload: Full trade details
├── Target: Connected user's session
└── Frontend updates portfolio in real-time
```

### 4.11 MemoryUpdateNode

**Purpose**: Update agent memory with learnings

```
Input: Complete session state
Output: Agent memory updated with embeddings

Memory Update Process:
├── 1. For each agent:
│  ├─ Summarize this session's analysis
│  ├─ Record debate contributions
│  ├─ Compare prediction to actual outcome (if available)
│  └─ Store in agent_memory table
├── 2. Generate embeddings for memory
├── 3. Tag memories for retrieval
├── 4. Update agent accuracy metrics
└── 5. Index new memories for vector search

What Gets Stored:
├── Agent Analysis:
│  └── "Technical Analyst: RSI at 78, MACD positive, BUY recommendation at $42,300"
├── Debate Contributions:
│  └── "Challenged News Analyst on macro impact, held position after evidence review"
├── Prediction vs Reality:
│  └── "Recommended BUY at $42,300, price reached $43,100 (accurate), closed at $42,800 (net +1.2%)"
├── Pattern Recognition:
│  └── "Similar pattern observed 3 times in past, win rate 67%"
└── Lessons Learned:
   └── "Extended rallies often see profit-taking at +5% levels"

Embedding Generation:
├── OpenAI ada-002 (1536 dimensions)
├── Vectorize: memory.content
├── Store in: agent_memory.embedding (pgvector)
├── Index for: Semantic search

Tagging Strategy:
├── By agent: ["technical"]
├── By symbol: ["BTC", "ETH"]
├── By market condition: ["bullish", "volatile"]
├── By trade type: ["scalp", "swing"]
├── By outcome: ["win", "loss"]
└── By pattern: ["rsi_divergence", "macd_crossover"]

Accuracy Tracking:
├── Record agent's confidence prediction
├── Compare to actual outcome
├── Calculate accuracy score
├── Update agent_performance.accuracy
├── Weight future votes by accuracy (credibility)

Timing:
├── Executed after trade completion
├── Or after VETO (still learns from attempt)
└── Async task (doesn't block session completion)
```

---

## 5. GRAPH STRUCTURE & EDGES

### 5.1 Complete Graph Flow

```
START
  │
  ├─→ [DataPreparationNode]
  │   └─→ Fetch market data, calculate indicators
  │
  ├─→ [TechnicalAnalystNode] ◄─── Parallel Execution
  │   ├─→ Analyze RSI, MACD, EMAs
  │   └─→ Generate analysis
  │
  ├─→ [NewsAnalystNode] ◄─── Parallel Execution
  │   ├─→ Analyze sentiment, whale activity
  │   └─→ Generate analysis
  │
  ├─→ [QuantAnalystNode] ◄─── Parallel Execution
  │   ├─→ Analyze patterns, probabilities
  │   └─→ Generate analysis
  │
  ├─→ [RiskManagerNode] ◄─── Parallel Execution
  │   ├─→ Assess risk, volatility
  │   └─→ Generate assessment (with veto authority)
  │
  ├─→ [DebateCoordinatorNode]
  │   ├─→ Round 1-N: Agents speak & debate
  │   ├─→ Messages collected
  │   ├─→ Consensus tracked
  │   └─→ Decision: Continue debate or proceed?
  │       ├─ If consensus < 80% AND rounds < max:
  │       │  └─→ [DebateCoordinatorNode] (next round)
  │       └─ Else:
  │          └─→ [VotingCoordinatorNode]
  │
  ├─→ [VotingCoordinatorNode]
  │   ├─→ Collect votes from all agents
  │   ├─→ Weight by agent credibility
  │   ├─→ Calculate consensus
  │   └─→ Determine: BUY/SELL/HOLD
  │
  ├─→ [ExecutionAgentNode]
  │   ├─→ Synthesize all inputs
  │   ├─→ Generate final recommendation
  │   └─→ Calculate confidence score
  │
  ├─→ [RiskValidationNode]
  │   ├─→ Check: Risk approved?
  │   ├─→ Decision point:
  │   │   ├─ If approved:
  │   │   │  └─→ [TradeExecutionNode]
  │   │   └─ If VETO:
  │   │      └─→ [MemoryUpdateNode] (skip trade)
  │   │
  │   └─→ [TradeExecutionNode]
  │       ├─→ Execute trade (if action != HOLD)
  │       ├─→ Update portfolio
  │       └─→ Broadcast to frontend
  │
  ├─→ [MemoryUpdateNode]
  │   ├─→ Store debate transcript
  │   ├─→ Generate embeddings
  │   ├─→ Update agent memory
  │   ├─→ Update agent performance
  │   └─→ Index for vector search
  │
  └─→ END
      └─→ Return: Complete session state + decision
```

### 5.2 Edge Definitions

```
Edge Logic:

START → DataPreparationNode
  └─ Always

DataPreparationNode → [TechnicalAnalystNode, NewsAnalystNode, QuantAnalystNode, RiskManagerNode]
  └─ Parallel (all 4 simultaneously)

All 4 Analysts → DebateCoordinatorNode
  └─ Join (wait for all to complete)

DebateCoordinatorNode → DebateCoordinatorNode (self-loop for next round)
  └─ If: current_round < max_rounds AND consensus_level < 80%

DebateCoordinatorNode → VotingCoordinatorNode
  └─ If: current_round >= max_rounds OR consensus_level >= 80%

VotingCoordinatorNode → ExecutionAgentNode
  └─ Always (after all votes collected)

ExecutionAgentNode → RiskValidationNode
  └─ Always

RiskValidationNode → TradeExecutionNode
  └─ If: risk_assessment.approved == True AND final_action != HOLD

RiskValidationNode → MemoryUpdateNode
  └─ If: risk_assessment.approved == False (VETO)

TradeExecutionNode → MemoryUpdateNode
  └─ Always (after execution)

MemoryUpdateNode → END
  └─ Always
```

### 5.3 Conditional Routing

```
Decision Points:

1. Debate Continuation:
   CONDITION: current_round < max_rounds AND consensus < 80%
   TRUE: Loop back to DebateCoordinatorNode (next round)
   FALSE: Proceed to VotingCoordinatorNode

2. Risk Validation:
   CONDITION: risk_manager.approved == True
   TRUE: → TradeExecutionNode
   FALSE: → MemoryUpdateNode (veto, skip trade)

3. Trade Execution:
   CONDITION: final_action != "HOLD"
   TRUE: Execute trade
   FALSE: Skip execution, record as HOLD
```

---

## 6. TOOL REGISTRY

### 6.1 Tool Categories

```
TechnicalAnalystTools:
├── calculate_rsi(candles: list, period: int = 14) → float
├── calculate_macd(candles: list) → {value, signal, histogram}
├── calculate_ema(candles: list, period: int) → float
├── find_support_resistance(candles: list) → {support: list, resistance: list}
├── analyze_volume_trend(candles: list) → {trend: str, strength: float}
├── identify_trend(candles: list) → {direction: str, strength: float}
└── get_candlestick_pattern(candles: list) → str

NewsAnalystTools:
├── fetch_recent_news(symbol: str, hours: int = 24) → list[NewsItem]
├── analyze_sentiment(text: str) → {score: float, confidence: float}
├── check_whale_activity(symbol: str) → {activity: str, details: dict}
├── fetch_market_events(symbol: str) → list[Event]
├── assess_macro_economic(indicators: dict) → str
├── check_regulatory_news(symbol: str) → list[Event]
└── analyze_social_sentiment(symbol: str) → {score: float, sources: list}

QuantAnalystTools:
├── identify_pattern(symbol: str, candles: list) → {pattern: str, confidence: float}
├── backtest_similar_patterns(symbol: str, current_pattern: str) → {win_rate: float, trades: int}
├── calculate_probability(symbol: str, pattern: str) → float
├── analyze_correlation(symbol: str, portfolio: dict) → {correlations: dict}
├── calculate_expected_value(prob_win: float, avg_win: float, prob_loss: float, avg_loss: float) → float
├── analyze_support_resistance_performance(symbol: str) → dict
└── get_statistical_summary(symbol: str, period: str) → dict

RiskManagerTools:
├── calculate_volatility(candles: list) → float
├── assess_drawdown_risk(portfolio: dict, position: dict) → float
├── calculate_position_size(portfolio_value: float, risk_percent: float, entry: float, stop: float) → float
├── check_exposure_limits(portfolio: dict, new_position: dict) → {approved: bool, reason: str}
├── calculate_var(portfolio: dict, confidence: float = 0.95) → float
├── assess_correlation_risk(portfolio: dict, new_symbol: str) → float
├── verify_user_risk_limits(user: User) → {max_position: float, max_daily_loss: float}
└── simulate_position_impact(portfolio: dict, new_position: dict) → {new_metrics: dict}

ExecutionAgentTools:
├── aggregate_agent_votes(votes: dict) → {buy_count, sell_count, hold_count}
├── calculate_weighted_consensus(votes: dict, weights: dict) → float
├── calculate_confidence_score(components: dict) → float
├── synthesize_decision_reasoning(analyses: dict, votes: dict, debate: list) → str
└── determine_position_size(confidence: float, risk_score: float, portfolio: dict) → float
```

### 6.2 Tool Access Control

```
Each Agent Can Access:

TechnicalAnalyst:
  ├─ TechnicalAnalystTools (all)
  ├─ ExecutionAgentTools (for synthesis only)
  └─ ReadOnly: Market data, candles

NewsAnalyst:
  ├─ NewsAnalystTools (all)
  ├─ ExecutionAgentTools (for synthesis only)
  └─ ReadOnly: Market data, news

QuantAnalyst:
  ├─ QuantAnalystTools (all)
  ├─ ExecutionAgentTools (for synthesis only)
  └─ ReadOnly: Historical data, portfolio

RiskManager:
  ├─ RiskManagerTools (all)
  ├─ ReadOnly: Portfolio, positions, user settings
  └─ Authority: VETO power (only this agent)

ExecutionAgent:
  ├─ ExecutionAgentTools (all)
  ├─ ReadOnly: All other agent analyses
  └─ Write: final_decision, confidence_score
```

---

## 7. COMMUNICATION PROTOCOL

### 7.1 Inter-Node Communication

```
Sequential Communication:
├── Node completes execution
├── Returns updated state
├── State passed to next node(s)
├── Each node has full read access to state
├── Each node can only modify its designated sections

No Direct Agent-to-Agent Calls:
├── ❌ Technical Analyst does NOT call News Analyst directly
├── ✅ All communication via State mutations
├── ✅ Debate coordinator reads all messages from state
├── ✅ Agents read prior messages when speaking

Debate Message Queuing:
├── Agent generates response
├── Message appended to state.messages
├── Immutable (cannot be modified)
├── Next agent reads all prior messages
├── Enables context-aware responses
```

### 7.2 State Mutation Rules

```
Read Access:
├── All nodes: Can read entire state
├── Enables: Full context awareness
└── Used for: Reasoning, reference

Write Access:
├── Technical Analyst: state.technical_analysis only
├── News Analyst: state.news_analysis only
├── Quant Analyst: state.quant_analysis only
├── Risk Manager: state.risk_assessment only
├── Execution Agent: state.execution_synthesis only
├── Debate Coordinator: state.messages, state.current_round
├── Voting Coordinator: state.votes
├── Risk Validation: state.risk_validation section
├── Trade Execution: state.trade_execution section
└── Memory Update: Persists to database (not state mutation)

Immutable Sections:
├── state.market_data (set once, never changed)
├── state.messages (append-only, never deleted/modified)
└── state.votes (immutable once vote cast)
```

---

## 8. ERROR HANDLING STRATEGY

### 8.1 Node Failure Modes

```
If Agent Node Fails:
├── Error caught, logged to state.error_log
├── Agent marked as having error
├── Confidence reduced for this analysis
├── Continue with other agents
├── Debate uses available analyses
└── Note: Trade may proceed with reduced consensus

If Debate Coordinator Fails:
├── Fallback: Skip to voting immediately
├── Log: Debate cut short due to error
└── Continue: Voting still happens

If Risk Manager Fails:
├── Cannot proceed (safety critical)
├── Log: Risk assessment failed
├── Default: VETO (deny trade)
└── Notify: User must retry

If Trade Execution Fails:
├── Log: Execution error details
├── Roll back: Undo portfolio changes
├── Retry: Attempt 2 more times
├── If still fails: Record as FAILED
└── Notify: User immediately

If Memory Update Fails:
├── Log: But do not stop session
├── Soft error: Non-critical
├── Continue: Session marked complete
└── Retry: In background task
```

### 8.2 Timeouts

```
Per-Node Timeouts:
├── DataPreparation: 5 seconds
├── Individual Agent Analysis: 10 seconds
├── Debate Round: 30 seconds
├── Voting: 30 seconds
├── Risk Validation: 5 seconds
├── Trade Execution: 10 seconds
└── Memory Update: 20 seconds (async)

Session-Level Timeout:
├── Total: 5 minutes
├── If exceeded: Mark as TIMEOUT
├── Log: All steps completed so far
└── Notify: User of incomplete state
```

---

## 9. MEMORY INTEGRATION

### 9.1 Memory Retrieval in Analysis

```
When TechnicalAnalyst Starts:
├── 1. Get agent_id
├── 2. Query: Find similar past analyses (semantic search)
├── 3. Retrieve: Top 3 similar patterns
├── 4. Use as: Context + precedent
├── 5. In analysis: Reference past accuracy
└── 6. Adjust: Confidence based on historical accuracy

Memory Query:
├── Embedding similarity: Current candles → stored memories
├── Filter: By symbol and market conditions
├── Rank: By relevance_score and success rate
├── Retrieve: Top K (K=3-5)
└── Use: "Similar pattern 3 months ago had 78% accuracy"

Semantic Search:
├── Generate embedding: Current market state
├── Query: pgvector index (ivfflat)
├── Distance metric: cosine similarity
├── Return: Top matches sorted by similarity
└── Fast: Indexed search (< 100ms)
```

### 9.2 Memory Updates Post-Session

```
After Session Completes:
├── 1. Summarize each agent's analysis
├── 2. Record debate contributions
├── 3. Record final decision & confidence
├── 4. Wait: For trade outcome (if applicable)
├── 5. Compare: Prediction vs actual
├── 6. Generate: Embedding
├── 7. Store: In agent_memory table
├── 8. Tag: By symbol, market condition, type
└── 9. Index: For future semantic search

Example Memory Entry:
├── agent_id: "technical-analyst"
├── memory_type: "past_trade"
├── content: "RSI at 78 with MACD histogram widening and price above EMA-50. Recommended BUY at $42,300. Actual: Reached $43,100, closed $42,800. Accurate signal."
├── symbol: "BTC"
├── market_conditions: "bullish_trend"
├── relevance_score: 0.89 (how useful was this memory?)
├── embedding: [vector of 1536 dimensions]
├── tags: ["rsi_divergence", "macd_crossover", "win", "trend_following"]
└── created_at: timestamp
```

---

## 10. REPLAY CAPABILITY

### 10.1 Session Replay Architecture

```
Replay Enabled by:
├── Deterministic execution: Same inputs → Same outputs
├── Complete state persistence: Every step saved
├── Message immutability: Debate cannot be altered
├── Checkpoints: State saved at each node
└── Audit trail: All decisions logged

Replay Process:
├── 1. Load original session state
├── 2. Re-execute graph with same inputs
├── 3. Compare outputs (should be identical)
├── 4. Display: Original debate, votes, decision
├── 5. Show: Original market state + candles
├── 6. Timeline: Scrubable, step through each node
└── 7. Analysis: Compare then vs now (market moved)
```

### 10.2 Replay UI Data Structure

```
ReplaySession:
├── session_id: UUID
├── market_context: Original market state
├── timestamp: When replay is requested
├── stages: list[Stage]
│   └── Stage:
│       ├── stage_name: str (DataPrep, Debate Round 1, Voting, etc)
│       ├── agents_involved: list[str]
│       ├── messages: list[Message]
│       ├── duration_ms: int
│       ├── key_metrics: dict
│       └── timestamp: ISO8601
├── final_decision: Decision object
├── trade_record: Trade object (if executed)
├── final_market_state: Market data after trade
└── timeline_points: list[point]
    └── Each point clickable to view stage
```

---

## STAGE 4 COMPLETE

**LangGraph Multi-Agent Architecture documented with:**

✅ 1. System overview & component hierarchy
✅ 2. Comprehensive AgentState definition (50+ fields)
✅ 3. Message structure & debate protocol
✅ 4. 11 node definitions (5 agents + 6 orchestration)
✅ 5. Complete graph flow & edge definitions
✅ 6. Conditional routing logic
✅ 7. Tool registry (40+ tools across agents)
✅ 8. Communication protocol (state-based, no direct calls)
✅ 9. Error handling & timeouts
✅ 10. Memory integration & retrieval
✅ 11. Replay capability design

**This architecture enables:**
- Parallel agent analysis
- Structured debate with message threading
- Risk validation with veto power
- Deterministic, reproducible decision-making
- Complete audit trail & replay capability

Ready to proceed to **STAGE 5 — TECHNICAL ANALYST AGENT** (first actual code)?
