# STAGE 1 — SYSTEM ARCHITECTURE
## Council: AI Investment Committee Platform

**Status**: Architecture Design (No Code)  
**Version**: 1.0  
**Date**: June 12, 2026

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│            (Next.js + React + TypeScript)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Dashboard | Council Chamber | Agent Panel | Portfolio│   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼──────────┐  ┌──────▼─────────────┐
│   API GATEWAY      │  │  WEBSOCKET LAYER   │
│  (FastAPI)         │  │  (Real-time Data)  │
│                    │  │                    │
└─────────┬──────────┘  └──────┬─────────────┘
          │                    │
          └──────────┬─────────┘
                     │
        ┌────────────▼────────────┐
        │  ORCHESTRATION LAYER    │
        │  (LangGraph + State)    │
        │                         │
        │ ┌─────────────────────┐ │
        │ │  Multi-Agent System │ │
        │ │  (5 Agents + Debate)│ │
        │ └─────────────────────┘ │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────────┐  ┌────▼────────┐  ┌──▼──────────┐
│  DATABASE  │  │  MARKET DATA │  │  VECTOR DB │
│ (Supabase) │  │   STREAMS    │  │(Embeddings)│
│            │  │              │  │            │
└────────────┘  └───────────────┘  └────────────┘
```

### 1.2 System Design Principles

- **Modularity**: Each agent is independent with clear interfaces
- **Real-time Processing**: WebSocket streaming for live market data
- **Deterministic State**: LangGraph ensures reproducible debates
- **Audit Trail**: Every decision is logged and replayable
- **Fault Tolerance**: Graceful degradation if an agent fails
- **Scalability**: Stateless service design allows horizontal scaling
- **Security**: API key authentication, rate limiting, data encryption

### 1.3 Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14 | Server-side rendering, API routes |
| Frontend | React 18 | Component-based UI |
| Frontend | TypeScript | Type-safe development |
| Frontend | Tailwind CSS | Responsive styling |
| Frontend | shadcn/ui | Pre-built components |
| Frontend | TradingView Lightweight Charts | Price charts |
| Backend | FastAPI | High-performance API server |
| Backend | Python 3.11+ | Server logic |
| Orchestration | LangGraph | Multi-agent workflows |
| Database | Supabase (PostgreSQL) | Relational data |
| Vector Database | Supabase pgvector | Semantic search |
| WebSocket | python-socketio | Real-time updates |
| Market Data | CoinGecko / Finnhub / Custom | Price feeds |
| LLM | OpenAI GPT-4 | Agent reasoning |
| Task Queue | Celery (optional) | Background jobs |
| Caching | Redis (optional) | Performance optimization |

---

## 2. FRONTEND ARCHITECTURE

### 2.1 Frontend Technology Stack

```
Next.js 14 (App Router)
├── TypeScript
├── React 18
├── Tailwind CSS
├── shadcn/ui Components
├── TanStack Query (React Query) - Data fetching
├── Zustand - State management
├── Socket.io-client - WebSocket
├── Chart.js / TradingView Charts - Visualization
└── TypeScript-strict mode enabled
```

### 2.2 Frontend Layer Architecture

```
┌─────────────────────────────────────────────┐
│           PRESENTATION LAYER                │
├─────────────────────────────────────────────┤
│ • Page Components (app/dashboard)           │
│ • Layout Components                         │
│ • Modal Components                          │
│ • Chart Components                          │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│            FEATURE LAYER                    │
├──────────────────────────────────────────────┤
│ • Council Chamber Feature                   │
│ • Agent Panel Feature                       │
│ • Voting Interface Feature                  │
│ • Portfolio Feature                         │
│ • Trade Journal Feature                     │
│ • Council Replay Feature                    │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│          INTEGRATION LAYER                  │
├──────────────────────────────────────────────┤
│ • API Client (fetch/axios wrapper)          │
│ • WebSocket Client                          │
│ • State Management (Zustand)                │
│ • React Query Hooks                         │
│ • Custom Hooks                              │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         EXTERNAL SERVICES LAYER             │
├──────────────────────────────────────────────┤
│ • FastAPI Backend                           │
│ • WebSocket Stream                          │
│ • TradingView Data                          │
│ • Analytics Services                        │
└──────────────────────────────────────────────┘
```

### 2.3 Frontend State Management Strategy

```
Zustand Store Architecture:
┌─────────────────────────────────────┐
│    Global State (Zustand)           │
├─────────────────────────────────────┤
│ • UI State (modals, panels)         │
│ • User Authentication               │
│ • Council Session State             │
│ • Real-time Market Data             │
│ • Portfolio Holdings                │
└─────────────────────────────────────┘
        │
        ├──→ Component Local State (useState)
        │    • Form inputs
        │    • UI interactions
        │    • Temporary filters
        │
        ├──→ Server State (React Query)
        │    • API responses
        │    • Cached data
        │    • Automatic revalidation
        │
        └──→ WebSocket State (Socket.io)
             • Live price updates
             • Agent analysis streams
             • Debate messages
