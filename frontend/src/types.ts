export type Bounds = {
  xmin: number;
  xmax: number;
  ymin: number;
  ymax: number;
};

export type FunctionSpec = {
  id: string;
  name: string;
  allowed_goals: ("min" | "max")[];
  target_z: number;
  tolerance: number;
  bounds: Bounds;
};

export type Point = {
  x: number;
  y: number;
  z: number;
  step: number;
};

export type LeaderboardRow = {
  participant_id: string;
  name: string;
  found: boolean;
  found_step: number | null;
  steps: number;
  best_z: number | null;
};

export type LeaderboardResponse = {
  leaderboard?: LeaderboardRow[];
};

export type JoinResponse = {
  participant_id: string;
  name: string;
  session_code: string;
};

export type EvaluateResponse = {
  x: number;
  y: number;
  z: number;
  step: number;
  best_z: number;
  found: boolean;
  found_step: number | null;
  found_now: boolean;
};

export type CreateSessionResponse = {
  session_code: string;
  function_id: string;
  goal: string;
  admin_token: string;
};

export type SessionInfo = {
  session_code: string;
  function_id: string;
  goal: string;
  participants: number;
  status: string;
};
