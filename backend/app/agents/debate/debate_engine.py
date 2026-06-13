"""
Live Debate Engine
LangGraph implementation for multi-agent coordination, sequential debate,
voting, and consensus synthesis.
"""

import logging
from typing import Dict, Any, List, Optional, Annotated
import operator
from datetime import datetime
import json

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.agents.schemas import (
    MarketData,
    TechnicalAnalysis,
    NewsAnalysis,
    QuantAnalysis,
    RiskAssessment,
    ExecutionSynthesis,
    FinalDecision,
    AgentMessage,
    Vote
)
from app.agents.technical_analyst.node import technical_analyst_node
from app.agents.news_analyst.node import news_analyst_node
from app.agents.quant_analyst.node import quant_analyst_node
from app.agents.risk_analyst.node import risk_manager_node
from app.agents.execution_agent.node import execution_agent_node

logger = logging.getLogger(__name__)


from typing import TypedDict

# 1. State Definition
class AgentState(TypedDict, total=False):
    """
    State representing the current investment committee session.
    """
    session_id: Optional[str]
    user_id: Optional[str]
    market_data: MarketData
    
    # Analyst outputs
    technical_analysis: Optional[TechnicalAnalysis]
    news_analysis: Optional[NewsAnalysis]
    quant_analysis: Optional[QuantAnalysis]
    risk_assessment: Optional[RiskAssessment]
    execution_synthesis: Optional[ExecutionSynthesis]
    
    # Debate & Voting
    messages: List[AgentMessage]
    votes: Dict[str, Vote]
    
    # Loop controls
    current_round: int
    max_rounds: int
    consensus_level: float
    
    # Portfolio context
    account_size: float
    current_holdings: Dict[str, float]
    current_equity: float
    
    # Outputs
    proposed_action: str
    final_decision: Optional[FinalDecision]
    
    error_log: List[str]


# 2. Debate Node Wrappers to support multi-round analysis
class DebateAgentWrapper:
    """
    Wraps standard analyst nodes to provide round-aware debate contributions.
    - Round 1: Runs the standard node, appends an ANALYSIS message.
    - Round 2+: Runs an LLM call over the entire debate thread to CHALLENGE, AGREE, or REVISE.
    """
    
    def __init__(self, agent_name: str, core_node_fn: Any, model_name: str = "gpt-4"):
        self.agent_name = agent_name
        self.core_node_fn = core_node_fn
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.7)
        
    async def __call__(self, state: AgentState) -> AgentState:
        current_round = state.get("current_round", 1)
        logger.info(f"[{self.agent_name}] running in Round {current_round}")
        
        # Initialize messages list if not present
        if "messages" not in state:
            state["messages"] = []
            
        if current_round == 1:
            # Run the baseline analyst node
            state = await self.core_node_fn(state)
            
            # Extract analysis output
            analysis = self._get_analysis_from_state(state)
            if not analysis:
                return state
                
            # Create ANALYSIS message
            msg = AgentMessage(
                agent_id=self.agent_name.lower().replace(" ", "_"),
                agent_name=self.agent_name,
                message_type="ANALYSIS",
                content=analysis.reasoning,
                confidence=analysis.confidence / 100.0,
                recommendation=analysis.recommendation,
                reasoning={
                    "key_points": getattr(analysis, "key_findings", getattr(analysis, "key_events", [])),
                    "supporting_data": getattr(analysis, "supporting_data", {})
                }
            )
            
            state["messages"] = state["messages"] + [msg]
            
        else:
            # Round 2+: Run debate logic (Challenge, Agree, Revise)
            state = await self._run_debate_round(state)
            
        return state

    def _get_analysis_from_state(self, state: AgentState) -> Any:
        if self.agent_name == "Technical Analyst":
            return state.get("technical_analysis")
        elif self.agent_name == "News Analyst":
            return state.get("news_analysis")
        elif self.agent_name == "Quant Analyst":
            return state.get("quant_analysis")
        return None

    async def _run_debate_round(self, state: AgentState) -> AgentState:
        market_data: MarketData = state["market_data"]
        messages: List[AgentMessage] = state["messages"]
        current_analysis = self._get_analysis_from_state(state)
        
        # Prepare debate transcript
        transcript = []
        for m in messages:
            transcript.append(f"{m.agent_name} ({m.message_type}): {m.content}")
        transcript_str = "\n".join(transcript)
        
        prompt_template = ChatPromptTemplate.from_template(
            """You are the {agent_name} in the AI Investment Committee. Review the committee's debate transcript so far and decide if you want to AGREE with another analyst, CHALLENGE another analyst's opinion, or REVISE your own opinion based on their arguments.

Asset: {symbol}
Current Price: ${current_price:.2f}
Your Current Recommendation: {current_rec} (Confidence: {current_conf:.1f}%)
Your Initial Reasoning: {current_reasoning}

Debate History:
{transcript}

Rules:
1. CHALLENGE: If you disagree with another agent's analysis, point out the logical or data flaw.
2. AGREEMENT: If another analyst's points support your thesis, reinforce it.
3. REVISION: If another analyst's data or arguments have convinced you that your initial analysis was incorrect, explain why you are changing your recommendation (e.g. from BUY to HOLD).

Respond in this exact JSON format:
{{
  "message_type": "<CHALLENGE|AGREEMENT|REVISION>",
  "target_agent": "<Name of the agent you are replying to, or null>",
  "recommendation": "<BUY|SELL|HOLD>",
  "confidence": <0.0 to 1.0>,
  "content": "<Your natural language response to the committee, explaining your position>",
  "reasoning_points": ["<Supporting point 1>", "<Supporting point 2>"]
}}"""
        )
        
        try:
            response = self.llm.invoke(
                prompt_template.format_prompt(
                    agent_name=self.agent_name,
                    symbol=market_data.symbol,
                    current_price=market_data.current_price,
                    current_rec=current_analysis.recommendation if current_analysis else "HOLD",
                    current_conf=current_analysis.confidence if current_analysis else 50.0,
                    current_reasoning=current_analysis.reasoning if current_analysis else "None",
                    transcript=transcript_str
                )
            )
            
            # Parse JSON
            res_text = response.content
            start = res_text.index("{")
            end = res_text.rindex("}") + 1
            json_str = res_text[start:end]
            debate_res = json.loads(json_str)
            
            # Create message
            msg = AgentMessage(
                agent_id=self.agent_name.lower().replace(" ", "_"),
                agent_name=self.agent_name,
                message_type=debate_res.get("message_type", "AGREEMENT"),
                content=debate_res.get("content", "I agree with the consensus."),
                confidence=float(debate_res.get("confidence", 0.5)),
                recommendation=debate_res.get("recommendation", "HOLD").upper(),
                reasoning={
                    "key_points": debate_res.get("reasoning_points", []),
                    "reply_to": debate_res.get("target_agent")
                }
            )
            
            # If agent chose REVISION, update their analysis block in state
            new_rec = debate_res.get("recommendation", "HOLD").upper()
            new_conf = float(debate_res.get("confidence", 0.5)) * 100.0
            new_reason = debate_res.get("content", "")
            
            if debate_res.get("message_type") == "REVISION" and current_analysis:
                logger.info(f"🔄 [{self.agent_name}] REVISED opinion from {current_analysis.recommendation} to {new_rec}")
                current_analysis.recommendation = new_rec
                current_analysis.confidence = new_conf
                current_analysis.reasoning = f"[REVISED] {new_reason}"
                
            state["messages"] = state["messages"] + [msg]
            
        except Exception as e:
            logger.warning(f"Debate round failed for {self.agent_name}: {e}. Skipping round.")
            # Append empty agreement to keep loop moving
            fallback_msg = AgentMessage(
                agent_id=self.agent_name.lower().replace(" ", "_"),
                agent_name=self.agent_name,
                message_type="AGREEMENT",
                content="I maintain my initial analysis.",
                confidence=(current_analysis.confidence / 100.0) if current_analysis else 0.5,
                recommendation=current_analysis.recommendation if current_analysis else "HOLD",
                reasoning={"key_points": []}
            )
            state["messages"] = state["messages"] + [fallback_msg]
            
        return state


