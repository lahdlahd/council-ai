import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.agents.schemas import (
    MarketData,
    CandleData,
    TechnicalAnalysis,
    NewsAnalysis,
    QuantAnalysis,
    RiskAssessment,
    AgentMessage,
    FinalDecision,
    PositionSize,
    ReplaySummary,
    ReplayTimeline
)

logger = logging.getLogger(__name__)

class ReplayService:
    """
    Service to retrieve, list, and mock complete Council Session trade replays.
    Supports querying Supabase PostgreSQL tables or falling back to local JSON storage.
    """
    
    def __init__(self, fallback_path: Optional[str] = None):
        if not fallback_path:
            # Place it in the same directory as this file
            fallback_path = os.path.join(os.path.dirname(__file__), "replay_fallback.json")
        self.fallback_path = fallback_path
        
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.supabase_client = None
        self.use_supabase = False
        
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                self.use_supabase = True
                logger.info("ReplayService successfully connected to Supabase.")
            except Exception as e:
                logger.warning(f"ReplayService failed to connect to Supabase: {e}. Using local JSON.")
                
        # Make sure fallback file is initialized with demo data
        self._init_fallback_file()

    def _init_fallback_file(self):
        """Initializes fallback file with detailed realistic mock debate timelines if missing."""
        if os.path.exists(self.fallback_path):
            return
            
        logger.info(f"Initializing replay fallback database file at {self.fallback_path}")
        
        # Scenario 1: Unanimous BUY, Completed Trade with profit
        session_id_1 = "d11b34a6-4be4-42f0-9a2c-e1f4864b22c0"
        created_1 = (datetime.utcnow() - timedelta(days=2)).isoformat()
        timeline_1 = {
            "session_id": session_id_1,
            "symbol": "BTC",
            "created_at": created_1,
            "market_state": {
                "symbol": "BTC",
                "current_price": 43500.0,
                "price_24h_high": 44200.0,
                "price_24h_low": 42900.0,
                "volume_24h": 125000000.0,
                "volatility": 0.22,
                "trend_direction": "UP",
                "market_news_count": 14,
                "market_conditions": "bullish",
                "historical_candles": []
            },
            "initial_opinions": {
                "technical_analyst": {
                    "bullish_score": 85.0,
                    "bearish_score": 15.0,
                    "confidence": 80.0,
                    "recommendation": "BUY",
                    "reasoning": "Golden cross on 4h chart with rising RSI indicators support breakout above resistance.",
                    "key_findings": ["RSI breakout", "EMA cross"],
                    "supporting_data": {}
                },
                "news_analyst": {
                    "sentiment_score": 0.65,
                    "confidence": 75.0,
                    "recommendation": "BUY",
                    "reasoning": "Sentiment is highly positive due to heavy ETF net inflows and rumors of corporate treasury buying.",
                    "key_events": ["ETF Net Inflows", "Treasury Rumors"],
                    "whale_activity": "BUYING",
                    "macro_impact": "Positive structural support"
                },
                "quant_analyst": {
                    "probability_score": 72.0,
                    "confidence": 70.0,
                    "recommendation": "BUY",
                    "reasoning": "Historical pattern matches suggest high probability momentum continuation with expected value of 1.4.",
                    "historical_pattern": "Momentum Breakout",
                    "expected_value": 1.4,
                    "correlation_analysis": {}
                }
            },
            "debate_transcript": [
                {
                    "agent_id": "news_analyst",
                    "agent_name": "News Analyst",
                    "message_type": "ANALYSIS",
                    "content": "Initial Analysis: BUY. Sentiment is highly positive due to heavy ETF net inflows.",
                    "confidence": 0.75,
                    "recommendation": "BUY",
                    "reasoning": {}
                },
                {
                    "agent_id": "quant_analyst",
                    "agent_name": "Quant Analyst",
                    "message_type": "ANALYSIS",
                    "content": "Initial Analysis: BUY. Expected value suggests upward bias.",
                    "confidence": 0.70,
                    "recommendation": "BUY",
                    "reasoning": {}
                },
                {
                    "agent_id": "technical_analyst",
                    "agent_name": "Technical Analyst",
                    "message_type": "AGREEMENT",
                    "content": "I agree with the News Analyst. The heavy volume breakout matches the structural ETF flows.",
                    "confidence": 0.85,
                    "recommendation": "BUY",
                    "reasoning": {}
                }
            ],
            "voting_tally": {
                "votes": {
                    "technical_analyst": {"vote": "BUY", "weight": 1.2, "confidence": 80.0},
                    "quant_analyst": {"vote": "BUY", "weight": 1.1, "confidence": 72.0},
                    "news_analyst": {"vote": "BUY", "weight": 1.0, "confidence": 75.0}
                },
                "proposed_action": "BUY"
            },
            "veto_verification": {
                "risk_score": 25.0,
                "risk_level": "low",
                "position_size_recommendation": 15000.0,
                "max_position_allowed": 0.15,
                "approved": True,
                "veto_reason": "Approved: Risk metrics are well within safe thresholds."
            },
            "execution_decision": {
                "action": "BUY",
                "confidence_score": 88.65,
                "confidence_factors": {
                    "raw_scores": {
                        "agent_agreement": 100.0,
                        "risk_score_factor": 75.0,
                        "volatility_factor": 78.0,
                        "sentiment_stability": 75.0,
                        "historical_accuracy": 69.0
                    },
                    "weighted_contributions": {
                        "agent_agreement": 40.0,
                        "risk_score_factor": 15.0,
                        "volatility_factor": 11.7,
                        "sentiment_stability": 11.25,
                        "historical_accuracy": 6.9
                    },
                    "total_score": 84.85
                },
                "position_size": {
                    "percentage_of_portfolio": 12.0,
                    "quantity": 0.2758,
                    "entry_price": 43500.0,
                    "target_price": 46500.0,
                    "stop_loss": 41800.0
                },
                "reasoning": "The committee reached a unanimous agreement to BUY BTC. Positive ETF inflows support technical breakout signals. Low risk volatility allows high positioning.",
                "key_factors": ["Unanimous consensus", "ETF inflows breakout", "Low risk profile"]
            },
            "trade_result": {
                "status": "completed",
                "entry_price": 43500.0,
                "quantity": 0.2758,
                "exit_price": 46500.0,
                "exit_timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "realized_pnl": 827.40,
                "notes": "Target hit. Trade exited automatically at $46,500."
            }
        }
        
        # Scenario 2: VETOED Decision
        session_id_2 = "bc3f4124-7f12-4cf4-912b-2a21b44b20cf"
        created_2 = (datetime.utcnow() - timedelta(days=4)).isoformat()
        timeline_2 = {
            "session_id": session_id_2,
            "symbol": "ETH",
            "created_at": created_2,
            "market_state": {
                "symbol": "ETH",
                "current_price": 2800.0,
                "price_24h_high": 2950.0,
                "price_24h_low": 2600.0,
                "volume_24h": 450000000.0,
                "volatility": 0.55, # high volatility
                "trend_direction": "DOWN",
                "market_news_count": 25,
                "market_conditions": "volatile",
                "historical_candles": []
            },
            "initial_opinions": {
                "technical_analyst": {
                    "bullish_score": 65.0,
                    "bearish_score": 35.0,
                    "confidence": 60.0,
                    "recommendation": "BUY",
                    "reasoning": "Aggressive oversold bounce support at $2,800. Fast reversal likely.",
                    "key_findings": ["Support bounce", "Oversold RSI"],
                    "supporting_data": {}
                },
                "news_analyst": {
                    "sentiment_score": -0.4,
                    "confidence": 70.0,
                    "recommendation": "HOLD",
                    "reasoning": "High fear surrounding a major smart contract exploit report. Sentiment is highly negative.",
                    "key_events": ["Exploit reports", "FUD selling"],
                    "whale_activity": "SELLING",
                    "macro_impact": "Critical negative catalyst"
                },
                "quant_analyst": {
                    "probability_score": 52.0,
                    "confidence": 60.0,
                    "recommendation": "HOLD",
                    "reasoning": "Model reports low probability of bounce success due to high drawdown speed.",
                    "historical_pattern": "Falling Knife",
                    "expected_value": -0.1,
                    "correlation_analysis": {}
                }
            },
            "debate_transcript": [
                {
                    "agent_id": "technical_analyst",
                    "agent_name": "Technical Analyst",
                    "message_type": "ANALYSIS",
                    "content": "Initial Analysis: BUY. Oversold support indicates bounce potential.",
                    "confidence": 0.60,
                    "recommendation": "BUY",
                    "reasoning": {}
                },
                {
                    "agent_id": "news_analyst",
                    "agent_name": "News Analyst",
                    "message_type": "CHALLENGE",
                    "content": "I challenge Technical Analyst. We are dealing with an active exploit report; buying now is highly speculative.",
                    "confidence": 0.70,
                    "recommendation": "HOLD",
                    "reasoning": {}
                },
                {
                    "agent_id": "technical_analyst",
                    "agent_name": "Technical Analyst",
                    "message_type": "REVISION",
                    "content": "Given the exploit detail, I will revise my recommendation to HOLD until smart contract integrity is confirmed.",
                    "confidence": 0.70,
                    "recommendation": "HOLD",
                    "reasoning": {}
                }
            ],
            "voting_tally": {
                "votes": {
                    "technical_analyst": {"vote": "HOLD", "weight": 1.2, "confidence": 70.0},
                    "quant_analyst": {"vote": "HOLD", "weight": 1.1, "confidence": 60.0},
                    "news_analyst": {"vote": "HOLD", "weight": 1.0, "confidence": 70.0}
                },
                "proposed_action": "HOLD"
            },
            "veto_verification": {
                "risk_score": 85.0,
                "risk_level": "critical",
                "position_size_recommendation": 0.0,
                "max_position_allowed": 0.0,
                "approved": False,
                "veto_reason": "VETO: Volatility is 0.55 and risk score is 85/100, which exceeds maximum drawdown limits. Exploits present systemic risk."
            },
            "execution_decision": {
                "action": "HOLD",
                "confidence_score": 45.3,
                "confidence_factors": {
                    "raw_scores": {"agent_agreement": 100.0, "risk_score_factor": 15.0, "volatility_factor": 45.0, "sentiment_stability": 40.0, "historical_accuracy": 69.0},
                    "weighted_contributions": {"agent_agreement": 40.0, "risk_score_factor": 3.0, "volatility_factor": 6.75, "sentiment_stability": 6.0, "historical_accuracy": 6.9},
                    "total_score": 62.65
                },
                "position_size": {
                    "percentage_of_portfolio": 0.0,
                    "quantity": 0.0,
                    "entry_price": 2800.0,
                    "target_price": None,
                    "stop_loss": None
                },
                "reasoning": "The trade proposal was rejected due to a Risk Manager VETO. The committee agreed on HOLD. Smart contract exploit reports and 55% volatility create critical downside risk.",
                "key_factors": ["Risk Manager VETO", "Exploit risk", "High market volatility"]
            },
            "trade_result": {
                "status": "failed",
                "entry_price": 2800.0,
                "quantity": 0.0,
                "exit_price": None,
                "exit_timestamp": None,
                "realized_pnl": 0.0,
                "notes": "VETOED by Risk Manager. No execution occurred."
            }
        }
        
        # Save both mock timeline sessions
        mock_db = {session_id_1: timeline_1, session_id_2: timeline_2}
        with open(self.fallback_path, "w") as f:
            json.dump(mock_db, f, indent=2)
            
        logger.info("Mock database initialized successfully.")

    def list_replays(self) -> List[ReplaySummary]:
        """Lists all replayable sessions with summary statistics."""
        if self.use_supabase:
            try:
                # Query Supabase council_sessions joined with trades
                res = self.supabase_client.table("council_sessions").select(
                    "id", "symbol", "final_decision", "final_decision_confidence", "created_at",
                    "trades(status, realized_pnl)"
                ).eq("status", "completed").execute()
                
                summaries = []
                if res.data:
                    for row in res.data:
                        trade_info = row.get("trades", [{}])
                        # Supabase might return trades as list or single object
                        if isinstance(trade_info, list) and len(trade_info) > 0:
                            trade = trade_info[0]
                        else:
                            trade = trade_info if isinstance(trade_info, dict) else {}
                            
                        summaries.append(ReplaySummary(
                            session_id=row["id"],
                            symbol=row["symbol"],
                            final_action=row["final_decision"] or "HOLD",
                            confidence_score=float(row["final_decision_confidence"] or 0.0),
                            trade_status=trade.get("status", "completed"),
                            realized_pnl=float(trade.get("realized_pnl")) if trade.get("realized_pnl") is not None else None,
                            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                        ))
                    return summaries
            except Exception as e:
                logger.error(f"Failed to list replays from Supabase: {e}. Falling back to local file.")
                
        # Fallback to local file
        try:
            with open(self.fallback_path, "r") as f:
                db = json.load(f)
            summaries = []
            for sid, timeline in db.items():
                tr = timeline.get("trade_result", {})
                summaries.append(ReplaySummary(
                    session_id=sid,
                    symbol=timeline["symbol"],
                    final_action=timeline["execution_decision"]["action"],
                    confidence_score=timeline["execution_decision"]["confidence_score"],
                    trade_status=tr.get("status", "completed"),
                    realized_pnl=tr.get("realized_pnl"),
                    created_at=datetime.fromisoformat(timeline["created_at"].replace("Z", "+00:00"))
                ))
            # Sort by date descending
            summaries.sort(key=lambda s: s.created_at, reverse=True)
            return summaries
        except Exception as e:
            logger.error(f"Failed to read local fallback replays: {e}")
            return []

    def get_replay_timeline(self, session_id: str) -> Optional[ReplayTimeline]:
        """Gets the detailed timeline of a specific council session by ID."""
        if self.use_supabase:
            try:
                # 1. Fetch Session
                sess_res = self.supabase_client.table("council_sessions").select("*").eq("id", session_id).execute()
                if sess_res.data:
                    sess = sess_res.data[0]
                    
                    # 2. Fetch Debates
                    deb_res = self.supabase_client.table("agent_debates").select("*").eq("session_id", session_id).order("spoken_at", desc=False).execute()
                    
                    # 3. Fetch Votes
                    vote_res = self.supabase_client.table("votes").select("*").eq("session_id", session_id).execute()
                    
                    # 4. Fetch Decision
                    dec_res = self.supabase_client.table("council_decisions").select("*").eq("session_id", session_id).execute()
                    
                    # 5. Fetch Trade
                    trade_res = self.supabase_client.table("trades").select("*").eq("session_id", session_id).execute()
                    
                    # Parse and construct the Pydantic timeline object
                    market_context = sess.get("market_context", {})
                    market_data = MarketData(**market_context) if market_context else None
                    
                    # Construct initial opinions (Round 1 debates)
                    initial_opinions = {}
                    debate_transcript = []
                    
                    for row in (deb_res.data or []):
                        msg = AgentMessage(
                            agent_id=row["agent_id"], # Note: UUID converted to str
                            agent_name=row.get("notes") or "Agent", # fallback name
                            timestamp=datetime.fromisoformat(row["spoken_at"].replace("Z", "+00:00")),
                            message_type=row["message_type"].upper(),
                            content=row["content"],
                            confidence=float(row["confidence_score"]) / 100.0,
                            recommendation=row["recommendation"],
                            reasoning=row.get("reasoning", {})
                        )
                        debate_transcript.append(msg)
                        
                        # Extract Round 1 as initial opinions
                        if row["message_type"] == "analysis":
                            role_key = msg.agent_id.lower().replace(" ", "_")
                            initial_opinions[role_key] = {
                                "recommendation": msg.recommendation,
                                "confidence": float(row["confidence_score"]),
                                "reasoning": msg.content,
                                "key_findings": msg.reasoning.get("key_points", []),
                                "supporting_data": msg.reasoning.get("supporting_data", {})
                            }
                            
                    # Votes
                    votes = {}
                    for row in (vote_res.data or []):
                        votes[row["agent_id"]] = {
                            "vote": row["vote"],
                            "weight": float(row["weight"]),
                            "confidence": float(row["confidence"])
                        }
                    voting_tally = {
                        "votes": votes,
                        "proposed_action": dec_res.data[0]["final_action"] if dec_res.data else "HOLD"
                    }
                    
                    # Veto validation
                    dec_row = dec_res.data[0] if dec_res.data else {}
                    veto_verification = RiskAssessment(
                        risk_score=float(dec_row.get("risk_score", 0.0)),
                        risk_level="high" if dec_row.get("risk_score", 0.0) > 50 else "low",
                        position_size_recommendation=float(dec_row.get("position_size", 0.0)),
                        max_position_allowed=0.15,
                        approved=bool(dec_row.get("risk_approved", True)),
                        veto_reason=dec_row.get("veto_reason", "Approved")
                    )
                    
                    # Execution decision
                    factors = dec_row.get("confidence_factors", {})
                    execution_decision = FinalDecision(
                        action=dec_row.get("final_action", "HOLD"),
                        confidence_score=float(dec_row.get("confidence_score", 0.0)),
                        confidence_factors=factors,
                        position_size=PositionSize(
                            percentage_of_portfolio=float(dec_row.get("position_size", 0.0)),
                            quantity=0.0,
                            entry_price=market_data.current_price if market_data else 0.0
                        ),
                        reasoning=dec_row.get("executive_summary", "No decision reasoning"),
                        key_factors=dec_row.get("key_factors", [])
                    )
                    
                    # Trade result
                    trade_result = None
                    if trade_res.data:
                        tr = trade_res.data[0]
                        trade_result = {
                            "status": tr["status"],
                            "entry_price": float(tr["entry_price"]),
                            "quantity": float(tr["quantity"]),
                            "exit_price": float(tr["exit_price"]) if tr.get("exit_price") else None,
                            "exit_timestamp": tr.get("exit_timestamp"),
                            "realized_pnl": float(tr["realized_pnl"]) if tr.get("realized_pnl") is not None else 0.0,
                            "notes": tr.get("execution_notes", "")
                        }
                        
                    return ReplayTimeline(
                        session_id=session_id,
                        symbol=sess["symbol"],
                        created_at=datetime.fromisoformat(sess["created_at"].replace("Z", "+00:00")),
                        market_state=market_data,
                        initial_opinions=initial_opinions,
                        debate_transcript=debate_transcript,
                        voting_tally=voting_tally,
                        veto_verification=veto_verification,
                        execution_decision=execution_decision,
                        trade_result=trade_result
                    )
            except Exception as e:
                logger.error(f"Failed to fetch replay {session_id} from Supabase: {e}. Falling back to local file.")
                
        # Fallback to local file
        try:
            with open(self.fallback_path, "r") as f:
                db = json.load(f)
            if session_id in db:
                sess_data = db[session_id]
                
                # Parse models
                m_state = MarketData(**sess_data["market_state"])
                
                transcript = []
                for msg in sess_data["debate_transcript"]:
                    transcript.append(AgentMessage(
                        agent_id=msg["agent_id"],
                        agent_name=msg["agent_name"],
                        message_type=msg["message_type"],
                        content=msg["content"],
                        confidence=msg["confidence"],
                        recommendation=msg["recommendation"],
                        reasoning={}
                    ))
                    
                veto = RiskAssessment(**sess_data["veto_verification"])
                
                # Setup Position Size properly for validation
                size_data = sess_data["execution_decision"]["position_size"]
                pos_size = PositionSize(
                    percentage_of_portfolio=size_data["percentage_of_portfolio"],
                    quantity=size_data["quantity"],
                    entry_price=size_data["entry_price"],
                    target_price=size_data.get("target_price"),
                    stop_loss=size_data.get("stop_loss")
                )
                
                exec_decision = FinalDecision(
                    action=sess_data["execution_decision"]["action"],
                    confidence_score=sess_data["execution_decision"]["confidence_score"],
                    confidence_factors=sess_data["execution_decision"].get("confidence_factors", {}),
                    position_size=pos_size,
                    reasoning=sess_data["execution_decision"]["reasoning"],
                    key_factors=sess_data["execution_decision"]["key_factors"]
                )
                
                return ReplayTimeline(
                    session_id=session_id,
                    symbol=sess_data["symbol"],
                    created_at=datetime.fromisoformat(sess_data["created_at"].replace("Z", "+00:00")),
                    market_state=m_state,
                    initial_opinions=sess_data["initial_opinions"],
                    debate_transcript=transcript,
                    voting_tally=sess_data["voting_tally"],
                    veto_verification=veto,
                    execution_decision=exec_decision,
                    trade_result=sess_data.get("trade_result")
                )
        except Exception as e:
            logger.error(f"Failed to load replay {session_id} from JSON: {e}")
            
        return None

    def run_demo_session(self, scenario: str) -> str:
        """
        Simulates running a new live debate session for a scenario (rally or crash)
        and saves it to the fallback database. Returns the generated session_id.
        """
        import uuid
        if scenario not in ["rally", "crash"]:
            raise ValueError(f"Unknown scenario: {scenario}")
            
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        if scenario == "rally":
            timeline = {
                "session_id": session_id,
                "symbol": "BTC",
                "created_at": created_at,
                "market_state": {
                    "symbol": "BTC",
                    "current_price": 42000.0,
                    "price_24h_high": 42500.0,
                    "price_24h_low": 40800.0,
                    "volume_24h": 150000000.0,
                    "volatility": 0.20,
                    "trend_direction": "UP",
                    "market_news_count": 18,
                    "market_conditions": "bullish",
                    "historical_candles": []
                },
                "initial_opinions": {
                    "technical_analyst": {
                        "bullish_score": 85.0,
                        "bearish_score": 10.0,
                        "confidence": 85.0,
                        "recommendation": "BUY",
                        "reasoning": "Strong trend confirmation above EMA-50 and EMA-200. Golden cross on 4h.",
                        "key_findings": ["EMA Cross", "Bullish RSI"],
                        "supporting_data": {}
                    },
                    "news_analyst": {
                        "sentiment_score": 0.90,
                        "confidence": 90.0,
                        "recommendation": "BUY",
                        "reasoning": "Institutional ETF approvals and record inflows create massive supply shock bullish sentiment.",
                        "key_events": ["SEC Spot Approval"],
                        "whale_activity": "BUYING",
                        "macro_impact": "Positive supply shock"
                    },
                    "quant_analyst": {
                        "probability_score": 82.0,
                        "confidence": 80.0,
                        "recommendation": "BUY",
                        "reasoning": "High probability momentum continuation. Statistics show 82% success rate, expected value +1.85.",
                        "historical_pattern": "Momentum Breakout",
                        "expected_value": 1.85,
                        "correlation_analysis": {}
                    }
                },
                "debate_transcript": [
                    {
                        "agent_id": "technical_analyst",
                        "agent_name": "Technical Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: BUY. Strong trend confirmation above EMA-50 and EMA-200. Golden cross on 4h.",
                        "confidence": 0.85,
                        "recommendation": "BUY",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "news_analyst",
                        "agent_name": "News Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: BUY. Institutional ETF approvals and record inflows create massive supply shock bullish sentiment.",
                        "confidence": 0.90,
                        "recommendation": "BUY",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "quant_analyst",
                        "agent_name": "Quant Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: BUY. High probability momentum continuation. Statistics show 82% success rate, expected value +1.85.",
                        "confidence": 0.80,
                        "recommendation": "BUY",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "news_analyst",
                        "agent_name": "News Analyst",
                        "message_type": "AGREEMENT",
                        "content": "I agree with Quant Analyst. ETF flows represent sticky capital, supporting positive momentum.",
                        "confidence": 0.95,
                        "recommendation": "BUY",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "quant_analyst",
                        "agent_name": "Quant Analyst",
                        "message_type": "AGREEMENT",
                        "content": "Maintaining BUY. Standard deviation is low. Sentiment is extremely stable.",
                        "confidence": 0.85,
                        "recommendation": "BUY",
                        "reasoning": {}
                    }
                ],
                "voting_tally": {
                    "votes": {
                        "technical_analyst": {"vote": "BUY", "weight": 1.2, "confidence": 85.0},
                        "quant_analyst": {"vote": "BUY", "weight": 1.1, "confidence": 80.0},
                        "news_analyst": {"vote": "BUY", "weight": 1.0, "confidence": 90.0}
                    },
                    "proposed_action": "BUY"
                },
                "veto_verification": {
                    "risk_score": 18.0,
                    "risk_level": "low",
                    "position_size_recommendation": 20000.0,
                    "max_position_allowed": 0.20,
                    "approved": True,
                    "veto_reason": "Approved: Risk metrics are highly favorable. Max sizing of 20% allowed."
                },
                "execution_decision": {
                    "action": "BUY",
                    "confidence_score": 91.25,
                    "confidence_factors": {
                        "raw_scores": {
                            "agent_agreement": 100.0,
                            "risk_score_factor": 82.0,
                            "volatility_factor": 80.0,
                            "sentiment_stability": 90.0,
                            "historical_accuracy": 69.0
                        },
                        "weighted_contributions": {
                            "agent_agreement": 40.0,
                            "risk_score_factor": 16.4,
                            "volatility_factor": 12.0,
                            "sentiment_stability": 13.5,
                            "historical_accuracy": 6.9
                        },
                        "total_score": 91.25
                    },
                    "position_size": {
                        "percentage_of_portfolio": 16.0,
                        "quantity": 0.7619,
                        "entry_price": 42000.0,
                        "target_price": 45500.0,
                        "stop_loss": 40500.0
                    },
                    "reasoning": "The committee reached a unanimous BUY decision. Structural institutional ETF demand creates a breakout setup. Low risk score authorizes a large position size.",
                    "key_factors": ["Spot ETF approval", "Unanimous committee consensus", "High sentiment stability", "Low risk profile"]
                },
                "trade_result": {
                    "status": "executed",
                    "entry_price": 42000.0,
                    "quantity": 0.7619,
                    "exit_price": None,
                    "exit_timestamp": None,
                    "realized_pnl": 0.0,
                    "notes": "Order executed at $42,000. Pending target $45,500."
                }
            }
        else: # crash
            timeline = {
                "session_id": session_id,
                "symbol": "ETH",
                "created_at": created_at,
                "market_state": {
                    "symbol": "ETH",
                    "current_price": 3100.0,
                    "price_24h_high": 3350.0,
                    "price_24h_low": 3050.0,
                    "volume_24h": 98000000.0,
                    "volatility": 0.48,
                    "trend_direction": "DOWN",
                    "market_news_count": 18,
                    "market_conditions": "volatile",
                    "historical_candles": []
                },
                "initial_opinions": {
                    "technical_analyst": {
                        "bullish_score": 65.0,
                        "bearish_score": 35.0,
                        "confidence": 65.0,
                        "recommendation": "BUY",
                        "reasoning": "RSI is oversold at 28, indicating bounce potential near support $3,050.",
                        "key_findings": ["Oversold RSI", "Support Level"],
                        "supporting_data": {}
                    },
                    "news_analyst": {
                        "sentiment_score": -0.80,
                        "confidence": 80.0,
                        "recommendation": "HOLD",
                        "reasoning": "Regulatory ETF delays and $250M whale inflows to Coinbase create heavy selling bias.",
                        "key_events": ["ETF Delays", "Whale Coinbase Inflow"],
                        "whale_activity": "SELLING",
                        "macro_impact": "Heavy downward pressure"
                    },
                    "quant_analyst": {
                        "probability_score": 30.0,
                        "confidence": 70.0,
                        "recommendation": "HOLD",
                        "reasoning": "Historical crash correlation analysis indicates momentum is negative, expected value falls to -0.12.",
                        "historical_pattern": "Momentum Collapse",
                        "expected_value": -0.12,
                        "correlation_analysis": {}
                    }
                },
                "debate_transcript": [
                    {
                        "agent_id": "technical_analyst",
                        "agent_name": "Technical Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: BUY. RSI is oversold at 28, indicating bounce potential near support $3,050.",
                        "confidence": 0.65,
                        "recommendation": "BUY",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "news_analyst",
                        "agent_name": "News Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: HOLD. Regulatory ETF delays and $250M whale inflows to Coinbase create heavy selling bias.",
                        "confidence": 0.80,
                        "recommendation": "HOLD",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "quant_analyst",
                        "agent_name": "Quant Analyst",
                        "message_type": "ANALYSIS",
                        "content": "Initial Analysis: HOLD. Historical crash correlation analysis indicates momentum is negative, expected value falls to -0.12.",
                        "confidence": 0.70,
                        "recommendation": "HOLD",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "news_analyst",
                        "agent_name": "News Analyst",
                        "message_type": "CHALLENGE",
                        "content": "Replying to Technical Analyst. Buying oversold support ignores the fact that whales are dumping. Sentiment is negative.",
                        "confidence": 0.85,
                        "recommendation": "HOLD",
                        "reasoning": {}
                    },
                    {
                        "agent_id": "technical_analyst",
                        "agent_name": "Technical Analyst",
                        "message_type": "REVISION",
                        "content": "Given whale outflows and quant statistics, I revise my stance from BUY to HOLD. Protecting capital is priority.",
                        "confidence": 0.75,
                        "recommendation": "HOLD",
                        "reasoning": {}
                    }
                ],
                "voting_tally": {
                    "votes": {
                        "technical_analyst": {"vote": "HOLD", "weight": 1.2, "confidence": 75.0},
                        "quant_analyst": {"vote": "HOLD", "weight": 1.1, "confidence": 70.0},
                        "news_analyst": {"vote": "HOLD", "weight": 1.0, "confidence": 80.0}
                    },
                    "proposed_action": "HOLD"
                },
                "veto_verification": {
                    "risk_score": 82.0,
                    "risk_level": "critical",
                    "position_size_recommendation": 0.0,
                    "max_position_allowed": 0.0,
                    "approved": False,
                    "veto_reason": "VETO: Portfolio drawdown limits breached. High volatility (0.48) and whale selling create excessive loss risk."
                },
                "execution_decision": {
                    "action": "HOLD",
                    "confidence_score": 64.30,
                    "confidence_factors": {
                        "raw_scores": {
                            "agent_agreement": 100.0,
                            "risk_score_factor": 18.0,
                            "volatility_factor": 52.0,
                            "sentiment_stability": 42.0,
                            "historical_accuracy": 69.0
                        },
                        "weighted_contributions": {
                            "agent_agreement": 40.0,
                            "risk_score_factor": 3.6,
                            "volatility_factor": 7.8,
                            "sentiment_stability": 6.3,
                            "historical_accuracy": 6.9
                        },
                        "total_score": 64.30
                    },
                    "position_size": {
                        "percentage_of_portfolio": 0.0,
                        "quantity": 0.0,
                        "entry_price": 3100.0,
                        "target_price": None,
                        "stop_loss": None
                    },
                    "reasoning": "The committee reached a HOLD consensus due to the Risk VETO. Smart contract ETF delay rumors and whale exchange inflows present excessive downside risks.",
                    "key_factors": ["Risk Manager VETO", "Whale selling inflows", "High volatility metrics"]
                },
                "trade_result": {
                    "status": "failed",
                    "entry_price": 3100.0,
                    "quantity": 0.0,
                    "exit_price": None,
                    "exit_timestamp": None,
                    "realized_pnl": 0.0,
                    "notes": "VETOED by Risk Manager. No execution occurred."
                }
            }

        # Save to fallback DB
        try:
            with open(self.fallback_path, "r") as f:
                db = json.load(f)
        except Exception:
            db = {}
            
        db[session_id] = timeline
        
        with open(self.fallback_path, "w") as f:
            json.dump(db, f, indent=2)
            
        logger.info(f"Demo session {session_id} successfully created and written to local fallback DB.")
        return session_id

    def mock_complete_trade(self, session_id: str, exit_price: float) -> bool:
        """Simulates completion of an active trade, calculating P&L (used for demo)."""
        # Load from file
        try:
            with open(self.fallback_path, "r") as f:
                db = json.load(f)
                
            if session_id in db:
                sess_data = db[session_id]
                tr = sess_data.get("trade_result", {})
                
                if tr and tr.get("status") == "completed":
                    # Already completed
                    return True
                    
                # Calculate P&L
                size_data = sess_data["execution_decision"]["position_size"]
                entry_price = size_data["entry_price"]
                quantity = size_data["quantity"]
                action = sess_data["execution_decision"]["action"]
                
                if action == "BUY":
                    pnl = (exit_price - entry_price) * quantity
                elif action == "SELL":
                    pnl = (entry_price - exit_price) * quantity
                else:
                    pnl = 0.0
                    
                sess_data["trade_result"] = {
                    "status": "completed",
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "exit_price": exit_price,
                    "exit_timestamp": datetime.utcnow().isoformat(),
                    "realized_pnl": round(pnl, 2),
                    "notes": f"Demo simulated exit. Price moved from ${entry_price:.2f} to ${exit_price:.2f}."
                }
                
                # Write back
                with open(self.fallback_path, "w") as f:
                    json.dump(db, f, indent=2)
                return True
        except Exception as e:
            logger.error(f"Failed to mock complete trade for {session_id}: {e}")
            
        return False
