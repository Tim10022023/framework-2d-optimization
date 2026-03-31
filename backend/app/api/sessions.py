from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import random
import asyncio
import json

from app.core.store import (
    add_click,
    compute_leaderboard,
    create_session,
    get_session,
    get_session_basic,
    get_participants_count,
    join_session,
    set_session_status,
)
from app.core.functions import evaluate_function, get_spec, get_blackbox_payload
from app.core.websocket import manager
from app.core.redis import get_redis
from app.core.config import settings

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


def require_admin_token(session, admin_token: str):
    if admin_token != session.admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")


@router.post("")
async def create_new_session(body: CreateSessionBody):
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

    s = await create_session(
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
async def get_session_info(code: str):
    s = await get_session_basic(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_code": s.code,
        "function_id": s.function_id,
        "goal": s.goal,
        "participants": await get_participants_count(code),
        "status": s.status,
        "max_steps": s.max_steps,
    }


@router.get("/{code}/public")
async def get_public_session_info(code: str):
    s = await get_session_basic(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_code": s.code,
        "participants": await get_participants_count(code),
        "status": s.status,
        "max_steps": s.max_steps,
    }


@router.post("/{code}/join")
async def join(code: str, body: JoinSessionBody):
    try:
        p = await join_session(code=code, name=body.name, is_bot=body.is_bot)
        s = await get_session_basic(code)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    await manager.trigger_update(code, "participant_joined", {
        "participant_id": p.id,
        "name": p.name,
        "participants_count": await get_participants_count(code)
    })

    spec = get_spec(s.function_id) if s else None

    return {
        "participant_id": p.id,
        "name": p.name,
        "session_code": code,
        "goal": s.goal if s else "min",
        "bounds": spec.bounds if spec else {"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5},
        "blackbox": get_blackbox_payload(s.function_id) if s else None
    }


class TrajectoryPoint(BaseModel):
    x: float
    y: float
    z: float

class SyncTrajectoryBody(BaseModel):
    participant_id: str
    points: list[TrajectoryPoint]


@router.post("/{code}/sync_trajectory")
async def sync_trajectory(code: str, body: SyncTrajectoryBody):
    from app.core.store import add_trajectory
    
    try:
        result = await add_trajectory(
            code=code,
            participant_id=body.participant_id,
            points=[{"x": p.x, "y": p.y, "z": p.z} for p in body.points]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail="session or participant not found")

    await manager.trigger_update(code, "leaderboard_updated", {
        "leaderboard": await compute_leaderboard(code)
    })

    return result


@router.websocket("/{code}/ws")
async def session_websocket(websocket: WebSocket, code: str):
    await manager.connect(code, websocket)
    try:
        while True:
            # Keep connection alive, though we mostly broadcast from server to client
            data = await websocket.receive_text()
            # Handle potential client messages if needed
    except WebSocketDisconnect:
        manager.disconnect(code, websocket)
    except Exception:
        manager.disconnect(code, websocket)


@router.post("/{code}/evaluate")
async def evaluate(code: str, body: EvaluateBody):
    s = await get_session_basic(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    if s.status == "ended":
        raise HTTPException(status_code=409, detail="session ended")

    try:
        z = evaluate_function(s.function_id, body.x, body.y)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await add_click(
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

    await manager.trigger_update(code, "click_added", {
        "participant_id": body.participant_id,
        "x": body.x,
        "y": body.y,
        "z": z,
        "leaderboard": await compute_leaderboard(code),
        **result,
    })

    return {
        "x": body.x,
        "y": body.y,
        "z": z,
        **result,
    }


@router.get("/{code}/leaderboard")
async def leaderboard(code: str):
    try:
        rows = await compute_leaderboard(code)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_code": code,
        "leaderboard": rows,
    }


@router.post("/{code}/end")
async def end_session(code: str, x_admin_token: str = Header(default="")):
    s = await get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    require_admin_token(s, x_admin_token)

    updated = await set_session_status(code, "ended")
    await manager.trigger_update(code, "session_ended", {
        "status": updated.status
    })
    return {
        "session_code": code,
        "status": updated.status,
    }


@router.get("/{code}/export")
async def export_session(code: str, x_admin_token: str = Header(default="")):
    s = await get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    require_admin_token(s, x_admin_token)


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
        "leaderboard": await compute_leaderboard(code),
    }


@router.post("/{code}/bots/random_search")
async def bot_random_search(
    code: str,
    admin_token: str,
    n: int = 20,
    seed: int | None = None,
    delay_ms: int = 0,
):
    s = await get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    require_admin_token(s, admin_token)

    if delay_ms < 0 or delay_ms > 5000:
        raise HTTPException(
            status_code=400, detail="delay_ms must be between 0 and 5000"
        )
    if n <= 0 or n > 1000:
        raise HTTPException(status_code=400, detail="n must be between 1 and 1000")

    if seed is not None:
        random.seed(seed)

    bot_name = f"Bot-Random(n={n})"
    try:
        bot = await join_session(code=code, name=bot_name, is_bot=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    spec = get_spec(s.function_id)
    b = spec.bounds

    for _ in range(n):
        x = random.uniform(b["xmin"], b["xmax"])
        y = random.uniform(b["ymin"], b["ymax"])
        z = evaluate_function(s.function_id, x, y)
        await add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)

    return {
        "session_code": code,
        "bot_participant_id": bot.id,
        "bot_name": bot.name,
        "n": n,
    }


@router.post("/{code}/bots/hill_climb")
async def bot_hill_climb(
    code: str,
    admin_token: str,
    n: int = 30,
    step_size: float = 0.5,
    seed: int | None = None,
    delay_ms: int = 0,
):
    s = await get_session(code)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")

    require_admin_token(s, admin_token)

    if delay_ms < 0 or delay_ms > 5000:
        raise HTTPException(
            status_code=400, detail="delay_ms must be between 0 and 5000"
        )
    if n <= 0 or n > 2000:
        raise HTTPException(status_code=400, detail="n must be between 1 and 2000")
    if step_size <= 0:
        raise HTTPException(status_code=400, detail="step_size must be > 0")

    if seed is not None:
        random.seed(seed)

    bot_name = f"Bot-HillClimb(n={n},h={step_size})"
    try:
        bot = await join_session(code=code, name=bot_name, is_bot=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")

    spec = get_spec(s.function_id)
    b = spec.bounds

    x = random.uniform(b["xmin"], b["xmax"])
    y = random.uniform(b["ymin"], b["ymax"])
    z = evaluate_function(s.function_id, x, y)
    await add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000.0)

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

        await add_click(code=code, participant_id=bot.id, x=x, y=y, z=z)

        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)

    return {
        "session_code": code,
        "bot_participant_id": bot.id,
        "bot_name": bot.name,
        "n": n,
        "final_step_size": step_size,
    }


@router.get("/{code}/snapshot")
async def session_snapshot(code: str):
    from app.core.store import get_session_snapshot
    
    redis = get_redis()
    cache_key = f"snapshot:{code}"
    cached = await redis.get(cache_key) if redis else None
    if cached:
        return json.loads(cached)

    res = await get_session_snapshot(code)
    if not res:
        raise HTTPException(status_code=404, detail="session not found")

    if redis:
        await redis.setex(cache_key, settings.SNAPSHOT_CACHE_TTL, json.dumps(res))
    return res
