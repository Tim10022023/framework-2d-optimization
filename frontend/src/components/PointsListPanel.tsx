import type { Point } from "../types";

type PointsListPanelProps = {
  points: Point[];
};

export default function PointsListPanel({ points }: PointsListPanelProps) {
  return (
    <div style={{ marginTop: 12 }}>
      <h3>Meine Klicks</h3>
      <div
        style={{
          fontSize: 12,
          maxHeight: 200,
          overflow: "auto",
          border: "1px solid #eee",
          padding: 8,
        }}
      >
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
  );
}