# 3. Debate Coordinator Node
def debate_coordinator_node(state: AgentState) -> AgentState:
    """
    Debate Coordinator Node.
    - Increments the round counter.
    - Calculates the current agreement percentage.
    - Logs state transitions.
    """
    current_round = state.get("current_round", 1)
    logger.info(f"Debate Coordinator evaluating Round {current_round}")
    
    # Calculate consensus level
    tech = state.get("technical_analysis")
    news = state.get("news_analysis")
    quant = state.get("quant_analysis")
    
    recs = [r.recommendation for r in [tech, news, quant] if r]
    
    if len(recs) > 0:
        # Simple agreement level calculation (percentage of matching analyst recommendations)
        from collections import Counter
        counts = Counter(recs)
        most_common_rec, count = counts.most_common(1)[0]
        agreement_level = (count / len(recs)) * 100.0
    else:
        agreement_level = 0.0
        
    state["consensus_level"] = agreement_level
    
    # Increment round counter for the next loop
    state["current_round"] = current_round + 1
    
    logger.info(f"Round {current_round} Complete. Consensus Agreement Level = {agreement_level:.1f}%")
    return state


# 4. Voting Coordinator Node
def voting_coordinator_node(state: AgentState) -> AgentState:
    """
    Voting Coordinator Node.
    - Pulls final recommendations from analysts.
    - Builds Vote objects with weights.
      Weights: Tech (1.2), Quant (1.1), News (1.0).
    - Writes votes dictionary to state.
    - Calculates the consensus action and sets proposed_action.
    """
    logger.info("Voting Coordinator: Tallies final votes")
    
    tech = state.get("technical_analysis")
    news = state.get("news_analysis")
    quant = state.get("quant_analysis")
    
    votes = {}
    
    rec_to_val = {"BUY": 1.0, "SELL": -1.0, "HOLD": 0.0}
    weighted_sum = 0.0
    total_weight = 0.0
    
    if tech:
        votes["technical_analyst"] = Vote(
            agent_id="technical_analyst",
            agent_name="Technical Analyst",
            vote=tech.recommendation,
            confidence=tech.confidence,
            weight=1.2,
            reasoning=tech.reasoning
        )
        weighted_sum += rec_to_val.get(tech.recommendation, 0.0) * 1.2
        total_weight += 1.2
        
    if quant:
        votes["quant_analyst"] = Vote(
            agent_id="quant_analyst",
            agent_name="Quant Analyst",
            vote=quant.recommendation,
            confidence=quant.confidence,
            weight=1.1,
            reasoning=quant.reasoning
        )
        weighted_sum += rec_to_val.get(quant.recommendation, 0.0) * 1.1
        total_weight += 1.1
        
    if news:
        votes["news_analyst"] = Vote(
            agent_id="news_analyst",
            agent_name="News Analyst",
            vote=news.recommendation,
            confidence=news.confidence,
            weight=1.0,
            reasoning=news.reasoning
        )
        weighted_sum += rec_to_val.get(news.recommendation, 0.0) * 1.0
        total_weight += 1.0
        
    # Calculate majority consensus proposed action
    if total_weight > 0:
        weighted_avg = weighted_sum / total_weight
        if weighted_avg >= 0.25:
            proposed_action = "BUY"
        elif weighted_avg <= -0.25:
            proposed_action = "SELL"
        else:
            proposed_action = "HOLD"
    else:
        proposed_action = "HOLD"
        
    state["votes"] = votes
    state["proposed_action"] = proposed_action
    
    logger.info(f"Votes tallied: { {k: v.vote for k, v in votes.items()} }. Proposed action: {proposed_action}")
    return state