```

### 2.4 Page Structure

```
app/
├── (auth)/
│   ├── login/
│   ├── signup/
│   └── forgot-password/
├── (dashboard)/
│   ├── layout.tsx
│   ├── page.tsx (Dashboard Home)
│   ├── council-chamber/
│   │   ├── page.tsx
│   │   └── [sessionId]/
│   ├── agents/
│   │   ├── page.tsx
│   │   └── [agentId]/
│   ├── portfolio/
│   │   └── page.tsx
│   ├── trade-journal/
│   │   └── page.tsx
│   └── council-replay/
│       └── [replayId]/
└── api/
    ├── websocket.ts
    ├── agents/
    ├── trades/
    ├── portfolio/
    └── sessions/
```

### 2.5 Component Hierarchy

```
<App>
├── <Header>
├── <Sidebar>
├── <MainContent>
│   ├── <DashboardView>
│   ├── <CouncilChamberView>
│   ├── <AgentPanelView>
│   ├── <VotingInterfaceView>
│   ├── <PortfolioView>
│   ├── <TradeJournalView>
│   └── <CouncilReplayView>
├── <WebSocketProvider>
├── <ToastProvider>
└── <ThemeProvider>
```

---

## 3. BACKEND ARCHITECTURE

### 3.1 Backend Technology Stack

```
FastAPI (Python 3.11+)
├── Pydantic v2 (data validation)
├── SQLAlchemy 2.0 (ORM)
├── Supabase SDK
├── LangGraph (multi-agent orchestration)
├── LangChain (agent tooling)
├── OpenAI SDK
├── python-socketio (WebSocket)
├── APScheduler (scheduling)
├── Celery (optional, task queues)
├── Redis (optional, caching)
└── Pytest (testing)
```

### 3.2 Backend Service Architecture

```
┌─────────────────────────────────────────────┐
│         FASTAPI APPLICATION                 │
├─────────────────────────────────────────────┤
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │      API ROUTER LAYER                   │ │
│ │  (/api/v1/sessions, /api/v1/agents)     │ │
│ └──────────────┬──────────────────────────┘ │
│                │                            │
│ ┌──────────────▼──────────────────────────┐ │
│ │    SERVICE/BUSINESS LOGIC LAYER         │ │
│ │  (SessionService, AgentService, etc)    │ │
│ └──────────────┬──────────────────────────┘ │
│                │                            │
│ ┌──────────────▼──────────────────────────┐ │
│ │      DATA ACCESS LAYER (DAL)            │ │
│ │   (Repository pattern, SQLAlchemy)      │ │
│ └──────────────┬──────────────────────────┘ │
│                │                            │
│ ┌──────────────▼──────────────────────────┐ │
│ │    ORCHESTRATION LAYER                  │ │
│ │  (LangGraph multi-agent system)         │ │
│ └──────────────┬──────────────────────────┘ │
│                │                            │
│ ┌──────────────▼──────────────────────────┐ │
│ │     EXTERNAL INTEGRATIONS                │ │
│ │  (Market data, LLMs, WebSocket)         │ │
│ └──────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.3 Service Layer Organization

```
services/
├── session_service.py
│   └── Manages council sessions lifecycle
├── council_service.py
│   └── Orchestrates agent debates
├── agent_service.py
│   └── Individual agent management
├── portfolio_service.py
│   └── Portfolio calculations
├── trade_service.py
│   └── Trade execution & tracking
├── market_data_service.py
│   └── Real-time market data
├── memory_service.py
│   └── Agent memory management
├── replay_service.py
│   └── Council replay functionality
└── notification_service.py
    └── WebSocket notifications
```

### 3.4 API Layer Design

```
/api/v1/
├── /sessions
│   ├── POST / (create session)
│   ├── GET / (list sessions)
│   ├── GET /{sessionId} (get session)
│   ├── POST /{sessionId}/start (start council)
│   ├── POST /{sessionId}/pause (pause)
│   ├── POST /{sessionId}/end (end session)
│   └── WS /{sessionId}/stream (WebSocket)
│
├── /agents
│   ├── GET / (list agents)
│   ├── GET /{agentId} (get agent)
│   ├── GET /{agentId}/history (performance)
│   ├── GET /{agentId}/memory (agent memory)
│   └── POST /{agentId}/memory/update (update)
│
├── /council
│   ├── POST /debate (start debate)
│   ├── GET /debate/{debateId} (get debate)
│   ├── POST /vote (cast vote)
│   ├── GET /confidence-score (calculate)
│   └── GET /decision (final decision)
│
├── /trades
│   ├── POST / (execute trade)
│   ├── GET / (list trades)
│   ├── GET /{tradeId} (get trade)
│   └── POST /{tradeId}/close (close trade)
│
├── /portfolio
│   ├── GET / (get portfolio)
│   ├── GET /performance (performance metrics)
│   └── GET /allocation (asset allocation)
│
├── /market
│   ├── GET /prices (current prices)
│   ├── GET /candles/{symbol} (historical)
│   ├── GET /sentiment (sentiment analysis)
│   └── GET /news (news feed)
│
└── /replay
    ├── GET / (list replays)
    ├── GET /{replayId} (get replay)
    └── POST /{replayId}/events (timeline)
```

### 3.5 Background Processing Architecture

