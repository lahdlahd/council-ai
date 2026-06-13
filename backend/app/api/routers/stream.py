import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.debate.debate_engine import build_debate_engine_graph, AgentState
from app.api.services.bitget_service import BitgetService

router = APIRouter(
    prefix="/stream",
    tags=["stream"]
)

class StreamRequest(BaseModel):
    symbol: str

async def generate_debate_stream(symbol: str) -> AsyncGenerator[str, None]:
    """
    Executes the debate graph asynchronously and yields SSE messages.
    """
    try:
        # 1. Fetch live market data
        bitget_service = BitgetService()
        market_data_dict = bitget_service.get_market_data(symbol)
        
        yield f"data: {json.dumps({'type': 'MARKET_DATA', 'data': market_data_dict})}\n\n"
        
        from app.agents.schemas import MarketData
        market_data = MarketData(**market_data_dict)
        
        # 2. Initialize graph
        graph = build_debate_engine_graph()
        initial_state: AgentState = {
            "market_data": market_data,
            "account_size": 100000.0,
            "current_holdings": {},
            "current_equity": 100000.0,
            "messages": [],
            "votes": {},
            "current_round": 1,
            "max_rounds": 2,
            "error_log": []
        }
        
        # 3. Stream graph execution
        async for output in graph.astream(initial_state):
            # output is a dict mapping node_name to the state updates
            for node_name, state_update in output.items():
                
                # Check for new messages from analyst nodes
                if "messages" in state_update and len(state_update["messages"]) > 0:
                    latest_msg = state_update["messages"][-1]
                    # Convert object to dict using model_dump_json to serialize datetimes
                    msg_dict = json.loads(latest_msg.model_dump_json()) if hasattr(latest_msg, 'model_dump_json') else latest_msg
                    yield f"data: {json.dumps({'type': 'AGENT_MESSAGE', 'node': node_name, 'data': msg_dict})}\n\n"
                    
                # Check for consensus calculation
                if node_name == "debate_coordinator" and "consensus_level" in state_update:
                    yield f"data: {json.dumps({'type': 'CONSENSUS_UPDATE', 'data': {'consensus_level': state_update['consensus_level'], 'round': state_update.get('current_round', 1) - 1}})}\n\n"
                    
                # Check for voting conclusion
                if node_name == "voting_coordinator" and "proposed_action" in state_update:
                    votes = state_update.get("votes", {})
                    # Convert Vote objects to dicts using model_dump_json
                    votes_dict = {k: json.loads(v.model_dump_json()) if hasattr(v, 'model_dump_json') else v for k, v in votes.items()}
                    yield f"data: {json.dumps({'type': 'VOTING_COMPLETE', 'data': {'proposed_action': state_update['proposed_action'], 'votes': votes_dict}})}\n\n"
                
                # Check for Risk Manager Veto
                if node_name == "risk_manager" and "risk_assessment" in state_update:
                    risk = state_update["risk_assessment"]
                    risk_dict = json.loads(risk.model_dump_json()) if hasattr(risk, 'model_dump_json') else risk
                    yield f"data: {json.dumps({'type': 'RISK_ASSESSMENT', 'data': risk_dict})}\n\n"
                
                # Check for Execution Decision
                if node_name == "execution_agent" and "final_decision" in state_update:
                    decision = state_update["final_decision"]
                    decision_dict = json.loads(decision.model_dump_json()) if hasattr(decision, 'model_dump_json') else decision
                    yield f"data: {json.dumps({'type': 'EXECUTION_DECISION', 'data': decision_dict})}\n\n"
                    
                # Small delay to simulate processing and allow UI typing effects
                await asyncio.sleep(1.0)
                
        # Send closing event
        yield f"data: {json.dumps({'type': 'STREAM_COMPLETE', 'data': {'status': 'success'}})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'ERROR', 'data': str(e)})}\n\n"

@router.post("/run")
async def run_live_debate(request: StreamRequest):
    """
    SSE Endpoint for live debate streaming.
    """
    return StreamingResponse(
        generate_debate_stream(request.symbol),
        media_type="text/event-stream"
    )
