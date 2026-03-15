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
  is_bot?: boolean;
  steps: number;
  best_z: number | null;
  found: boolean;
  found_step: number | null;
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
  max_steps: number;
};

export type SnapshotClick = { x: number; y: number; z: number };

export type SnapshotParticipant = {
  participant_id: string;
  name: string;
  is_bot: boolean;
  found: boolean;
  found_step: number | null;
  clicks: SnapshotClick[];
};

export type SessionSnapshot = {
  session_code: string;
  status: string;
  function_id: string;
  goal: string;
  participants: SnapshotParticipant[];
};

export type ExportReveal = {
  function_id: string;
  title: string;
  description?: string | null;
  image?: string | null;
};

export type ExportParticipant = {
  participant_id: string;
  name: string;
  is_bot?: boolean;
  steps: number;
  found: boolean;
  found_step: number | null;
  found_z?: number | null;
  clicks: { x: number; y: number; z: number }[];
};

export type ExportData = {
  session_code: string;
  status: string;
  goal: "min" | "max";
  function: {
    id: string;
    name: string;
    allowed_goals: string[];
    target_z: number;
    tolerance: number;
    bounds: {
      xmin: number;
      xmax: number;
      ymin: number;
      ymax: number;
    };
  };
  reveal?: ExportReveal;
  participants: ExportParticipant[];
  leaderboard: unknown;
};