```
FastAPI Application
│
├── Immediate (Request/Response)
│   └── API calls, WebSocket messages
│
├── Background Tasks (Celery)
│   ├── Market data collection
│   ├── Agent analysis runs
│   ├── Sentiment analysis
│   ├── Memory embeddings
│   └── Historical data aggregation
│
└── Scheduled Tasks (APScheduler)
    ├── Hourly market updates
    ├── Daily performance reports
    ├── Weekly memory snapshots
    └── Memory index rebuilding
```

---

## 4. LANGGRAPH MULTI-AGENT ARCHITECTURE

### 4.1 LangGraph System Overview

```
LangGraph Multi-Agent System
├── Graph Definition
│   ├── Nodes (5 Agent Nodes + Debate Node)
│   ├── Edges (Routing Logic)
│   ├── Conditional Routing (Risk Validation)
│   └── Message Passing Protocol
│
├── Agent Nodes
│   ├── TechnicalAnalystNode
│   ├── NewsAnalystNode
│   ├── QuantAnalystNode
│   ├── RiskManagerNode (with veto power)
│   └── ExecutionAgentNode
│
├── Workflow Nodes
│   ├── DataPreparationNode
│   ├── DebateCoordinatorNode
│   ├── DecisionMakingNode
│   └── TradeExecutionNode
│
└── Support Components
    ├── State Definition (AgentState)
    ├── Message Structure (AgentMessage)
    ├── Tool Registry
    └── Memory Integration
```

### 4.2 Workflow Architecture

```
START
  │
  ├─→ [Data Preparation]
  │   • Fetch market data
  │   • Retrieve historical data
  │   • Prepare inputs
  │
  ├─→ [Independent Analysis Phase]
  │   ├─→ Technical Analyst (parallel)
  │   ├─→ News Analyst (parallel)
  │   ├─→ Quant Analyst (parallel)
  │   └─→ Merged: All analyses collected
  │
  ├─→ [Debate Coordination]
  │   ├─→ Agent 1 speaks
  │   ├─→ Agent 2 speaks
  │   ├─→ Agent 3 speaks
  │   ├─→ Agents can challenge/agree
  │   └─→ Opinion revision allowed
  │
  ├─→ [Risk Validation]
  │   ├─→ Risk Manager analysis
  │   └─→ Decision node: Risk OK? 
  │       ├─ YES → Continue
  │       └─ NO → VETO (block trade)
  │
  ├─→ [Voting Phase]
  │   ├─→ Each agent votes
  │   ├─→ Weighted voting system
  │   └─→ Calculate consensus
  │
  ├─→ [Final Decision]
  │   ├─→ Execution Agent synthesizes
  │   ├─→ Calculates confidence score
  │   └─→ Outputs: BUY/SELL/HOLD
  │
  ├─→ [Trade Execution]
  │   ├─→ Execute if approved
  │   ├─→ Record in journal
  │   └─→ Broadcast to frontend
  │
  ├─→ [Memory Update]
  │   ├─→ Store debate transcript
  │   ├─→ Generate embeddings
  │   ├─→ Update agent memory
  │   └─→ Update performance metrics
  │
  └─→ END
```

### 4.3 State Definition Architecture

```
AgentState (Shared State for all agents)
├── market_data
│   ├── symbol (string)
│   ├── current_price (float)
│   ├── historical_candles (list)
│   ├── volume (float)
│   └── volatility (float)
│
├── agent_analyses
│   ├── technical_analysis (dict)
│   ├── news_analysis (dict)
│   ├── quant_analysis (dict)
│   └── risk_assessment (dict)
│
├── debate_state
│   ├── messages (list of AgentMessage)
│   ├── round (int)
│   ├── max_rounds (int)
│   └── speaker_order (list)
│
├── votes
│   ├── technical_vote (str: BUY/SELL/HOLD)
│   ├── news_vote (str)
│   ├── quant_vote (str)
│   ├── risk_vote (str)
│   └── execution_vote (str)
│
├── risk_validation
│   ├── risk_score (float 0-100)
│   ├── exposure_level (str: LOW/MEDIUM/HIGH)
│   ├── approved (boolean)
│   └── veto_reason (str or null)
│
├── final_decision
│   ├── action (BUY/SELL/HOLD)
│   ├── confidence_score (float 0-100)
│   ├── position_size (float)
│   ├── reasoning (str)
│   └── timestamp (ISO8601)
│
├── trade_record
│   ├── trade_id (uuid)
│   ├── execution_price (float)
│   ├── execution_time (timestamp)
│   └── status (PENDING/EXECUTED/FAILED)
│
└── session_metadata
    ├── session_id (uuid)
    ├── user_id (uuid)
    ├── start_time (timestamp)
    └── market_conditions (str)
```

### 4.4 Message Structure Architecture

```
AgentMessage:
├── agent_id (str)
├── agent_name (str)
├── timestamp (ISO8601)
├── message_type (ANALYSIS|CHALLENGE|AGREEMENT|REVISION|VOTE|DECISION)
├── content (str) - Natural language response
├── confidence (float 0-1)
├── reasoning (dict)
│   ├── key_points (list)
│   ├── supporting_data (list)
│   └── risk_factors (list)
├── recommendation (dict)
│   ├── action (BUY/SELL/HOLD)
│   ├── score (float)
│   └── target_price (optional)
├── reply_to (uuid or null) - for debates
└── metadata (dict)
    ├── processing_time_ms (int)
    └── tokens_used (int)
```

