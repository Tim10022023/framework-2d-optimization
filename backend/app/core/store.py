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
    # Detailed session with sampled clicks
    async with AsyncSessionLocal() as db:
        # Avoid selectinload for clicks as it might still be many points
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.participants))
            .where(SessionModel.code == code)
        )
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            return None

        participants = {}
        for p in db_session.participants:
            # Load clicks separately and sorted - only the ones we actually stored!
            click_stmt = select(ClickModel).where(ClickModel.participant_id == p.id).order_by(ClickModel.step)
            clicks_db = (await db.execute(click_stmt)).scalars().all()
            
            clicks = [
                Click(x=c.x, y=c.y, z=c.z)
                for c in clicks_db
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

        # 3. Step Count & Limits
        if db_participant.total_clicks >= db_session.max_steps:
            raise ValueError("max steps reached")
        
        step = db_participant.total_clicks + 1

        # 4. Add Click (Always store single clicks)
        db_click = ClickModel(
            x=x,
            y=y,
            z=z,
            step=step,
            participant_id=db_participant.id,
        )
        db.add(db_click)
        
        # 5. Update Participant Metrics
        db_participant.total_clicks = step
        if db_participant.best_z is None:
            db_participant.best_z = z
        else:
            if db_session.goal == "min":
                db_participant.best_z = min(db_participant.best_z, z)
            else:
                db_participant.best_z = max(db_participant.best_z, z)

        spec = get_spec(db_session.function_id)
        found_now = False

        if db_participant.found_step is None:
            if db_session.goal == "min" and db_participant.best_z <= spec.target_z + spec.tolerance:
                db_participant.found_step = step
                db_participant.found_z = db_participant.best_z
                found_now = True
            elif db_session.goal == "max" and db_participant.best_z >= spec.target_z - spec.tolerance:
                db_participant.found_step = step
                db_participant.found_z = db_participant.best_z
                found_now = True

        await db.commit()

        # Invalidate leaderboard and snapshot cache
        redis = get_redis()
        if redis:
            await redis.delete(f"leaderboard:{code}")
            await redis.delete(f"snapshot:{code}")

        return {
            "step": step,
            "best_z": db_participant.best_z,
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

        # 3. Anti-Cheat Verification (Sample 5 points)
        sample_size_verify = min(len(points), 5)
        verify_samples = random.sample(points, sample_size_verify)
        spec = get_spec(db_session.function_id)
        for p in verify_samples:
            true_z = evaluate_function(db_session.function_id, p["x"], p["y"])
            if abs(p["z"] - true_z) > 1e-4:
                raise ValueError(f"Anti-cheat verification failed for point ({p['x']}, {p['y']})")

        # 4. Step Management
        start_step = db_participant.total_clicks
        if start_step + len(points) > db_session.max_steps:
            raise ValueError("Trajectory would exceed max steps limit")

        # 5. Sampling (Root of performance fix)
        # We only want to store a few points in the DB for visualization, 
        # but the bot counts all of them for total_clicks.
        MAX_POINTS_TO_STORE_PER_BATCH = 50
        stride = max(1, len(points) // MAX_POINTS_TO_STORE_PER_BATCH)
        
        best_point_in_batch = None
        new_clicks_to_db = []
        
        for i, p in enumerate(points):
            current_abs_step = start_step + i + 1
            
            # Track best point globally for the participant
            is_new_best = False
            if db_participant.best_z is None:
                db_participant.best_z = p["z"]
                is_new_best = True
            else:
                if db_session.goal == "min" and p["z"] < db_participant.best_z:
                    db_participant.best_z = p["z"]
                    is_new_best = True
                elif db_session.goal == "max" and p["z"] > db_participant.best_z:
                    db_participant.best_z = p["z"]
                    is_new_best = True

            # Track if this point found the goal
            found_now = False
            if db_participant.found_step is None:
                if db_session.goal == "min" and p["z"] <= spec.target_z + spec.tolerance:
                    db_participant.found_step = current_abs_step
                    db_participant.found_z = p["z"]
                    found_now = True
                elif db_session.goal == "max" and p["z"] >= spec.target_z - spec.tolerance:
                    db_participant.found_step = current_abs_step
                    db_participant.found_z = p["z"]
                    found_now = True

            # Decision: Should we store this point in the DB for the plot?
            # 1. Take every N-th point (stride)
            # 2. Or if it is the best point of the batch
            # 3. Or if it is the very last point
            should_store = (i % stride == 0) or (i == len(points) - 1) or is_new_best
            
            if should_store:
                new_clicks_to_db.append({
                    "x": p["x"],
                    "y": p["y"],
                    "z": p["z"],
                    "step": current_abs_step,
                    "participant_id": db_participant.id
                })

        # 6. Finalize
        db_participant.total_clicks = start_step + len(points)
        
        if new_clicks_to_db:
            # Sort to ensure order and avoid duplicates in the same step
            unique_clicks = {c["step"]: c for c in new_clicks_to_db}.values()
            await db.execute(insert(ClickModel), list(unique_clicks))
        
        await db.commit()

        # Invalidate caches
        redis = get_redis()
        if redis:
            await redis.delete(f"leaderboard:{code}")
            await redis.delete(f"snapshot:{code}")

        return {
            "batch_size": len(points),
            "total_steps": db_participant.total_clicks,
            "best_z": db_participant.best_z,
            "found": db_participant.found_step is not None,
            "found_step": db_participant.found_step,
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

        # Get participants - use the metrics stored on the participant model!
        part_stmt = select(ParticipantModel).where(ParticipantModel.session_id == db_session.id)
        result = await db.execute(part_stmt)
        participants = result.scalars().all()
        
        rows: list[dict] = []
        for p in participants:
            rows.append({
                "participant_id": p.participant_code,
                "name": p.name,
                "is_bot": getattr(p, "is_bot", False),
                "steps": p.total_clicks,
                "best_z": p.best_z,
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
            .where(SessionModel.code == code)
        )
        result = await db.execute(stmt)
        db_session = result.scalar_one_or_none()
        
        if not db_session:
            raise KeyError("session not found")

        db_session.status = status
        await db.commit()
        
        # Reuse optimized get_session to return updated state
        return await get_session(code)
