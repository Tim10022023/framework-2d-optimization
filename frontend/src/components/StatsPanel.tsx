import type { Point } from "../types";

type Props = {
  points: Point[];
  targetZ: number;
  tolerance: number;
};

export default function StatsPanel({ points, targetZ, tolerance }: Props) {
  const clicks = points.length;

  const bestZ = points.length > 0 ? Math.min(...points.map((p) => p.z)) : null;

  const foundStep =
    points.find((p) => Math.abs(p.z - targetZ) <= tolerance)?.step ?? null;

  const found = foundStep !== null;

  return (
    <div style={{ border: "1px solid #eee", padding: 14 }}>
      <h3 style={{ marginTop: 0, marginBottom: 12 }}>Meine Statistik</h3>

      <div
        style={{
          fontSize: 12,
          opacity: 0.8,
          marginBottom: 6,
          textTransform: "uppercase",
          letterSpacing: 0.4,
        }}
      >
        Bester Wert
      </div>

      <div
        style={{
          fontSize: 24,
          fontWeight: 800,
          marginBottom: 14,
          lineHeight: 1.1,
        }}
      >
        {bestZ ?? "—"}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "auto auto",
          gap: "8px 16px",
          fontSize: 14,
          alignItems: "center",
        }}
      >
        <div style={{ opacity: 0.8 }}>Klicks</div>
        <div>
          <b>{clicks}</b>
        </div>

        <div style={{ opacity: 0.8 }}>Gefunden</div>
        <div>
          <b>{found ? "Ja" : "Nein"}</b>
        </div>

        <div style={{ opacity: 0.8 }}>Found-Step</div>
        <div>
          <b>{foundStep ?? "—"}</b>
        </div>
      </div>
    </div>
  );
}