### 4.5 Orchestration Strategy

```
LangGraph Execution Model:

Single Graph Instance Per Session
│
├── Compiled Graph
│   └── Deterministic execution path
│
├── State Threading
│   └── State flows through each node
│
├── Parallel Execution
│   ├── Independent analyses run in parallel
│   └── Results merged automatically
│
├── Conditional Routing
│   ├── Risk check blocks trade if needed
│   └── Alternative paths for failure modes
│
└── Error Handling
    ├── Agent failure → Continue with other agents
    ├── Risk veto → Report and suggest alternatives
    └── Network failures → Graceful degradation
```

### 4.6 Tool Registry

```
Each Agent Has Access To:

TechnicalAnalyst Tools:
├── calculate_rsi()
├── calculate_macd()
├── calculate_ema()
├── analyze_volume_trend()
├── identify_support_resistance()
└── get_trend_direction()

NewsAnalyst Tools:
├── fetch_crypto_news()
├── analyze_sentiment()
├── check_etf_news()
├── analyze_whale_activity()
└── assess_macro_events()

QuantAnalyst Tools:
├── backtest_strategy()
├── calculate_probability()
├── analyze_correlations()
├── calculate_expected_value()
└── get_historical_patterns()

RiskManager Tools:
├── calculate_volatility()
├── assess_drawdown_risk()
├── calculate_position_size()
├── check_exposure_limits()
└── calculate_var()

ExecutionAgent Tools:
├── aggregate_votes()
├── calculate_weighted_consensus()
├── calculate_confidence_score()
├── execute_trade()
└── record_decision()
```

---

## 5. DATABASE SCHEMA ARCHITECTURE

### 5.1 Database Technology

- **Primary Database**: Supabase (PostgreSQL 15+)
- **Vector Store**: Supabase pgvector extension
- **Caching**: Optional Redis layer
- **Backup**: Automatic Supabase backups

### 5.2 Table Grouping Strategy

```
User Management Tables
├── users
├── user_portfolios
└── user_preferences

Agent Tables
├── agents
├── agent_performance
└── agent_memory

Council Session Tables
├── council_sessions
├── debate_rounds
└── agent_debates

Voting Tables
├── votes
└── vote_history

Trade Tables
├── trades
├── trade_journal
└── position_tracking

Market Data Tables
├── market_events
├── price_snapshots
└── news_feed

Memory/Search Tables
├── agent_memories
├── memory_embeddings
└── semantic_search

Analytics Tables
├── performance_metrics
├── decision_accuracy
└── trade_performance
```

### 5.3 Relationship Diagram (High-Level)

```
users
  ├─→ user_portfolios (1:Many)
  ├─→ council_sessions (1:Many)
  ├─→ votes (1:Many)
  └─→ user_preferences (1:1)

council_sessions
  ├─→ debate_rounds (1:Many)
  ├─→ trades (1:Many)
  ├─→ market_events (Many:Many)
  └─→ council_decisions (1:Many)

debate_rounds
  ├─→ agent_debates (1:Many)
  └─→ votes (1:Many)

agents
  ├─→ agent_performance (1:Many)
  ├─→ agent_memory (1:Many)
  ├─→ agent_debates (1:Many)
  └─→ votes (1:Many)

trades
  ├─→ position_tracking (1:Many)
  ├─→ trade_journal (1:1)
  └─→ decision_accuracy (1:1)

agent_memory
  └─→ memory_embeddings (1:1)

performance_metrics
  └─→ decision_accuracy (1:Many)
```

### 5.4 Key Indexes Strategy

```
High-Priority Indexes:
├── users(id, email) - UNIQUE
├── council_sessions(user_id, created_at DESC)
├── council_sessions(status) - for filtering
├── trades(session_id, created_at DESC)
├── trades(user_id, status)
├── agent_performance(agent_id, created_at DESC)
├── votes(session_id, agent_id)
├── agent_memory(agent_id, created_at DESC)
├── memory_embeddings(agent_id) - for vector search
├── market_events(created_at DESC)
├── decision_accuracy(session_id)
└── position_tracking(trade_id, active)
```

---

## 6. API DESIGN ARCHITECTURE

### 6.1 API Versioning & Structure

```
https://api.council.app/v1/

- Always use /v1/ prefix
- Versioning in URL, not headers
- Support backward compatibility
- Deprecation policy: 6-month notice
```

### 6.2 API Request/Response Pattern

```
Request:
{
  "timestamp": "ISO8601",
  "user_id": "uuid",
  "data": { /* payload */ },
  "metadata": { /* optional */ }
}

Response (Success):
{
  "status": "success",
  "data": { /* payload */ },
  "timestamp": "ISO8601",
  "request_id": "uuid"
}

Response (Error):
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { /* optional */ }
  },
  "timestamp": "ISO8601",
  "request_id": "uuid"
}
```

### 6.3 Authentication & Authorization

```
Authentication:
├── JWT tokens (access + refresh)
├── HttpOnly cookies
├── Token expiration: 1 hour (access), 7 days (refresh)
└── CORS properly configured

Authorization:
├── Role-based access control (RBAC)
├── Session ownership validation
├── Portfolio access restrictions
└── API key rate limiting (if applicable)
```

