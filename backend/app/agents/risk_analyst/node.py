"""
Risk Manager Agent Node
LangGraph node implementation for risk management and veto enforcement

Responsibilities:
- Portfolio risk assessment
- Position sizing validation
- Drawdown limit enforcement
- Correlation-based diversification checking
- Value at Risk calculation
- Veto power (blocking approved trades)

CRITICAL: This agent has VETO POWER - its approval is MANDATORY
If approved=False, the trade is BLOCKED and cannot be overridden

Output: Updates state.risk_assessment with RiskAssessment object (approved: bool)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.agents.schemas import RiskAssessment, MarketData, AgentMessage
from app.agents.tools.risk_tools import RiskTools

logger = logging.getLogger(__name__)


class RiskManagerNode:
    """
    LangGraph node for risk management with VETO POWER
    
    This agent has final say on whether trades are approved.
    No other agent can override its decision.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,  # Lower temp for conservative risk decisions
        max_daily_loss_pct: float = 0.01,
        max_position_pct: float = 0.15
    ):
        """
        Initialize Risk Manager
        
        Args:
            model_name: OpenAI model to use
            temperature: LLM temperature (0.3 for conservative)
            max_daily_loss_pct: Maximum daily loss % before veto
            max_position_pct: Maximum single position %
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1500
        )
        
        self.risk_tools = RiskTools()
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_position_pct = max_position_pct
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk assessment and veto check
        
        CRITICAL: This method determines whether trade is APPROVED or BLOCKED
        
        Args:
            state: Current graph state with market_data and proposed_action
        
        Returns:
            Updated state with risk_assessment (with approved: bool)
        """
        try:
            logger.info("Risk Manager starting assessment")
            
            # Extract market data
            market_data: MarketData = state.get("market_data")
            if not market_data:
                raise ValueError("market_data not found in state")
            
            # Check if this is even a trade request
            proposed_action = state.get("proposed_action")
            if not proposed_action or proposed_action not in ["BUY", "SELL"]:
                # Not a trade - no risk to assess
                state["risk_assessment"] = RiskAssessment(
                    risk_score=0.0,
                    risk_level="none",
                    approved=True,
                    veto_reason="No trade proposed",
                    position_size_recommendation=0.0,
                    max_position_allowed=0.0
                )
                return state
            
            # Extract account state
            account_size = state.get("account_size", 100000.0)
            current_holdings = state.get("current_holdings", {})
            current_equity = state.get("current_equity", account_size)
            
            # Perform risk assessment
            logger.info(f"Assessing risk for {proposed_action} on {market_data.symbol}")
            
            risk_data = self._perform_risk_assessment(
                market_data=market_data,
                account_size=account_size,
                current_holdings=current_holdings,
                current_equity=current_equity
            )
            
            # Fetch past trade context from memory
            try:
                from app.agents.memory.memory_manager import AgentMemoryManager
                memory_manager = AgentMemoryManager()
                past_trades = memory_manager.get_similar_trades(market_data.symbol, limit=3)
                risk_data["historical_trades"] = past_trades
            except Exception as e:
                logger.warning(f"Failed to fetch historical trades from memory: {e}")
                risk_data["historical_trades"] = []
            
            # Make veto decision (with LLM synthesis)
            assessment = self._make_veto_decision(
                market_data=market_data,
                risk_data=risk_data,
                proposed_action=proposed_action
            )
            
            # Log decision
            if assessment.approved:
                logger.info(f"✅ Trade APPROVED: {proposed_action} {market_data.symbol}")
            else:
                logger.warning(f"🚫 Trade BLOCKED (veto): {assessment.veto_reason}")
            
            state["risk_assessment"] = assessment
            state["error_log"].append(f"Risk Manager: {assessment.veto_reason}")
            
            # Append message to transcript for UI
            msg = AgentMessage(
                agent_id="risk_manager",
                agent_name="Risk Manager",
                message_type="ASSESSMENT",
                content=assessment.veto_reason,
                confidence=assessment.risk_score / 100.0,
                recommendation="VETO" if not assessment.approved else "APPROVE",
                reasoning={"risk_score": assessment.risk_score}
            )
            if "messages" not in state:
                state["messages"] = []
            state["messages"] = state["messages"] + [msg]
            
            return state
            
        except Exception as e:
            logger.error(f"Risk Manager error: {str(e)}", exc_info=True)
            # On error, VETO the trade (fail-safe)
            state["risk_assessment"] = RiskAssessment(
                risk_score=100.0,
                risk_level="critical",
                approved=False,
                veto_reason=f"Risk assessment failed: {str(e)} - VETOED for safety",
                position_size_recommendation=0.0,
                max_position_allowed=0.0
            )
            state["error_log"].append(f"Risk Manager critical error: {str(e)}")
            return state
    
    def _perform_risk_assessment(
        self,
        market_data: MarketData,
        account_size: float,
        current_holdings: Dict[str, float],
        current_equity: float
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment
        
        Returns: Dict with all risk metrics
        """
        assessment = {}
        
        try:
            # Extract price data
            closes = [c.close for c in market_data.historical_candles]
            if len(closes) < 2:
                return {"error": "Insufficient data"}
            
            # Calculate returns
            returns = [
                (closes[i] - closes[i-1]) / closes[i-1]
                for i in range(1, len(closes))
            ]
            
            # Value at Risk
            var = self.risk_tools.calculate_value_at_risk(
                returns=returns,
                position_size=current_equity,
                confidence_level=0.95
            )
            assessment["var"] = var
            logger.debug(f"VaR (95%): {var['var_pct']:.2%}")
            
        except Exception as e:
            logger.warning(f"VaR calculation failed: {e}")
            assessment["var"] = None
        
        try:
            # Position sizing
            volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0.15
            position_sizing = self.risk_tools.calculate_position_size(
                account_size=account_size,
                volatility=volatility,
                max_risk_pct=self.max_daily_loss_pct
            )
            assessment["position_sizing"] = position_sizing
            logger.debug(f"Recommended position size: ${position_sizing['position_size']:.2f}")
            
        except Exception as e:
            logger.warning(f"Position sizing failed: {e}")
            assessment["position_sizing"] = None
        
        try:
            # Portfolio concentration
            concentration = self.risk_tools.assess_portfolio_concentration(
                current_holdings=current_holdings,
                account_size=account_size
            )
            assessment["concentration"] = concentration
            logger.debug(f"Concentration score: {concentration['concentration_score']:.2f}")
            
        except Exception as e:
            logger.warning(f"Concentration assessment failed: {e}")
            assessment["concentration"] = None
        
        try:
            # Drawdown limits
            daily_vol = np.std(returns) if len(returns) > 1 else 0.01
            drawdown = self.risk_tools.calculate_drawdown_limit(
                account_size=account_size,
                daily_vol=daily_vol,
                max_daily_loss_pct=self.max_daily_loss_pct
            )
            assessment["drawdown_limits"] = drawdown
            logger.debug(f"Daily loss limit: ${drawdown['daily_limit']:.2f}")
            
        except Exception as e:
            logger.warning(f"Drawdown limit calculation failed: {e}")
            assessment["drawdown_limits"] = None
        
        try:
            # Overall risk score
            max_dd = (closes[0] - min(closes)) / closes[0] if closes else 0
            concentration_score = assessment["concentration"]["concentration_score"] if assessment.get("concentration") else 0.5
            
            overall_risk = self.risk_tools.calculate_overall_risk_score(
                volatility=volatility,
                max_drawdown=max_dd,
                concentration_score=concentration_score,
                correlation_risk=0.3,  # Assume moderate for now
                position_sizing_ratio=1.0
            )
            assessment["overall_risk"] = overall_risk
            logger.debug(f"Overall risk score: {overall_risk['overall_risk_score']:.0f}/100")
            
        except Exception as e:
            logger.warning(f"Overall risk calculation failed: {e}")
            assessment["overall_risk"] = None
        
        return assessment
    
    def _make_veto_decision(
        self,
        market_data: MarketData,
        risk_data: Dict[str, Any],
        proposed_action: str
    ) -> RiskAssessment:
        """
        Make final veto decision with LLM synthesis
        
        CRITICAL: This decides if trade is APPROVED or BLOCKED
        
        Args:
            market_data: Current market data
            risk_data: Calculated risk metrics
            proposed_action: Proposed action (BUY/SELL)
        
        Returns:
            RiskAssessment with approved: bool (MANDATORY FINAL DECISION)
        """
        # Prepare summary
        risk_summary = self._summarize_risk_data(risk_data)
        
        # Create prompt for LLM
        prompt_template = ChatPromptTemplate.from_template(
            """You are a conservative risk manager. Your ONLY job is to determine if a trade is SAFE.
            
This is your FINAL DECISION - once you approve/reject, there is NO OVERRIDE.

Symbol: {symbol}
Proposed Action: {proposed_action}
Current Price: ${current_price:.2f}

Risk Assessment:
{risk_summary}

Historical Similar Trades:
{historical_trades}

Your decision criteria:
1. VETO (approve=false) if: Risk score > 75 OR VaR > 5% of account OR position > 20%
2. VETO if: Concentration risk already high AND adding more to concentrated position
3. VETO if: Correlation shows assets moving together AND adding correlated position
4. VETO if: Similar past trades in these market conditions resulted in severe losses.
5. APPROVE (approve=true) if: All metrics within acceptable ranges

Respond ONLY with this JSON - no other text:
{{
  "approved": <true or false>,
  "risk_score": <0-100>,
  "veto_reason": "<1 short, punchy sentence (e.g. 'Volatility remains elevated.')>",
  "position_size_recommendation": <max USD position size>,
  "max_position_allowed": <max % of account>
}}

Remember: Err on the side of CAUTION. When in doubt, VETO."""
        )
        
        try:
            # Format historical trades
            hist_str = "None found."
            if risk_data.get("historical_trades"):
                hist_str = json.dumps([t.get("summary", "") for t in risk_data["historical_trades"]], indent=2)
                
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    symbol=market_data.symbol,
                    proposed_action=proposed_action,
                    current_price=market_data.current_price,
                    risk_summary=risk_summary,
                    historical_trades=hist_str
                )
            )
            
            response_text = response.content
            
            # Extract JSON
            try:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                json_str = response_text[start:end]
                decision = json.loads(json_str)
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                decision = self._fallback_veto_decision(risk_data)
            
            # Create assessment
            assessment = RiskAssessment(
                risk_score=float(decision.get("risk_score", 50)),
                risk_level=self._risk_level_from_score(decision.get("risk_score", 50)),
                approved=bool(decision.get("approved", False)),
                veto_reason=decision.get("veto_reason", "No reason given"),
                position_size_recommendation=float(decision.get("position_size_recommendation", 0)),
                max_position_allowed=float(decision.get("max_position_allowed", 0.15))
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"LLM decision failed: {e}")
            # Fallback: VETO on LLM failure (fail-safe)
            return RiskAssessment(
                risk_score=100.0,
                risk_level="critical",
                approved=False,
                veto_reason=f"LLM decision failed - VETOED for safety: {str(e)}",
                position_size_recommendation=0.0,
                max_position_allowed=0.0
            )
    
    def _summarize_risk_data(self, risk_data: Dict[str, Any]) -> str:
        """Create human-readable risk summary"""
        lines = []
        
        if risk_data.get("var"):
            var = risk_data["var"]
            lines.append(f"Value at Risk (95%): {var['var_pct']:.1%} of account (${var['var_amount']:.2f})")
        
        if risk_data.get("position_sizing"):
            ps = risk_data["position_sizing"]
            lines.append(f"Recommended position size: ${ps['position_size']:.2f} ({ps['kelly_fraction']:.1%} of account)")
        
        if risk_data.get("concentration"):
            conc = risk_data["concentration"]
            lines.append(f"Portfolio concentration: {conc['concentration_score']:.0%} (largest: {conc['largest_position_pct']:.1%})")
        
        if risk_data.get("drawdown_limits"):
            dd = risk_data["drawdown_limits"]
            lines.append(f"Daily loss limit: ${dd['daily_limit']:.2f}")
        
        if risk_data.get("overall_risk"):
            overall = risk_data["overall_risk"]
            lines.append(f"Overall risk score: {overall['overall_risk_score']:.0f}/100 ({overall['risk_level']})")
            if overall.get("should_veto"):
                lines.append(f"⚠️ VETO TRIGGERED: {overall['veto_reason']}")
        
        return "\n".join(lines)
    
    def _fallback_veto_decision(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback veto decision if LLM fails"""
        
        # Extract risk score if available
        risk_score = 50.0
        approved = True
        veto_reason = "Approved"
        
        if risk_data.get("overall_risk"):
            risk_score = risk_data["overall_risk"]["overall_risk_score"]
            if risk_data["overall_risk"].get("should_veto"):
                approved = False
                veto_reason = risk_data["overall_risk"]["veto_reason"]
        
        # Hard limits
        if risk_data.get("var") and risk_data["var"]["var_pct"] > 0.05:
            approved = False
            veto_reason = "VaR > 5% - excessive downside risk"
        
        if risk_data.get("concentration") and risk_data["concentration"]["concentration_score"] > 0.6:
            approved = False
            veto_reason = "Portfolio too concentrated"
        
        return {
            "approved": approved,
            "risk_score": risk_score,
            "veto_reason": veto_reason,
            "position_size_recommendation": 0.0 if not approved else 10000.0,
            "max_position_allowed": 0.0 if not approved else 0.15
        }
    
    def _risk_level_from_score(self, score: float) -> str:
        """Convert risk score to level"""
        if score > 75:
            return "critical"
        elif score > 60:
            return "high"
        elif score > 40:
            return "medium"
        elif score > 20:
            return "low"
        else:
            return "minimal"


# Need numpy for std calculation
import numpy as np

# Instantiate global node (lazy-loaded on first use)
_risk_manager_node: Optional[RiskManagerNode] = None


def get_risk_manager_node() -> RiskManagerNode:
    """Get or create Risk Manager node"""
    global _risk_manager_node
    if _risk_manager_node is None:
        _risk_manager_node = RiskManagerNode()
    return _risk_manager_node


async def risk_manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for LangGraph integration
    
    CRITICAL: This agent has VETO POWER
    approved=False cannot be overridden
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with risk_assessment (with approved: bool)
    """
    node = get_risk_manager_node()
    return node(state)
