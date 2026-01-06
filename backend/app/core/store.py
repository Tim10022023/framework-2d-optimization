from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

from app.core.functions import get_spec


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
    goal: str  # "min" or "max"
    participants: Dict[str, Participant] = field(default_factory=dict)


# In-memory "DB"
SESSIONS: Dict[str, Session] = {}


def new_code() -> str:
    # kurz & gut genug fürs MVP
    return uuid4().hex[:6].upper()


def create_session(function_id: str, goal: str) -> Session:
    code = new_code()
    session = Session(code=code, function_id=function_id, goal=goal)
    SESSIONS[code] = session
    return session


def get_session(code: str) -> Optional[Session]:
    return SESSIONS.get(code)

def join_session(code: str, name: str) -> Participant:
    s = get_session(code)
    if not s:
        raise KeyError("session not found")

    pid = uuid4().hex[:8]
    p = Participant(id=pid, name=name)
    s.participants[pid] = p
    return p

def add_click(code: str, participant_id: str, x: float, y: float, z: float) -> dict:
    s = get_session(code)
    if not s:
        raise KeyError("session not found")

    p = s.participants.get(participant_id)
    if not p:
        raise KeyError("participant not found")

    p.clicks.append(Click(x=x, y=y, z=z))
    step = len(p.clicks)

    # Bestes z so far
    zs = [c.z for c in p.clicks]
    best_z = min(zs) if s.goal == "min" else max(zs)

    # Found-Kriterium anhand FunctionSpec
    spec = get_spec(s.function_id)
    found_now = False

    if p.found_step is None:
        if s.goal == "min" and best_z <= spec.target_z + spec.tolerance:
            p.found_step = step
            p.found_z = best_z
            found_now = True

    return {
        "step": step,
        "best_z": best_z,
        "found": p.found_step is not None,
        "found_step": p.found_step,
        "found_now": found_now,
    }


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


