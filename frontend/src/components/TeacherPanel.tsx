import { QRCodeSVG } from "qrcode.react";
import type { Bounds, FunctionSpec } from "../types";

type TeacherPanelProps = {
  functions: FunctionSpec[];
  selectedFunctionId: string;
  selectedGoal: "min" | "max";
  selectedFunction: FunctionSpec | null;
  bounds: Bounds;
  createdCode: string;
  adminToken: string;
  joinLink: string;
  functionDescription: string;
  onChangeFunction: (value: string) => void;
  onChangeGoal: (value: "min" | "max") => void;
  onCreateSession: () => void;
  onEndSession: () => void;
  isCreatingSession: boolean;
  isEndingSession: boolean;
};

export default function TeacherPanel({
  functions,
  selectedFunctionId,
  selectedGoal,
  selectedFunction,
  bounds,
  createdCode,
  adminToken,
  joinLink,
  isCreatingSession,
  isEndingSession,
  functionDescription,
  onChangeFunction,
  onChangeGoal,
  onCreateSession,
  onEndSession,
}: TeacherPanelProps) {
  return (
    <div style={{ border: "1px solid #eee", padding: 12, marginBottom: 12 }}>
      <h3 style={{ marginTop: 0 }}>Dozentenbereich</h3>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
        Session konfigurieren, starten, QR-Link teilen und nach Ende Export
        laden.
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

      {selectedFunction && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          <div>
            <b>Aktive Funktion:</b> {selectedFunction.name}
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
        <button onClick={onCreateSession} disabled={isCreatingSession}>
          {isCreatingSession ? "Erstelle Session..." : "Neue Session erstellen"}
        </button>{" "}
      </div>

      <div style={{ marginTop: 8, fontSize: 12 }}>
        <div>
          <b>session_code:</b> {createdCode || "-"}
        </div>
        <div>
          <b>admin_token:</b> <code>{adminToken || "-"}</code>
        </div>
      </div>

      {joinLink && (
        <div style={{ marginTop: 8, fontSize: 12 }}>
          <div>
            <b>Join-Link:</b>
          </div>
          <code>{joinLink}</code>
        </div>
      )}
      {joinLink && (
        <div style={{ marginTop: 12 }}>
          <div style={{ fontSize: 12, marginBottom: 6 }}>
            <b>QR-Code für den Join-Link:</b>
          </div>
          <QRCodeSVG value={joinLink} size={160} />
        </div>
      )}

      <div style={{ marginTop: 8 }}>
        <button
          onClick={onEndSession}
          disabled={!createdCode || !adminToken || isEndingSession}
        >
          {isEndingSession
            ? "Beende Session..."
            : "Session beenden + Export laden"}
        </button>
      </div>
    </div>
  );
}
