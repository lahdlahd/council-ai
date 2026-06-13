"""
News Analyst Agent Node
LangGraph node implementation for news analysis

Responsibilities:
- News sentiment analysis
- Macro-economic event assessment
- Whale activity detection
- Regulatory news tracking
- Social media sentiment aggregation
- Generate market sentiment and event analysis

Output: Updates state.news_analysis with NewsAnalysis object
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.agents.schemas import NewsAnalysis, MarketData
from app.agents.tools.news_tools import NewsTools

logger = logging.getLogger(__name__)


class NewsEvent:
    """Simple news event data class"""
    def __init__(
        self,
        title: str,
        content: str,
        source: str = "unknown",
        timestamp: Optional[datetime] = None,
        url: str = ""
    ):
        self.title = title
        self.content = content
        self.source = source
        self.timestamp = timestamp or datetime.now()
        self.url = url


class NewsAnalystNode:
    """
    LangGraph node for news analysis
    
    Processes market news and generates structured sentiment/event analysis
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize News Analyst
        
        Args:
            model_name: OpenAI model to use
            temperature: LLM temperature (0.7 for balanced analysis)
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1500
        )
        
        self.news_tools = NewsTools()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute news analysis on market events
        
        Args:
            state: Current graph state with market_data
        
        Returns:
            Updated state with news_analysis populated
        """
        try:
            logger.info("News Analyst starting analysis")
            
            # Extract market data from state
            market_data: MarketData = state.get("market_data")
            if not market_data:
                raise ValueError("market_data not found in state")
            
            # Extract news items (if available)
            news_items = market_data.market_news if hasattr(market_data, 'market_news') else []
            
            if not news_items:
                logger.warning("No news items provided")
                return self._empty_analysis(state, "No recent news")
            
            logger.info(f"Analyzing {len(news_items)} news items for {market_data.symbol}")
            
            # Analyze all news items
            news_analysis_data = self._analyze_news_batch(news_items)
            
            # Generate synthesis and recommendation
            analysis = self._generate_analysis(
                market_data,
                news_analysis_data
            )
            
            # Update state
            state["news_analysis"] = analysis
            logger.info(
                f"News analysis complete: {analysis.recommendation} "
                f"(confidence: {analysis.confidence}%)"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"News Analyst error: {str(e)}", exc_info=True)
            state["error_log"].append(f"News Analyst: {str(e)}")
            return self._empty_analysis(state, str(e))
    
    def _analyze_news_batch(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze batch of news items
        
        Returns: Aggregated analysis across all items
        """
        analyses = []
        sentiment_scores = []
        macro_impacts = []
        whale_signals = []
        regulatory_flags = []
        
        for item in news_items:
            try:
                title = item.get("title", "")
                content = item.get("content", "")
                source = item.get("source", "unknown")
                
                if not title:
                    continue
                
                # Sentiment analysis
                sentiment = self.news_tools.analyze_sentiment(title, content, source)
                analyses.append({
                    "title": title,
                    "sentiment": sentiment,
                    "source": source
                })
                sentiment_scores.append(sentiment["sentiment_score"])
                
                # Macro impact assessment
                macro = self.news_tools.assess_macro_impact(title, content)
                macro_impacts.append(macro["impact_level"])
                
                # Whale detection
                whale = self.news_tools.detect_whale_activity(title, content)
                if whale["whale_signal"]:
                    whale_signals.append(whale)
                
                # Regulatory classification
                regulatory = self.news_tools.classify_regulatory_news(title, content)
                if regulatory["is_regulatory"]:
                    regulatory_flags.append(regulatory)
                
            except Exception as e:
                logger.warning(f"Failed to analyze news item: {e}")
                continue
        
        # Aggregate results
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            extreme_bullish = sum(1 for s in sentiment_scores if s > 0.5)
            extreme_bearish = sum(1 for s in sentiment_scores if s < -0.5)
        else:
            avg_sentiment = 0.0
            extreme_bullish = 0
            extreme_bearish = 0
        
        return {
            "analyses": analyses,
            "avg_sentiment": avg_sentiment,
            "sentiment_scores": sentiment_scores,
            "extreme_bullish_count": extreme_bullish,
            "extreme_bearish_count": extreme_bearish,
            "macro_impacts": macro_impacts,
            "whale_signals": whale_signals,
            "regulatory_flags": regulatory_flags,
            "total_items": len(analyses)
        }
    
    def _generate_analysis(
        self,
        market_data: MarketData,
        news_data: Dict[str, Any]
    ) -> NewsAnalysis:
        """
        Generate structured news analysis using LLM synthesis
        
        Args:
            market_data: Current market data
            news_data: Aggregated news analysis
        
        Returns:
            NewsAnalysis object with recommendation and scores
        """
        # Prepare news summary
        news_summary = self._summarize_news(news_data)
        
        # Create prompt for LLM analysis
        prompt_template = ChatPromptTemplate.from_template(
            """You are an expert news analyst. Analyze the following news and market context 
and provide a structured analysis.

Symbol: {symbol}
Current Price: ${current_price:.2f}

News Summary:
{news_summary}

Key Stats:
- Total news items: {total_items}
- Average sentiment: {avg_sentiment:.2f}
- Extreme bullish: {extreme_bullish}
- Extreme bearish: {extreme_bearish}
- Whale activity: {whale_activity}
- Regulatory flags: {regulatory_count}

Provide analysis in this exact JSON format:
{{
  "sentiment_score": <-1.0 to 1.0>,
  "confidence": <0-100>,
  "recommendation": "<BUY|SELL|HOLD>",
  "key_events": [<list of 2-3 major events>],
  "whale_activity": "<high|medium|low|none>",
  "macro_impact": "<critical|high|medium|low|none>",
  "reasoning": "<1 short, punchy sentence (e.g. 'ETF inflows support momentum.')>"
}}

Remember:
- Sentiment score: -1.0 = very bearish, +1.0 = very bullish
- Confidence reflects news clarity and consistency
- Consider event significance, not just volume
- Account for whale activity and regulatory changes
- Consider macro implications"""
        )
        
        try:
            # Call LLM for analysis
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    symbol=market_data.symbol,
                    current_price=market_data.current_price,
                    news_summary=news_summary,
                    total_items=news_data["total_items"],
                    avg_sentiment=news_data["avg_sentiment"],
                    extreme_bullish=news_data["extreme_bullish_count"],
                    extreme_bearish=news_data["extreme_bearish_count"],
                    whale_activity="high" if news_data["whale_signals"] else "low",
                    regulatory_count=len(news_data["regulatory_flags"])
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
                analysis_dict = self._fallback_analysis(news_data)
            
            # Create NewsAnalysis object
            analysis = NewsAnalysis(
                sentiment_score=float(analysis_dict.get("sentiment_score", 0.0)),
                confidence=float(analysis_dict.get("confidence", 50)),
                recommendation=analysis_dict.get("recommendation", "HOLD").upper(),
                key_events=analysis_dict.get("key_events", []),
                whale_activity=analysis_dict.get("whale_activity", "none"),
                macro_impact=analysis_dict.get("macro_impact", "none"),
                reasoning=analysis_dict.get("reasoning", "No reasoning provided")
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to rule-based analysis
            return self._fallback_analysis_to_pydantic(news_data)
    
    def _summarize_news(self, news_data: Dict[str, Any]) -> str:
        """Create human-readable summary of news"""
        summary_lines = []
        
        # Overall sentiment
        avg_sent = news_data["avg_sentiment"]
        if avg_sent > 0.3:
            summary_lines.append(f"Overall: BULLISH (avg sentiment {avg_sent:.2f})")
        elif avg_sent < -0.3:
            summary_lines.append(f"Overall: BEARISH (avg sentiment {avg_sent:.2f})")
        else:
            summary_lines.append(f"Overall: NEUTRAL (avg sentiment {avg_sent:.2f})")
        
        # Sentiment distribution
        extreme_bull = news_data["extreme_bullish_count"]
        extreme_bear = news_data["extreme_bearish_count"]
        if extreme_bull > 0:
            summary_lines.append(f"Bullish signals: {extreme_bull} stories")
        if extreme_bear > 0:
            summary_lines.append(f"Bearish signals: {extreme_bear} stories")
        
        # Macro impacts
        impacts = news_data["macro_impacts"]
        if "critical" in impacts:
            summary_lines.append("⚠️ CRITICAL macro event detected")
        elif "high" in impacts:
            summary_lines.append("📊 High-impact macro news present")
        
        # Whale activity
        if news_data["whale_signals"]:
            whale_types = set()
            for whale in news_data["whale_signals"]:
                if whale.get("activity_type"):
                    whale_types.add(whale["activity_type"])
            summary_lines.append(f"🐋 Whale activity: {', '.join(whale_types)}")
        
        # Regulatory flags
        if news_data["regulatory_flags"]:
            agencies = set()
            for reg in news_data["regulatory_flags"]:
                agencies.update(reg.get("agencies", []))
            summary_lines.append(f"⚖️ Regulatory: {', '.join(agencies)} activity")
        
        # Sample news items
        if news_data["analyses"]:
            summary_lines.append("\nTop stories:")
            for item in news_data["analyses"][:3]:
                summary_lines.append(f"- {item['title'][:80]}... ({item['source']})")
        
        return "\n".join(summary_lines)
    
    def _fallback_analysis(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback analysis if LLM fails"""
        avg_sentiment = news_data["avg_sentiment"]
        
        # Determine recommendation based on sentiment
        if avg_sentiment > 0.3:
            recommendation = "BUY"
            confidence = min(70 + abs(avg_sentiment) * 30, 95)
        elif avg_sentiment < -0.3:
            recommendation = "SELL"
            confidence = min(70 + abs(avg_sentiment) * 30, 95)
        else:
            recommendation = "HOLD"
            confidence = 50
        
        # Adjust for whale signals
        if news_data["whale_signals"]:
            confidence += 10
        
        # Adjust for regulatory flags
        if news_data["regulatory_flags"]:
            confidence += 5
        
        # Whale activity assessment
        if news_data["whale_signals"]:
            whale_activity = "high"
        else:
            whale_activity = "low"
        
        # Macro impact assessment
        impacts = news_data["macro_impacts"]
        if "critical" in impacts:
            macro_impact = "critical"
        elif "high" in impacts:
            macro_impact = "high"
        elif "medium" in impacts:
            macro_impact = "medium"
        else:
            macro_impact = "low"
        
        return {
            "sentiment_score": avg_sentiment,
            "confidence": min(confidence, 100),
            "recommendation": recommendation,
            "key_events": [item["title"] for item in news_data["analyses"][:2]],
            "whale_activity": whale_activity,
            "macro_impact": macro_impact,
            "reasoning": f"Rule-based analysis ({news_data['total_items']} news items, avg sentiment {avg_sentiment:.2f})"
        }
    
    def _fallback_analysis_to_pydantic(
        self,
        news_data: Dict[str, Any]
    ) -> NewsAnalysis:
        """Convert fallback analysis to NewsAnalysis object"""
        analysis_dict = self._fallback_analysis(news_data)
        return NewsAnalysis(
            sentiment_score=analysis_dict["sentiment_score"],
            confidence=analysis_dict["confidence"],
            recommendation=analysis_dict["recommendation"],
            key_events=analysis_dict.get("key_events", []),
            whale_activity=analysis_dict.get("whale_activity", "none"),
            macro_impact=analysis_dict.get("macro_impact", "none"),
            reasoning=analysis_dict["reasoning"]
        )
    
    def _empty_analysis(
        self,
        state: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """Return empty analysis when data is insufficient"""
        state["news_analysis"] = NewsAnalysis(
            sentiment_score=0.0,
            confidence=0.0,
            recommendation="HOLD",
            key_events=["No recent news"],
            whale_activity="none",
            macro_impact="none",
            reasoning=f"Unable to perform analysis: {reason}"
        )
        return state


# Instantiate global node (lazy-loaded on first use)
_news_analyst_node: Optional[NewsAnalystNode] = None


def get_news_analyst_node() -> NewsAnalystNode:
    """Get or create News Analyst node"""
    global _news_analyst_node
    if _news_analyst_node is None:
        _news_analyst_node = NewsAnalystNode()
    return _news_analyst_node


async def news_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for LangGraph integration
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with news_analysis
    """
    node = get_news_analyst_node()
    return node(state)
