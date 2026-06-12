"""
Pydantic schemas for agent analyses and shared state structures.
Used across all agents for consistent data types.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CandleData(BaseModel):
    """OHLCV candle data point"""
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @validator("high")
    def high_is_highest(cls, v, values):
        if "low" in values and v < values["low"]:
            raise ValueError("high must be >= low")
        return v

    @validator("low")
    def low_is_lowest(cls, v, values):
        if "high" in values and v > values["high"]:
            raise ValueError("low must be <= high")
        return v


class TechnicalAnalysis(BaseModel):
    """Output from Technical Analyst Agent"""
    
    # Scores
    bullish_score: float = Field(ge=0, le=100, description="Bullish confidence 0-100")
    bearish_score: float = Field(ge=0, le=100, description="Bearish confidence 0-100")
    confidence: float = Field(ge=0, le=100, description="Overall confidence in analysis")
    
    # Recommendation
    recommendation: str = Field(..., description="BUY, SELL, or HOLD")
    
    # Reasoning
    reasoning: str = Field(..., description="Natural language explanation")
    key_findings: List[str] = Field(default_factory=list)
    
    # Supporting Data
    supporting_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Technical indicators: rsi, macd, ema_50, ema_200, etc"
    )
    
    # Timestamp
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("recommendation")
    def valid_recommendation(cls, v):
        if v not in ["BUY", "SELL", "HOLD"]:
            raise ValueError("recommendation must be BUY, SELL, or HOLD")
        return v
    
    @validator("bullish_score", "bearish_score", pre=True)
    def round_scores(cls, v):
        return round(v, 2)


class NewsAnalysis(BaseModel):
    """Output from News Analyst Agent"""
    
    # Sentiment
    sentiment_score: float = Field(ge=-1, le=1, description="-1 (bearish) to +1 (bullish)")
    confidence: float = Field(ge=0, le=100)
    
    # Recommendation
    recommendation: str = Field(...)
    
    # Reasoning
    reasoning: str
    key_events: List[str] = Field(default_factory=list)
    
    # Market Intelligence
    whale_activity: str = Field(description="BUYING, SELLING, or NEUTRAL")
    macro_impact: str = Field(description="Description of macro impacts")
    
    # Timestamp
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class QuantAnalysis(BaseModel):
    """Output from Quant Analyst Agent"""
    
    # Probability & Value
    probability_score: float = Field(ge=0, le=100, description="Probability of success")
    confidence: float = Field(ge=0, le=100)
    
    # Recommendation
    recommendation: str
    
    # Analysis
    reasoning: str
    historical_pattern: str = Field(description="Name/description of pattern found")
    expected_value: float = Field(description="EV calculation result")
    
    # Correlations
    correlation_analysis: Dict[str, float] = Field(
        default_factory=dict,
        description="Symbol -> correlation coefficient"
    )
    
    # Timestamp
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class RiskAssessment(BaseModel):
    """Output from Risk Manager Agent - VETO ENFORCEMENT"""
    
    # Overall Risk Score (0-100)
    risk_score: float = Field(ge=0, le=100, description="Overall risk score 0-100")
    risk_level: str = Field(
        description="critical, high, medium, low, minimal, or none"
    )
    
    # Component Scores (if available)
    volatility_score: Optional[float] = Field(default=None, ge=0, le=100)
    drawdown_risk: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Position Sizing
    position_size_recommendation: float = Field(
        ge=0,
        description="Recommended maximum position size in USD"
    )
    max_position_allowed: float = Field(
        ge=0,
        le=1.0,
        description="Maximum position as % of account (0.15 = 15%)"
    )
    
    # Approval Status - CRITICAL: This determines if trade is BLOCKED
    approved: bool = Field(
        description="CRITICAL: True if approved, False = VETO (cannot be overridden)"
    )
    veto_reason: str = Field(
        description="Reason for decision (approval or veto)"
    )
    
    # Alternatives
    alternative_suggestions: List[str] = Field(
        default_factory=list,
        description="If rejected: suggested modifications"
    )
    
    # Timestamp
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMessage(BaseModel):
    """Message in the debate"""
    
    agent_id: str
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: str  # ANALYSIS, CHALLENGE, AGREEMENT, REVISION, VOTE, FINAL
    content: str  # Natural language
    confidence: float = Field(ge=0, le=1)
    recommendation: str  # BUY, SELL, HOLD
    reasoning: Dict[str, Any]  # key_points, supporting_data, risk_factors
    reply_to: Optional[str] = None  # Message ID if replying
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Vote(BaseModel):
    """A vote from an agent"""
    
    agent_id: str
    agent_name: str
    vote: str  # BUY, SELL, HOLD, ABSTAIN
    confidence: float = Field(ge=0, le=100)
    weight: float = Field(ge=0.1, le=5.0, description="Voting weight (1.0 = equal)")
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketData(BaseModel):
    """Real-time market data snapshot"""
    
    symbol: str
    current_price: float = Field(gt=0)
    price_24h_high: float = Field(gt=0)
    price_24h_low: float = Field(gt=0)
    volume_24h: float = Field(ge=0)
    volatility: float = Field(ge=0, le=1, description="0=stable, 1=highly volatile")
    
    # Technical indicators (pre-calculated)
    current_rsi: Optional[float] = Field(default=None, ge=0, le=100)
    current_macd: Optional[Dict[str, float]] = None  # {value, signal, histogram}
    current_ema_50: Optional[float] = None
    current_ema_200: Optional[float] = None
    
    # Levels
    support_levels: List[float] = Field(default_factory=list)
    resistance_levels: List[float] = Field(default_factory=list)
    trend_direction: str = Field(description="UP, DOWN, or SIDEWAYS")
    
    # Additional
    market_news_count: int = Field(ge=0)
    market_conditions: str = Field(description="bullish, bearish, volatile, stable")
    
    # Historical data
    historical_candles: List[CandleData] = Field(
        default_factory=list,
        description="Last N candles (typically 200 for full analysis)"
    )


class ExecutionSynthesis(BaseModel):
    """Final synthesis from Execution Agent"""
    
    aggregated_recommendation: str
    weighted_consensus: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    confidence_factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Confidence score breakdown of factors: agreement, risk, volatility, sentiment, accuracy"
    )
    reasoning: str
    key_factors: List[str] = Field(default_factory=list)


class PositionSize(BaseModel):
    """Recommended position sizing"""
    
    percentage_of_portfolio: float = Field(ge=0, le=100)
    quantity: float = Field(ge=0)
    entry_price: float = Field(gt=0)
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None


class FinalDecision(BaseModel):
    """Final council decision"""
    
    action: str  # BUY, SELL, HOLD
    confidence_score: float = Field(ge=0, le=100)
    confidence_factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Confidence score breakdown of factors: agreement, risk, volatility, sentiment, accuracy"
    )
    position_size: PositionSize
    reasoning: str
    key_factors: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReplaySummary(BaseModel):
    """Summary of a replayable council session"""
    session_id: str
    symbol: str
    final_action: str
    confidence_score: float
    trade_status: str  # 'pending', 'executed', 'failed', 'completed'
    realized_pnl: Optional[float] = None
    created_at: datetime


class ReplayTimeline(BaseModel):
    """Full timeline for replaying a council session decision"""
    session_id: str
    symbol: str
    created_at: datetime
    
    # 1. Market state at start of session
    market_state: MarketData
    
    # 2. Initial Opinions (Round 1)
    initial_opinions: Dict[str, Any]
    
    # 3. Debate rounds (Round 2+)
    debate_transcript: List[AgentMessage]
    
    # 4. Voting Tally
    voting_tally: Dict[str, Any]
    
    # 5. Risk Veto verification
    veto_verification: RiskAssessment
    
    # 6. Final Decision Synthesis
    execution_decision: FinalDecision
    
    # 7. Completed Trade Result details (if executed)
    trade_result: Optional[Dict[str, Any]] = None

