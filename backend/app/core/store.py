from __future__ import annotations

import time
import asyncio
import json
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select, func, insert
from sqlalchemy.orm import selectinload

from app.core.functions import get_spec, evaluate_function
from app.db.session import AsyncSessionLocal
from app.db.models import SessionModel, ParticipantModel, ClickModel
from app.core.redis import get_redis
from app.core.config import settings

@dataclass
class Click:
    x: float
    y: float
    z: float


@dataclass
class Participant:
    id: str
    name: str
    is_bot: bool = False
    clicks: list = field(default_factory=list)
    found_step: int | None = None
    found_z: float | None = None



@dataclass
class Session:
    code: str
    function_id: str
    goal: str
    admin_token: str
    status: str = "running"
    max_steps: int = 30
    participants: dict[str, "Participant"] = field(default_factory=dict)




def new_code() -> str:
    return uuid4().hex[:6].upper()


async def create_session(function_id: str, goal: str, max_steps: int) -> Session:
    code = new_code()
    admin_token = uuid4().hex

    async with AsyncSessionLocal() as db:
        db_session = SessionModel(
            code=code,
            function_id=function_id,
            goal=goal,
            admin_token=admin_token,
            status="running",
            max_steps=max_steps,
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)

        return Session(
            code=db_session.code,
            function_id=db_session.function_id,
            goal=db_session.goal,
            admin_token=db_session.admin_token,
            status=db_session.status,
            participants={},
            max_steps=db_session.max_steps,
        )


async def get_session_basic(code: str) -> Optional[Session]:
    redis = get_redis()
    cache_key = f"session_basic:{code}"
    cached = await redis.get(cache_key) if redis else None
    if cached:
        data = json.loads(cached)
        # Participants are empty in basic view
        data["participants"] = {}
        return Session(**data)

    async with AsyncSessionLocal() as db:
        stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            return None

        val = Session(
            code=db_session.code,
            function_id=db_session.function_id,
            goal=db_session.goal,
            admin_token=db_session.admin_token,
            status=db_session.status,
            participants={},  # Empty for basic info
            max_steps=db_session.max_steps
        )
        
        # Cache for basic info doesn't need participants
        cache_data = asdict(val)
        if redis:
            await redis.setex(cache_key, settings.CACHE_TTL, json.dumps(cache_data))
        return val

async def get_participants_count(code: str) -> int:
    redis = get_redis()
    cache_key = f"participants_count:{code}"
    cached = await redis.get(cache_key) if redis else None
    if cached:
        return int(cached)

    async with AsyncSessionLocal() as db:
        # Join to count participants efficiently
        stmt = (
            select(func.count(ParticipantModel.id))
            .join(SessionModel)
            .where(SessionModel.code == code)
        )
        result = await db.execute(stmt)
        val = result.scalar() or 0
        if redis:
            await redis.setex(cache_key, settings.CACHE_TTL, str(val))
        return val

async def get_session(code: str) -> Optional[Session]:
    # Detailed session with all participants and clicks - not cached for now as it's large
    async with AsyncSessionLocal() as db:
        # Use selectinload to avoid lazy loading issues in async
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.participants).selectinload(ParticipantModel.clicks))
            .where(SessionModel.code == code)
        )
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            return None

        participants = {}
        for p in db_session.participants:
            clicks = [
                Click(x=c.x, y=c.y, z=c.z)
                for c in sorted(p.clicks, key=lambda click: click.step)
            ]

            participants[p.participant_code] = Participant(
                id=p.participant_code,
                name=p.name,
                clicks=clicks,
                is_bot=getattr(p, "is_bot", False),
                found_step=p.found_step,
                found_z=p.found_z,
            )

        return Session(
            code=db_session.code,
            function_id=db_session.function_id,
            goal=db_session.goal,
            admin_token=db_session.admin_token,
            status=db_session.status,
            participants=participants,
            max_steps=db_session.max_steps
        )


