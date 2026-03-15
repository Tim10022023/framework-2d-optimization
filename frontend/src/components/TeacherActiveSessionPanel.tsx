import React from "react";
import { QRCodeSVG } from "qrcode.react";

type Props = {
  createdCode: string;
  adminToken: string;
  joinLink: string;
  isAdmin: boolean;

  onEndSession: () => void;
  isEndingSession: boolean;

  onStartRandomBot: (n: number, seed?: number, delayMs?: number) => void;
  isStartingBot: boolean;

  onStartHillClimbBot: (
    n: number,
    stepSize: number,
    seed?: number,
    delayMs?: number,
  ) => void;
  isStartingHillClimbBot: boolean;
};

export default function TeacherActiveSessionPanel({
  createdCode,
  adminToken,
  joinLink,
  onEndSession,
  isAdmin,
  isEndingSession,
  onStartRandomBot,
  isStartingBot,
  onStartHillClimbBot,
  isStartingHillClimbBot,
}: Props) {
  const [botN, setBotN] = React.useState(30);
  const [botSeed, setBotSeed] = React.useState<number | "">("");
  const [botStepSize, setBotStepSize] = React.useState(0.5);
  const [beamerMode, setBeamerMode] = React.useState(false);
  const [showAdvanced, setShowAdvanced] = React.useState(false);
  const [botDelayMs, setBotDelayMs] = React.useState(500);
  const hasSession = Boolean(createdCode);
  const maskedAdmin = adminToken ? adminToken.slice(0, 6) + "…" : "-";

  return (
    <>
      <div style={{ border: "1px solid #eee", padding: 12 }}>
        <h3 style={{ marginTop: 0 }}>Aktive Session</h3>
        <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
          Code/QR teilen, Bots starten, Session beenden und Export laden.
        </div>

        <div style={{ fontSize: 12, marginBottom: 10 }}>
          <div>
            <b>session_code:</b> <code>{createdCode || "-"}</code>
          </div>

          {isAdmin && (
            <label
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                marginTop: 8,
              }}
            >
              <input
                type="checkbox"
                checked={showAdvanced}
                onChange={(e) => setShowAdvanced(e.target.checked)}
              />
              Advanced (Admin-Details anzeigen)
            </label>
          )}
          {isAdmin && showAdvanced && (
            <div style={{ marginTop: 6 }}>
              <div>
                <b>admin_token:</b>{" "}
                <code title="Token wird nicht voll angezeigt">
                  {maskedAdmin}
                </code>
              </div>
              <button
                style={{ marginTop: 6 }}
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(adminToken);
                    alert("Admin-Token kopiert.");
                  } catch {
                    alert("Kopieren nicht möglich (Browser/Permissions).");
                  }
                }}
              >
                Admin-Token kopieren
              </button>
            </div>
          )}
        </div>

        {joinLink && (
          <div style={{ fontSize: 12, marginBottom: 10 }}>
            <div>
              <b>Join-Link:</b>
            </div>
            <code>{joinLink}</code>
            <div style={{ marginTop: 8 }}>
              <QRCodeSVG value={joinLink} size={160} />
            </div>

            <button
              onClick={() => setBeamerMode(true)}
              disabled={!hasSession}
              style={{ marginTop: 8 }}
            >
              Beamer Mode (QR groß)
            </button>
          </div>
        )}

        {isAdmin && (
          <div style={{ marginTop: 8 }}>
            <button
              onClick={onEndSession}
              disabled={!hasSession || isEndingSession}
            >
              {isEndingSession
                ? "Beende Session..."
                : "Session beenden + Export laden"}
            </button>
          </div>
        )}
        {isAdmin && (
          <div
            style={{
              marginTop: 16,
              borderTop: "1px solid #eee",
              paddingTop: 12,
            }}
          >
            <h4 style={{ margin: "0 0 8px" }}>Bots</h4>

            <div style={{ display: "grid", gap: 8, maxWidth: 260 }}>
              <label style={{ fontSize: 12 }}>
                n (Klicks)
                <input
                  type="number"
                  value={botN}
                  min={1}
                  max={1000}
                  onChange={(e) => setBotN(Number(e.target.value))}
                  style={{ width: "100%" }}
                />
              </label>

              <label style={{ fontSize: 12 }}>
                seed (optional)
                <input
                  type="number"
                  value={botSeed}
                  onChange={(e) => {
                    const v = e.target.value;
                    setBotSeed(v === "" ? "" : Number(v));
                  }}
                  style={{ width: "100%" }}
                />
              </label>
              <label style={{ fontSize: 12 }}>
                delay_ms
                <input
                  type="number"
                  value={botDelayMs}
                  min={0}
                  max={5000}
                  step={100}
                  onChange={(e) => setBotDelayMs(Number(e.target.value))}
                  style={{ width: "100%" }}
                />
              </label>

              <button
                onClick={() =>
                  onStartRandomBot(
                    botN,
                    botSeed === "" ? undefined : botSeed,
                    botDelayMs,
                  )
                }
                disabled={!hasSession || isStartingBot}
              >
                {isStartingBot ? "Bot läuft..." : "Random Search Bot starten"}
              </button>

              <label style={{ fontSize: 12 }}>
                step_size (Hill Climb)
                <input
                  type="number"
                  value={botStepSize}
                  step={0.1}
                  min={0.0001}
                  onChange={(e) => setBotStepSize(Number(e.target.value))}
                  style={{ width: "100%" }}
                />
              </label>

              <button
                onClick={() =>
                  onStartHillClimbBot(
                    botN,
                    botStepSize,
                    botSeed === "" ? undefined : botSeed,
                    botDelayMs,
                  )
                }
                disabled={!hasSession || isStartingHillClimbBot}
              >
                {isStartingHillClimbBot
                  ? "Bot läuft..."
                  : "Hill Climb Bot starten"}
              </button>
            </div>
          </div>
        )}
      </div>

      {beamerMode && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.85)",
            zIndex: 9999,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: 24,
          }}
          onClick={() => setBeamerMode(false)}
        >
          <div
            style={{
              background: "#111",
              color: "white",
              padding: 24,
              borderRadius: 12,
              width: "min(900px, 95vw)",
              textAlign: "center",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ fontSize: 18, fontWeight: 700 }}>
                Session beitreten
              </div>
              <button onClick={() => setBeamerMode(false)}>Schließen</button>
            </div>

            <div style={{ marginTop: 16, fontSize: 14, opacity: 0.9 }}>
              Scan den QR-Code oder gib den Code ein:
            </div>

            <div
              style={{
                marginTop: 12,
                fontSize: 42,
                fontWeight: 800,
                letterSpacing: 2,
              }}
            >
              {createdCode}
            </div>

            <div
              style={{
                marginTop: 18,
                display: "flex",
                justifyContent: "center",
              }}
            >
              <div
                style={{ background: "white", padding: 12, borderRadius: 8 }}
              >
                <QRCodeSVG value={joinLink} size={360} />
              </div>
            </div>

            <div style={{ marginTop: 14, fontSize: 12, opacity: 0.8 }}>
              {joinLink}
            </div>

            <div style={{ marginTop: 10, fontSize: 12, opacity: 0.7 }}>
              (Klick außerhalb schließt)
            </div>
          </div>
        </div>
      )}
    </>
  );
}
