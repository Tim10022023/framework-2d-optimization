/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useMemo, useState } from "react";
import PlotCanvas from "./PlotCanvas";
import FunctionContourPlot from "./FunctionContourPlot";
import FunctionSurfacePlot from "./FunctionSurfacePlot";
import type { Bounds, SessionSnapshot, Point } from "../types";

type Props = {
  sessionCode: string;
  sessionStatus: string;
  bounds: Bounds;
  snapshot: SessionSnapshot | null;
  selectedPid: string;
  revealFunctionId?: string | null;
  revealed: boolean;
  onSelectPid: (pid: string) => void;
};

export default function TeacherInspectPanel({
  sessionCode,
  sessionStatus,
  bounds,
  snapshot,
  selectedPid,
  revealFunctionId,
  revealed,
  onSelectPid,
}: Props) {
  // useMemo to stabilize participants array to prevent useEffect dependency issues
  const participants = useMemo(
    () => snapshot?.participants ?? [],
    [snapshot?.participants]
  );
  const [visibleStep, setVisibleStep] = useState<number>(0);
  const [showRevealPlots, setShowRevealPlots] = useState(false);

  useEffect(() => {
    if (participants.length === 0) return;

    const stillExists = participants.some(
      (p) => p.participant_id === selectedPid,
    );

    if (!selectedPid || !stillExists) {
      onSelectPid(participants[0].participant_id);
    }
  }, [participants, selectedPid, onSelectPid]);

  const selected =
    participants.find((p) => p.participant_id === selectedPid) ?? null;

  useEffect(() => {
    if (!selected) {
      setVisibleStep(0);
      return;
    }

    if (visibleStep > selected.clicks.length) {
      setVisibleStep(selected.clicks.length);
    }
  }, [selected, visibleStep]);

  useEffect(() => {
    if (!selected) return;
    setVisibleStep(selected.clicks.length);
  }, [selected, selectedPid]);

  useEffect(() => {
    if (!revealed) {
      setShowRevealPlots(false);
    } else if (revealFunctionId) {
      setShowRevealPlots(true);
    }
  }, [revealed, revealFunctionId]);

  const points: Point[] = useMemo(() => {
    if (!selected) return [];
    
    const trailLength = 15;
    const sliced = selected.clicks.slice(0, visibleStep);
    
    return sliced.map((c, idx) => {
      // Trail-Effekt: Berechne Distanz zum aktuell sichtbaren Schritt
      const dist = sliced.length - 1 - idx;
      let opacity = 1.0;
      let size = undefined;
      
      if (dist > 0 && dist < trailLength) {
        // Lineares Fading für die letzten N Schritte
        opacity = 1.0 - (dist / trailLength) * 0.8; // Fadet bis auf 0.2 runter
        size = Math.max(2, 4 - (dist / trailLength) * 2); // Wird etwas kleiner
      } else if (dist >= trailLength) {
        // Alles was älter ist, ist sehr blass
        opacity = 0.15;
        size = 2;
      }
      
      return {
        x: c.x,
        y: c.y,
        z: c.z,
        step: c.step,
        opacity,
        size,
      };
    });
  }, [selected, visibleStep]);

  const goal = snapshot?.goal as "min" | "max" ?? "min";

  const bestZ = useMemo(() => {
    if (points.length === 0) return null;
    const zs = points.map((p) => p.z);
    return goal === "min" ? Math.min(...zs) : Math.max(...zs);
  }, [points, goal]);

  const canShowReveal = revealed && !!revealFunctionId;
  const renderRevealPlots = canShowReveal && showRevealPlots;

  return (
    <div style={{ border: "1px solid #eee", padding: 12 }}>
      <h3 style={{ marginTop: 0 }}>Teilnehmer-Pfade ansehen</h3>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
        Teilnehmer auswählen und deren Klickpfad Schritt für Schritt anzeigen.
      </div>

      {participants.length === 0 ? (
        <div style={{ fontSize: 12, opacity: 0.8 }}>
          Noch keine Teilnehmer in der Session.
        </div>
      ) : (
        <>
          <div style={{ marginBottom: 8 }}>
            <label style={{ fontSize: 12 }}>
              Teilnehmer
              <select
                value={selectedPid}
                onChange={(e) => onSelectPid(e.target.value)}
                style={{
                  display: "block",
                  width: "100%",
                  marginTop: 4,
                }}
              >
                {participants.map((p) => (
                  <option key={p.participant_id} value={p.participant_id}>
                    {p.name}
                    {p.is_bot ? " [Bot]" : ""} ({p.total_clicks})
                  </option>
                ))}
              </select>
            </label>
          </div>

          {selected && (
            <>
              <div style={{ fontSize: 12, marginBottom: 8 }}>
                <b>Auswahl:</b> {selected.name}
                {selected.is_bot ? " [Bot]" : ""} • <b>Klicks:</b>{" "}
                {selected.total_clicks} • <b>sichtbar:</b> {visibleStep} •{" "}
                <b>best_z:</b> {bestZ ?? "-"} • <b>found_step:</b>{" "}
                {selected.found_step ?? "-"}
              </div>

              <div style={{ marginBottom: 10 }}>
                <label style={{ fontSize: 12 }}>
                  Sichtbarer Schritt: <b>{visibleStep}</b> /{" "}
                  {selected.clicks.length}
                  <input
                    type="range"
                    min={0}
                    max={selected.clicks.length}
                    step={1}
                    value={visibleStep}
                    onChange={(e) => setVisibleStep(Number(e.target.value))}
                    style={{ display: "block", width: "100%", marginTop: 6 }}
                  />
                </label>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: 8,
                  marginBottom: 10,
                  flexWrap: "wrap",
                }}
              >
                <button onClick={() => setVisibleStep(0)}>Reset</button>
                <button
                  onClick={() => setVisibleStep((s) => Math.max(0, s - 1))}
                >
                  -1
                </button>
                <button
                  onClick={() =>
                    setVisibleStep((s) =>
                      Math.min(selected.clicks.length, s + 1),
                    )
                  }
                >
                  +1
                </button>
                <button onClick={() => setVisibleStep(selected.clicks.length)}>
                  Alles
                </button>
              </div>

              {canShowReveal && (
                <label
                  style={{ fontSize: 12, display: "block", marginBottom: 12 }}
                >
                  <input
                    type="checkbox"
                    checked={showRevealPlots}
                    onChange={(e) => setShowRevealPlots(e.target.checked)}
                  />{" "}
                  Reveal-Plots anzeigen
                </label>
              )}
            </>
          )}

          <div
            style={{
              display: "grid",
              gridTemplateColumns: renderRevealPlots ? "1fr 1fr" : "1fr",
              gap: 16,
              alignItems: "start",
            }}
          >
            <div style={{ minWidth: 0 }}>
              <PlotCanvas
                code={sessionCode}
                participantId={selectedPid || "-"}
                sessionStatus={sessionStatus}
                bounds={bounds}
                points={points}
                goal={goal}
                onEvaluate={async () => {}}
                disableClick={true}
                hideDetails={true}
                size={340}
              />
            </div>

            {renderRevealPlots && revealFunctionId && (
              <div
                className="reveal-animate"
                style={{
                  minWidth: 0,
                  display: "grid",
                  gridTemplateRows: "auto auto",
                  gap: 16,
                }}
              >
                <style>
                  {`
                    @keyframes fadeInReveal {
                      from { opacity: 0; transform: translateY(30px) scale(0.95); filter: blur(10px); }
                      to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
                    }
                    .reveal-animate {
                      animation: fadeInReveal 1.0s cubic-bezier(0.22, 1, 0.36, 1) forwards;
                    }
                  `}
                </style>
                <FunctionContourPlot
                  functionId={revealFunctionId}
                  points={points}
                  height={300}
                />

                <FunctionSurfacePlot
                  functionId={revealFunctionId}
                  points={points}
                  height={320}
                />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}