async def get_session_snapshot(code: str, max_points_per_participant: int = 200) -> dict:
    """
    Returns a downsampled snapshot of the session. 
    If a participant has more than max_points_per_participant clicks, 
    the result is decimated to include:
    - The first click (step 1)
    - The best click (global min/max)
    - The latest click
    - A uniform sample of points in between
    """
    async with AsyncSessionLocal() as db:
        session_stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(session_stmt)
        db_session = result.scalar_one_or_none()
        if not db_session:
            return None

        # Get all participants
        part_stmt = select(ParticipantModel).where(ParticipantModel.session_id == db_session.id)
        result = await db.execute(part_stmt)
        participants_db = result.scalars().all()

        participants_res = []
        for p in participants_db:
            # Get total count
            count_stmt = select(func.count(ClickModel.id)).where(ClickModel.participant_id == p.id)
            total_count = (await db.execute(count_stmt)).scalar() or 0

            clicks_res = []
            if total_count > 0:
                if total_count <= max_points_per_participant:
                    # Load all
                    click_stmt = select(ClickModel).where(ClickModel.participant_id == p.id).order_by(ClickModel.step)
                    clicks_db = (await db.execute(click_stmt)).scalars().all()
                    clicks_res = [{"x": c.x, "y": c.y, "z": c.z, "step": c.step} for c in clicks_db]
                else:
                    # DOWNSAMPLING LOGIC
                    # 1. Get Best Point
                    best_op = func.min(ClickModel.z) if db_session.goal == "min" else func.max(ClickModel.z)
                    best_z_val = (await db.execute(select(best_op).where(ClickModel.participant_id == p.id))).scalar()
                    best_click_stmt = select(ClickModel).where(
                        ClickModel.participant_id == p.id, 
                        ClickModel.z == best_z_val
                    ).limit(1)
                    best_click = (await db.execute(best_click_stmt)).scalar()

                    # 2. Get Sampled Points (including first and last)
                    # We use a stride to pick points
                    stride = total_count // (max_points_per_participant - 1)
                    # Use modulo in SQL to sample
                    sample_stmt = select(ClickModel).where(
                        ClickModel.participant_id == p.id,
                        (ClickModel.step - 1) % stride == 0
                    ).order_by(ClickModel.step).limit(max_points_per_participant)
                    
                    sampled_clicks = (await db.execute(sample_stmt)).scalars().all()
                    
                    # 3. Combine and Deduplicate (ensure best and last are in)
                    last_click_stmt = select(ClickModel).where(ClickModel.participant_id == p.id).order_by(ClickModel.step.desc()).limit(1)
                    last_click = (await db.execute(last_click_stmt)).scalar()
                    
                    seen_steps = set()
                    for c in sampled_clicks:
                        if c.step not in seen_steps:
                            clicks_res.append({"x": c.x, "y": c.y, "z": c.z, "step": c.step})
                            seen_steps.add(c.step)
                    
                    if best_click and best_click.step not in seen_steps:
                        clicks_res.append({"x": best_click.x, "y": best_click.y, "z": best_click.z, "step": best_click.step})
                        seen_steps.add(best_click.step)
                    
                    if last_click and last_click.step not in seen_steps:
                        clicks_res.append({"x": last_click.x, "y": last_click.y, "z": last_click.z, "step": last_click.step})
                        seen_steps.add(last_click.step)
                    
                    # Sort by step again for the UI
                    clicks_res.sort(key=lambda x: x["step"])

            participants_res.append({
                "participant_id": p.participant_code,
                "name": p.name,
                "is_bot": p.is_bot,
                "found": p.found_step is not None,
                "found_step": p.found_step,
                "clicks": clicks_res,
                "total_clicks": total_count 
            })

        return {
            "session_code": db_session.code,
            "status": db_session.status,
            "function_id": db_session.function_id,
            "goal": db_session.goal,
            "participants": participants_res,
        }

async def join_session(code: str, name: str, is_bot: bool = False) -> Participant:
    # Invalidate participant count and snapshot cache
    redis = get_redis()
    if redis:
        await redis.delete(f"participants_count:{code}")
        await redis.delete(f"snapshot:{code}")

    async with AsyncSessionLocal() as db:
        stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            raise KeyError("session not found")

        pid = uuid4().hex[:8]

        db_participant = ParticipantModel(
            participant_code=pid,
            is_bot=is_bot,
            name=name,
            session_id=db_session.id,
        )
        db.add(db_participant)
        await db.commit()
        await db.refresh(db_participant)

        return Participant(
            id=db_participant.participant_code,
            name=db_participant.name,
            clicks=[],
            found_step=db_participant.found_step,
            found_z=db_participant.found_z,
        )

