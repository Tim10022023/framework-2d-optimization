from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import random
import time

from app.core.store import (
    add_click,
    compute_leaderboard,
    create_session,
    get_session,
    join_session,
    set_session_status,
)
from app.core.functions import evaluate_function, get_spec

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionBody(BaseModel):
    function_id: str = "sphere_shifted"
    goal: str = "min"
    max_steps: int = 30


class JoinSessionBody(BaseModel):
    name: str
    is_bot: bool = False


class EvaluateBody(BaseModel):
    participant_id: str
    x: float
    y: float


@router.post("")
def create_new_session(body: CreateSessionBody):
    if body.goal not in ("min", "max"):
        raise HTTPException(status_code=400, detail="goal must be 'min' or 'max'")

    try:
        spec = get_spec(body.function_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if body.goal not in spec.allowed_goals:
        raise HTTPException(
            status_code=400,
            detail=f"goal '{body.goal}' not allowed for function '{body.function_id}'",
        )

    s = create_session(
        function_id=body.function_id,
        goal=body.goal,
        max_steps=body.max_steps,
    )

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
        "max_steps": s.max_steps,
    }


@router.get("/{code}/public")
def get_public_session_info(code: str):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_code": s.code,
        "participants": len(s.participants),
        "status": s.status,
        "max_steps": s.max_steps,
    }


@router.post("/{code}/join")
def join(code: str, body: JoinSessionBody):
    try:
        p = join_session(code=code, name=body.name, is_bot=body.is_bot)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "participant_id": p.id,
        "name": p.name,
        "session_code": code,
    }


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
        result = add_click(
            code=code,
            participant_id=body.participant_id,
            x=body.x,
            y=body.y,
            z=z,
        )
    except ValueError as e:
        if str(e) == "max steps reached":
            raise HTTPException(status_code=409, detail="max steps reached")
        raise HTTPException(status_code=400, detail=str(e))
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

    return {
        "session_code": code,
        "leaderboard": rows,
    }


@router.post("/{code}/end")
def end_session(code: str, x_admin_token: str = Header(default="")):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    if x_admin_token != s.admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")

    updated = set_session_status(code, "ended")
    return {
        "session_code": code,
        "status": updated.status,
    }


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
                "is_bot": getattr(p, "is_bot", False),
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
        "reveal": {
            "function_id": spec.id,
            "title": spec.reveal_title or spec.name,
            "description": spec.reveal_description,
            "image": spec.reveal_image,
        },
        "participants": participants,
        "leaderboard": compute_leaderboard(code),
    }


@router.post("/{code}/bots/random_search")
def bot_random_search(
    code: str,
    n: int = 20,
    seed: int | None = None,
    delay_ms: int = 0,
):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    if s.status == "ended":
        raise HTTPException(status_code=409, detail="session ended")
    if delay_ms < 0 or delay_ms > 5000:
        raise HTTPException(status_code=400, detail="delay_ms must be between 0 and 5000")
    if n <= 0 or n > 1000:
        raise HTTPException(status_code=400, detail="n must be between 1 and 1000")

    if seed is not None:
        random.seed(seed)

    bot_name = f"Bot-Random(n={n})"
    try:
        bot = join_session(code=code, name=bot_name, is_bot=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    spec = get_spec(s.function_id)
    b = spec.bounds

    for _ in range(n):
        x = random.uniform(b["xmin"], b["xmax"])
        y = random.uniform(b["ymin"], b["ymax"])
        z = evaluate_function(s.function_id, x, y)
        add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

    return {
        "session_code": code,
        "bot_participant_id": bot.id,
        "bot_name": bot.name,
        "n": n,
    }


@router.post("/{code}/bots/hill_climb")
def bot_hill_climb(
    code: str,
    n: int = 30,
    step_size: float = 0.5,
    seed: int | None = None,
    delay_ms: int = 0,
):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    if s.status == "ended":
        raise HTTPException(status_code=409, detail="session ended")
    if delay_ms < 0 or delay_ms > 5000:
        raise HTTPException(status_code=400, detail="delay_ms must be between 0 and 5000")
    if n <= 0 or n > 2000:
        raise HTTPException(status_code=400, detail="n must be between 1 and 2000")
    if step_size <= 0:
        raise HTTPException(status_code=400, detail="step_size must be > 0")

    if seed is not None:
        random.seed(seed)

    bot_name = f"Bot-HillClimb(n={n},h={step_size})"
    bot = join_session(code=code, name=bot_name, is_bot=True)

    spec = get_spec(s.function_id)
    b = spec.bounds

    x = random.uniform(b["xmin"], b["xmax"])
    y = random.uniform(b["ymin"], b["ymax"])
    z = evaluate_function(s.function_id, x, y)
    add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    def neighbors(cx: float, cy: float):
        return [
            (cx + step_size, cy),
            (cx - step_size, cy),
            (cx, cy + step_size),
            (cx, cy - step_size),
        ]

    def clamp(v: float, vmin: float, vmax: float) -> float:
        return max(vmin, min(vmax, v))

    for _ in range(n - 1):
        best_x, best_y, best_z = x, y, z

        for nx, ny in neighbors(x, y):
            nx = clamp(nx, b["xmin"], b["xmax"])
            ny = clamp(ny, b["ymin"], b["ymax"])
            nz = evaluate_function(s.function_id, nx, ny)

            if s.goal == "min":
                if nz < best_z:
                    best_x, best_y, best_z = nx, ny, nz
            else:
                if nz > best_z:
                    best_x, best_y, best_z = nx, ny, nz

        if best_z == z:
            step_size = step_size * 0.5
            if step_size < 1e-6:
                break
        else:
            x, y, z = best_x, best_y, best_z

        add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

    return {
        "session_code": code,
        "bot_participant_id": bot.id,
        "bot_name": bot.name,
        "n": n,
        "final_step_size": step_size,
    }


@router.get("/{code}/snapshot")
def session_snapshot(code: str):
    s = get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    participants = []
    for p in s.participants.values():
        participants.append(
            {
                "participant_id": p.id,
                "name": p.name,
                "is_bot": getattr(p, "is_bot", False),
                "found": p.found_step is not None,
                "found_step": p.found_step,
                "clicks": [
                    {"x": c.x, "y": c.y, "z": c.z, "step": i + 1}
                    for i, c in enumerate(p.clicks)
                ],
            }
        )

    return {
        "session_code": s.code,
        "status": s.status,
        "function_id": s.function_id,
        "goal": s.goal,
        "participants": participants,
    }