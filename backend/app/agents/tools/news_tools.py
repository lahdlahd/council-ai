"""
News Analysis Tools
Sentiment analysis, macro event assessment, whale activity detection, regulatory tracking

Production-grade with validation and scoring
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SentimentLabel(str, Enum):
    """Sentiment classification"""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


class MacroImpactLevel(str, Enum):
    """Macro economic impact levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class RegulatoryCategory(str, Enum):
    """Regulatory news categories"""
    APPROVAL = "approval"
    RESTRICTION = "restriction"
    INVESTIGATION = "investigation"
    POLICY = "policy"
    COMPLIANCE = "compliance"
    OTHER = "other"


class NewsTools:
    """Suite of news analysis tools"""
    
    # Sentiment keywords (expanded lexicon)
    BULLISH_KEYWORDS = {
        "partnership", "acquisition", "approval", "bullish", "surge", "rally",
        "breakthrough", "wins", "beats", "record", "milestone", "expansion",
        "collaboration", "integration", "upgrade", "launch", "growth", "adoption",
        "positive", "strong", "outperform", "rally", "recovery", "catalyst",
        "momentum", "bull", "gains", "profit", "success", "innovative"
    }
    
    BEARISH_KEYWORDS = {
        "crash", "decline", "drop", "bearish", "sell", "loss", "losses",
        "failure", "scandal", "hack", "exploit", "investigate", "shutdown",
        "restriction", "ban", "negative", "weak", "underperform", "risk",
        "concern", "warning", "bear", "losses", "bankrupt", "default",
        "regulatory", "lawsuit", "probe", "concern", "threat", "crisis"
    }
    
    WHALE_ACTIVITY_KEYWORDS = {
        "whale", "large transaction", "major trade", "big move", "massive",
        "accumulation", "distribution", "smart money", "institution",
        "million", "billion", "massive outflow", "massive inflow",
        "significant volume", "unusual activity"
    }
    
    MACRO_KEYWORDS = {
        "fed", "federal reserve", "interest rate", "inflation", "gdp",
        "employment", "unemployment", "recession", "economy", "macro",
        "central bank", "policy", "stimulus", "quantitative", "taper",
        "cycle", "volatility", "correlation", "market structure"
    }
    
    REGULATORY_KEYWORDS = {
        "sec", "cftc", "regulation", "approved", "approved", "compliance",
        "license", "ban", "restriction", "lawsuit", "investigation",
        "enforcement", "policy", "rule", "framework", "approval"
    }
    
    @staticmethod
    def analyze_sentiment(
        title: str,
        content: str,
        source: str = "unknown"
    ) -> Dict[str, any]:
        """
        Analyze sentiment of news article
        
        Args:
            title: News headline
            content: Article body
            source: News source for context
        
        Returns:
            Dict with sentiment_score, label, confidence, reasoning
        """
        try:
            # Combine title and content, lowercase for analysis
            text = (title + " " + content).lower()
            
            # Count keyword occurrences
            bullish_count = sum(text.count(kw) for kw in NewsTools.BULLISH_KEYWORDS)
            bearish_count = sum(text.count(kw) for kw in NewsTools.BEARISH_KEYWORDS)
            
            # Calculate sentiment score (-1 to +1)
            total_sentiment_words = bullish_count + bearish_count
            
            if total_sentiment_words == 0:
                sentiment_score = 0.0
                confidence = 0.3  # Low confidence if no clear sentiment
            else:
                sentiment_score = (bullish_count - bearish_count) / total_sentiment_words
                confidence = min(total_sentiment_words / 20, 1.0)  # Scale confidence
            
            # Ensure score is in [-1, 1] range
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            # Classify into label
            if sentiment_score > 0.5:
                label = SentimentLabel.VERY_BULLISH
            elif sentiment_score > 0.2:
                label = SentimentLabel.BULLISH
            elif sentiment_score > -0.2:
                label = SentimentLabel.NEUTRAL
            elif sentiment_score > -0.5:
                label = SentimentLabel.BEARISH
            else:
                label = SentimentLabel.VERY_BEARISH
            
            # Build reasoning
            reasoning = f"{bullish_count} positive indicators vs {bearish_count} negative"
            if source.lower() in ["bloomberg", "cnbc", "reuters", "ap"]:
                reasoning += " (trusted financial source)"
            
            return {
                "sentiment_score": float(sentiment_score),
                "label": label.value,
                "confidence": float(confidence),
                "reasoning": reasoning,
                "bullish_count": bullish_count,
                "bearish_count": bearish_count
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment_score": 0.0,
                "label": SentimentLabel.NEUTRAL.value,
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
                "bullish_count": 0,
                "bearish_count": 0
            }
    
    @staticmethod
    def assess_macro_impact(
        title: str,
        content: str,
        symbol: str = ""
    ) -> Dict[str, any]:
        """
        Assess macro-economic impact of news
        
        Args:
            title: News headline
            content: Article body
            symbol: Asset being analyzed (for context)
        
        Returns:
            Dict with impact_level, factors, expected_volatility
        """
        try:
            text = (title + " " + content).lower()
            
            # Check for macro keywords
            macro_mentions = sum(text.count(kw) for kw in NewsTools.MACRO_KEYWORDS)
            
            # Identify specific macro factors
            factors = []
            
            if any(kw in text for kw in ["fed", "federal reserve", "interest rate"]):
                factors.append("Monetary Policy")
            
            if any(kw in text for kw in ["inflation", "cpi", "price"]):
                factors.append("Inflation Data")
            
            if any(kw in text for kw in ["employment", "unemployment", "jobs"]):
                factors.append("Employment")
            
            if any(kw in text for kw in ["gdp", "growth", "recession"]):
                factors.append("Economic Growth")
            
            if any(kw in text for kw in ["stimulus", "quantitative", "taper"]):
                factors.append("Liquidity")
            
            if any(kw in text for kw in ["volatility", "correlation"]):
                factors.append("Market Structure")
            
            # Determine impact level
            if macro_mentions > 5 or len(factors) > 3:
                impact_level = MacroImpactLevel.CRITICAL
                expected_volatility = 0.8
            elif macro_mentions > 3 or len(factors) > 2:
                impact_level = MacroImpactLevel.HIGH
                expected_volatility = 0.6
            elif macro_mentions > 1:
                impact_level = MacroImpactLevel.MEDIUM
                expected_volatility = 0.4
            elif macro_mentions > 0:
                impact_level = MacroImpactLevel.LOW
                expected_volatility = 0.2
            else:
                impact_level = MacroImpactLevel.NONE
                expected_volatility = 0.0
            
            return {
                "impact_level": impact_level.value,
                "factors": factors,
                "expected_volatility": float(expected_volatility),
                "macro_mentions": macro_mentions
            }
            
        except Exception as e:
            logger.error(f"Macro impact assessment failed: {e}")
            return {
                "impact_level": MacroImpactLevel.NONE.value,
                "factors": [],
                "expected_volatility": 0.0,
                "macro_mentions": 0
            }
    
    @staticmethod
    def detect_whale_activity(
        title: str,
        content: str,
        volume_context: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Detect whale (large trader) activity
        
        Args:
            title: News headline
            content: Article body
            volume_context: Current volume (for comparison)
        
        Returns:
            Dict with whale_signal, activity_type, confidence
        """
        try:
            text = (title + " " + content).lower()
            
            # Check for whale indicators
            whale_mentions = sum(text.count(kw) for kw in NewsTools.WHALE_ACTIVITY_KEYWORDS)
            
            # Identify activity type
            activity_type = None
            if any(kw in text for kw in ["accumulation", "buying", "inflow"]):
                activity_type = "accumulation"
            elif any(kw in text for kw in ["distribution", "selling", "outflow"]):
                activity_type = "distribution"
            elif any(kw in text for kw in ["transfer", "movement"]):
                activity_type = "movement"
            
            # Extract numbers if present
            numbers = re.findall(r'\b\d+(?:[,\.]\d+)*\s*(?:million|billion|thousand|M|B|K)\b', text, re.IGNORECASE)
            large_amount = len(numbers) > 0
            
            # Determine signal strength
            if whale_mentions > 2 and large_amount:
                whale_signal = True
                confidence = 0.85
            elif whale_mentions > 1:
                whale_signal = True
                confidence = 0.65
            elif large_amount:
                whale_signal = True
                confidence = 0.5
            else:
                whale_signal = False
                confidence = 0.0
            
            return {
                "whale_signal": whale_signal,
                "activity_type": activity_type,
                "confidence": float(confidence),
                "whale_mentions": whale_mentions,
                "large_amounts_detected": large_amount
            }
            
        except Exception as e:
            logger.error(f"Whale activity detection failed: {e}")
            return {
                "whale_signal": False,
                "activity_type": None,
                "confidence": 0.0,
                "whale_mentions": 0,
                "large_amounts_detected": False
            }
    
    @staticmethod
    def classify_regulatory_news(
        title: str,
        content: str
    ) -> Dict[str, any]:
        """
        Classify and analyze regulatory news
        
        Args:
            title: News headline
            content: Article body
        
        Returns:
            Dict with is_regulatory, category, sentiment, agencies
        """
        try:
            text = (title + " " + content).lower()
            
            # Check if regulatory news
            has_regulatory_keywords = any(kw in text for kw in NewsTools.REGULATORY_KEYWORDS)
            
            if not has_regulatory_keywords:
                return {
                    "is_regulatory": False,
                    "category": None,
                    "sentiment": None,
                    "agencies": [],
                    "impact": None
                }
            
            # Classify category
            if any(kw in text for kw in ["approved", "approval"]):
                category = RegulatoryCategory.APPROVAL
                sentiment = "positive"
            elif any(kw in text for kw in ["ban", "restriction", "restricted"]):
                category = RegulatoryCategory.RESTRICTION
                sentiment = "negative"
            elif any(kw in text for kw in ["investigate", "investigation", "probe"]):
                category = RegulatoryCategory.INVESTIGATION
                sentiment = "negative"
            elif any(kw in text for kw in ["policy", "rule", "framework"]):
                category = RegulatoryCategory.POLICY
                sentiment = "neutral"
            elif any(kw in text for kw in ["compliance", "compliant"]):
                category = RegulatoryCategory.COMPLIANCE
                sentiment = "neutral"
            else:
                category = RegulatoryCategory.OTHER
                sentiment = "neutral"
            
            # Identify agencies
            agencies = []
            if "sec" in text:
                agencies.append("SEC")
            if "cftc" in text:
                agencies.append("CFTC")
            if "occ" in text:
                agencies.append("OCC")
            if "fed" in text or "federal reserve" in text:
                agencies.append("Federal Reserve")
            if "finra" in text:
                agencies.append("FINRA")
            
            return {
                "is_regulatory": True,
                "category": category.value,
                "sentiment": sentiment,
                "agencies": agencies,
                "impact": "high" if category == RegulatoryCategory.APPROVAL else "medium"
            }
            
        except Exception as e:
            logger.error(f"Regulatory classification failed: {e}")
            return {
                "is_regulatory": False,
                "category": None,
                "sentiment": None,
                "agencies": [],
                "impact": None
            }
    
    @staticmethod
    def aggregate_social_sentiment(
        twitter_sentiment: Optional[float] = None,
        reddit_sentiment: Optional[float] = None,
        forum_sentiment: Optional[float] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Aggregate sentiment from multiple social sources
        
        Args:
            twitter_sentiment: Twitter sentiment score (-1 to +1)
            reddit_sentiment: Reddit sentiment score (-1 to +1)
            forum_sentiment: Forum sentiment score (-1 to +1)
            weights: Custom weights for each source
        
        Returns:
            Dict with aggregated_sentiment, source_breakdown, reliability
        """
        try:
            # Default weights
            if weights is None:
                weights = {
                    "twitter": 0.4,      # Twitter = 40% (highest volume)
                    "reddit": 0.35,      # Reddit = 35% (engaged community)
                    "forum": 0.25        # Forums = 25% (niche but informed)
                }
            
            sentiments = {}
            total_weight = 0
            weighted_sum = 0
            
            if twitter_sentiment is not None:
                sentiments["twitter"] = twitter_sentiment
                weight = weights.get("twitter", 0.4)
                weighted_sum += twitter_sentiment * weight
                total_weight += weight
            
            if reddit_sentiment is not None:
                sentiments["reddit"] = reddit_sentiment
                weight = weights.get("reddit", 0.35)
                weighted_sum += reddit_sentiment * weight
                total_weight += weight
            
            if forum_sentiment is not None:
                sentiments["forum"] = forum_sentiment
                weight = weights.get("forum", 0.25)
                weighted_sum += forum_sentiment * weight
                total_weight += weight
            
            if total_weight == 0:
                aggregated = 0.0
                reliability = 0.0
            else:
                aggregated = weighted_sum / total_weight
                reliability = min(len(sentiments) / 3, 1.0)  # Higher with more sources
            
            return {
                "aggregated_sentiment": float(aggregated),
                "source_breakdown": sentiments,
                "reliability": float(reliability),
                "sources_used": len(sentiments),
                "total_weight": float(total_weight)
            }
            
        except Exception as e:
            logger.error(f"Social sentiment aggregation failed: {e}")
            return {
                "aggregated_sentiment": 0.0,
                "source_breakdown": {},
                "reliability": 0.0,
                "sources_used": 0,
                "total_weight": 0.0
            }
    
    @staticmethod
    def calculate_news_impact_score(
        sentiment_score: float,
        macro_impact: str,
        whale_signal: bool,
        regulatory: bool,
        source_credibility: float = 0.7,
        recency_hours: int = 1
    ) -> Dict[str, any]:
        """
        Calculate overall impact score of news
        
        Args:
            sentiment_score: News sentiment (-1 to +1)
            macro_impact: Impact level (critical, high, medium, low, none)
            whale_signal: Is whale activity detected?
            regulatory: Is this regulatory news?
            source_credibility: Source reliability (0-1)
            recency_hours: How recent is the news (for time decay)
        
        Returns:
            Dict with impact_score, urgency, recommendation
        """
        try:
            impact_score = 0.0
            
            # Sentiment contribution
            impact_score += abs(sentiment_score) * 0.3  # 30% from sentiment
            
            # Macro impact contribution
            macro_impact_map = {
                "critical": 1.0,
                "high": 0.75,
                "medium": 0.5,
                "low": 0.25,
                "none": 0.0
            }
            impact_score += macro_impact_map.get(macro_impact, 0.0) * 0.35  # 35% from macro
            
            # Whale signal contribution
            if whale_signal:
                impact_score += 0.2  # 20% bonus for whale activity
            
            # Regulatory contribution
            if regulatory:
                impact_score += 0.15  # 15% bonus for regulatory news
            
            # Source credibility multiplier
            impact_score *= source_credibility
            
            # Time decay (recent news = higher impact)
            time_decay = 1.0 if recency_hours < 1 else 1.0 - (recency_hours / 48)  # 48-hour half-life
            impact_score *= max(time_decay, 0.5)
            
            # Normalize to 0-1
            impact_score = min(impact_score, 1.0)
            
            # Determine urgency
            if impact_score > 0.75:
                urgency = "critical"
            elif impact_score > 0.5:
                urgency = "high"
            elif impact_score > 0.25:
                urgency = "medium"
            else:
                urgency = "low"
            
            # Recommendation
            if impact_score > 0.6 and abs(sentiment_score) > 0.5:
                recommendation = "immediate_action"
            elif impact_score > 0.4:
                recommendation = "monitor_closely"
            else:
                recommendation = "note_for_context"
            
            return {
                "impact_score": float(impact_score),
                "urgency": urgency,
                "recommendation": recommendation,
                "components": {
                    "sentiment_contribution": abs(sentiment_score) * 0.3,
                    "macro_contribution": macro_impact_map.get(macro_impact, 0.0) * 0.35,
                    "whale_bonus": 0.2 if whale_signal else 0.0,
                    "regulatory_bonus": 0.15 if regulatory else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Impact score calculation failed: {e}")
            return {
                "impact_score": 0.0,
                "urgency": "unknown",
                "recommendation": "investigate",
                "components": {}
            }