# 5. Data Preparation Node
def data_preparation_node(state: AgentState) -> AgentState:
    """
    Initializes debate graph variables.
    """
    logger.info("Initializing Debate Graph state variables")
    
    if "current_round" not in state or not state["current_round"]:
        state["current_round"] = 1
    if "max_rounds" not in state or not state["max_rounds"]:
        state["max_rounds"] = 3
    if "messages" not in state:
        state["messages"] = []
    if "votes" not in state:
        state["votes"] = {}
    if "error_log" not in state:
        state["error_log"] = []
        
    return state


# 6. Routing Condition Functions
def should_continue_debate(state: AgentState) -> str:
    """
    Route loop decision.
    - If round count < max_rounds AND consensus agreement < 80%: continue debate.
    - Else: proceed to voting.
    """
    current_round = state.get("current_round", 1)
    max_rounds = state.get("max_rounds", 3)
    consensus_level = state.get("consensus_level", 0.0)
    
    # Note: Coordinator increments round counter.
    # So if it was round 1, Coordinator set current_round = 2.
    if current_round <= max_rounds and consensus_level < 80.0:
        logger.info(f"Consensus ({consensus_level:.1f}%) < 80% and round {current_round} <= max {max_rounds}. LOOPING debate.")
        return "debate_loop"
    else:
        logger.info(f"Ending debate (Consensus: {consensus_level:.1f}%, Next Round: {current_round}). Proceeding to VOTING.")
        return "voting"


# 7. Compile the LangGraph state graph
def build_debate_engine_graph(model_name: str = "gpt-4") -> StateGraph:
    """
    Compile the LangGraph debate flow.
    Sequential speaks: Technical -> News -> Quant -> DebateCoordinator -> Loop/Voting
    """
    workflow = StateGraph(AgentState)
    
    # Instantiate wrapped agents
    wrapped_tech = DebateAgentWrapper("Technical Analyst", technical_analyst_node, model_name=model_name)
    wrapped_news = DebateAgentWrapper("News Analyst", news_analyst_node, model_name=model_name)
    wrapped_quant = DebateAgentWrapper("Quant Analyst", quant_analyst_node, model_name=model_name)
    
    # Add nodes
    workflow.add_node("data_prep", data_preparation_node)
    workflow.add_node("technical_analyst", wrapped_tech)
    workflow.add_node("news_analyst", wrapped_news)
    workflow.add_node("quant_analyst", wrapped_quant)
    workflow.add_node("debate_coordinator", debate_coordinator_node)
    workflow.add_node("voting_coordinator", voting_coordinator_node)
    workflow.add_node("execution_agent", execution_agent_node)
    workflow.add_node("risk_manager", risk_manager_node)
    
    # Connect nodes sequentially (as required: agents speak sequentially)
    workflow.set_entry_point("data_prep")
    
    workflow.add_edge("data_prep", "technical_analyst")
    workflow.add_edge("technical_analyst", "news_analyst")
    workflow.add_edge("news_analyst", "quant_analyst")
    workflow.add_edge("quant_analyst", "debate_coordinator")
    
    # Conditional edge for debate loop
    workflow.add_conditional_edges(
        "debate_coordinator",
        should_continue_debate,
        {
            "debate_loop": "technical_analyst",
            "voting": "voting_coordinator"
        }
    )
    
    # Connect voting to risk validation & then final decision synthesis
    workflow.add_edge("voting_coordinator", "risk_manager")
    workflow.add_edge("risk_manager", "execution_agent")
    workflow.add_edge("execution_agent", END)
    
    return workflow.compile()
