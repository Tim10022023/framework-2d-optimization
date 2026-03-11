import type { LeaderboardResponse } from "../types";

type LeaderboardPanelProps = {
  leaderboard: LeaderboardResponse | null;
};

export default function LeaderboardPanel({
  leaderboard,
}: LeaderboardPanelProps) {
  return (
    <div style={{ width: 380 }}>
      <h3>Live-Leaderboard</h3>{" "}
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 8 }}>
        Rangliste der aktuellen Session.
      </div>
      <div
        style={{
          fontSize: 12,
          border: "1px solid #eee",
          padding: 8,
          minHeight: 200,
        }}
      >
        {!leaderboard ? (
          <div>No data yet.</div>
        ) : (
          <ol>
            {leaderboard.leaderboard?.map((r) => (
              <li key={r.participant_id}>
                <b>{r.name}</b> — found: {String(r.found)} — found_step:{" "}
                {r.found_step ?? "-"} — steps: {r.steps} — best_z:{" "}
                {r.best_z ?? "-"}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
