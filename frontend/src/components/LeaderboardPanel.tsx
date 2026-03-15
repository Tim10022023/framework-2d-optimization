import type { LeaderboardResponse } from "../types";

type Props = {
  leaderboard: LeaderboardResponse | null;
  onSelectParticipant?: (participantId: string) => void;
};

type Row = {
  participant_id: string;
  name: string;
  steps: number;
  best_z: number | null;
  found_step: number | null;
};

function extractRows(lb: LeaderboardResponse | null): Row[] {
  if (!lb) return [];

  // Variant A: { entries: [...] }
  const anyLb = lb as unknown as { entries?: Row[] };
  if (Array.isArray(anyLb.entries)) return anyLb.entries;

  // Variant B: { leaderboard: [...] }
  const anyLb2 = lb as unknown as { leaderboard?: Row[] };
  if (Array.isArray(anyLb2.leaderboard)) return anyLb2.leaderboard;

  // Variant C: direct array (just in case)
  if (Array.isArray(lb)) return lb as unknown as Row[];

  return [];
}

export default function LeaderboardPanel({
  leaderboard,
  onSelectParticipant,
}: Props) {
  const rows = extractRows(leaderboard);

  return (
    <div style={{ border: "1px solid #eee", padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Live-Leaderboard</h3>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
        Rangliste der aktuellen Session.
      </div>

      {rows.length === 0 ? (
        <div style={{ fontSize: 12, opacity: 0.8 }}>No data yet.</div>
      ) : (
        <ul style={{ listStyle: "none", paddingLeft: 0, margin: 0 }}>
          {rows.map((r, idx) => (
            <li key={r.participant_id} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "baseline" }}>
                <div style={{ width: 18, textAlign: "right", opacity: 0.8 }}>
                  {idx + 1}.
                </div>

                <button
                  onClick={() => onSelectParticipant?.(r.participant_id)}
                  style={{
                    background: "transparent",
                    border: "none",
                    padding: 0,
                    cursor: onSelectParticipant ? "pointer" : "default",
                    textDecoration: onSelectParticipant ? "underline" : "none",
                    fontWeight: 700,
                  }}
                  title={r.participant_id}
                >
                  {r.name}
                </button>
              </div>

              <div style={{ marginLeft: 26, fontSize: 12, opacity: 0.9 }}>
                steps: <b>{r.steps}</b> • best_z: <b>{r.best_z ?? "-"}</b> •
                found_step: <b>{r.found_step ?? "-"}</b>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
