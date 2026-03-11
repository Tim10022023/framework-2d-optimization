import { useState } from "react";

type ExportPanelProps = {
  exportData: any;
};

export default function ExportPanel({ exportData }: ExportPanelProps) {
  const [showRawExport, setShowRawExport] = useState(false);

  if (!exportData) return null;

  return (
    <div style={{ marginTop: 12, border: "1px solid #eee", padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Reveal / Export nach Session-Ende</h3>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 8 }}>
        Zusammenfassung der beendeten Session mit Gewinner und Leaderboard.
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <div>
          <b>Funktion:</b> {exportData.function?.name ?? "-"} (
          {exportData.function?.id ?? "-"})
        </div>
        <div>
          <b>Ziel:</b> {exportData.goal ?? "-"}
        </div>
        <div>
          <b>Teilnehmer:</b> {exportData.participants?.length ?? 0}
        </div>
      </div>

      {exportData.leaderboard?.length > 0 ? (
        <>
          <div style={{ marginBottom: 8 }}>
            <b>Gewinner:</b> {exportData.leaderboard[0].name} (found_step:{" "}
            {exportData.leaderboard[0].found_step ?? "-"}, best_z:{" "}
            {exportData.leaderboard[0].best_z ?? "-"})
          </div>

          <div style={{ fontSize: 12 }}>
            <b>Top 5</b>
            <ol style={{ marginTop: 6 }}>
              {exportData.leaderboard.slice(0, 5).map((r: any) => (
                <li key={r.participant_id} style={{ marginBottom: 4 }}>
                  <b>{r.name}</b> — found: {String(r.found)} — found_step:{" "}
                  {r.found_step ?? "-"} — steps: {r.steps} — best_z:{" "}
                  {r.best_z ?? "-"}
                </li>
              ))}
            </ol>
          </div>
        </>
      ) : (
        <div style={{ fontSize: 12 }}>Kein Leaderboard verfügbar.</div>
      )}

      <div style={{ marginTop: 10 }}>
        <button onClick={() => setShowRawExport((v) => !v)}>
          {showRawExport ? "Raw JSON ausblenden" : "Raw JSON anzeigen"}
        </button>
      </div>

      {showRawExport && (
        <div
          style={{
            marginTop: 10,
            fontSize: 12,
            maxHeight: 260,
            overflow: "auto",
            border: "1px solid #eee",
            padding: 8,
          }}
        >
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(exportData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