### 6.4 Real-time API (WebSocket)

```
WebSocket Connection: wss://api.council.app/v1/sessions/{sessionId}/stream

Message Format:
{
  "type": "MARKET_UPDATE|AGENT_ANALYSIS|DEBATE_MESSAGE|VOTE|DECISION|ERROR",
  "payload": { /* type-specific data */ },
  "timestamp": "ISO8601"
}

Connection Lifecycle:
├── Handshake with auth token
├── Subscribe to session stream
├── Receive real-time updates
├── Heartbeat every 30s
└── Graceful disconnect handling
```

### 6.5 API Pagination & Filtering

```
Pagination (List endpoints):
- Default limit: 20
- Max limit: 100
- Offset or cursor-based

Filtering:
- status=ACTIVE|COMPLETED|FAILED
- date_from=ISO8601
- date_to=ISO8601
- symbol=BTC|ETH

Sorting:
- sort_by=created_at|performance|confidence
- order=ASC|DESC
```

---

## 7. FOLDER STRUCTURE ARCHITECTURE

### 7.1 Frontend Folder Structure

```
frontend/
├── public/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   ├── signup/
│   │   │   └── layout.tsx
│   │   │
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── council-chamber/
│   │   │   ├── agents/
│   │   │   ├── portfolio/
│   │   │   ├── trade-journal/
│   │   │   └── council-replay/
│   │   │
│   │   ├── api/
│   │   │   ├── websocket.ts
│   │   │   └── [path].ts
│   │   │
│   │   └── layout.tsx (root)
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainContent.tsx
│   │   │
│   │   ├── council/
│   │   │   ├── CouncilChamber.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   ├── DebateView.tsx
│   │   │   └── VotingPanel.tsx
│   │   │
│   │   ├── portfolio/
│   │   │   ├── PortfolioSummary.tsx
│   │   │   ├── HoldingsList.tsx
│   │   │   └── AllocationChart.tsx
│   │   │
│   │   ├── trading/
│   │   │   ├── TradingChart.tsx
│   │   │   ├── TradeJournal.tsx
│   │   │   └── OrderForm.tsx
│   │   │
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── Loading.tsx
│   │   │
│   │   └── ui/ (shadcn)
│   │
│   ├── hooks/
│   │   ├── useCouncilSession.ts
│   │   ├── useWebSocket.ts
│   │   ├── useMarketData.ts
│   │   ├── usePortfolio.ts
│   │   └── useAuth.ts
│   │
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── sessionStore.ts
│   │   ├── marketStore.ts
│   │   ├── portfolioStore.ts
│   │   └── uiStore.ts
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   ├── auth.ts
│   │   └── storage.ts
│   │
│   ├── types/
│   │   ├── index.ts
│   │   ├── agent.ts
│   │   ├── council.ts
│   │   ├── trade.ts
│   │   └── market.ts
│   │
│   ├── utils/
│   │   ├── formatting.ts
│   │   ├── calculations.ts
│   │   └── validators.ts
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── animations.css
│   │
│   └── config/
│       └── constants.ts
│
├── .env.local
├── .env.example
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── README.md
```

### 7.2 Backend Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py (FastAPI app)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── sessions.py
│   │   │   ├── agents.py
│   │   │   ├── council.py
│   │   │   ├── trades.py
│   │   │   ├── portfolio.py
│   │   │   ├── market.py
│   │   │   ├── memory.py
│   │   │   └── replay.py
│   │   │
│   │   └── websocket.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── council_service.py
│   │   ├── agent_service.py
│   │   ├── trade_service.py
│   │   ├── portfolio_service.py
│   │   ├── market_data_service.py
│   │   ├── memory_service.py
│   │   ├── replay_service.py
│   │   └── notification_service.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── technical_analyst.py
│   │   ├── news_analyst.py
│   │   ├── quant_analyst.py
│   │   ├── risk_manager.py
│   │   ├── execution_agent.py
│   │   ├── tools/
│   │   │   ├── technical_tools.py
│   │   │   ├── news_tools.py
│   │   │   ├── quant_tools.py
│   │   │   └── risk_tools.py
│   │   │
│   │   └── orchestrator.py (LangGraph)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py (SQLAlchemy models)
│   │   ├── users.py
│   │   ├── agents.py
│   │   ├── sessions.py
│   │   ├── trades.py
│   │   ├── memory.py
│   │   └── analytics.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request_schemas.py (Pydantic)
│   │   ├── response_schemas.py
│   │   ├── agent_schemas.py
│   │   └── trade_schemas.py
│   │
│   ├── dao/ (Data Access Objects)
│   │   ├── __init__.py
│   │   ├── base_dao.py
│   │   ├── user_dao.py
│   │   ├── session_dao.py
│   │   ├── trade_dao.py
│   │   ├── agent_dao.py
│   │   └── memory_dao.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   └── helpers.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── error_handler.py
│   │   └── cors.py
│   │
│   └── background_tasks/
│       ├── __init__.py
│       ├── market_data_scheduler.py
│       ├── memory_update_scheduler.py
│       └── analytics_scheduler.py
│
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_services/
│   ├── test_api/
│   └── conftest.py
│
├── migrations/ (Alembic)
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env
├── .env.example
├── requirements.txt
├── pytest.ini
├── main.py (entry point)
└── README.md
```

---

## 8. AGENT COMMUNICATION FLOW ARCHITECTURE

### 8.1 Communication Protocol

```
Communication Layers:

