"""
Technical Analyst Agent Node
LangGraph node implementation for technical analysis

Responsibilities:
- RSI, MACD, EMA analysis
- Volume trend analysis
- Support/Resistance identification
- Trend analysis
- Candlestick pattern recognition
- Generate bullish/bearish scores
- Produce structured analysis with confidence

Output: Updates state.technical_analysis with TechnicalAnalysis object
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser

from app.agents.schemas import TechnicalAnalysis, MarketData, CandleData
from app.agents.tools.technical_tools import TechnicalIndicators

logger = logging.getLogger(__name__)


class TechnicalAnalystNode:
    """
    LangGraph node for technical analysis
    
    Processes market data and generates structured technical analysis
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize Technical Analyst
        
        Args:
            model_name: OpenAI model to use
            temperature: LLM temperature (0.7 for balanced analysis)
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1500
        )
        
        self.indicators = TechnicalIndicators()
        
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute technical analysis on market data
        
        Args:
            state: Current graph state with market_data
        
        Returns:
            Updated state with technical_analysis populated
        """
        try:
            logger.info("Technical Analyst starting analysis")
            
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
            
            # Calculate all technical indicators
            logger.info(f"Analyzing {len(candles)} candles for {market_data.symbol}")
            
            technical_data = self._calculate_indicators(
                opens, highs, lows, closes, volumes
            )
            
            # Generate analysis and scores
            analysis = self._generate_analysis(
                market_data,
                technical_data,
                closes
            )
            
            # Update state
            state["technical_analysis"] = analysis
            logger.info(
                f"Technical analysis complete: {analysis.recommendation} "
                f"(confidence: {analysis.confidence}%)"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Technical Analyst error: {str(e)}", exc_info=True)
            state["error_log"].append(f"Technical Analyst: {str(e)}")
            return self._empty_analysis(state, str(e))
    
    def _calculate_indicators(
        self,
        opens: List[float],
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate all technical indicators
        
        Returns: Dict with all indicator values
        """
        indicators = {}
        
        try:
            # RSI
            indicators["rsi"] = self.indicators.calculate_rsi(closes, period=14)
            logger.debug(f"RSI: {indicators['rsi']:.2f}")
        except Exception as e:
            logger.warning(f"RSI calculation failed: {e}")
            indicators["rsi"] = None
        
        try:
            # MACD
            indicators["macd"] = self.indicators.calculate_macd(closes)
            logger.debug(
                f"MACD: {indicators['macd']['value']:.6f}, "
                f"Signal: {indicators['macd']['signal']:.6f}, "
                f"Histogram: {indicators['macd']['histogram']:.6f}"
            )
        except Exception as e:
            logger.warning(f"MACD calculation failed: {e}")
            indicators["macd"] = None
        
        try:
            # EMAs
            indicators["ema_50"] = self.indicators.calculate_ema(closes, 50)
            indicators["ema_200"] = self.indicators.calculate_ema(closes, 200)
            logger.debug(f"EMA 50: {indicators['ema_50']:.2f}, EMA 200: {indicators['ema_200']:.2f}")
        except Exception as e:
            logger.warning(f"EMA calculation failed: {e}")
            indicators["ema_50"] = None
            indicators["ema_200"] = None
        
        try:
            # Bollinger Bands
            indicators["bb"] = self.indicators.calculate_bollinger_bands(closes)
            logger.debug(f"BB: {indicators['bb']['upper']:.2f} / {indicators['bb']['middle']:.2f} / {indicators['bb']['lower']:.2f}")
        except Exception as e:
            logger.warning(f"Bollinger Bands calculation failed: {e}")
            indicators["bb"] = None
        
        try:
            # Volume analysis
            indicators["volume"] = self.indicators.analyze_volume_trend(volumes, closes)
            logger.debug(f"Volume trend: {indicators['volume']['trend']}")
        except Exception as e:
            logger.warning(f"Volume analysis failed: {e}")
            indicators["volume"] = None
        
        try:
            # Trend
            indicators["trend"] = self.indicators.identify_trend(closes)
            logger.debug(f"Trend: {indicators['trend']['direction']} (strength: {indicators['trend']['strength']:.2f})")
        except Exception as e:
            logger.warning(f"Trend analysis failed: {e}")
            indicators["trend"] = None
        
        try:
            # Support/Resistance
            indicators["levels"] = self.indicators.find_support_resistance(closes, highs, lows)
            logger.debug(f"Support: {indicators['levels']['support']}, Resistance: {indicators['levels']['resistance']}")
        except Exception as e:
            logger.warning(f"Support/Resistance analysis failed: {e}")
            indicators["levels"] = None
        
        try:
            # Candlestick pattern
            indicators["pattern"] = self.indicators.identify_candlestick_pattern(opens, highs, lows, closes)
            logger.debug(f"Pattern: {indicators['pattern']}")
        except Exception as e:
            logger.warning(f"Pattern recognition failed: {e}")
            indicators["pattern"] = None
        
        return indicators
    
    def _generate_analysis(
        self,
        market_data: MarketData,
        indicators: Dict[str, Any],
        closes: List[float]
    ) -> TechnicalAnalysis:
        """
        Generate structured analysis using LLM synthesis
        
        Args:
            market_data: Current market data
            indicators: Calculated technical indicators
            closes: List of closing prices
        
        Returns:
            TechnicalAnalysis object with recommendation and scores
        """
        current_price = closes[-1]
        
        # Prepare indicator summary
        indicator_summary = self._summarize_indicators(indicators, current_price)
        
        # Create prompt for LLM analysis
        prompt_template = ChatPromptTemplate.from_template(
            """You are an expert technical analyst. Analyze the following technical indicators 
and provide a structured analysis.

Symbol: {symbol}
Current Price: ${current_price:.2f}
24h High: ${price_24h_high:.2f}
24h Low: ${price_24h_low:.2f}

Technical Indicators:
{indicator_summary}

Provide analysis in this exact JSON format:
{{
  "bullish_score": <0-100>,
  "bearish_score": <0-100>,
  "confidence": <0-100>,
  "recommendation": "<BUY|SELL|HOLD>",
  "reasoning": "<2-3 sentence explanation>",
  "key_findings": [<list of 3-4 key observations>]
}}

Remember:
- Bullish and bearish scores should sum to <= 100 (can have neutral)
- Confidence reflects how clear the technical picture is
- Base recommendation on strongest signals
- Ensure reasoning explains the scores and recommendation"""
        )
        
        try:
            # Call LLM for analysis
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    symbol=market_data.symbol,
                    current_price=current_price,
                    price_24h_high=market_data.price_24h_high,
                    price_24h_low=market_data.price_24h_low,
                    indicator_summary=indicator_summary
                )
            )
            
            # Parse response
            import json
            response_text = response.content
            
            # Extract JSON from response
            try:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                json_str = response_text[start:end]
                analysis_dict = json.loads(json_str)
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                analysis_dict = self._fallback_analysis(indicators, current_price)
            
            # Create TechnicalAnalysis object
            analysis = TechnicalAnalysis(
                bullish_score=float(analysis_dict.get("bullish_score", 50)),
                bearish_score=float(analysis_dict.get("bearish_score", 50)),
                confidence=float(analysis_dict.get("confidence", 50)),
                recommendation=analysis_dict.get("recommendation", "HOLD").upper(),
                reasoning=analysis_dict.get("reasoning", "No reasoning provided"),
                key_findings=analysis_dict.get("key_findings", []),
                supporting_data=indicators
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to rule-based analysis
            return self._fallback_analysis_to_pydantic(indicators, current_price)
    
    def _summarize_indicators(self, indicators: Dict[str, Any], current_price: float) -> str:
        """Create human-readable summary of indicators"""
        summary = []
        
        if indicators.get("rsi") is not None:
            rsi = indicators["rsi"]
            rsi_signal = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
            summary.append(f"RSI (14): {rsi:.2f} ({rsi_signal})")
        
        if indicators.get("macd"):
            macd = indicators["macd"]
            macd_signal = "bullish" if macd["histogram"] > 0 else "bearish"
            summary.append(f"MACD: {macd['value']:.6f}, Signal: {macd['signal']:.6f} ({macd_signal})")
        
        if indicators.get("ema_50") and indicators.get("ema_200"):
            ema_50 = indicators["ema_50"]
            ema_200 = indicators["ema_200"]
            price_vs_50 = "above" if current_price > ema_50 else "below"
            price_vs_200 = "above" if current_price > ema_200 else "below"
            ema_signal = "bullish" if ema_50 > ema_200 else "bearish"
            summary.append(
                f"EMA 50: {ema_50:.2f}, EMA 200: {ema_200:.2f} "
                f"(Price {price_vs_50} EMA50, {price_vs_200} EMA200, {ema_signal})"
            )
        
        if indicators.get("bb"):
            bb = indicators["bb"]
            bb_position = "upper" if current_price > bb["middle"] else "lower"
            summary.append(f"Bollinger Bands: Upper {bb['upper']:.2f}, Middle {bb['middle']:.2f}, Lower {bb['lower']:.2f} (Price in {bb_position} half)")
        
        if indicators.get("volume"):
            vol = indicators["volume"]
            summary.append(f"Volume: {vol['trend']} (Strength: {vol['strength']:.2f})")
        
        if indicators.get("trend"):
            trend = indicators["trend"]
            summary.append(f"Trend: {trend['direction']} (Strength: {trend['strength']:.2f})")
        
        if indicators.get("levels"):
            levels = indicators["levels"]
            if levels["support"]:
                summary.append(f"Support: {', '.join([f'${s:.2f}' for s in levels['support']])}")
            if levels["resistance"]:
                summary.append(f"Resistance: {', '.join([f'${r:.2f}' for r in levels['resistance']])}")
        
        if indicators.get("pattern"):
            summary.append(f"Candlestick Pattern: {indicators['pattern']}")
        
        return "\n".join(summary)
    
    def _fallback_analysis(self, indicators: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Rule-based fallback analysis if LLM fails"""
        bullish_score = 50.0
        bearish_score = 50.0
        confidence = 50.0
        
        # RSI rules
        if indicators.get("rsi"):
            rsi = indicators["rsi"]
            if rsi > 70:
                bullish_score += 15
                confidence += 10
            elif rsi < 30:
                bearish_score += 15
                confidence += 10
        
        # MACD rules
        if indicators.get("macd"):
            macd = indicators["macd"]
            if macd["histogram"] > 0:
                bullish_score += 10
                confidence += 5
            else:
                bearish_score += 10
                confidence += 5
        
        # EMA rules
        if indicators.get("ema_50") and indicators.get("ema_200"):
            if current_price > indicators["ema_50"] > indicators["ema_200"]:
                bullish_score += 20
                confidence += 15
            elif current_price < indicators["ema_50"] < indicators["ema_200"]:
                bearish_score += 20
                confidence += 15
        
        # Trend rules
        if indicators.get("trend"):
            trend = indicators["trend"]
            if trend["direction"] == "UP":
                bullish_score += 10
                confidence += 5
            elif trend["direction"] == "DOWN":
                bearish_score += 10
                confidence += 5
        
        # Normalize
        bullish_score = min(bullish_score, 100)
        bearish_score = min(bearish_score, 100)
        confidence = min(confidence, 100)
        
        # Determine recommendation
        if bullish_score > bearish_score + 10:
            recommendation = "BUY"
        elif bearish_score > bullish_score + 10:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        return {
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "confidence": confidence,
            "recommendation": recommendation,
            "reasoning": "Rule-based analysis (LLM unavailable)",
            "key_findings": []
        }
    
    def _fallback_analysis_to_pydantic(
        self,
        indicators: Dict[str, Any],
        current_price: float
    ) -> TechnicalAnalysis:
        """Convert fallback analysis to TechnicalAnalysis object"""
        analysis_dict = self._fallback_analysis(indicators, current_price)
        return TechnicalAnalysis(
            bullish_score=analysis_dict["bullish_score"],
            bearish_score=analysis_dict["bearish_score"],
            confidence=analysis_dict["confidence"],
            recommendation=analysis_dict["recommendation"],
            reasoning=analysis_dict["reasoning"],
            key_findings=analysis_dict.get("key_findings", []),
            supporting_data=indicators
        )
    
    def _empty_analysis(
        self,
        state: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """Return empty analysis when data is insufficient"""
        state["technical_analysis"] = TechnicalAnalysis(
            bullish_score=50.0,
            bearish_score=50.0,
            confidence=0.0,
            recommendation="HOLD",
            reasoning=f"Unable to perform analysis: {reason}",
            key_findings=["Insufficient data"],
            supporting_data={}
        )
        return state


# Instantiate global node (lazy-loaded on first use)
_technical_analyst_node: Optional[TechnicalAnalystNode] = None


def get_technical_analyst_node() -> TechnicalAnalystNode:
    """Get or create Technical Analyst node"""
    global _technical_analyst_node
    if _technical_analyst_node is None:
        _technical_analyst_node = TechnicalAnalystNode()
    return _technical_analyst_node


async def technical_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for LangGraph integration
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with technical_analysis
    """
    node = get_technical_analyst_node()
    return node(state)
