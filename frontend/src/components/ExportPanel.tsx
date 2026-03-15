import type { ExportData } from "../types";
import FunctionSurfacePlot from "./FunctionSurfacePlot";
type Props = {
  exportData: ExportData | null;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function ExportPanel({ exportData }: Props) {
  if (!exportData) return null;

  const revealImageUrl = exportData.reveal?.image
    ? `${API_URL}${exportData.reveal.image}`
    : null;

  return (
    <div style={{ border: "1px solid #eee", padding: 12, marginTop: 12 }}>
      <h3 style={{ marginTop: 0 }}>Reveal / Export</h3>

      <div style={{ fontSize: 12, marginBottom: 10 }}>
        <div>
          <b>Session:</b> {exportData.session_code}
        </div>
        <div>
          <b>Status:</b> {exportData.status}
        </div>
        <div>
          <b>Ziel:</b> {exportData.goal}
        </div>
      </div>

      {exportData.reveal && (
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>
            {exportData.reveal.title}
          </div>

          {exportData.reveal.description && (
            <div style={{ fontSize: 13, opacity: 0.9, marginBottom: 10 }}>
              {exportData.reveal.description}
            </div>
          )}

          {exportData.function?.id ? (
            <FunctionSurfacePlot
              functionId={exportData.function.id}
              height={420}
            />
          ) : revealImageUrl ? (
            <div style={{ marginBottom: 10 }}>
              <img
                src={revealImageUrl}
                alt={exportData.reveal.title}
                style={{
                  maxWidth: "100%",
                  border: "1px solid #ddd",
                  borderRadius: 8,
                }}
              />
            </div>
          ) : null}
        </div>
      )}

      <div style={{ fontSize: 13 }}>
        <b>Teilnehmer:</b> {exportData.participants.length}
      </div>
    </div>
  );
}
