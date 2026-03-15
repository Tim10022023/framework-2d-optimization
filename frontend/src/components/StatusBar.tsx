type Props = {
  mode: "teacher" | "participant";
  participantsCount: number;
  goal: "min" | "max";
  sessionStatus: string;
  stepsUsed?: number;
  maxSteps?: number;
};

function pill(label: string, value: string | number) {
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
      }}
    >
      <span
        style={{
          fontSize: 11,
          opacity: 0.75,
          textTransform: "uppercase",
          letterSpacing: 0.4,
        }}
      >
        {label}
      </span>
      <span style={{ fontSize: 15, fontWeight: 700 }}>{value}</span>
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
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        marginBottom: 12,
      }}
    >
      {pill("Teilnehmer", participantsCount)}
      {pill("Ziel", goal)}
      {pill("Status", sessionStatus)}
      {maxSteps !== undefined ? pill("Max Klicks", maxSteps) : null}
      {mode === "participant" && stepsUsed !== undefined
        ? pill("Meine Klicks", stepsUsed)
        : null}
    </div>
  );
}
