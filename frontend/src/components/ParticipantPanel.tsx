type ParticipantPanelProps = {
  code: string;
  name: string;
  apiUrl: string;
  isJoining: boolean;
  onChangeCode: (value: string) => void;
  onChangeName: (value: string) => void;
  onJoin: () => void;
};

export default function ParticipantPanel({
  code,
  name,
  apiUrl,
  isJoining,
  onChangeCode,
  onChangeName,
  onJoin,
}: ParticipantPanelProps) {
  return (
    <div style={{ display: "grid", gap: 8, maxWidth: 360 }}>
      <h3 style={{ margin: 0 }}>Teilnehmerbereich</h3>
      <div style={{ fontSize: 12, opacity: 0.8 }}>
        Mit Session-Code beitreten und dann im Koordinatensystem klicken.
      </div>
      <label>
        Session-Code
        <input
          value={code}
          onChange={(e) => onChangeCode(e.target.value)}
          style={{ width: "100%" }}
        />
      </label>

      <label>
        Name
        <input
          value={name}
          onChange={(e) => onChangeName(e.target.value)}
          style={{ width: "100%" }}
        />
      </label>

      <button
        onClick={onJoin}
        disabled={!code.trim() || !name.trim() || isJoining}
      >
        {isJoining ? "Trete bei..." : "Join"}
      </button>

      <div style={{ fontSize: 12, opacity: 0.7 }}>
        API: <code>{apiUrl}</code>
      </div>
    </div>
  );
}
