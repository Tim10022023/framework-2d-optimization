import { useEffect, useState } from "react";
import type { Bounds, FunctionSpec } from "../types";

type Props = {
  functions: FunctionSpec[];
  selectedFunctionId: string;
  selectedGoal: "min" | "max";
  selectedFunction: FunctionSpec | null;
  bounds: Bounds;
  functionDescription: string;
  collapseSignal?: number;

  maxSteps: number;
  onChangeMaxSteps: (v: number) => void;

  teacherPin?: string;

  onChangeFunction: (v: string) => void;
  onChangeGoal: (v: "min" | "max") => void;
  onCreateSession: () => void;

  isCreatingSession: boolean;
};

export default function TeacherCreatePanel({
  functions,
  selectedFunctionId,
  selectedGoal,
  selectedFunction,
  bounds,
  functionDescription,
  maxSteps,
  onChangeMaxSteps,
  teacherPin,
  onChangeFunction,
  onChangeGoal,
  onCreateSession,
  isCreatingSession,
  collapseSignal,
}: Props) {
  const [pinInput, setPinInput] = useState("");
  const pinOk = !teacherPin || pinInput === teacherPin;
  const [isOpen, setIsOpen] = useState(false); // default zu

  useEffect(() => {
    if (collapseSignal !== undefined) setIsOpen(false);
  }, [collapseSignal]);

  return (
    <div style={{ border: "1px solid #eee", padding: 12, marginBottom: 12 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>
              Session konfigurieren
            </div>
            {!isOpen && (
              <div style={{ fontSize: 12, opacity: 0.8, marginTop: 2 }}>
                Draft: <b>{selectedFunction?.name ?? selectedFunctionId}</b> •
                Ziel: <b>{selectedGoal}</b> • Max: <b>{maxSteps}</b>
              </div>
            )}
          </div>

          <button onClick={() => setIsOpen((v) => !v)}>
            {isOpen ? "Einklappen" : "Ausklappen"}
          </button>
        </div>
      </div>
      {isOpen && (
        <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
          Funktion und Ziel festlegen und eine neue Session starten.
        </div>
      )}

      {isOpen && (
        <>
          <div style={{ marginBottom: 10 }}>
            <label style={{ fontSize: 12 }}>
              Dozenten-PIN
              <input
                type="password"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value)}
                placeholder="PIN eingeben"
                style={{
                  display: "block",
                  width: "100%",
                  marginTop: 4,
                  maxWidth: 240,
                }}
              />
            </label>
            {!pinOk && (
              <div style={{ fontSize: 12, color: "crimson", marginTop: 4 }}>
                PIN falsch – Session erstellen ist gesperrt.
              </div>
            )}
          </div>

          <div style={{ marginBottom: 8 }}>
            <label>
              Funktion
              <select
                value={selectedFunctionId}
                onChange={(e) => onChangeFunction(e.target.value)}
                style={{ display: "block", width: "100%", marginTop: 4 }}
              >
                {functions.map((fn) => (
                  <option key={fn.id} value={fn.id}>
                    {fn.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ marginBottom: 8 }}>
            <label>
              Ziel
              <select
                value={selectedGoal}
                onChange={(e) => onChangeGoal(e.target.value as "min" | "max")}
                style={{ display: "block", width: "100%", marginTop: 4 }}
              >
                {(selectedFunction?.allowed_goals ?? []).map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ marginBottom: 8 }}>
            <label>
              Max. Klicks pro Teilnehmer
              <input
                type="number"
                value={maxSteps}
                min={1}
                max={1000}
                onChange={(e) => onChangeMaxSteps(Number(e.target.value))}
                style={{ display: "block", width: "100%", marginTop: 4 }}
              />
            </label>
          </div>

          {selectedFunction && (
            <div style={{ marginTop: 8, fontSize: 12, opacity: 0.85 }}>
              <div>
                <b>Auswahl:</b> {selectedFunction.name}
              </div>
              <div>
                <b>Ziel:</b> {selectedGoal}
              </div>
              <div>
                <b>Bounds:</b> x ∈ [{bounds.xmin}, {bounds.xmax}], y ∈ [
                {bounds.ymin}, {bounds.ymax}]
              </div>
              <div style={{ marginTop: 6 }}>
                <b>Beschreibung:</b> {functionDescription}
              </div>
            </div>
          )}

          <div style={{ marginTop: 12 }}>
            <button
              onClick={onCreateSession}
              disabled={isCreatingSession || !pinOk}
            >
              {isCreatingSession
                ? "Erstelle Session..."
                : "Neue Session erstellen"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
