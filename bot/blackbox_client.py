from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests
import math


@dataclass
class PublicSessionInfo:
    session_code: str
    participants: int
    status: str
    max_steps: int


class BlackBoxClient:
    def __init__(self, api_url: str, session_code: str, participant_id: str | None = None):
        self.api_url = api_url.rstrip("/")
        self.session_code = session_code
        self.participant_id = participant_id
        self.blackbox_payload = None

    def get_public_info(self) -> PublicSessionInfo:
        r = requests.get(f"{self.api_url}/sessions/{self.session_code}/public", timeout=10)
        r.raise_for_status()
        data = r.json()
        return PublicSessionInfo(
            session_code=data["session_code"],
            participants=data["participants"],
            status=data["status"],
            max_steps=data["max_steps"],
        )

    def join(self, name: str, is_bot: bool = True) -> str:
        r = requests.post(
            f"{self.api_url}/sessions/{self.session_code}/join",
            json={"name": name, "is_bot": is_bot},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        self.participant_id = data["participant_id"]
        self.blackbox_payload = data.get("blackbox")
        return self.participant_id

    def evaluate(self, x: float, y: float) -> dict[str, Any]:
        """Official evaluation on the server (counts as a step)."""
        if not self.participant_id:
            raise RuntimeError("participant_id missing. Call join() first.")

        r = requests.post(
            f"{self.api_url}/sessions/{self.session_code}/evaluate",
            json={
                "participant_id": self.participant_id,
                "x": x,
                "y": y,
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def sync_trajectory(self, points: list[dict[str, float]]) -> dict[str, Any]:
        """Sync a batch of points to the server."""
        if not self.participant_id:
            raise RuntimeError("participant_id missing. Call join() first.")

        r = requests.post(
            f"{self.api_url}/sessions/{self.session_code}/sync_trajectory",
            json={
                "participant_id": self.participant_id,
                "points": points,
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def evaluate_local(self, x: float, y: float) -> float:
        """Evaluates the function locally using the obfuscated blackbox payload."""
        if not self.blackbox_payload:
            raise RuntimeError("No blackbox payload available. Did you join the session?")

        stack = []
        it = iter(self.blackbox_payload)
        
        # Opcodes mapping (must match backend/app/core/functions.py)
        # X: 1, Y: 2, CONST: 3, ADD: 10, SUB: 11, MUL: 12, DIV: 13, POW: 14, SIN: 15, COS: 16, SQRT: 17, ABS: 18, EXP: 19, PI: 20
        
        for op in it:
            if op == 1: # OP_X
                stack.append(x)
            elif op == 2: # OP_Y
                stack.append(y)
            elif op == 3: # OP_CONST
                stack.append(next(it))
            elif op == 10: # OP_ADD
                b, a = stack.pop(), stack.pop()
                stack.append(a + b)
            elif op == 11: # OP_SUB
                b, a = stack.pop(), stack.pop()
                stack.append(a - b)
            elif op == 12: # OP_MUL
                b, a = stack.pop(), stack.pop()
                stack.append(a * b)
            elif op == 13: # OP_DIV
                b, a = stack.pop(), stack.pop()
                stack.append(a / b)
            elif op == 14: # OP_POW
                b, a = stack.pop(), stack.pop()
                stack.append(a ** b)
            elif op == 15: # OP_SIN
                stack.append(math.sin(stack.pop()))
            elif op == 16: # OP_COS
                stack.append(math.cos(stack.pop()))
            elif op == 17: # OP_SQRT
                stack.append(math.sqrt(stack.pop()))
            elif op == 18: # OP_ABS
                stack.append(abs(stack.pop()))
            elif op == 19: # OP_EXP
                stack.append(math.exp(stack.pop()))
            elif op == 20: # OP_PI
                stack.append(math.pi)
            else:
                raise ValueError(f"Unknown opcode: {op}")
        
        return stack.pop()
