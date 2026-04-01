import type { LeaderboardResponse } from "../types";

type Props = {
  leaderboard: LeaderboardResponse | null;
  onSelectParticipant?: (participantId: string) => void;
  onHover?: (pid: string | null) => void;
  hoveredPid?: string | null;
};

type Row = {
  participant_id: string;
  name: string;
  is_bot?: boolean;
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
  onHover,
  hoveredPid,
}: Props) {
  const rows = extractRows(leaderboard);

  return (
    <div style={{ border: "1px solid #eee", padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Live-Leaderboard</h3>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
        Beste aktuelle Werte der laufenden Session.
      </div>

      {rows.length === 0 ? (
        <div style={{ fontSize: 12, opacity: 0.8 }}>No data yet.</div>
      ) : (
        <ul style={{ listStyle: "none", paddingLeft: 0, margin: 0 }}>
          {rows.map((r, idx) => {
            const isHovered = hoveredPid === r.participant_id;
            return (
              <li
                key={r.participant_id}
                onMouseEnter={() => onHover?.(r.participant_id)}
                onMouseLeave={() => onHover?.(null)}
                style={{
                  marginBottom: 12,
                  padding: "8px 10px",
                  border: isHovered ? "2px solid #4dabf7" : "1px solid #333",
                  borderRadius: 8,
                  backgroundColor: isHovered ? "rgba(77, 171, 247, 0.05)" : "transparent",
                  transition: "all 0.2s ease",
                  transform: isHovered ? "translateX(4px)" : "none",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    gap: 8,
                    alignItems: "center",
                    marginBottom: 4,
                  }}
                >
                  <div
                    style={{
                      width: 22,
                      textAlign: "right",
                      opacity: 0.8,
                      fontWeight: 700,
                    }}
                  >
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
                      fontWeight: 800,
                      fontSize: 15,
                    }}
                    title={r.participant_id}
                  >
                    {r.name}
                    {r.is_bot ? " [Bot]" : ""}
                  </button>
                </div>

                <div
                  style={{
                    marginLeft: 30,
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 8,
                    fontSize: 12,
                  }}
                >
                  <span>
                    Klicks: <b>{r.steps}</b>
                  </span>
                  <span>
                    best_z: <b>{r.best_z ?? "-"}</b>
                  </span>
                  <span>
                    found_step: <b>{r.found_step ?? "—"}</b>
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
