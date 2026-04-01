type Props = {
  mode: "teacher" | "participant";
  participantsCount: number;
  goal: "min" | "max";
  sessionStatus: string;
  stepsUsed?: number;
  maxSteps?: number;
};

function pill(label: string, value: string | number, isLive?: boolean) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 2,
        padding: "8px 10px",
        border: "1px solid #333",
        borderRadius: 8,
        minWidth: 90,
        position: "relative",
        background: isLive ? "rgba(43, 138, 62, 0.05)" : "transparent",
      }}
    >
      <span
        style={{
          fontSize: 11,
          opacity: 0.75,
          textTransform: "uppercase",
          letterSpacing: 0.4,
          display: "flex",
          alignItems: "center",
          gap: 4
        }}
      >
        {label}
        {isLive && (
          <span className="pulse-dot" style={{
            width: 6,
            height: 6,
            backgroundColor: "#2b8a3e",
            borderRadius: "50%",
            display: "inline-block"
          }} />
        )}
      </span>
      <span style={{ fontSize: 15, fontWeight: 700, color: isLive ? "#2b8a3e" : "inherit" }}>
        {value}
      </span>
    </div>
  );
}

export default function StatusBar({
  mode,
  participantsCount,
  goal,
  sessionStatus,
  stepsUsed,
  maxSteps,
}: Props) {
  const isRunning = sessionStatus === "running";

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        marginBottom: 12,
      }}
    >
      <style>
        {`
          @keyframes pulseLive {
            0% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(43, 138, 62, 0.7); }
            70% { transform: scale(1.4); opacity: 0.8; box-shadow: 0 0 0 6px rgba(43, 138, 62, 0); }
            100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(43, 138, 62, 0); }
          }
          .pulse-dot {
            animation: pulseLive 2s infinite;
          }
        `}
      </style>
      {pill("Teilnehmer", participantsCount)}
      {pill("Ziel", goal)}
      {pill("Status", sessionStatus, isRunning)}
      {maxSteps !== undefined ? pill("Max Klicks", maxSteps) : null}
      {mode === "participant" && stepsUsed !== undefined
        ? pill("Meine Klicks", stepsUsed)
        : null}
    </div>
  );
}
