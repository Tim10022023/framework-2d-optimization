import { useEffect, useMemo, useRef, useState } from "react";
import { createSession, endSession, evaluatePoint, exportSession, getLeaderboard, joinSession } from "./api";

type Point = { x: number; y: number; z: number; step: number };

export default function App() {
  const [error, setError] = useState<string | null>(null);

  // Dozent
  const [createdCode, setCreatedCode] = useState<string>("");
  const [adminToken, setAdminToken] = useState<string>("");

  // Teilnehmer
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [participantId, setParticipantId] = useState<string | null>(null);

  const [points, setPoints] = useState<Point[]>([]);
  const [leaderboard, setLeaderboard] = useState<any>(null);

  const [exportData, setExportData] = useState<any>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // MVP: feste Bounds
  const bounds = useMemo(() => ({ xmin: -5, xmax: 5, ymin: -5, ymax: 5 }), []);

  async function onCreateSession() {
    setError(null);
    try {
      const r = await createSession("sphere", "min");
      setCreatedCode(r.session_code);
      setAdminToken(r.admin_token);
      setCode(r.session_code); // bequem: direkt ins Join-Feld übernehmen
      setParticipantId(null);
      setPoints([]);
      setExportData(null);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onEndSession() {
    setError(null);
    try {
      await endSession(code.trim(), adminToken.trim());
      const data = await exportSession(code.trim(), adminToken.trim());
      setExportData(data);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onJoin() {
    setError(null);
    try {
      const r = await joinSession(code.trim(), name.trim());
      setParticipantId(r.participant_id);
      setPoints([]);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  // Polling Leaderboard
  useEffect(() => {
    if (!code.trim()) return;
    const id = setInterval(async () => {
      try {
        const lb = await getLeaderboard(code.trim());
        setLeaderboard(lb);
      } catch {
        // ignore
      }
    }, 1000);
    return () => clearInterval(id);
  }, [code]);

  // Canvas render
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;

    const w = c.width, h = c.height;
    ctx.clearRect(0, 0, w, h);

    // Achsen
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h);
    ctx.stroke();

    // Punkte
    for (const p of points) {
      const px = ((p.x - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
      const py = (1 - (p.y - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [points, bounds]);

  async function onCanvasClick(ev: React.MouseEvent<HTMLCanvasElement>) {
    if (!participantId) return;

    const c = canvasRef.current!;
    const rect = c.getBoundingClientRect();
    const xPix = ev.clientX - rect.left;
    const yPix = ev.clientY - rect.top;

    const x = bounds.xmin + (xPix / c.width) * (bounds.xmax - bounds.xmin);
    const y = bounds.ymax - (yPix / c.height) * (bounds.ymax - bounds.ymin);

    setError(null);
    try {
      const r = await evaluatePoint(code.trim(), participantId, Number(x.toFixed(4)), Number(y.toFixed(4)));
      setPoints((prev) => [...prev, { x: r.x, y: r.y, z: r.z, step: r.step }]);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  return (
    <div style={{ display: "flex", gap: 16, padding: 16, fontFamily: "system-ui, sans-serif" }}>
      <div style={{ flex: 1 }}>
        <h2>2D Optimization (Frontend MVP)</h2>

        {/* Dozent */}
        <div style={{ border: "1px solid #eee", padding: 12, marginBottom: 12 }}>
          <h3 style={{ marginTop: 0 }}>Dozent</h3>
          <button onClick={onCreateSession}>Neue Session erstellen (sphere/min)</button>
          <div style={{ marginTop: 8, fontSize: 12 }}>
            session_code: <b>{createdCode || "-"}</b>
            <br />
            admin_token: <code>{adminToken || "-"}</code>
          </div>
          <div style={{ marginTop: 8 }}>
            <button onClick={onEndSession} disabled={!code.trim() || !adminToken.trim()}>
              Session beenden + Export laden
            </button>
          </div>
        </div>

        {/* Teilnehmer */}
        {!participantId ? (
          <div style={{ display: "grid", gap: 8, maxWidth: 360 }}>
            <h3 style={{ margin: 0 }}>Teilnehmer</h3>
            <label>
              Session-Code
              <input value={code} onChange={(e) => setCode(e.target.value)} style={{ width: "100%" }} />
            </label>
            <label>
              Name
              <input value={name} onChange={(e) => setName(e.target.value)} style={{ width: "100%" }} />
            </label>
            <button onClick={onJoin} disabled={!code.trim() || !name.trim()}>
              Join
            </button>
            <div style={{ fontSize: 12, opacity: 0.7 }}>
              API: <code>{import.meta.env.VITE_API_URL}</code>
            </div>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: 8, fontSize: 14 }}>
              Session: <b>{code}</b> • Participant: <code>{participantId}</code>
            </div>

            <canvas
              ref={canvasRef}
              width={600}
              height={600}
              onClick={onCanvasClick}
              style={{ border: "1px solid #ccc", cursor: "crosshair" }}
              title="Klicken zum Evaluieren"
            />

            <div style={{ marginTop: 12 }}>
              <h3>Meine Klicks</h3>
              <div style={{ fontSize: 12, maxHeight: 200, overflow: "auto", border: "1px solid #eee", padding: 8 }}>
                {points.length === 0 ? (
                  <div>Noch keine Klicks.</div>
                ) : (
                  points
                    .slice()
                    .reverse()
                    .map((p) => (
                      <div key={p.step}>
                        #{p.step} → (x={p.x}, y={p.y}) ⇒ z={p.z}
                      </div>
                    ))
                )}
              </div>
            </div>
          </>
        )}

        {exportData && (
          <div style={{ marginTop: 12, border: "1px solid #eee", padding: 12 }}>
            <h3 style={{ marginTop: 0 }}>Export (Reveal)</h3>
            <div style={{ fontSize: 12, maxHeight: 220, overflow: "auto" }}>
              <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(exportData, null, 2)}</pre>
            </div>
          </div>
        )}

        {error && (
          <pre style={{ marginTop: 12, color: "crimson", whiteSpace: "pre-wrap" }}>
            {error}
          </pre>
        )}
      </div>

      {/* Leaderboard */}
      <div style={{ width: 380 }}>
        <h3>Leaderboard (polling)</h3>
        <div style={{ fontSize: 12, border: "1px solid #eee", padding: 8, minHeight: 200 }}>
          {!leaderboard ? (
            <div>No data yet.</div>
          ) : (
            <ol>
              {leaderboard.leaderboard?.map((r: any) => (
                <li key={r.participant_id}>
                  <b>{r.name}</b> — found: {String(r.found)} — found_step: {r.found_step ?? "-"} — steps: {r.steps} — best_z: {r.best_z ?? "-"}
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}
