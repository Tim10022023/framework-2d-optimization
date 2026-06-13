import { useEffect, useRef, useState } from "react";
import type { Bounds, Point } from "../types";

type PlotCanvasProps = {
  hideDetails?: boolean;
  code: string;
  participantId: string;
  sessionStatus: string;
  bounds: Bounds;
  points: Point[];
  goal: "min" | "max";
  disableClick?: boolean;
  size?: number;
  extraParticipants?: {
    name: string;
    isBot?: boolean;
    color?: string;
    clicks: { x: number; y: number; step: number; z?: number }[];
  }[];
  onEvaluate: (x: number, y: number) => Promise<void>;
  hoveredPid?: string | null;
};

function getStableColor(name: string): string {
  const palette = [
    "#4dabf7",
    "#f783ac",
    "#69db7c",
    "#ffd43b",
    "#b197fc",
    "#ffa94d",
    "#63e6be",
    "#ff8787",
  ];

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  }

  return palette[hash % palette.length];
}

export default function PlotCanvas({
  code,
  size = 600,
  hideDetails = false,
  disableClick = false,
  participantId,
  sessionStatus,
  bounds,
  points,
  goal,
  extraParticipants,
  onEvaluate,
  hoveredPid = null,
}: PlotCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [pulseScale, setPulseScale] = useState(1);
  const [hoverCoords, setHoverCoords] = useState<{
    x: number;
    y: number;
  } | null>(null);

  // Animation loop for pulsing best point
  useEffect(() => {
    let frameId: number;
    const start = performance.now();
    const animate = (time: number) => {
      const elapsed = time - start;
      setPulseScale(1 + Math.sin(elapsed / 300) * 0.2);
      frameId = requestAnimationFrame(animate);
    };
    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, []);

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

    const w = c.width;
    const h = c.height;

    ctx.clearRect(0, 0, w, h);
    
    // Helpers for mapping
    const toX = (val: number) => ((val - bounds.xmin) / (bounds.xmax - bounds.xmin)) * w;
    const toY = (val: number) => (1 - (val - bounds.ymin) / (bounds.ymax - bounds.ymin)) * h;

    const zeroX = toX(0);
    const zeroY = toY(0);

    // Achsen
    ctx.save();
    ctx.strokeStyle = "#555";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, zeroY); ctx.lineTo(w, zeroY);
    ctx.moveTo(zeroX, 0); ctx.lineTo(zeroX, h);
    ctx.stroke();
    ctx.restore();

    // Extra-Pfade (z.B. Bots)
    if (extraParticipants && extraParticipants.length > 0) {
      for (const ep of extraParticipants) {
        if (!ep.clicks || ep.clicks.length === 0) continue;

        // Wir brauchen hier eigentlich die participant_id zum Vergleichen.
        // Da wir sie im Prop extraParticipants nicht haben, nutzen wir den Namen als Proxy.
        const isHovered = hoveredPid === ep.name || (ep as any).participant_id === hoveredPid;
        const color = ep.color ?? getStableColor(ep.name);

        ctx.save();
        ctx.globalAlpha = isHovered ? 1.0 : 0.6;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = isHovered ? 3 : 1.5;

        if (ep.isBot) ctx.setLineDash([5, 4]);

        if (ep.clicks.length >= 2) {
          ctx.beginPath();
          ep.clicks.forEach((p, idx) => {
            if (idx === 0) ctx.moveTo(toX(p.x), toY(p.y));
            else ctx.lineTo(toX(p.x), toY(p.y));
          });
          ctx.stroke();
        }

        ep.clicks.forEach((p, idx) => {
          ctx.beginPath();
          const isLast = idx === ep.clicks.length - 1;
          const radius = isLast ? (isHovered ? 6 : 4) : 2.5;
          ctx.arc(toX(p.x), toY(p.y), radius, 0, Math.PI * 2);
          ctx.fill();
        });
        ctx.restore();
      }
    }

    // Eigener Pfad
    if (points.length >= 2) {
      ctx.save();
      ctx.lineWidth = 2.0;
      for (let i = 0; i < points.length - 1; i++) {
        const p1 = points[i];
        const p2 = points[i + 1];
        ctx.beginPath();
        ctx.moveTo(toX(p1.x), toY(p1.y));
        ctx.lineTo(toX(p2.x), toY(p2.y));
        ctx.globalAlpha = p2.opacity ?? 1.0;
        ctx.strokeStyle = p2.color ?? "#111";
        ctx.stroke();
      }
      ctx.restore();
    }

    // Bester Punkt (min/max z) - Global
    const allPoints = [
      ...points.map(p => ({...p, owner: 'me'})),
      ... (extraParticipants ?? []).flatMap(ep => ep.clicks.map(c => ({...c, owner: ep.name})))
    ];

    let bestPoint = null;
    if (allPoints.length > 0) {
      bestPoint = allPoints.reduce((prev, curr) => {
        if (curr.z === undefined) return prev;
        if (prev.z === undefined) return curr;
        if (goal === "min") return curr.z < prev.z ? curr : prev;
        return curr.z > prev.z ? curr : prev;
      });
    }

    // Eigene Punkte
    points.forEach((p, i) => {
      const isLast = i === points.length - 1;
      const radius = p.size ?? (isLast ? 6 : 4);
      ctx.save();
      ctx.globalAlpha = p.opacity ?? 1.0;
      ctx.beginPath();
      ctx.arc(toX(p.x), toY(p.y), radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color ?? "#111";
      ctx.fill();
      if (isLast) {
        ctx.lineWidth = 2;
        ctx.strokeStyle = "white";
        ctx.stroke();
      }
      ctx.restore();
    });

    // Pulse für Besten Punkt
    if (bestPoint && bestPoint.z !== undefined) {
      const bx = toX(bestPoint.x);
      const by = toY(bestPoint.y);
      ctx.save();
      ctx.beginPath();
      ctx.arc(bx, by, 10 * pulseScale, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(255, 215, 0, 0.4)";
      ctx.lineWidth = 3;
      ctx.stroke();
      
      ctx.beginPath();
      ctx.arc(bx, by, 5, 0, Math.PI * 2);
      ctx.fillStyle = "#ffd700";
      ctx.shadowBlur = 15;
      ctx.shadowColor = "#ffd700";
      ctx.fill();
      ctx.restore();
    }

  }, [points, bounds, extraParticipants, pulseScale, goal, hoveredPid]);

  async function onCanvasClick(ev: React.MouseEvent<HTMLCanvasElement>) {
    if (sessionStatus === "ended" || disableClick) return;

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
          cursor:
            sessionStatus === "ended" || disableClick
              ? "not-allowed"
              : "crosshair",
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