Layer 1: Session Initialization
├── User initiates council session
├── FastAPI endpoint: POST /api/v1/sessions
├── Create session record
└── Initialize LangGraph state

Layer 2: Data Preparation
├── Fetch market data
├── Retrieve historical data
├── Load agent memory
└── Prepare agent inputs

Layer 3: Agent Analysis Phase
├── Parallel execution of 5 agents
├── Each agent processes independently
├── Results collected in state
└── No inter-agent communication yet

Layer 4: Debate Coordination
├── Sequential agent speaking
├── Each agent reads prior messages
├── Agents can challenge/revise
├── Controlled debate flow
└── Messages passed through state

Layer 5: Voting Phase
├── All agents vote simultaneously
├── Votes collected in state
├── Weighted voting applied
└── Consensus calculated

Layer 6: Decision Output
├── Execution agent synthesizes
├── Final recommendation prepared
├── Broadcast to frontend via WebSocket
└── Record in database
```

### 8.2 Message Flow Within LangGraph

```
Market Data
    ↓
[Data Preparation Node]
    ↓
[Parallel Analysis]
├─→ [Technical Analyst Node]
├─→ [News Analyst Node]
├─→ [Quant Analyst Node]
├─→ [Risk Manager Node]
└─→ State merged
    ↓
[Debate Coordinator Node]
├─→ Round 1: Agents speak in order
├─→ Messages added to state
├─→ Check: More debate needed?
│   ├─ YES → Next round
│   └─ NO → Proceed to voting
    ↓
[Risk Validation Node]
├─→ Risk Manager analysis
├─→ Risk exceeds threshold?
│   ├─ YES → VETO (end here)
│   └─ NO → Continue
    ↓
[Voting Node]
├─→ All agents vote
├─→ Weighted voting
└─→ Results to state
    ↓
[Execution Agent Node]
├─→ Synthesize decision
├─→ Calculate confidence score
└─→ Determine action: BUY/SELL/HOLD
    ↓
[Trade Execution Node] (if approved)
├─→ Execute trade
├─→ Record trade
└─→ Update portfolio
    ↓
[Memory Update Node]
├─→ Store debate transcript
├─→ Generate embeddings
├─→ Update agent memory
└─→ Update performance metrics
    ↓
Output to Frontend (WebSocket)
```

### 8.3 Agent-to-Agent Communication Rules

```
Direct Communication:
❌ Agents do NOT call each other directly
❌ No agent-to-agent message passing
❌ No private channels

Indirect Communication (via State):
✓ All agents write to shared state
✓ Each agent reads from state
✓ Debate coordinator manages sequencing
✓ Messages are immutable once added

Debate Rules:
✓ Agent speaks based on turn order
✓ Agent reads all prior messages
✓ Agent can explicitly challenge (message.type = CHALLENGE)
✓ Agent can agree (message.type = AGREEMENT)
✓ Agent can revise opinion (message.type = REVISION)
✓ Speaker order preserved to prevent chaos
```

### 8.4 External Communication (to Frontend)

```
Backend → Frontend:

WebSocket Events (Real-time):
├── agent_started: { agent_id, name, timestamp }
├── analysis_complete: { agent_id, analysis_data }
├── debate_message: { agent_id, message, round }
├── vote_cast: { agent_id, vote }
├── risk_assessment: { score, approved }
├── final_decision: { action, confidence_score, reasoning }
├── trade_executed: { trade_id, symbol, quantity, price }
├── memory_updated: { agent_id, update_count }
└── session_complete: { session_id, results }

REST API (Batch):
├── GET /sessions/{sessionId} → Full session data
├── GET /sessions/{sessionId}/decisions → Decision history
├── GET /agents/{agentId}/memory → Agent memory
└── GET /replay/{replayId} → Complete replay data
```

---

## 9. EVENT FLOW ARCHITECTURE

### 9.1 Complete Event Timeline

```
User Session Lifecycle:

1. SESSION CREATION
   Event: session_created
   Data: { user_id, session_id, timestamp, market_conditions }
   Source: User clicks "Start Council"
   Target: Database + WebSocket broadcast

2. DATA FETCH
   Event: market_data_loaded
   Data: { symbol, price, volume, volatility, news_count }
   Source: Market data service
   Target: State preparation

3. ANALYSIS REQUESTED
   Event: analysis_started
   Data: { session_id, task_id }
   Source: Council service
   Target: LangGraph orchestrator

4. AGENT ANALYSIS IN PROGRESS
   Event: agent_analyzing
   Data: { agent_id, agent_name, status, progress }
   Source: Individual agent nodes
   Target: WebSocket stream

5. ANALYSIS COMPLETE
   Event: agent_analysis_done
   Data: { agent_id, analysis_object, confidence }
   Source: Agent nodes
   Target: State + WebSocket

6. DEBATE STARTED
   Event: debate_started
   Data: { session_id, round, total_rounds }
   Source: Debate coordinator
   Target: WebSocket broadcast

