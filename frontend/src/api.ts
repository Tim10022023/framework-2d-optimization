import type {
  CreateSessionResponse,
  EvaluateResponse,
  FunctionSpec,
  JoinResponse,
  SessionInfo,
  SessionSnapshot,
} from "./types";
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    const detail = data?.detail;

    if (detail === "session not found") return "Session-Code nicht gefunden.";
    if (detail === "session ended") return "Die Session wurde bereits beendet.";
    if (detail === "participant not found") return "Teilnehmer nicht gefunden.";
    if (detail === "invalid admin token") return "Admin-Token ungültig.";
    if (typeof detail === "string") return detail;

    return "Unbekannter Fehler.";
  } catch {
    return `HTTP ${res.status}`;
  }
}

export async function joinSession(
  code: string,
  name: string,
): Promise<JoinResponse> {
  const res = await fetch(`${API_URL}/sessions/${code}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function evaluatePoint(
  code: string,
  participantId: string,
  x: number,
  y: number,
): Promise<EvaluateResponse> {
  const res = await fetch(`${API_URL}/sessions/${code}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ participant_id: participantId, x, y }),
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function getLeaderboard(code: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/leaderboard`);
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function createSession(
  functionId: string,
  goal: "min" | "max",
  maxSteps: number,
): Promise<CreateSessionResponse> {
  const res = await fetch(`${API_URL}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      function_id: functionId,
      goal,
      max_steps: maxSteps,
    }),
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function endSession(code: string, adminToken: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/end`, {
    method: "POST",
    headers: { "X-Admin-Token": adminToken },
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function exportSession(code: string, adminToken: string) {
  const res = await fetch(`${API_URL}/sessions/${code}/export`, {
    headers: { "X-Admin-Token": adminToken },
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function getFunctions(): Promise<{ functions: FunctionSpec[] }> {
  const res = await fetch(`${API_URL}/functions`);
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function getSessionInfo(code: string): Promise<SessionInfo> {
  const res = await fetch(`${API_URL}/sessions/${code}`);
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function startRandomBot(code: string, n: number, seed?: number) {
  const params = new URLSearchParams();
  params.set("n", String(n));
  if (seed !== undefined && seed !== null) params.set("seed", String(seed));

  const res = await fetch(
    `${API_URL}/sessions/${code}/bots/random_search?${params.toString()}`,
    {
      method: "POST",
    },
  );

  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function startHillClimbBot(
  code: string,
  n: number,
  stepSize: number,
  seed?: number,
) {
  const params = new URLSearchParams();
  params.set("n", String(n));
  params.set("step_size", String(stepSize));
  if (seed !== undefined && seed !== null) params.set("seed", String(seed));

  const res = await fetch(
    `${API_URL}/sessions/${code}/bots/hill_climb?${params.toString()}`,
    {
      method: "POST",
    },
  );

  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}

export async function getSessionSnapshot(
  code: string,
): Promise<SessionSnapshot> {
  const res = await fetch(`${API_URL}/sessions/${code}/snapshot`);
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return res.json();
}
