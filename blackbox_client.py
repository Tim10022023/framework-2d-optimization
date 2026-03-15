from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests


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
        self.participant_id = r.json()["participant_id"]
        return self.participant_id

    def evaluate(self, x: float, y: float) -> dict[str, Any]:
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