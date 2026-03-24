import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
import uuid

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_list_functions(client):
    response = await client.get("/functions")
    assert response.status_code == 200
    assert "functions" in response.json()
    assert len(response.json()["functions"]) > 0

@pytest.mark.asyncio
async def test_create_session(client):
    body = {
        "function_id": "sphere_shifted",
        "goal": "min",
        "max_steps": 10
    }
    response = await client.post("/sessions", json=body)
    assert response.status_code == 200
    data = response.json()
    assert "session_code" in data
    assert "admin_token" in data
    assert data["function_id"] == "sphere_shifted"
    assert data["goal"] == "min"
    return data["session_code"], data["admin_token"]

@pytest.mark.asyncio
async def test_join_and_evaluate(client):
    # 1. Create session
    create_body = {
        "function_id": "sphere_shifted",
        "goal": "min",
        "max_steps": 10
    }
    create_res = await client.post("/sessions", json=create_body)
    session_code = create_res.json()["session_code"]

    # 2. Join session
    join_body = {"name": "TestUser", "is_bot": False}
    join_res = await client.post(f"/sessions/{session_code}/join", json=join_body)
    assert join_res.status_code == 200
    participant_id = join_res.json()["participant_id"]

    # 3. Evaluate point
    eval_body = {
        "participant_id": participant_id,
        "x": 3.7,
        "y": -2.1
    }
    eval_res = await client.post(f"/sessions/{session_code}/evaluate", json=eval_body)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["x"] == 3.7
    assert eval_data["y"] == -2.1
    assert eval_data["z"] == 0.0  # Sphere global minimum
    assert eval_data["best_z"] == 0.0
    assert eval_data["step"] == 1

@pytest.mark.asyncio
async def test_leaderboard(client):
    # 1. Create session
    create_body = {"function_id": "sphere_shifted", "goal": "min", "max_steps": 5}
    create_res = await client.post("/sessions", json=create_body)
    session_code = create_res.json()["session_code"]

    # 2. Join
    join_res = await client.post(f"/sessions/{session_code}/join", json={"name": "Player1"})
    p1_id = join_res.json()["participant_id"]

    # 3. Evaluate
    await client.post(f"/sessions/{session_code}/evaluate", json={"participant_id": p1_id, "x": 1, "y": 1})

    # 4. Check leaderboard
    lb_res = await client.get(f"/sessions/{session_code}/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    assert len(lb_data["leaderboard"]) == 1
    assert lb_data["leaderboard"][0]["name"] == "Player1"

@pytest.mark.asyncio
async def test_end_session(client):
    # 1. Create session
    create_res = await client.post("/sessions", json={"function_id": "sphere_shifted", "goal": "min"})
    data = create_res.json()
    session_code = data["session_code"]
    admin_token = data["admin_token"]

    # 2. End session
    headers = {"x-admin-token": admin_token}
    end_res = await client.post(f"/sessions/{session_code}/end", headers=headers)
    assert end_res.status_code == 200
    assert end_res.json()["status"] == "ended"

    # 3. Verify evaluate fails
    join_res = await client.post(f"/sessions/{session_code}/join", json={"name": "LatePlayer"})
    p_id = join_res.json()["participant_id"]
    eval_res = await client.post(f"/sessions/{session_code}/evaluate", json={"participant_id": p_id, "x": 0, "y": 0})
    assert eval_res.status_code == 409
    assert eval_res.json()["detail"] == "session ended"