async def add_click(code: str, participant_id: str, x: float, y: float, z: float) -> dict:
    async with AsyncSessionLocal() as db:
        # 1. Get Session
        session_stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(session_stmt)
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise KeyError("session not found")

        # 2. Get Participant
        participant_stmt = select(ParticipantModel).where(
            ParticipantModel.session_id == db_session.id,
            ParticipantModel.participant_code == participant_id,
        )
        result = await db.execute(participant_stmt)
        db_participant = result.scalar_one_or_none()
        if not db_participant:
            raise KeyError("participant not found")

        # 3. Step Count
        count_stmt = select(func.count(ClickModel.id)).where(ClickModel.participant_id == db_participant.id)
        result = await db.execute(count_stmt)
        step_count = result.scalar() or 0
        
        if step_count >= db_session.max_steps:
            raise ValueError("max steps reached")
        step = step_count + 1

        # 4. Add Click
        db_click = ClickModel(
            x=x,
            y=y,
            z=z,
            step=step,
            participant_id=db_participant.id,
        )
        db.add(db_click)
        await db.commit()
        await db.refresh(db_click)

        # 5. Best Z
        z_agg = func.min(ClickModel.z) if db_session.goal == "min" else func.max(ClickModel.z)
        best_z_stmt = select(z_agg).where(ClickModel.participant_id == db_participant.id)
        result = await db.execute(best_z_stmt)
        best_z = result.scalar()

        spec = get_spec(db_session.function_id)
        found_now = False

        if db_participant.found_step is None:
            if db_session.goal == "min" and best_z <= spec.target_z + spec.tolerance:
                db_participant.found_step = step
                db_participant.found_z = best_z
                found_now = True

            elif db_session.goal == "max" and best_z >= spec.target_z - spec.tolerance:
                db_participant.found_step = step
                db_participant.found_z = best_z
                found_now = True

            if found_now:
                await db.commit()
                await db.refresh(db_participant)

        # Invalidate leaderboard and snapshot cache
        redis = get_redis()
        if redis:
            await redis.delete(f"leaderboard:{code}")
            await redis.delete(f"snapshot:{code}")

        return {
            "step": step,
            "best_z": best_z,
            "found": db_participant.found_step is not None,
            "found_step": db_participant.found_step,
            "found_now": found_now,
        }


async def add_trajectory(code: str, participant_id: str, points: list[dict]) -> dict:
    if not points:
        return {}

    async with AsyncSessionLocal() as db:
        # 1. Get Session
        session_stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(session_stmt)
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise KeyError("session not found")

        # 2. Get Participant
        participant_stmt = select(ParticipantModel).where(
            ParticipantModel.session_id == db_session.id,
            ParticipantModel.participant_code == participant_id,
        )
        result = await db.execute(participant_stmt)
        db_participant = result.scalar_one_or_none()
        if not db_participant:
            raise KeyError("participant not found")

        # 3. Anti-Cheat Verification
        # Sample up to 5 points to verify
        sample_size = min(len(points), 5)
        samples = random.sample(points, sample_size)
        spec = get_spec(db_session.function_id)

        for p in samples:
            true_z = evaluate_function(db_session.function_id, p["x"], p["y"])
            if abs(p["z"] - true_z) > 1e-4:  # Small epsilon for float comparison
                raise ValueError(f"Anti-cheat verification failed for point ({p['x']}, {p['y']})")

        # 4. Step Management
        count_stmt = select(func.count(ClickModel.id)).where(ClickModel.participant_id == db_participant.id)
        result = await db.execute(count_stmt)
        current_steps = result.scalar() or 0
        
        if current_steps + len(points) > db_session.max_steps:
            raise ValueError("Trajectory would exceed max steps limit")

        # 5. Bulk Insert
        new_clicks = []
        best_z = None
        found_now = False
        found_step = db_participant.found_step

        for i, p in enumerate(points):
            step = current_steps + i + 1
            new_clicks.append({
                "x": p["x"],
                "y": p["y"],
                "z": p["z"],
                "step": step,
                "participant_id": db_participant.id
            })

            # Track best Z in this batch
            if best_z is None:
                best_z = p["z"]
            else:
                if db_session.goal == "min":
                    best_z = min(best_z, p["z"])
                else:
                    best_z = max(best_z, p["z"])

            # Check if found
            if found_step is None:
                if db_session.goal == "min" and p["z"] <= spec.target_z + spec.tolerance:
                    found_step = step
                    db_participant.found_step = step
                    db_participant.found_z = p["z"]
                    found_now = True
                elif db_session.goal == "max" and p["z"] >= spec.target_z - spec.tolerance:
                    found_step = step
                    db_participant.found_step = step
                    db_participant.found_z = p["z"]
                    found_now = True

        # Perform bulk insert
        if new_clicks:
            await db.execute(insert(ClickModel), new_clicks)
        
        if found_now:
            await db.commit()
            await db.refresh(db_participant)
        else:
            await db.commit()

        # Invalidate caches
        redis = get_redis()
        if redis:
            await redis.delete(f"leaderboard:{code}")
            await redis.delete(f"snapshot:{code}")

        return {
            "batch_size": len(points),
            "total_steps": current_steps + len(points),
            "best_z": best_z,
            "found": db_participant.found_step is not None,
            "found_step": db_participant.found_step,
            "found_now": found_now,
        }