7. AGENT SPEAKING (repeated per agent)
   Event: agent_speaking
   Data: { agent_id, message, round, opinion }
   Source: Agent during debate
   Target: WebSocket + State

8. DEBATE ENDED
   Event: debate_ended
   Data: { session_id, total_rounds, consensus_level }
   Source: Debate coordinator
   Target: WebSocket

9. RISK ASSESSMENT
   Event: risk_assessment_started
   Data: { session_id, proposed_action }
   Source: Risk manager node
   Target: WebSocket

10. RISK DECISION
    Event: risk_decision_made
    Data: { approved: bool, risk_score, veto_reason? }
    Source: Risk manager
    Target: State + WebSocket

11. VOTING STARTED
    Event: voting_started
    Data: { session_id, voting_agents }
    Source: Voting coordinator
    Target: WebSocket

12. VOTE CAST (repeated per agent)
    Event: vote_cast
    Data: { agent_id, vote, reasoning }
    Source: Voting agent
    Target: WebSocket + State

13. CONFIDENCE SCORE CALCULATED
    Event: confidence_calculated
    Data: { score: 0-100, factors: {...} }
    Source: Execution agent
    Target: WebSocket

14. FINAL DECISION
    Event: final_decision_made
    Data: { action: BUY|SELL|HOLD, confidence, reasoning }
    Source: Execution agent
    Target: WebSocket + Database

15. TRADE EXECUTION (if approved)
    Event: trade_executed
    Data: { trade_id, symbol, quantity, price, timestamp }
    Source: Trade service
    Target: Database + Portfolio + WebSocket

16. MEMORY UPDATE
    Event: memory_updated
    Data: { agents_updated, embeddings_generated }
    Source: Memory service
    Target: Database

17. SESSION ENDED
    Event: session_complete
    Data: { session_id, duration, decisions_count, trades_count }
    Source: Session service
    Target: Database + WebSocket + Analytics
```

### 9.2 Event Routing Architecture

```
Event Bus (Internal):

Market Data Service
    ↓
[market_data_loaded]
    ↓
    ├─→ State Update
    ├─→ WebSocket Broadcast
    └─→ Cache Update

Agent Nodes (LangGraph)
    ↓
[agent_analysis_done]
    ↓
    ├─→ State Merge
    ├─→ WebSocket Update
    └─→ Next Node Trigger

Debate Coordinator
    ↓
[agent_speaking / debate_message]
    ↓
    ├─→ State Append
    ├─→ WebSocket Broadcast
    └─→ Trigger Next Speaker

Risk Manager
    ↓
[risk_assessment / risk_decision]
    ↓
    ├─→ State Update
    ├─→ WebSocket Update
    └─→ Conditional Routing

Trade Service
    ↓
[trade_executed]
    ↓
    ├─→ Database Insert
    ├─→ Portfolio Update
    ├─→ WebSocket Broadcast
    └─→ Journal Record
```

### 9.3 Error Event Handling

```
Error Events:

1. agent_error
   └─→ { agent_id, error_code, message, recoverable }
       → Continue with other agents
       → Mark agent as having error
       → Reduce agent confidence weight

2. data_fetch_error
   └─→ { error_code, retry_count, next_retry }
       → Notify user
       → Offer retry option
       → Fall back to cached data

3. risk_veto
   └─→ { reason, risk_score, recommended_action }
       → Stop trade execution
       → Suggest alternatives
       → Log for audit trail

4. execution_failed
   └─→ { trade_id, error_code, message }
       → Rollback portfolio changes
       → Alert user
       → Store for retry
```

---

## 10. STATE MANAGEMENT STRATEGY

### 10.1 State Layers

```
Three-Layer State Architecture:

┌──────────────────────────────────┐
│   LANGRAPH STATE (Backend)        │
│   • Shared across agent nodes     │
│   • Deterministic & traceable     │
│   • Single source of truth        │
│   • Persisted to database         │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│   ZUSTAND STORE (Frontend)        │
│   • User auth                     │
│   • UI state (modals, panels)     │
│   • Real-time updates             │
│   • Local preferences             │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│   REACT QUERY (Frontend)          │
│   • Server cache                  │
│   • API responses                 │
│   • Automatic revalidation        │
│   • Stale-while-revalidate        │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│   COMPONENT STATE (Frontend)      │
│   • Form inputs                   │
│   • Local UI interactions         │
│   • Temporary filters             │
│   • Animation states              │
└──────────────────────────────────┘
```

### 10.2 Data Flow Diagram

```
User Interaction (Frontend)
    ↓
[React Component] (local state)
    ↓
[Zustand Store] (global state)
    ↓
[API Call] (HTTP/REST)
    ↓
[FastAPI] (backend)
    ↓
[Service Layer] (business logic)
    ↓
[LangGraph State] (agent state)
    ↓
[Agent Nodes] (analysis & debate)
    ↓
[State Update] (merged results)
    ↓
[Database Persist] (PostgreSQL)
    ↓
[WebSocket Emit] (real-time)
    ↓
[React Query Cache] (frontend)
    ↓
[Zustand Store Update] (frontend)
    ↓
[Component Re-render]
    ↓
