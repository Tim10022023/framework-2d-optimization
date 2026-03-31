import pytest
import asyncio
import math
from app.core.functions import get_blackbox_payload, evaluate_function
from bot.blackbox_client import BlackBoxClient

def test_rpn_evaluators():
    """Test that all RPN payloads evaluate correctly against true functions."""
    functions_to_test = ["sphere_shifted", "booth", "himmelblau", "rosenbrock", "eggholder", "rastrigin_shifted", "schwefel", "easom"]
    
    # Fake client to use evaluate_local
    client = BlackBoxClient("http://localhost:8000", "DEBUG")
    
    test_points = [(0.0, 0.0), (1.2, -3.4), (5.0, 5.0), (-2.1, 0.5)]
    
    for fid in functions_to_test:
        payload = get_blackbox_payload(fid)
        if payload == [3, 0.0]: # OP_CONST, 0.0 (placeholder)
            continue
            
        client.blackbox_payload = payload
        
        for x, y in test_points:
            true_z = evaluate_function(fid, x, y)
            local_z = client.evaluate_local(x, y)
            assert math.isclose(true_z, local_z, rel_tol=1e-5), f"Mismatch in {fid} at ({x}, {y}): true={true_z}, local={local_z}"
    print("RPN Evaluators verified!")

@pytest.mark.asyncio
async def test_anti_cheat_server_side():
    """Test that the server catches spoofed Z values."""
    from app.core.store import add_trajectory, create_session, join_session
    
    # 1. Create a real session
    s = await create_session("sphere_shifted", "min", 30)
    p = await join_session(s.code, "TestBot")
    
    # 2. Valid trajectory
    valid_points = [
        {"x": 1.0, "y": 1.0, "z": evaluate_function("sphere_shifted", 1.0, 1.0)},
        {"x": 2.0, "y": 2.0, "z": evaluate_function("sphere_shifted", 2.0, 2.0)},
    ]
    res = await add_trajectory(s.code, p.id, valid_points)
    assert res["batch_size"] == 2
    
    # 3. Invalid trajectory (Spoofed Z)
    invalid_points = [
        {"x": 3.0, "y": 3.0, "z": -999.0}, # Cheating!
    ]
    with pytest.raises(ValueError, match="Anti-cheat verification failed"):
        await add_trajectory(s.code, p.id, invalid_points)
    
    print("Anti-cheat verification verified!")

if __name__ == "__main__":
    # Manual run if not using pytest
    test_rpn_evaluators()
    asyncio.run(test_anti_cheat_server_side())
