const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type JoinResponse = { participant_id: string; name: string; session_code: string };

export async function joinSession(code: string, name: string): Promise<JoinResponse> {
  const res = await fetch(`${API_URL}/sessions/${code}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export type EvaluateResponse = {
  x: number; y: number; z: number;
  step: number; best_z: number;
  found: boolean; found_step: number | null; found_now: boolean;
};

export async function evaluatePoint(code: string, participantId: string, x: number, y: number): Promise<EvaluateResponse> {
  const res = await fetch(`${API_URL}/sessions/${code}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ participant_id: participantId, x, y }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getLeaderboard(code: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/leaderboard`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export type CreateSessionResponse = { session_code: string; function_id: string; goal: string; admin_token: string };

export async function createSession(function_id: string, goal: "min" | "max"): Promise<CreateSessionResponse> {
  const res = await fetch(`${API_URL}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ function_id, goal }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function endSession(code: string, adminToken: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/end`, {
    method: "POST",
    headers: { "X-Admin-Token": adminToken },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function exportSession(code: string, adminToken: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/export`, {
    headers: { "X-Admin-Token": adminToken },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
