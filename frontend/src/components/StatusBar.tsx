type StatusBarProps = {
  mode: "teacher" | "participant";
  participantsCount: number;
  functionName?: string;
  goal: string;
  sessionStatus: string;
  stepsUsed?: number;
  maxSteps?: number;
};

export default function StatusBar({
  mode,
  maxSteps,
  participantsCount,
  goal,
  sessionStatus,
  stepsUsed,
}: StatusBarProps) {
  return (
    <div
      style={{
        marginBottom: 12,
        padding: 10,
        border: "1px solid #ddd",
        background: "#f7f7f7",
        color: "#111",
        fontSize: 12,
      }}
    >
      <b>Teilnehmer:</b> {participantsCount} {" | "}
      <b>Ziel:</b> {goal || "-"} {" | "}
      <b>Status:</b> {sessionStatus || "-"}
      {typeof maxSteps === "number" && (
        <>
          {" | "}
          <b>Max Klicks:</b> {maxSteps}
        </>
      )}
      {mode === "participant" &&
        typeof stepsUsed === "number" &&
        typeof maxSteps === "number" && (
          <>
            {" | "}
            <b>Klicks:</b> {stepsUsed}/{maxSteps}
          </>
        )}
    </div>
  );
}
