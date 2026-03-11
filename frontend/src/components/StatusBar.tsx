type StatusBarProps = {
  code: string;
  name: string;
  functionName: string;
  goal: string;
  sessionStatus: string;
};

export default function StatusBar({
  code,
  name,
  functionName,
  goal,
  sessionStatus,
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
      <b>Session:</b> {code || "-"} | <b>Name:</b> {name || "-"} |{" "}
      <b>Funktion:</b> {functionName || "-"} | <b>Ziel:</b> {goal || "-"} |{" "}
      <b>Status:</b> {sessionStatus || "-"}
    </div>
  );
}
