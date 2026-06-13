"""
Quant Analyst Agent Node
LangGraph node implementation for quantitative analysis

Responsibilities:
- Pattern recognition and classification
- Probability scoring
- Expected value calculation
- Historical backtesting
- Correlation analysis
- Risk-adjusted performance metrics
- Scenario analysis

Output: Updates state.quant_analysis with QuantAnalysis object
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.agents.schemas import QuantAnalysis, MarketData
from app.agents.tools.quant_tools import QuantTools

logger = logging.getLogger(__name__)


class QuantAnalystNode:
    """
    LangGraph node for quantitative analysis
    
    Processes market data and generates probabilistic analysis
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize Quant Analyst
        
        Args:
            model_name: OpenAI model to use
            temperature: LLM temperature (0.7 for balanced analysis)
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1500
        )
        
        self.quant_tools = QuantTools()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute quantitative analysis on market data
        
        Args:
            state: Current graph state with market_data
        
        Returns:
            Updated state with quant_analysis populated
        """
        try:
            logger.info("Quant Analyst starting analysis")
            
            # Extract market data from state
            market_data: MarketData = state.get("market_data")
            if not market_data:
                raise ValueError("market_data not found in state")
            
            # Extract candles
            candles = market_data.historical_candles
            if not candles:
                logger.warning("No historical candles provided")
                return self._empty_analysis(state, "Insufficient historical data")
            
            # Convert to lists for analysis
            opens = [c.open for c in candles]
            highs = [c.high for c in candles]
            lows = [c.low for c in candles]
            closes = [c.close for c in candles]
            volumes = [c.volume for c in candles]
            
            # Perform quantitative analysis
            logger.info(f"Analyzing {len(candles)} candles for {market_data.symbol}")
            
            quant_data = self._perform_analysis(
                opens, highs, lows, closes, volumes
            )
            
            # Generate analysis and recommendation
            analysis = self._generate_analysis(
                market_data,
                quant_data
            )
            
            # Update state
            state["quant_analysis"] = analysis
            logger.info(
                f"Quant analysis complete: {analysis.recommendation} "
                f"(EV: {analysis.expected_value:.3f}, confidence: {analysis.confidence}%)"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Quant Analyst error: {str(e)}", exc_info=True)
            state["error_log"].append(f"Quant Analyst: {str(e)}")
            return self._empty_analysis(state, str(e))
    
    def _perform_analysis(
        self,
        opens: List[float],
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive quantitative analysis
        
        Returns: Dict with all quantitative metrics
        """
        analysis = {}
        
        try:
            # Pattern recognition
            pattern = self.quant_tools.identify_pattern(closes, highs, lows, lookback=20)
            analysis["pattern"] = pattern
            logger.debug(f"Pattern: {pattern['pattern']} (confidence: {pattern['confidence']:.2f})")
        except Exception as e:
            logger.warning(f"Pattern identification failed: {e}")
            analysis["pattern"] = None
        
        try:
            # Sharpe ratio
            returns = [
                (closes[i] - closes[i-1]) / closes[i-1]
                for i in range(1, len(closes))
            ]
            sharpe = self.quant_tools.calculate_sharpe_ratio(returns)
            analysis["sharpe"] = sharpe
            logger.debug(f"Sharpe ratio: {sharpe['sharpe_ratio']:.3f}")
        except Exception as e:
            logger.warning(f"Sharpe ratio calculation failed: {e}")
            analysis["sharpe"] = None
        
        try:
            # Max drawdown
            drawdown = self.quant_tools.calculate_max_drawdown(closes)
            analysis["drawdown"] = drawdown
            logger.debug(f"Max drawdown: {drawdown['max_drawdown']:.2%}")
        except Exception as e:
            logger.warning(f"Drawdown calculation failed: {e}")
            analysis["drawdown"] = None
        
        try:
            # Trend strength
            trend_strength = self.quant_tools.calculate_trend_strength(closes)
            analysis["trend_strength"] = trend_strength
            logger.debug(f"Trend strength: {trend_strength['trend_strength']:.2f}")
        except Exception as e:
            logger.warning(f"Trend strength calculation failed: {e}")
            analysis["trend_strength"] = None
        
        try:
            # Win rate (simplified: assume technical indicators as signal)
            signal_indicators = [min(abs(close - closes[0]) / closes[0] * 10, 1.0) for close in closes]
            win_rate = self.quant_tools.calculate_win_rate(closes, signal_indicators)
            analysis["win_rate"] = win_rate
            logger.debug(f"Win rate: {win_rate['win_rate']:.2%} ({win_rate['total_signals']} signals)")
        except Exception as e:
            logger.warning(f"Win rate calculation failed: {e}")
            analysis["win_rate"] = None
        
        try:
            # Probability score
            if analysis.get("pattern") and analysis.get("win_rate"):
                pattern_conf = analysis["pattern"].get("confidence", 0.5)
                win_rate = analysis["win_rate"].get("win_rate", 0.5)
                prob = self.quant_tools.calculate_probability_score(
                    historical_pattern_matches=analysis["win_rate"].get("total_signals", 10),
                    historical_pattern_wins=analysis["win_rate"].get("wins", 5),
                    current_signal_strength=pattern_conf,
                    sample_size_confidence=analysis["win_rate"].get("confidence", 0.5)
                )
                analysis["probability"] = prob
                logger.debug(f"Probability score: {prob['probability_score']:.2%}")
            else:
                analysis["probability"] = None
        except Exception as e:
            logger.warning(f"Probability calculation failed: {e}")
            analysis["probability"] = None
        
        try:
            # Expected value
            if analysis.get("probability") and analysis.get("win_rate"):
                prob_score = analysis["probability"].get("probability_score", 0.5)
                avg_win = 0.02 if analysis["pattern"]["pattern"] == "momentum" else 0.01
                avg_loss = 0.015
                ev = self.quant_tools.calculate_expected_value(
                    win_probability=prob_score,
                    average_win=avg_win,
                    average_loss=avg_loss,
                    win_rate_confidence=analysis["probability"].get("confidence", 0.5)
                )
                analysis["expected_value"] = ev
                logger.debug(f"Expected value: {ev['expected_value']:.3%}")
            else:
                analysis["expected_value"] = None
        except Exception as e:
            logger.warning(f"Expected value calculation failed: {e}")
            analysis["expected_value"] = None
        
        return analysis
    
    def _generate_analysis(
        self,
        market_data: MarketData,
        quant_data: Dict[str, Any]
    ) -> QuantAnalysis:
        """
        Generate structured quant analysis using LLM synthesis
        
        Args:
            market_data: Current market data
            quant_data: Calculated quantitative metrics
        
        Returns:
            QuantAnalysis object with recommendation and scores
        """
        # Prepare quant summary
        quant_summary = self._summarize_quant_data(quant_data)
        
        # Create prompt for LLM analysis
        prompt_template = ChatPromptTemplate.from_template(
            """You are an expert quantitative analyst. Analyze the following quantitative metrics 
and provide a structured probability and expected value analysis.

Symbol: {symbol}
Current Price: ${current_price:.2f}

Quantitative Metrics:
{quant_summary}

Provide analysis in this exact JSON format:
{{
  "probability_score": <0.0 to 1.0>,
  "confidence": <0-100>,
  "recommendation": "<BUY|SELL|HOLD>",
  "historical_pattern": "<description of identified pattern>",
  "expected_value": <decimal, e.g., 0.0234 for 2.34%>,
  "correlation_analysis": "<brief analysis of relationships>",
  "reasoning": "<1 short, punchy sentence (e.g. 'Historical probability: 64%')>"
}}

Remember:
- Probability score is likelihood of upside (0.5 = neutral)
- Confidence is based on data quality and sample size
- Expected value should be positive for BUY recommendations
- Consider risk-adjusted returns (Sharpe ratio)
- Base recommendation on statistical significance
- Include pattern recognition insights"""
        )
        
        try:
            # Call LLM for analysis
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    symbol=market_data.symbol,
                    current_price=market_data.current_price,
                    quant_summary=quant_summary
                )
            )
            
            # Parse response
            response_text = response.content
            
            # Extract JSON from response
            try:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                json_str = response_text[start:end]
                analysis_dict = json.loads(json_str)
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                analysis_dict = self._fallback_analysis(quant_data)
            
            # Create QuantAnalysis object
            analysis = QuantAnalysis(
                probability_score=float(analysis_dict.get("probability_score", 0.5)),
                confidence=float(analysis_dict.get("confidence", 50)),
                recommendation=analysis_dict.get("recommendation", "HOLD").upper(),
                historical_pattern=analysis_dict.get("historical_pattern", "Unknown pattern"),
                expected_value=float(analysis_dict.get("expected_value", 0.0)),
                correlation_analysis=analysis_dict.get("correlation_analysis", {}),
                reasoning=analysis_dict.get("reasoning", "No reasoning provided")
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to rule-based analysis
            return self._fallback_analysis_to_pydantic(quant_data)
    
    def _summarize_quant_data(self, quant_data: Dict[str, Any]) -> str:
        """Create human-readable summary of quantitative metrics"""
        summary_lines = []
        
        # Pattern
        if quant_data.get("pattern"):
            pattern = quant_data["pattern"]
            summary_lines.append(f"Pattern: {pattern['pattern']} (confidence: {pattern['confidence']:.0%})")
            summary_lines.append(f"  {pattern['description']}")
        
        # Sharpe ratio
        if quant_data.get("sharpe"):
            sharpe = quant_data["sharpe"]
            sharpe_val = sharpe["sharpe_ratio"]
            if sharpe_val > 1.0:
                quality = "excellent risk-adjusted returns"
            elif sharpe_val > 0.5:
                quality = "good risk-adjusted returns"
            elif sharpe_val > 0:
                quality = "positive risk-adjusted returns"
            else:
                quality = "negative risk-adjusted returns"
            summary_lines.append(f"Sharpe Ratio: {sharpe_val:.2f} ({quality})")
            summary_lines.append(f"  Annualized return: {sharpe['annualized_return']:.1%}, Volatility: {sharpe['annualized_volatility']:.1%}")
        
        # Drawdown
        if quant_data.get("drawdown"):
            dd = quant_data["drawdown"]
            summary_lines.append(f"Max Drawdown: {dd['max_drawdown']:.1%} (from ${dd['peak_value']:.2f} to ${dd['trough_value']:.2f})")
        
        # Trend strength
        if quant_data.get("trend_strength"):
            ts = quant_data["trend_strength"]
            trend_qual = "strong" if ts["trend_strength"] > 0.7 else "moderate" if ts["trend_strength"] > 0.4 else "weak"
            summary_lines.append(f"Trend Strength: {trend_qual} ({ts['trend_strength']:.2f} R²)")
        
        # Win rate
        if quant_data.get("win_rate"):
            wr = quant_data["win_rate"]
            if wr["total_signals"] > 0:
                summary_lines.append(f"Historical Win Rate: {wr['win_rate']:.1%} ({wr['wins']} wins, {wr['losses']} losses in {wr['total_signals']} signals)")
        
        # Probability
        if quant_data.get("probability"):
            prob = quant_data["probability"]
            summary_lines.append(f"Probability Score: {prob['probability_score']:.1%} (confidence: {prob['confidence']:.0%})")
        
        # Expected value
        if quant_data.get("expected_value"):
            ev = quant_data["expected_value"]
            summary_lines.append(f"Expected Value: {ev['expected_value']:.3%} ({ev['ev_classification']})")
            summary_lines.append(f"  Profit Factor: {ev['profit_factor']:.2f}x")
        
        return "\n".join(summary_lines)
    
    def _fallback_analysis(self, quant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback analysis if LLM fails"""
        
        # Calculate scores from available data
        probability_score = 0.5  # neutral default
        confidence = 50
        expected_value = 0.0
        
        # Probability from pattern
        if quant_data.get("pattern"):
            pattern = quant_data["pattern"]
            probability_score += (pattern["confidence"] - 0.5) * 0.2
            confidence += pattern["confidence"] * 20
        
        # Probability from win rate
        if quant_data.get("win_rate"):
            win_rate = quant_data["win_rate"]
            if win_rate["total_signals"] > 0:
                wr = win_rate["win_rate"]
                probability_score += (wr - 0.5) * 0.3
                confidence += min(win_rate["total_signals"] / 50 * 20, 30)
        
        # Expected value
        if quant_data.get("expected_value"):
            expected_value = quant_data["expected_value"]["expected_value"]
        
        # Recommendation based on EV
        if expected_value > 0.015:
            recommendation = "BUY"
        elif expected_value > 0.005:
            recommendation = "BUY"
        elif expected_value < -0.015:
            recommendation = "SELL"
        elif expected_value < -0.005:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        # Pattern identification
        historical_pattern = "Unknown"
        if quant_data.get("pattern"):
            historical_pattern = quant_data["pattern"]["pattern"]
        
        # Normalize probability
        probability_score = max(0.0, min(1.0, probability_score))
        confidence = min(int(confidence), 100)
        
        return {
            "probability_score": probability_score,
            "confidence": confidence,
            "recommendation": recommendation,
            "historical_pattern": historical_pattern,
            "expected_value": expected_value,
            "correlation_analysis": {},
            "reasoning": f"Rule-based analysis with probability {probability_score:.1%} and EV {expected_value:.3%}"
        }
    
    def _fallback_analysis_to_pydantic(
        self,
        quant_data: Dict[str, Any]
    ) -> QuantAnalysis:
        """Convert fallback analysis to QuantAnalysis object"""
        analysis_dict = self._fallback_analysis(quant_data)
        return QuantAnalysis(
            probability_score=analysis_dict["probability_score"],
            confidence=analysis_dict["confidence"],
            recommendation=analysis_dict["recommendation"],
            historical_pattern=analysis_dict["historical_pattern"],
            expected_value=analysis_dict["expected_value"],
            correlation_analysis=analysis_dict["correlation_analysis"],
            reasoning=analysis_dict["reasoning"]
        )
    
    def _empty_analysis(
        self,
        state: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """Return empty analysis when data is insufficient"""
        state["quant_analysis"] = QuantAnalysis(
            probability_score=0.5,
            confidence=0.0,
            recommendation="HOLD",
            historical_pattern="Insufficient data",
            expected_value=0.0,
            correlation_analysis={},
            reasoning=f"Unable to perform analysis: {reason}"
        )
        return state


# Instantiate global node (lazy-loaded on first use)
_quant_analyst_node: Optional[QuantAnalystNode] = None


def get_quant_analyst_node() -> QuantAnalystNode:
    """Get or create Quant Analyst node"""
    global _quant_analyst_node
    if _quant_analyst_node is None:
        _quant_analyst_node = QuantAnalystNode()
    return _quant_analyst_node


async def quant_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for LangGraph integration
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with quant_analysis
    """
    node = get_quant_analyst_node()
    return node(state)