UI Updated
```

### 10.3 Frontend State Management (Zustand)

```
Store Structure:

authStore:
├── user (User | null)
├── token (string | null)
├── isAuthenticated (boolean)
├── login(email, password)
├── logout()
└── refreshToken()

sessionStore:
├── currentSession (Session | null)
├── sessions (Session[])
├── createSession(data)
├── updateSession(sessionId, data)
├── endSession(sessionId)
└── getSession(sessionId)

marketStore:
├── prices (Map<symbol, Price>)
├── news (NewsItem[])
├── sentiment (SentimentData)
├── updatePrice(symbol, price)
├── updateNews(news[])
└── subscribe(symbol)

portfolioStore:
├── holdings (Holding[])
├── totalValue (number)
├── allocation (AllocationData)
├── updateHolding(symbol, quantity)
├── calculateAllocation()
└── syncWithServer()

uiStore:
├── modals (Map<string, boolean>)
├── panels (Map<string, boolean>)
├── theme (light | dark)
├── openModal(id)
├── closeModal(id)
└── togglePanel(id)
```

### 10.4 Backend State Management (LangGraph)

```
Session-Scoped State:

Per Session Instance:
├── session_id (uuid)
├── user_id (uuid)
├── market_data (current snapshot)
├── agent_analyses (accumulated)
├── debate_messages (ordered list)
├── votes (collected)
├── final_decision (result)
├── trade_record (execution data)
└── metadata (timing, conditions)

State Immutability Rules:
✓ State never mutated in-place
✓ New state created at each node
✓ Previous states retained for replay
✓ Fully deterministic execution
✓ Can be saved & restored

State Persistence:
├── Save to database after completion
├── Encrypt sensitive data
├── Index for quick retrieval
├── Enable replay functionality
└── Audit trail complete
```

### 10.5 Real-time Synchronization

```
WebSocket State Sync:

┌─────────────┐
│  Backend    │ Updates state from LangGraph
│  (State)    │
└──────┬──────┘
       │
       ├─→ Emit via WebSocket
       │
┌──────▼──────┐
│ Frontend    │ Receives & updates Zustand
│ (WebSocket) │
└──────┬──────┘
       │
       ├─→ Update React Query cache
       ├─→ Update Zustand store
       ├─→ Trigger component re-render
       │
┌──────▼──────┐
│ Component   │ Displays updated state
│ (UI)        │
└─────────────┘

Conflict Resolution:
├── Timestamp-based validation
├── Server state as source of truth
├── Client-side optimistic updates with rollback
└── Retry logic for failed syncs
```

### 10.6 Caching Strategy

```
Frontend Caching:

React Query:
├── Queries: staleTime = 5 minutes
├── Queries: cacheTime = 10 minutes
├── Background revalidation enabled
├── Automatic retry on failure
└── Manual invalidation on actions

Browser Cache:
├── Images: 1 year
├── CSS/JS: 1 week
├── API responses: Cache-Control headers
└── Service worker for offline support

Backend Caching (optional Redis):
├── Market data: 1 minute
├── Agent memory: 1 hour
├── Portfolio snapshots: 5 minutes
├── User sessions: TTL based
└── Invalidation on updates
```

---

## 11. PRODUCTION READINESS CHECKLIST

- [ ] Error handling (all layers)
- [ ] Logging & monitoring
- [ ] Rate limiting
- [ ] Input validation
- [ ] CORS configuration
- [ ] Database migrations
- [ ] Performance optimization
- [ ] Security (auth, encryption)
- [ ] Testing (unit, integration, e2e)
- [ ] CI/CD pipeline
- [ ] Documentation
- [ ] Disaster recovery
- [ ] Backup strategy
- [ ] Analytics tracking

---

## 12. DEPLOYMENT ARCHITECTURE

```
Development → Staging → Production

Frontend:
├── Vercel (Next.js hosting)
├── GitHub integration
├── Preview deployments
└── Automatic rollback

Backend:
├── Docker containerization
├── AWS ECS / Railway / Heroku
├── Load balancing
├── Auto-scaling
└── Health checks

Database:
├── Supabase managed PostgreSQL
├── Automated backups
├── Read replicas
└── Point-in-time recovery

Monitoring:
├── Application: Sentry / DataDog
├── Infrastructure: CloudWatch / Prometheus
├── Database: Supabase dashboard
└── Frontend: Vercel analytics
```

---

## STAGE 1 COMPLETE

**Architecture documentation generated for all 10 required sections:**

✅ 1. System architecture (high-level topology, principles, tech stack)
✅ 2. Frontend architecture (layering, state management, components)
✅ 3. Backend architecture (service design, API layer)
✅ 4. LangGraph architecture (agent workflow, state definitions)
✅ 5. Database schema (table grouping, relationships, indexes)
✅ 6. API design (versioning, patterns, WebSocket, pagination)
✅ 7. Folder structure (frontend & backend organization)
✅ 8. Agent communication flow (protocol, message flow, rules)
✅ 9. Event flow (complete timeline, routing, error handling)
✅ 10. State management strategy (layers, data flow, synchronization, caching)

**This documentation provides a production-grade blueprint for building Council.**

Ready to proceed to **STAGE 2 — UI/UX SYSTEM**?
