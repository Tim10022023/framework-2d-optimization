import { useEffect, useRef, useState } from "react";
import type { Bounds, Point } from "../types";

type PlotCanvasProps = {
  hideDetails?: boolean;
  code: string;
  participantId: string;
  sessionStatus: string;
  bounds: Bounds;
  points: Point[];
  disableClick?: boolean;
  size?: number;
  extraParticipants?: {
    name: string;
    isBot: boolean;
    clicks: { x: number; y: number }[];
  }[];
  onEvaluate: (x: number, y: number) => Promise<void>;
};

export default function PlotCanvas({
  code,
  size = 600,
  hideDetails = false,
  disableClick = false,
  participantId,
  sessionStatus,
  bounds,
  points,
  extraParticipants,
  onEvaluate,
}: PlotCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hoverCoords, setHoverCoords] = useState<{
    x: number;
    y: number;
  } | null>(null);

  function canvasPixelToCoords(
    xPix: number,
    yPix: number,
    width: number,
    height: number,
  ) {
    const x = bounds.xmin + (xPix / width) * (bounds.xmax - bounds.xmin);
    const y = bounds.ymax - (yPix / height) * (bounds.ymax - bounds.ymin);
    return { x, y };
  }

  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;

    const w = c.width,
      h = c.height;
    ctx.clearRect(0, 0, w, h);

    // Achsen
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h);
    ctx.stroke();

    // Extra Pfade (z.B. Bots / andere Teilnehmer)
    if (extraParticipants && extraParticipants.length > 0) {
      for (const ep of extraParticipants) {
        if (!ep.clicks || ep.clicks.length < 2) continue;

        ctx.save();
        ctx.globalAlpha = 0.5;

        // Bots gestrichelt
        if (ep.isBot) {
          ctx.setLineDash([6, 6]);
        } else {
          ctx.setLineDash([]);
        }

        ctx.beginPath();

        ep.clicks.forEach((p, idx) => {
          const px = ((p.x - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
          const py =
            (1 - (p.y - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;

          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });

        ctx.stroke();
        ctx.restore();
      }
    }

    // Pfadlinie
    if (points.length >= 2) {
      ctx.beginPath();

      points.forEach((p, index) => {
        const px = ((p.x - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
        const py = (1 - (p.y - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;

        if (index === 0) {
          ctx.moveTo(px, py);
        } else {
          ctx.lineTo(px, py);
        }
      });

      ctx.stroke();
    }

    // bester Punkt bestimmen (min z)
    let bestIndex = -1;
    if (points.length > 0) {
      let bestZ = points[0].z;
      bestIndex = 0;
      for (let i = 1; i < points.length; i++) {
        if (points[i].z < bestZ) {
          bestZ = points[i].z;
          bestIndex = i;
        }
      }
    }

    // Punkte
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const px = ((p.x - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
      const py = (1 - (p.y - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;

      const isLast = i === points.length - 1;
      const isBest = i === bestIndex;

      const radius = isLast ? 6 : i === 0 ? 3 : 4;

      ctx.beginPath();
      ctx.arc(px, py, radius, 0, Math.PI * 2);

      // Farbe setzen
      ctx.save();
      if (isBest) {
        ctx.fillStyle = "green";
      }
      ctx.fill();
      ctx.restore();

      // optional: letzten Punkt umranden
      if (isLast) {
        ctx.save();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "black";
        ctx.stroke();
        ctx.restore();
      }
    }

    // Label für letzten Punkt
    if (points.length > 0) {
      const last = points[points.length - 1];
      const px = ((last.x - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
      const py = (1 - (last.y - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;

      ctx.fillText(`#${last.step}`, px + 8, py - 8);
    }
  }, [points, bounds, extraParticipants]);

  async function onCanvasClick(ev: React.MouseEvent<HTMLCanvasElement>) {
    if (sessionStatus === "ended") return;
    if (disableClick) return;
    const c = canvasRef.current;
    if (!c) return;

    const rect = c.getBoundingClientRect();
    const xPix = ev.clientX - rect.left;
    const yPix = ev.clientY - rect.top;

    const { x, y } = canvasPixelToCoords(xPix, yPix, c.width, c.height);
    await onEvaluate(Number(x.toFixed(4)), Number(y.toFixed(4)));
  }

  function onCanvasMove(ev: React.MouseEvent<HTMLCanvasElement>) {
    const c = canvasRef.current;
    if (!c) return;

    const rect = c.getBoundingClientRect();
    const xPix = ev.clientX - rect.left;
    const yPix = ev.clientY - rect.top;

    const { x, y } = canvasPixelToCoords(xPix, yPix, c.width, c.height);
    setHoverCoords({
      x: Number(x.toFixed(3)),
      y: Number(y.toFixed(3)),
    });
  }

  function onCanvasLeave() {
    setHoverCoords(null);
  }

  return (
    <>
      <h3 style={{ marginBottom: 8 }}>Optimierungsfläche</h3>
      {!hideDetails && (
        <div style={{ marginBottom: 8, fontSize: 14 }}>
          Session: <b>{code}</b> • Participant: <code>{participantId}</code>
        </div>
      )}

      {!hideDetails && (
        <div style={{ marginBottom: 8, fontSize: 12, opacity: 0.8 }}>
          Klickbereich: x ∈ [{bounds.xmin}, {bounds.xmax}], y ∈ [{bounds.ymin},{" "}
          {bounds.ymax}]
        </div>
      )}

      <div style={{ marginBottom: 8, fontSize: 12 }}>
        Status: <b>{sessionStatus}</b>
        {sessionStatus === "ended" && (
          <span style={{ color: "crimson", marginLeft: 8 }}>
            Session ist beendet – keine weiteren Klicks möglich.
          </span>
        )}
      </div>

      <canvas
        ref={canvasRef}
        width={size}
        height={size}
        onClick={onCanvasClick}
        onMouseMove={onCanvasMove}
        onMouseLeave={onCanvasLeave}
        style={{
          border: "1px solid #ccc",
          cursor: sessionStatus === "ended" ? "not-allowed" : "crosshair",
          opacity: sessionStatus === "ended" ? 0.6 : 1,
        }}
        title="Klicken zum Evaluieren"
      />

      <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
        Cursor:
        {hoverCoords ? (
          <>
            {" "}
            x = {hoverCoords.x}, y = {hoverCoords.y}
          </>
        ) : (
          <> –</>
        )}
      </div>
    </>
  );
}
