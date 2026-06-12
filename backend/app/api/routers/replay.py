from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.agents.schemas import ReplaySummary, ReplayTimeline
from app.api.services.replay_service import ReplayService

router = APIRouter(
    prefix="/replay",
    tags=["replay"],
    responses={404: {"description": "Session replay not found"}},
)

# Instantiate singleton service
replay_service = ReplayService()

class MockCompleteRequest(BaseModel):
    exit_price: float

class DemoRunRequest(BaseModel):
    scenario: str

@router.post("/demo/run")
def run_demo_committee_session(request: DemoRunRequest):
    """
    Launches a new simulated committee session (rally or crash) and returns the session_id.
    """
    try:
        session_id = replay_service.run_demo_session(request.scenario)
        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Demo session successfully generated for scenario: {request.scenario}."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ReplaySummary])
def get_replay_sessions():
    """
    Get all completed investment committee sessions available for replay.
    """
    try:
        return replay_service.list_replays()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=ReplayTimeline)
def get_session_replay_timeline(session_id: str):
    """
    Get the full chronological debate and execution timeline for a specific session.
    """
    timeline = replay_service.get_replay_timeline(session_id)
    if not timeline:
        raise HTTPException(
            status_code=404, 
            detail=f"Replay timeline for session {session_id} not found."
        )
    return timeline

@router.post("/{session_id}/mock-complete")
def simulate_trade_completion(session_id: str, request: MockCompleteRequest):
    """
    Simulates exiting a trade and completing a replay timeline (useful for hackathon demo).
    """
    success = replay_service.mock_complete_trade(session_id, request.exit_price)
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to mock complete trade. Replay session {session_id} may not exist or is already finalized."
        )
    return {"status": "success", "message": f"Simulated trade exit processed at ${request.exit_price:.2f}."}
