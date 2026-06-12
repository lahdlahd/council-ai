import sys
import os
import json
import shutil
from datetime import datetime
from unittest.mock import MagicMock

# Setup path and environment
sys.path.append(r"c:\Users\USER\OneDrive\Desktop\councilB\backend")
os.environ["OPENAI_API_KEY"] = "mock-key"

from fastapi.testclient import TestClient

# Mock any required outer packages if uvicorn or langchain is loaded
mock_chat_models = MagicMock()
sys.modules['langchain.chat_models'] = mock_chat_models
sys.modules['langchain_community.chat_models'] = mock_chat_models
sys.modules['langchain_openai'] = mock_chat_models

mock_prompts = MagicMock()
sys.modules['langchain.prompts'] = mock_prompts
sys.modules['langchain_core.prompts'] = mock_prompts

mock_output_parsers = MagicMock()
sys.modules['langchain.output_parsers'] = mock_output_parsers
sys.modules['langchain_core.output_parsers'] = mock_output_parsers

from app.main import app
from app.api.services.replay_service import ReplayService

def setup_test_db():
    """Sets up a clean temporary database JSON file for testing."""
    test_db_path = os.path.join(os.path.dirname(__file__), "test_demo_fallback.json")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    return test_db_path

def test_rally_scenario(client):
    print("--- Test: POST /api/replay/demo/run (Rally Scenario) ---")
    response = client.post("/api/replay/demo/run", json={"scenario": "rally"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    session_id = res_data["session_id"]
    assert len(session_id) > 10
    print(f"[OK] Rally session successfully generated: {session_id}")
    
    print("\n--- Test: GET /api/replay/{session_id} (Rally Timeline verification) ---")
    timeline_res = client.get(f"/api/replay/{session_id}")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["symbol"] == "BTC"
    assert timeline["market_state"]["current_price"] == 42000.0
    assert timeline["execution_decision"]["action"] == "BUY"
    assert timeline["execution_decision"]["position_size"]["percentage_of_portfolio"] == 16.0
    assert timeline["veto_verification"]["approved"] is True
    assert len(timeline["debate_transcript"]) == 5
    print("[OK] Rally timeline values verified successfully.")
    
    print("\n--- Test: POST /api/replay/{session_id}/mock-complete (Exit simulated trade) ---")
    exit_price = 45500.0
    complete_res = client.post(
        f"/api/replay/{session_id}/mock-complete",
        json={"exit_price": exit_price}
    )
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "success"
    
    # Reload timeline to check P&L calculation
    # P&L = (45500 - 42000) * 0.7619 = +2666.65
    timeline_res2 = client.get(f"/api/replay/{session_id}")
    timeline2 = timeline_res2.json()
    assert timeline2["trade_result"]["status"] == "completed"
    assert timeline2["trade_result"]["exit_price"] == exit_price
    assert timeline2["trade_result"]["realized_pnl"] == 2666.65
    print("[OK] Simulated trade target exit verified. Realized P&L matched expected (+$2,666.65).")
    return session_id

def test_crash_scenario(client):
    print("\n--- Test: POST /api/replay/demo/run (Crash Scenario) ---")
    response = client.post("/api/replay/demo/run", json={"scenario": "crash"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    session_id = res_data["session_id"]
    assert len(session_id) > 10
    print(f"[OK] Crash session successfully generated: {session_id}")
    
    print("\n--- Test: GET /api/replay/{session_id} (Crash Timeline verification) ---")
    timeline_res = client.get(f"/api/replay/{session_id}")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["symbol"] == "ETH"
    assert timeline["market_state"]["current_price"] == 3100.0
    assert timeline["execution_decision"]["action"] == "HOLD"
    assert timeline["veto_verification"]["approved"] is False # Risk Vetoed
    assert "VETO:" in timeline["veto_verification"]["veto_reason"]
    assert len(timeline["debate_transcript"]) == 5
    print("[OK] Crash timeline with Risk VETO verified successfully.")

def main():
    print("=== STARTING FASTAPI HACKATHON DEMO TESTS ===")
    
    # Setup test DB
    test_db_path = setup_test_db()
    test_service = ReplayService(fallback_path=test_db_path)
    
    # Inject service into router
    import app.api.routers.replay as replay_module
    replay_module.replay_service = test_service
    
    client = TestClient(app)
    
    try:
        test_rally_scenario(client)
        test_crash_scenario(client)
        print("\n=== ALL FASTAPI HACKATHON DEMO TESTS PASSED ===")
    finally:
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

if __name__ == "__main__":
    main()
