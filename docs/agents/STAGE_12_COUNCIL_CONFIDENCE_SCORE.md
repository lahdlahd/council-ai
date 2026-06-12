# STAGE 12 — COUNCIL CONFIDENCE SCORE
## Council: Explainable Multi-Factor Decision Confidence

**Status**: Complete Council Confidence Score  
**Implementation**: Multi-Factor Linear Weighting  
**Version**: 1.0  
**Date**: June 12, 2026

---

## 1. THE SCORING FORMULA

The Council Confidence Score is a number between `0` and `100` that represents the investment committee's collective confidence in a final trading decision. It is designed to be highly conservative and explainable.

The score combines five factors using a weighted sum:

$$\text{Confidence Score} = w_1 \cdot \text{Agreement} + w_2 \cdot \text{RiskFactor} + w_3 \cdot \text{VolatilityFactor} + w_4 \cdot \text{SentimentStability} + w_5 \cdot \text{AccuracyFactor}$$

### 1.1 Weighting Strategy and Rationale

| Weight ($w_i$) | Factor | Rationale |
| :--- | :--- | :--- |
| **0.40 (40%)** | **Agent Agreement** | Considers how aligned the committee is. If there is a unanimous agreement (100% agreement raw), the contribution is 40%. A divided committee lowers confidence significantly. |
| **0.20 (20%)** | **Risk Factor** | Derived as $100.0 - \text{RiskScore}$. Decision confidence must be low for high-risk trades. A critical risk score drops confidence. |
| **0.15 (15%)** | **Market Volatility** | Derived as $(1.0 - \text{Volatility}) \cdot 100.0$. In highly volatile markets, trading carries wider spreads and higher slippage risk; confidence is penalized. |
| **0.15 (15%)** | **Sentiment Stability** | Measures how steady news and analyst opinions were during the debate. A high-variance debate is penalized. |
| **0.10 (10%)** | **Historical Accuracy** | Measures the historic accuracy of the active agents (fetchable from Supabase or configured fallbacks). |

---

## 2. DETAIL OF INPUTS & CALCULATIONS

### 2.1 Sentiment Stability Math
If the News Analyst changed recommendations or sentiment during the debate (e.g., from BUY in Round 1 to HOLD in Round 2 and SELL in Round 3), the debate thread has high variance. 
The system tracks all recommendations made by the News Analyst in `state["messages"]`, maps them to numerical values (`BUY = 1.0`, `HOLD = 0.0`, `SELL = -1.0`), and calculates the standard deviation ($\sigma$).

$$\text{SentimentStability} = \text{NewsAnalysis.confidence} \cdot \max(0.0, 1.0 - \sigma)$$

- If the analyst never changes their recommendation: $\sigma = 0.0 \implies \text{Stability} = \text{NewsAnalysis.confidence}$.
- If the stance shifts frequently (e.g. from `BUY` to `SELL`): $\sigma$ is high, applying a penalty scale that reduces the stability factor significantly.

### 2.2 Historical Accuracy Fetching
The node queries the Supabase `agents` table to determine the actual performance track record of the analysts:

```sql
SELECT role, success_count, total_analyses 
FROM agents 
WHERE is_active = true;
```

For each agent, the historical accuracy is calculated as:
$$\text{Accuracy} = \frac{\text{success\_count}}{\text{total\_analyses}} \cdot 100$$

If Supabase is offline or credentials are not configured, the node falls back to historical baseline constants:
- **Technical Analyst**: 72.0%
- **Quant Analyst**: 70.0%
- **News Analyst**: 65.0%

---

## 3. EXPLAINABILITY JSON BREAKDOWN

The final score is stored in the database `council_decisions` under `confidence_factors` and returned inside the `FinalDecision` and `ExecutionSynthesis` Pydantic models. It has this explainable structure:

```json
{
  "raw_scores": {
    "agent_agreement": 100.0,
    "risk_score_factor": 70.0,
    "volatility_factor": 80.0,
    "sentiment_stability": 90.0,
    "historical_accuracy": 69.0
  },
  "weighted_contributions": {
    "agent_agreement": 40.0,
    "risk_score_factor": 14.0,
    "volatility_factor": 12.0,
    "sentiment_stability": 13.5,
    "historical_accuracy": 6.9
  },
  "total_score": 86.4
}
```

This breakdown is injected into the prompt of the Execution Agent (acting as Chairman of the AI Investment Committee) so that the LLM generates a natural language synthesis explaining how these specific factors drove the decision confidence.

---

## STAGE 12 COMPLETE
✅ 1. Formula integrating agreement, accuracy, volatility, risk, and sentiment stability implemented.  
✅ 2. Explainability dictionary structure added to Pydantic models.  
✅ 3. Sentiment stability standard deviation decay implemented.  
✅ 4. Supabase DB client connectivity for real-time historical accuracy implemented.  
✅ 5. Verification tests written and verified.  