async def compute_leaderboard(code: str) -> list[dict]:
    redis = get_redis()
    cache_key = f"leaderboard:{code}"
    cached = await redis.get(cache_key) if redis else None
    if cached:
        return json.loads(cached)

    async with AsyncSessionLocal() as db:
        session_stmt = select(SessionModel).where(SessionModel.code == code)
        result = await db.execute(session_stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            raise KeyError("session not found")

        # Get participants
        part_stmt = select(ParticipantModel).where(ParticipantModel.session_id == db_session.id)
        result = await db.execute(part_stmt)
        participants = result.scalars().all()
        
        rows: list[dict] = []
        for p in participants:
            z_agg = func.min(ClickModel.z) if db_session.goal == "min" else func.max(ClickModel.z)
            res_stmt = select(func.count(ClickModel.id), z_agg).where(ClickModel.participant_id == p.id)
            res_result = await db.execute(res_stmt)
            res = res_result.first()
            
            steps = res[0] or 0
            best_z = res[1]

            rows.append({
                "participant_id": p.participant_code,
                "name": p.name,
                "is_bot": getattr(p, "is_bot", False),
                "steps": steps,
                "best_z": best_z,
                "found": p.found_step is not None,
                "found_step": p.found_step,
            })

        if db_session.goal == "min":
            rows.sort(
                key=lambda r: (
                    not r["found"],
                    r["found_step"] if r["found_step"] is not None else 10**9,
                    r["best_z"] if r["best_z"] is not None else float("inf"),
                    r["steps"],
                )
            )
        else:
            rows.sort(
                key=lambda r: (
                    not r["found"],
                    r["found_step"] if r["found_step"] is not None else 10**9,
                    -(r["best_z"] if r["best_z"] is not None else float("-inf")),
                    r["steps"],
                )
            )

        if redis:
            await redis.setex(cache_key, settings.CACHE_TTL, json.dumps(rows))
        return rows

async def set_session_status(code: str, status: str) -> Session:
    # Invalidate cache
    redis = get_redis()
    if redis:
        await redis.delete(f"session_basic:{code}")
        await redis.delete(f"participants_count:{code}")
        await redis.delete(f"snapshot:{code}")

    async with AsyncSessionLocal() as db:
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.participants).selectinload(ParticipantModel.clicks))
            .where(SessionModel.code == code)
        )
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            raise KeyError("session not found")

        db_session.status = status
        await db.commit()
        await db.refresh(db_session)

        participants = {}
        for p in db_session.participants:
            clicks = [
                Click(x=c.x, y=c.y, z=c.z)
                for c in sorted(p.clicks, key=lambda click: click.step)
            ]

            participants[p.participant_code] = Participant(
                id=p.participant_code,
                name=p.name,
                clicks=clicks,
                is_bot=getattr(p, "is_bot", False),
                found_step=p.found_step,
                found_z=p.found_z,
            )

        return Session(
            code=db_session.code,
            function_id=db_session.function_id,
            goal=db_session.goal,
            admin_token=db_session.admin_token,
            status=db_session.status,
            participants=participants,
            max_steps=db_session.max_steps
        )
