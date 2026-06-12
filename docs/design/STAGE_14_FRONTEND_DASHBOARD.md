# Stage 14 — Frontend Dashboard Documentation

This document describes the design, layout, state management, API integration, and simulation engine for the **Stage 14 — Frontend Dashboard** of Council.

---

## 1. Overview & UI System Architecture

The frontend dashboard is implemented in [page.tsx](file:///c:/Users/USER/OneDrive/Desktop/councilB/frontend/src/app/page.tsx) as a single-page application under the Next.js App Router. It is designed to look like a high-end Bloomberg/BlackRock terminal, using custom styles in [globals.css](file:///c:/Users/USER/OneDrive/Desktop/councilB/frontend/src/app/globals.css).

### Design Tokens & Color Palette
- **Primary background**: `#111315` (matte deep black)
- **Secondary card background**: `#1B1F24` (cool terminal grey)
- **Accent color**: `#D4A24C` (institutional gold)
- **Success color**: `#1D9B72` (emerald green)
- **Danger color**: `#A84747` (muted crimson)
- **Border color**: `#2C323B` (slate terminal border)

---

## 2. Panels and Components Layout

The dashboard is structured as a responsive 12-column grid system featuring 8 distinct sections:

1. **Header Panel**: Contains the "COUNCIL" brand title, live API connection status indicator, total portfolio Net Asset Value (NAV: `$100,827.40`), and win rate metrics (`66.7%`).
2. **Market Overview Panel**: Shows the selected symbol, current price ticker, volatility, 24h trend, and a high-fidelity SVG candle chart representing asset price trends. Includes interactive buttons to switch active tracking between BTC and ETH.
3. **Portfolio Summary Panel**: Tracks starting capital, realized/unrealized P&L, active position details (quantity, entry, targets, and stop-losses), and features a button to simulate hitting targets during demo runs.
4. **Committee Chamber Panel**: Displays a scrolling live transcript of agent speech bubbles (initial analyses, challenges, agreements, and revisions) with distinct, color-coded borders indicating speech intent.
5. **Voting Tally Panel**: Renders vote direction (`BUY`/`SELL`/`HOLD`), individual agent weight multipliers, and confidence percentages, alongside the final committee proposed action.
6. **Confidence Gauge Panel**: Highlights the 0-100 Council Confidence Score in a custom circular radial SVG gauge, accompanied by the executive summary and a detailed linear-weighted multi-factor breakdown.
7. **Agent Panel**: Displays a directory of active committee members, including their system model configurations, role tags, and historical success rates.
8. **Tabs Panel**:
   - **Replays**: Lists historical sessions fetched from the FastAPI backend. Clicking a replay loads the entire timeline dynamically.
   - **Journal**: Records completed trades and valuable lessons learned.
   - **Demo**: Hosts triggers to launch live mock catalysts (ETF approvals, smart contract exploits) simulating complete multi-round agent interactions.

---

## 3. Client-Side State Machine

The dashboard tracks the state of the investment committee debate and trade execution through these key variables:

- `selectedAsset` (`"BTC" | "ETH"`): Tracks the currently inspected asset.
- `replays` (`ReplaySummary[]`): A list of available session summaries.
- `activeSessionId` (`string | null`): The ID of the currently selected or running session.
- `marketState` (`any`): Real-time metrics of the active symbol (high/low price, volume, volatility).
- `initialOpinions` (`Record<string, any>`): Initial opinions issued by Technical, Quant, and News analysts.
- `debateTranscript` (`AgentMessage[]`): Messages currently rendered in the Chamber's chat transcript.
- `votingTally` (`any`): The aggregated vote direction and individual weights.
- `vetoVerification` (`any`): Risk assessment score and veto approval status.
- `executionDecision` (`any`): Chairman's final synthesized action, reasoning, and position sizes.
- `tradeResult` (`any`): Trade execution parameters (status, entry price, P&L, notes).
- `isPlaying` (`boolean`): Tracks whether a debate replay is currently animating step-by-step.
- `isSimulating` (`boolean`): Tracks if an interactive catalyst simulation is active.

---

## 4. API Integration & Offline Fallback

The client communicates with the FastAPI backend through native `fetch` operations to:
- `GET http://localhost:8000/api/replay`: Retrieves summaries of all committee runs.
- `GET http://localhost:8000/api/replay/{session_id}`: Fetches the detailed multi-step timeline for a specific session.

### Automatic Offline Fallback
To ensure maximum availability during offline hackathon demonstrations, [page.tsx](file:///c:/Users/USER/OneDrive/Desktop/councilB/frontend/src/app/page.tsx) automatically captures network errors and activates local static mock fallbacks. The local mocks perfectly mirror the schema of the FastAPI replay database:
- Preloads two complete historical sessions (unanimous BUY on BTC, vetoed HOLD on ETH).
- Supports fully local debate playback and simulation animations without requiring a live database or API connection.
