"""
Execution Analyst Agent Node
LangGraph node implementation for trade synthesis and execution decision

Responsibilities:
- Gather all agent outputs (Technical, News, Quant, Risk)
- Calculate weighted consensus
- Calculate Council Confidence Score
- Enforce Risk Manager veto
- Determine final action (BUY, SELL, HOLD)
- Produce final decision with recommended position sizing, target price, and stop loss
- Generate unified reasoning via LLM synthesis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.agents.schemas import (
    ExecutionSynthesis,
    FinalDecision,
    PositionSize,
    MarketData,
    TechnicalAnalysis,
    NewsAnalysis,
    QuantAnalysis,
    RiskAssessment
)

logger = logging.getLogger(__name__)


class ExecutionAgentNode:
    """
    LangGraph node for trade decision execution synthesis.
    
    Synthesizes analyses from all committee members into a final investment committee decision.
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.5):
        """
        Initialize the Execution Agent Node.
        
        Args:
            model_name: OpenAI model to use
            temperature: LLM temperature (0.5 for balanced synthesis and clarity)
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1500
        )
        
        # Committee weights
        self.weights = {
            "technical": 1.2,
            "quant": 1.1,
            "news": 1.0
        }
        
        # Fallback accuracies for agents
        self.accuracies = {
            "technical": 72.0,
            "quant": 70.0,
            "news": 65.0
        }
        
    def _fetch_historical_accuracies(self) -> Dict[str, float]:
        """
        Attempts to fetch historical accuracies from Supabase database.
        Falls back to configured default accuracies if Supabase is offline
        or if credentials are not configured.
        """
        import os
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        accuracies = self.accuracies.copy()
        
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                supabase_client = create_client(supabase_url, supabase_key)
                
                # Fetch performance metrics from agents table
                res = supabase_client.table("agents").select("role", "success_count", "total_analyses").eq("is_active", True).execute()
                if res.data:
                    for row in res.data:
                        role = row.get("role", "").lower()
                        success = row.get("success_count", 0)
                        total = row.get("total_analyses", 0)
                        if total > 0:
                            accuracy = (success / total) * 100.0
                            if "technical" in role:
                                accuracies["technical"] = round(accuracy, 2)
                            elif "quant" in role:
                                accuracies["quant"] = round(accuracy, 2)
                            elif "news" in role:
                                accuracies["news"] = round(accuracy, 2)
                    logger.info("Successfully fetched agent historical accuracies from Supabase.")
            except Exception as e:
                logger.warning(f"Failed to fetch historical accuracies from Supabase: {e}. Using configured default values.")
                
        return accuracies

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize agent analyses and make a final trading decision.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with execution_synthesis and final_decision
        """
        try:
            logger.info("Execution Agent starting synthesis")
            
            # Extract market data
            market_data: MarketData = state.get("market_data")
            if not market_data:
                raise ValueError("market_data not found in state")
                
            # Extract analyses
            tech_analysis: Optional[TechnicalAnalysis] = state.get("technical_analysis")
            news_analysis: Optional[NewsAnalysis] = state.get("news_analysis")
            quant_analysis: Optional[QuantAnalysis] = state.get("quant_analysis")
            risk_assessment: Optional[RiskAssessment] = state.get("risk_assessment")
            
            if not all([tech_analysis, news_analysis, quant_analysis, risk_assessment]):
                raise ValueError("Missing one or more analyst outputs in the state")
            
            # 1. Determine base consensus action from weighted analyst recommendations
            consensus_action, weighted_consensus = self._calculate_weighted_consensus(
                tech_analysis=tech_analysis,
                news_analysis=news_analysis,
                quant_analysis=quant_analysis
            )
            
            # 2. Calculate Council Confidence Score
            confidence_score, confidence_factors = self._calculate_confidence_score(
                consensus_action=consensus_action,
                weighted_consensus=weighted_consensus,
                volatility=market_data.volatility,
                risk_assessment=risk_assessment,
                news_analysis=news_analysis,
                messages=state.get("messages", [])
            )
            
            # 3. Check and enforce Risk Manager VETO
            veto_active = not risk_assessment.approved
            
            final_action = consensus_action
            if veto_active:
                logger.warning(f"Risk Manager VETO active! Overriding final action to HOLD. Reason: {risk_assessment.veto_reason}")
                final_action = "HOLD"
                
            # 4. Calculate Position Sizing
            position_size = self._calculate_position_size(
                action=final_action,
                market_data=market_data,
                risk_assessment=risk_assessment,
                confidence_score=confidence_score
            )
            
            # 5. Synthesize reasoning using the LLM
            synthesis = self._synthesize_reasoning(
                symbol=market_data.symbol,
                current_price=market_data.current_price,
                tech=tech_analysis,
                news=news_analysis,
                quant=quant_analysis,
                risk=risk_assessment,
                final_action=final_action,
                weighted_consensus=weighted_consensus,
                confidence_score=confidence_score,
                confidence_factors=confidence_factors,
                veto_active=veto_active
            )
            
            # Update state with Execution Synthesis
            state["execution_synthesis"] = ExecutionSynthesis(
                aggregated_recommendation=final_action,
                weighted_consensus=weighted_consensus,
                confidence_score=confidence_score,
                confidence_factors=confidence_factors,
                reasoning=synthesis["reasoning"],
                key_factors=synthesis["key_factors"]
            )
            
            # Update state with Final Decision
            state["final_decision"] = FinalDecision(
                action=final_action,
                confidence_score=confidence_score,
                confidence_factors=confidence_factors,
                position_size=position_size,
                reasoning=synthesis["reasoning"],
                key_factors=synthesis["key_factors"],
                timestamp=datetime.utcnow()
            )
            
            # Update proposed_action (which is needed by other steps or backend)
            state["proposed_action"] = final_action
            
            # Place live/mock order on Bitget if action is BUY or SELL
            if final_action in ["BUY", "SELL"]:
                try:
                    from app.api.services.bitget_service import BitgetService
                    bitget = BitgetService()
                    order_res = bitget.place_spot_order(
                        symbol=market_data.symbol,
                        side=final_action,
                        quantity=position_size.quantity,
                        price=market_data.current_price
                    )
                    state["bitget_order"] = order_res
                    logger.info(f"Bitget execution processed: {order_res.get('notes')}")
                except Exception as bitget_err:
                    logger.error(f"Bitget execution exception: {bitget_err}")
                    state["bitget_order"] = {
                        "success": False,
                        "error": str(bitget_err),
                        "notes": f"Failed to execute Bitget order: {bitget_err}"
                    }
            
            logger.info(
                f"Execution synthesis complete: Final Action = {final_action}, "
                f"Confidence = {confidence_score:.1f}%, Position % = {position_size.percentage_of_portfolio:.1f}%"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Execution Agent error: {str(e)}", exc_info=True)
            state["error_log"].append(f"Execution Agent: {str(e)}")
            
            # Fallback to safe HOLD decision
            current_price = state.get("market_data", {}).current_price if state.get("market_data") else 1.0
            fallback_position = PositionSize(
                percentage_of_portfolio=0.0,
                quantity=0.0,
                entry_price=current_price
            )
            
            state["execution_synthesis"] = ExecutionSynthesis(
                aggregated_recommendation="HOLD",
                weighted_consensus=0.0,
                confidence_score=0.0,
                confidence_factors={},
                reasoning=f"Execution Agent error fallback: {str(e)}",
                key_factors=["Execution error"]
            )
            
            state["final_decision"] = FinalDecision(
                action="HOLD",
                confidence_score=0.0,
                confidence_factors={},
                position_size=fallback_position,
                reasoning=f"Execution Agent error fallback: {str(e)}",
                key_factors=["Execution error"],
                timestamp=datetime.utcnow()
            )
            
            state["proposed_action"] = "HOLD"
            return state

    def _calculate_weighted_consensus(
        self,
        tech_analysis: TechnicalAnalysis,
        news_analysis: NewsAnalysis,
        quant_analysis: QuantAnalysis
    ) -> tuple[str, float]:
        """
        Calculate weighted consensus from committee member recommendations.
        
        BUY = +1, SELL = -1, HOLD = 0
        Weights: Technical (1.2), Quant (1.1), News (1.0)
        
        Returns:
            Tuple of (consensus_action, weighted_consensus_percentage)
        """
        rec_to_val = {"BUY": 1.0, "SELL": -1.0, "HOLD": 0.0}
        
        tech_val = rec_to_val.get(tech_analysis.recommendation, 0.0)
        news_val = rec_to_val.get(news_analysis.recommendation, 0.0)
        quant_val = rec_to_val.get(quant_analysis.recommendation, 0.0)
        
        # Calculate weighted average
        weighted_sum = (
            tech_val * self.weights["technical"] +
            news_val * self.weights["news"] +
            quant_val * self.weights["quant"]
        )
        total_weight = sum(self.weights.values())
        weighted_average = weighted_sum / total_weight
        
        # Determine consensus action
        if weighted_average >= 0.25:
            consensus_action = "BUY"
        elif weighted_average <= -0.25:
            consensus_action = "SELL"
        else:
            consensus_action = "HOLD"
            
        # Calculate agreement percentage (weighted_consensus)
        # Agreement score for each analyst:
        # Match = 1.0, HOLD vs BUY/SELL = 0.5, Opposite = 0.0, BUY/SELL vs HOLD = 0.0
        agreement_scores = []
        for name, val, analysis in [
            ("technical", tech_val, tech_analysis),
            ("news", news_val, news_analysis),
            ("quant", quant_val, quant_analysis)
        ]:
            rec = analysis.recommendation
            if rec == consensus_action:
                score = 1.0
            elif rec == "HOLD" and consensus_action in ["BUY", "SELL"]:
                score = 0.5
            else:
                score = 0.0
            agreement_scores.append(score * self.weights[name])
            
        weighted_consensus_percentage = (sum(agreement_scores) / total_weight) * 100.0
        return consensus_action, round(weighted_consensus_percentage, 2)

    def _calculate_confidence_score(
        self,
        consensus_action: str,
        weighted_consensus: float,
        volatility: float,
        risk_assessment: RiskAssessment,
        news_analysis: NewsAnalysis,
        messages: List[Any] = None
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate Council Confidence Score (0-100) and return breakdown.
        
        Formula:
        confidence = 0.4 * agreement + 0.2 * (100 - risk_score) + 0.15 * (1 - volatility) * 100 + 0.15 * sentiment_conf + 0.1 * avg_accuracy
        """
        # 1. Agent Agreement (40%)
        agreement_raw = weighted_consensus
        agreement_contribution = 0.40 * agreement_raw
        
        # 2. Risk Manager Score (20%)
        risk_raw = max(0.0, 100.0 - risk_assessment.risk_score)
        risk_contribution = 0.20 * risk_raw
        
        # 3. Volatility Factor (15%)
        volatility_raw = max(0.0, (1.0 - volatility) * 100.0)
        volatility_contribution = 0.15 * volatility_raw
        
        # 4. Sentiment Stability Factor (15%)
        news_rec_values = []
        rec_map = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}
        
        if messages:
            for msg in messages:
                agent_id = getattr(msg, "agent_id", "") or (msg.get("agent_id") if isinstance(msg, dict) else "")
                rec = getattr(msg, "recommendation", "") or (msg.get("recommendation") if isinstance(msg, dict) else "")
                
                if "news" in agent_id.lower() and rec in rec_map:
                    news_rec_values.append(rec_map[rec])
                    
        if len(news_rec_values) > 1:
            import numpy as np
            std_dev = float(np.std(news_rec_values))
            penalty_scale = max(0.0, 1.0 - std_dev)
            sentiment_stability_raw = news_analysis.confidence * penalty_scale
        else:
            sentiment_stability_raw = news_analysis.confidence
            
        sentiment_contribution = 0.15 * sentiment_stability_raw
        
        # 5. Historical Accuracy (10%)
        accuracies = self._fetch_historical_accuracies()
        avg_accuracy_raw = sum(accuracies.values()) / len(accuracies)
        accuracy_contribution = 0.10 * avg_accuracy_raw
        
        # Total
        total_score = (
            agreement_contribution +
            risk_contribution +
            volatility_contribution +
            sentiment_contribution +
            accuracy_contribution
        )
        
        total_score = round(min(100.0, max(0.0, total_score)), 2)
        
        breakdown = {
            "raw_scores": {
                "agent_agreement": round(agreement_raw, 2),
                "risk_score_factor": round(risk_raw, 2),
                "volatility_factor": round(volatility_raw, 2),
                "sentiment_stability": round(sentiment_stability_raw, 2),
                "historical_accuracy": round(avg_accuracy_raw, 2)
            },
            "weighted_contributions": {
                "agent_agreement": round(agreement_contribution, 2),
                "risk_score_factor": round(risk_contribution, 2),
                "volatility_factor": round(volatility_contribution, 2),
                "sentiment_stability": round(sentiment_contribution, 2),
                "historical_accuracy": round(accuracy_contribution, 2)
            },
            "total_score": total_score
        }
        
        return total_score, breakdown

    def _calculate_position_size(
        self,
        action: str,
        market_data: MarketData,
        risk_assessment: RiskAssessment,
        confidence_score: float
    ) -> PositionSize:
        """
        Calculate target position size based on action, risk limits, and confidence.
        """
        current_price = market_data.current_price
        
        if action == "HOLD":
            return PositionSize(
                percentage_of_portfolio=0.0,
                quantity=0.0,
                entry_price=current_price,
                target_price=None,
                stop_loss=None
            )
            
        # Extract risk sizing recommendations
        max_allowed_pct = risk_assessment.max_position_allowed * 100.0  # Convert to percent, e.g. 0.15 -> 15.0
        rec_usd = risk_assessment.position_size_recommendation
        
        # Scale position based on confidence score (e.g., linear scaling between 50% and 100% confidence)
        confidence_scaler = max(0.5, confidence_score / 100.0)
        
        final_pct = round(max_allowed_pct * confidence_scaler, 2)
        final_usd = rec_usd * confidence_scaler
        
        quantity = round(final_usd / current_price, 4)
        
        # Calculate entry / target / stop loss
        # Use volatility as a buffer if available, default to 5% volatility
        vol_pct = market_data.volatility if market_data.volatility > 0 else 0.05
        
        # Calculate support / resistance overrides
        support = market_data.support_levels[0] if market_data.support_levels else None
        resistance = market_data.resistance_levels[0] if market_data.resistance_levels else None
        
        if action == "BUY":
            # Target is 3x volatility upside, Stop is 1.5x volatility downside
            stop_loss = current_price * (1.0 - 1.5 * vol_pct)
            target_price = current_price * (1.0 + 3.0 * vol_pct)
            
            # Refine with support/resistance if reasonable
            if support and support < current_price and support > current_price * 0.90:
                stop_loss = support * 0.99  # Place slightly below support
            if resistance and resistance > current_price and resistance < current_price * 1.15:
                target_price = resistance * 1.01  # Target slightly above resistance breakthrough
                
        else:  # SELL (Shorting scenario)
            # Target is 3x volatility downside, Stop is 1.5x volatility upside
            stop_loss = current_price * (1.0 + 1.5 * vol_pct)
            target_price = current_price * (1.0 - 3.0 * vol_pct)
            
            # Refine with support/resistance if reasonable
            if resistance and resistance > current_price and resistance < current_price * 1.10:
                stop_loss = resistance * 1.01  # Place slightly above resistance
            if support and support < current_price and support > current_price * 0.85:
                target_price = support * 0.99  # Target slightly below support breakthrough
                
        return PositionSize(
            percentage_of_portfolio=final_pct,
            quantity=quantity,
            entry_price=current_price,
            target_price=round(target_price, 2),
            stop_loss=round(stop_loss, 2)
        )

    def _synthesize_reasoning(
        self,
        symbol: str,
        current_price: float,
        tech: TechnicalAnalysis,
        news: NewsAnalysis,
        quant: QuantAnalysis,
        risk: RiskAssessment,
        final_action: str,
        weighted_consensus: float,
        confidence_score: float,
        confidence_factors: Dict[str, Any],
        veto_active: bool
    ) -> Dict[str, Any]:
        """
        Synthesize the reasoning of all analysts using the LLM.
        """
        prompt_template = ChatPromptTemplate.from_template(
            """You are the Chairman of the AI Investment Committee. Synthesize the reports of your committee members into a unified institutional-grade decision.
 
Asset: {symbol}
Current Price: ${current_price:.2f}
Committee Consensus Recommendation: {final_action}
Weighted Consensus Agreement: {weighted_consensus:.1f}%
Council Confidence Score: {confidence_score:.1f}%
Risk Veto Applied: {veto_active}

Council Confidence Score Breakdown:
- Agent Agreement: {agreement_contrib:.1f}% contribution (Raw Score: {agreement_raw:.1f}%)
- Risk Score Impact: {risk_contrib:.1f}% contribution (Raw Score: {risk_raw:.1f}%)
- Market Volatility Impact: {volatility_contrib:.1f}% contribution (Raw Score: {volatility_raw:.1f}%)
- Sentiment Stability: {sentiment_contrib:.1f}% contribution (Raw Score: {sentiment_raw:.1f}%)
- Historical Accuracy: {accuracy_contrib:.1f}% contribution (Raw Score: {accuracy_raw:.1f}%)
 
Committee Member Analyses:
1. Technical Analyst:
- Recommendation: {tech_rec} (Bullish Score: {tech_bullish:.1f}, Bearish Score: {tech_bearish:.1f})
- Findings: {tech_findings}
- Reasoning: {tech_reasoning}
 
2. News Analyst:
- Recommendation: {news_rec} (Sentiment Score: {news_sentiment:.2f})
- Findings: {news_events}
- Reasoning: {news_reasoning}
- Macro Impact: {news_macro}
 
3. Quant Analyst:
- Recommendation: {quant_rec} (Success Prob: {quant_prob:.1f}%, EV: {quant_ev:.2f})
- Findings: Pattern {quant_pattern}
- Reasoning: {quant_reasoning}
 
4. Risk Manager:
- Approved: {risk_approved} (Risk Score: {risk_score:.1f}/100)
- Veto Reason: {risk_veto_reason}
- Sizing Limits: Max position allowed {risk_max_pct:.1f}%
 
Provide the final synthesis in this exact JSON format:
{{
  "reasoning": "<A detailed, professional 3-4 sentence paragraph that consolidates the viewpoints, explains any conflicts, and provides institutional justification for the final action and the level of confidence in the decision>",
  "key_factors": [
    "<Key factor 1 explaining the decision>",
    "<Key factor 2 explaining the decision>",
    "<Key factor 3 explaining the decision>",
    "<Key factor 4 explaining the decision>"
  ]
}}
 
Note: If the Risk Veto was applied, your reasoning MUST explain that although some analysts may have been bullish, the trade was blocked due to critical risk limits and safety rules."""
        )
        
        try:
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    symbol=symbol,
                    current_price=current_price,
                    final_action=final_action,
                    weighted_consensus=weighted_consensus,
                    confidence_score=confidence_score,
                    agreement_contrib=confidence_factors["weighted_contributions"]["agent_agreement"],
                    agreement_raw=confidence_factors["raw_scores"]["agent_agreement"],
                    risk_contrib=confidence_factors["weighted_contributions"]["risk_score_factor"],
                    risk_raw=confidence_factors["raw_scores"]["risk_score_factor"],
                    volatility_contrib=confidence_factors["weighted_contributions"]["volatility_factor"],
                    volatility_raw=confidence_factors["raw_scores"]["volatility_factor"],
                    sentiment_contrib=confidence_factors["weighted_contributions"]["sentiment_stability"],
                    sentiment_raw=confidence_factors["raw_scores"]["sentiment_stability"],
                    accuracy_contrib=confidence_factors["weighted_contributions"]["historical_accuracy"],
                    accuracy_raw=confidence_factors["raw_scores"]["historical_accuracy"],
                    veto_active=veto_active,
                    tech_rec=tech.recommendation,
                    tech_bullish=tech.bullish_score,
                    tech_bearish=tech.bearish_score,
                    tech_findings=", ".join(tech.key_findings),
                    tech_reasoning=tech.reasoning,
                    news_rec=news.recommendation,
                    news_sentiment=news.sentiment_score,
                    news_events=", ".join(news.key_events),
                    news_reasoning=news.reasoning,
                    news_macro=news.macro_impact,
                    quant_rec=quant.recommendation,
                    quant_prob=quant.probability_score,
                    quant_ev=quant.expected_value,
                    quant_pattern=quant.historical_pattern,
                    quant_reasoning=quant.reasoning,
                    risk_approved=risk.approved,
                    risk_score=risk.risk_score,
                    risk_veto_reason=risk.veto_reason,
                    risk_max_pct=risk.max_position_allowed * 100.0
                )
            )
            
            response_text = response.content
            
            # Extract JSON from response
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            synthesis_dict = json.loads(json_str)
            
            return {
                "reasoning": synthesis_dict.get("reasoning", "Consensus synthesis completed successfully."),
                "key_factors": synthesis_dict.get("key_factors", ["Committee consensus", "Risk approval"])
            }
            
        except Exception as e:
            logger.warning(f"Failed to generate LLM synthesis: {e}")
            # Fallback reasoning
            factors = [
                f"Technical Analysis: {tech.recommendation}",
                f"News Analysis: {news.recommendation}",
                f"Quant Analysis: {quant.recommendation}",
                f"Risk Manager Status: {'Approved' if risk.approved else 'VETOED'}"
            ]
            if veto_active:
                reasoning = f"The trade proposal was rejected due to a Risk Manager VETO: {risk.veto_reason}."
            else:
                reasoning = (
                    f"The committee reached a {weighted_consensus}% consensus to {final_action} {symbol}. "
                    f"Key drivers include technical indicators advising {tech.recommendation} and news sentiment "
                    f"indicating a {news.recommendation} bias."
                )
            return {
                "reasoning": reasoning,
                "key_factors": factors
            }


# Instantiate global node (lazy-loaded on first use)
_execution_agent_node: Optional[ExecutionAgentNode] = None


def get_execution_agent_node() -> ExecutionAgentNode:
    """Get or create Execution Agent node"""
    global _execution_agent_node
    if _execution_agent_node is None:
        _execution_agent_node = ExecutionAgentNode()
    return _execution_agent_node


async def execution_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for LangGraph integration.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with execution_synthesis and final_decision
    """
    node = get_execution_agent_node()
    return node(state)
