from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

from app.core.functions import get_spec

from app.db.session import SessionLocal
from app.db.models import SessionModel, ParticipantModel, ClickModel

@dataclass
class Click:
    x: float
    y: float
    z: float


@dataclass
class Participant:
    id: str
    name: str
    clicks: List[Click] = field(default_factory=list)
    found_step: Optional[int] = None
    found_z: Optional[float] = None



@dataclass
class Session:
    code: str
    function_id: str
    goal: str
    admin_token: str
    max_steps: int
    status: str = "running"
    participants: Dict[str, Participant] = field(default_factory=dict)




# In-memory "DB"
SESSIONS: Dict[str, Session] = {}


def new_code() -> str:
    # kurz & gut genug fürs MVP
    return uuid4().hex[:6].upper()


def create_session(function_id: str, goal: str, max_steps: int) -> Session:
    code = new_code()
    admin_token = uuid4().hex

    db = SessionLocal()
    try:
        db_session = SessionModel(
            code=code,
            function_id=function_id,
            goal=goal,
            admin_token=admin_token,
            status="running",
            max_steps=max_steps,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return Session(
            code=db_session.code,
            function_id=db_session.function_id,
            goal=db_session.goal,
            admin_token=db_session.admin_token,
            status=db_session.status,
            participants={},
            max_steps=db_session.max_steps
        )
    finally:
        db.close()


def get_session(code: str) -> Optional[Session]:
    db = SessionLocal()
    try:
        db_session = db.query(SessionModel).filter(SessionModel.code == code).first()
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
    finally:
        db.close()

def join_session(code: str, name: str, is_bot: bool = False) -> Participant:
    db = SessionLocal()
    try:
        db_session = db.query(SessionModel).filter(SessionModel.code == code).first()
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
        db.commit()
        db.refresh(db_participant)

        return Participant(
            id=db_participant.participant_code,
            name=db_participant.name,
            clicks=[],
            found_step=db_participant.found_step,
            found_z=db_participant.found_z,
        )
    finally:
        db.close()

def add_click(code: str, participant_id: str, x: float, y: float, z: float) -> dict:
    db = SessionLocal()
    try:
        db_session = db.query(SessionModel).filter(SessionModel.code == code).first()
        if not db_session:
            raise KeyError("session not found")

        db_participant = (
            db.query(ParticipantModel)
            .filter(
                ParticipantModel.session_id == db_session.id,
                ParticipantModel.participant_code == participant_id,
            )
            .first()
        )
        if not db_participant:
            raise KeyError("participant not found")

        current_clicks = sorted(db_participant.clicks, key=lambda c: c.step)
        if len(current_clicks) >= db_session.max_steps:
            raise ValueError("max steps reached")
        step = len(current_clicks) + 1

        db_click = ClickModel(
            x=x,
            y=y,
            z=z,
            step=step,
            participant_id=db_participant.id,
        )
        db.add(db_click)
        db.commit()
        db.refresh(db_click)

        all_zs = [c.z for c in current_clicks] + [z]
        best_z = min(all_zs) if db_session.goal == "min" else max(all_zs)

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
                db.commit()
                db.refresh(db_participant)

        return {
            "step": step,
            "best_z": best_z,
            "found": db_participant.found_step is not None,
            "found_step": db_participant.found_step,
            "found_now": found_now,
        }
    finally:
        db.close()


def compute_leaderboard(code: str) -> list[dict]:
    s = get_session(code)
    if not s:
        raise KeyError("session not found")

    rows: list[dict] = []
    for p in s.participants.values():
        if not p.clicks:
            best_z = None
        else:
            zs = [c.z for c in p.clicks]
            best_z = min(zs) if s.goal == "min" else max(zs)

        rows.append(
            {
                "participant_id": p.id,
                "name": p.name,
                "steps": len(p.clicks),
                "best_z": best_z,
                "found_step": p.found_step,
                "found_z": p.found_z,
                "found": p.found_step is not None,
            }
        )

    # Sortierlogik:
    # 1) Found zuerst (found=True vor found=False)
    # 2) Wenigste found_step (wer schneller "gefunden" hat)
    # 3) Danach best_z (kleiner ist besser bei min, größer ist besser bei max)
    # 4) Danach steps
    if s.goal == "min":
        rows.sort(
            key=lambda r: (
                not r["found"],  # found=True zuerst
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

    return rows

def set_session_status(code: str, status: str) -> Session:
    db = SessionLocal()
    try:
        db_session = db.query(SessionModel).filter(SessionModel.code == code).first()
        if not db_session:
            raise KeyError("session not found")

        db_session.status = status
        db.commit()
        db.refresh(db_session)

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
    finally:
        db.close()

