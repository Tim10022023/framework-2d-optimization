import type { Point } from "../types";

type StatsPanelProps = {
  points: Point[];
  targetZ: number;
  tolerance: number;
};

export default function StatsPanel({
  points,
  targetZ,
  tolerance,
}: StatsPanelProps) {
  const steps = points.length;
  const bestZ = points.length > 0 ? Math.min(...points.map((p) => p.z)) : null;

  const found =
    bestZ !== null && bestZ <= targetZ + tolerance;

  const foundStep =
    found
      ? points.find((p) => p.z <= targetZ + tolerance)?.step ?? null
      : null;

  return (
    <div style={{ marginTop: 12, border: "1px solid #eee", padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Meine Statistik</h3>
      <div style={{ fontSize: 12 }}>
        <div><b>Klicks:</b> {steps}</div>
        <div><b>Bester z-Wert:</b> {bestZ ?? "-"}</div>
        <div><b>Target z:</b> {targetZ}</div>
        <div><b>Toleranz:</b> {tolerance}</div>
        <div><b>Found:</b> {found ? "Ja" : "Nein"}</div>
        <div><b>Found-Step:</b> {foundStep ?? "-"}</div>
      </div>
    </div>
  );
}