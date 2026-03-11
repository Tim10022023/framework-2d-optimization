from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from app.core.store import create_session, get_session, join_session, add_click, compute_leaderboard, set_session_status
from app.core.functions import evaluate_function
from app.core.functions import get_spec




router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionBody(BaseModel):
    function_id: str = "sphere"
    goal: str = "min"  # "min" oder "max"


@router.post("")
def create_new_session(body: CreateSessionBody):
    if body.goal not in ("min", "max"):
        raise HTTPException(status_code=400, detail="goal must be 'min' or 'max'")

    try:
        spec = get_spec(body.function_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if body.goal not in spec.allowed_goals:
        raise HTTPException(status_code=400, detail=f"goal '{body.goal}' not allowed for function '{body.function_id}'")

    s = create_session(function_id=body.function_id, goal=body.goal)
    return {
    "session_code": s.code,
    "function_id": s.function_id,
    "goal": s.goal,
    "admin_token": s.admin_token,
    }




@router.get("/{code}")
def get_session_info(code: str):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    return {
    "session_code": s.code,
    "function_id": s.function_id,
    "goal": s.goal,
    "participants": len(s.participants),
    "status": s.status,
}

class JoinSessionBody(BaseModel):
    name: str


@router.post("/{code}/join")
def join(code: str, body: JoinSessionBody):
    try:
        p = join_session(code=code, name=body.name)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    return {"participant_id": p.id, "name": p.name, "session_code": code}

class EvaluateBody(BaseModel):
    participant_id: str
    x: float
    y: float


@router.post("/{code}/evaluate")
def evaluate(code: str, body: EvaluateBody):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    if s.status == "ended":
        raise HTTPException(status_code=409, detail="session ended")

    try:
        z = evaluate_function(s.function_id, body.x, body.y)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = add_click(code=code, participant_id=body.participant_id, x=body.x, y=body.y, z=z)
    except KeyError as e:
        msg = str(e)
        if "participant" in msg:
            raise HTTPException(status_code=404, detail="participant not found")
        raise HTTPException(status_code=404, detail="session not found")

    return {
    "x": body.x,
    "y": body.y,
    "z": z,
    **result,
}

@router.get("/{code}/leaderboard")
def leaderboard(code: str):
    try:
        rows = compute_leaderboard(code)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    return {"session_code": code, "leaderboard": rows}

@router.post("/{code}/end")
def end_session(code: str, x_admin_token: str = Header(default="")):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    if x_admin_token != s.admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")

    updated = set_session_status(code, "ended")
    return {"session_code": code, "status": updated.status}

@router.get("/{code}/export")
def export_session(code: str, x_admin_token: str = Header(default="")):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    if x_admin_token != s.admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")

    if s.status != "ended":
        raise HTTPException(status_code=409, detail="session not ended")

    spec = get_spec(s.function_id)

    participants = []
    for p in s.participants.values():
        participants.append(
            {
                "participant_id": p.id,
                "name": p.name,
                "steps": len(p.clicks),
                "found": p.found_step is not None,
                "found_step": p.found_step,
                "found_z": p.found_z,
                "clicks": [{"x": c.x, "y": c.y, "z": c.z} for c in p.clicks],
            }
        )

    return {
        "session_code": s.code,
        "status": s.status,
        "goal": s.goal,
        "function": {
            "id": spec.id,
            "name": spec.name,
            "allowed_goals": list(spec.allowed_goals),
            "target_z": spec.target_z,
            "tolerance": spec.tolerance,
            "bounds": spec.bounds,
        },
        "participants": participants,
        "leaderboard": compute_leaderboard(code),
    }

