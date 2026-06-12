# Stage 15 — Hackathon Demo Mode Documentation

This document describes the design, API contracts, frontend state transitions, and database integrations for **Stage 15 — Hackathon Demo Mode** of Council.

---

## 1. Architectural Overview

The **Hackathon Demo Mode** connects the Bloomberg-style user interface directly to the FastAPI multi-agent debate coordination backend. When a user selects a market catalyst scenario (e.g. BTC ETF approvals or ETH smart contract exploits), it triggers a live execution session.

### Core Architecture Flow
```
[Next.js UI Demo Panel] 
         │ 
         ▼ (POST /api/replay/demo/run)
[FastAPI Replay Router]
         │
         ▼ (execute run_demo_session)
[LangGraph Agent Graph] ──(Inject Catalyst Context)──► [Consensus Debate Engine]
         │                                                      │
         ▼ (Update Session & Timelines)                         ▼
[Local Fallback JSON DB / Supabase] ◄───────────────────────────┘
         │
         ▼ (Return session_id)
[Next.js UI] ──(Auto-play Debate sequentially)──► [Live Screen Render]
```

---

## 2. API Endpoint Design

### 2.1 Demo Run Trigger
- **Path**: `POST /api/replay/demo/run`
- **Request Body**:
  ```json
  {
    "scenario": "rally" | "crash"
  }
  ```
- **Description**: Generates a new chronological timeline containing all debate message transcripts, voting logs, risk checks, and execution orders.
- **Return Value**:
  ```json
  {
    "status": "success",
    "session_id": "ef826057-6d8b-42ed-82dc-b24b28871e8c",
    "message": "Demo session successfully generated for scenario: rally."
  }
  ```

### 2.2 Trade Completion Integration
- **Path**: `POST /api/replay/{session_id}/mock-complete`
- **Request Body**:
  ```json
  {
    "exit_price": 45500.0
  }
  ```
- **Description**: Exits the active position for the session on the backend. Computes realized return P&L and updates the trade ledger state.
- **Return Value**:
  ```json
  {
    "status": "success",
    "message": "Simulated trade exit processed at $45500.00."
  }
  ```

---

## 3. Frontend Orchestration

In [page.tsx](file:///c:/Users/USER/OneDrive/Desktop/councilB/frontend/src/app/page.tsx), clicking a catalyst button triggers `triggerSimulation(scenario)`:
1. Dispatches the catalyst scenario request to the backend.
2. Clears the Chamber's chat transcript and resets playback indexes.
3. Retrieves the new `session_id` and refreshes the replay lists sidebar.
4. Invokes `loadTimeline(session_id)` to load the market data, positions, and executive breakdown.
5. Initiates sequential play animation (`isPlaying = true`), rendering the transcript bubble-by-bubble.
6. Once the BUY order is filled and in the ledger, the user can click **Simulate Target Hit** which calls `/api/replay/{session_id}/mock-complete`, updating the realized P&L and synchronizing the state permanently.

---

## 4. Verification Results

### Backend API Tests
We verified the endpoints via [test_hackathon_demo.py](file:///c:/Users/USER/OneDrive/Desktop/councilB/scratch/test_hackathon_demo.py) using the FastAPI `TestClient`:
- **Rally Execution**: Verified BTC is recommended for a `BUY` with `91.25%` confidence, risk manager approved, and trade target exit realizes `+$2,666.65` P&L.
- **Crash Execution**: Verified ETH triggers a Risk Manager `VETO` with a critical risk score of `82.0` and position sizing is blocked to `0.0`.
- **Result**: ✅ Passed all assertions.

### Next.js Compile Verification
- Verified compile correctness using [test_frontend_build.py](file:///c:/Users/USER/OneDrive/Desktop/councilB/scratch/test_frontend_build.py).
- **Result**: ✅ Compile succeeded with exit code 0.
