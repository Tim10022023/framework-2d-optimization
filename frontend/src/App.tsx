import { useEffect, useMemo, useState } from "react";
import {
  createSession,
  endSession,
  evaluatePoint,
  exportSession,
  getFunctions,
  getLeaderboard,
  joinSession,
  getSessionInfo,
} from "./api";
import TeacherPanel from "./components/TeacherPanel";
import ParticipantPanel from "./components/ParticipantPanel";
import PlotCanvas from "./components/PlotCanvas";
import LeaderboardPanel from "./components/LeaderboardPanel";
import ExportPanel from "./components/ExportPanel";
import type { FunctionSpec, Point } from "./types";
import StatusBar from "./components/StatusBar";
import PointsListPanel from "./components/PointsListPanel";
import StatsPanel from "./components/StatsPanel";

export default function App() {
  const [error, setError] = useState<string | null>(null);

  // Dozent
  const [createdCode, setCreatedCode] = useState<string>("");
  const [adminToken, setAdminToken] = useState<string>("");

  // Teilnehmer
  const [code, setCode] = useState(
    () => localStorage.getItem("opt2d_code") ?? "",
  );
  const [name, setName] = useState(
    () => localStorage.getItem("opt2d_name") ?? "",
  );
  const [participantId, setParticipantId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<string>("running");
  const [joinMessage, setJoinMessage] = useState<string | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [isEndingSession, setIsEndingSession] = useState(false);

  const [functions, setFunctions] = useState<FunctionSpec[]>([]);
  const [selectedFunctionId, setSelectedFunctionId] = useState("sphere");
  const [selectedGoal, setSelectedGoal] = useState<"min" | "max">("min");

  const [points, setPoints] = useState<Point[]>([]);
  const [leaderboard, setLeaderboard] = useState<any>(null);

  const [exportData, setExportData] = useState<any>(null);

  const selectedFunction = useMemo(
    () => functions.find((f) => f.id === selectedFunctionId) ?? null,
    [functions, selectedFunctionId],
  );

  const bounds = useMemo(
    () => selectedFunction?.bounds ?? { xmin: -5, xmax: 5, ymin: -5, ymax: 5 },
    [selectedFunction],
  );

  function resetSessionView() {
    setParticipantId(null);
    setPoints([]);
    setLeaderboard(null);
    setExportData(null);
    setSessionStatus("running");
    setError(null);
  }

  function leaveSession() {
    setParticipantId(null);
    setPoints([]);
    setLeaderboard(null);
    setExportData(null);
    setSessionStatus("running");
    setJoinMessage(null);
    setError(null);
  }
  async function onCreateSession() {
    setError(null);
    setIsCreatingSession(true);

    try {
      const r = await createSession(selectedFunctionId, selectedGoal);
      setCreatedCode(r.session_code);
      setAdminToken(r.admin_token);
      setCode(r.session_code);
      resetSessionView();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsCreatingSession(false);
    }
  }

  async function onEndSession() {
    setError(null);
    setIsEndingSession(true);

    try {
      await endSession(code.trim(), adminToken.trim());
      const data = await exportSession(code.trim(), adminToken.trim());
      setExportData(data);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsEndingSession(false);
    }
  }

  async function handleEvaluate(x: number, y: number) {
    if (!participantId) return;

    setError(null);
    try {
      const r = await evaluatePoint(code.trim(), participantId, x, y);
      setPoints((prev) => [...prev, { x: r.x, y: r.y, z: r.z, step: r.step }]);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onJoin() {
    setError(null);
    setJoinMessage(null);
    setIsJoining(true);

    try {
      const r = await joinSession(code.trim(), name.trim());
      setParticipantId(r.participant_id);
      setPoints([]);
      setLeaderboard(null);
      setExportData(null);
      setSessionStatus("running");
      setJoinMessage(`Beigetreten als ${r.name}`);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsJoining(false);
    }
  }

  useEffect(() => {
    localStorage.setItem("opt2d_code", code);
  }, [code]);

  useEffect(() => {
    localStorage.setItem("opt2d_name", name);
  }, [name]);

  useEffect(() => {
    async function loadFunctions() {
      try {
        const data = await getFunctions();
        setFunctions(data.functions);

        if (data.functions.length > 0) {
          const first = data.functions[0];
          setSelectedFunctionId(first.id);
          setSelectedGoal(first.allowed_goals[0] as "min" | "max");
        }
      } catch (e: any) {
        setError(e?.message ?? String(e));
      }
    }

    loadFunctions();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const codeFromUrl = params.get("code");
    if (codeFromUrl) {
      setCode(codeFromUrl);
    }
  }, []);

  useEffect(() => {
    async function syncSessionInfo() {
      if (!code.trim()) return;

      try {
        const info = await getSessionInfo(code.trim());

        setSessionStatus(info.status);
        setSelectedFunctionId(info.function_id);

        if (info.goal === "min" || info.goal === "max") {
          setSelectedGoal(info.goal);
        }
      } catch {
        // bewusst still: z.B. wenn Code noch unvollständig eingetippt wird
      }
    }

    syncSessionInfo();
  }, [code]);

  useEffect(() => {
    const fn = functions.find((f) => f.id === selectedFunctionId);
    if (!fn) return;

    if (!fn.allowed_goals.includes(selectedGoal)) {
      setSelectedGoal(fn.allowed_goals[0] as "min" | "max");
    }
  }, [functions, selectedFunctionId, selectedGoal]);

  // Polling Leaderboard
  useEffect(() => {
    if (!code.trim()) return;
    const id = setInterval(async () => {
      try {
        const lb = await getLeaderboard(code.trim());
        setLeaderboard(lb);

        const info = await getSessionInfo(code.trim());
        setSessionStatus(info.status);
        setSelectedFunctionId(info.function_id);

        if (info.goal === "min" || info.goal === "max") {
          setSelectedGoal(info.goal);
        }
      } catch {
        // ignore
      }
    }, 1000);
    return () => clearInterval(id);
  }, [code]);

  const publicAppUrl =
    import.meta.env.VITE_PUBLIC_APP_URL ?? window.location.origin;

  const joinLink = createdCode ? `${publicAppUrl}/?code=${createdCode}` : "";

  function getFunctionDescription(functionId: string | null) {
    switch (functionId) {
      case "sphere":
        return "Einfache, glatte Testfunktion mit einem klaren globalen Minimum.";
      case "himmelblau":
        return "Multimodale Funktion mit mehreren gleich guten Minima.";
      case "rastrigin":
        return "Schwierigere Benchmark-Funktion mit vielen lokalen Minima.";
      case "ackley":
        return "Benchmark-Funktion mit vielen lokalen Strukturen und globalem Minimum im Zentrum.";
      case "rosenbrock":
        return "Klassische Tal-Funktion mit globalem Minimum bei (1,1), also nicht im Zentrum.";
      default:
        return "Keine Beschreibung verfügbar.";
    }
  }

  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        padding: 16,
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div style={{ flex: 1 }}>
        <h2>2D Optimization (Frontend MVP)</h2>

        <StatusBar
          code={code}
          name={name}
          functionName={selectedFunction?.name ?? "-"}
          goal={selectedGoal}
          sessionStatus={sessionStatus}
        />
        <TeacherPanel
          functions={functions}
          selectedFunctionId={selectedFunctionId}
          selectedGoal={selectedGoal}
          selectedFunction={selectedFunction}
          bounds={bounds}
          createdCode={createdCode}
          adminToken={adminToken}
          joinLink={joinLink}
          functionDescription={getFunctionDescription(
            selectedFunction?.id ?? null,
          )}
          onChangeFunction={setSelectedFunctionId}
          onChangeGoal={setSelectedGoal}
          onCreateSession={onCreateSession}
          onEndSession={onEndSession}
          isCreatingSession={isCreatingSession}
          isEndingSession={isEndingSession}
        />

        {joinMessage && (
          <div style={{ marginBottom: 8, fontSize: 12, color: "green" }}>
            {joinMessage}
          </div>
        )}

        {/* Teilnehmer */}
        {!participantId ? (
          <ParticipantPanel
            code={code}
            name={name}
            apiUrl={import.meta.env.VITE_API_URL}
            onChangeCode={setCode}
            onChangeName={setName}
            onJoin={onJoin}
            isJoining={isJoining}
          />
        ) : (
          <>
            <div style={{ marginBottom: 8 }}>
              <button onClick={leaveSession}>Session verlassen</button>
            </div>
            <PlotCanvas
              code={code}
              participantId={participantId}
              sessionStatus={sessionStatus}
              bounds={bounds}
              points={points}
              onEvaluate={handleEvaluate}
            />
            <StatsPanel
              points={points}
              targetZ={selectedFunction?.target_z ?? 0}
              tolerance={selectedFunction?.tolerance ?? 0.01}
            />{" "}
            <PointsListPanel points={points} />
          </>
        )}
        <ExportPanel exportData={exportData} />

        {error && (
          <pre
            style={{ marginTop: 12, color: "crimson", whiteSpace: "pre-wrap" }}
          >
            {error}
          </pre>
        )}
      </div>

      <LeaderboardPanel leaderboard={leaderboard} />
    </div>
  );
}
