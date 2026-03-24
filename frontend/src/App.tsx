import { useEffect, useMemo, useState } from "react";
import {
  createSession,
  endSession,
  evaluatePoint,
  exportSession,
  getFunctions,
  getLeaderboard,
  getSessionInfo,
  getSessionSnapshot,
  joinSession,
  startHillClimbBot,
  startRandomBot,
} from "./api";

import TeacherCreatePanel from "./components/TeacherCreatePanel";
import TeacherActiveSessionPanel from "./components/TeacherActiveSessionPanel";
import TeacherInspectPanel from "./components/TeacherInspectPanel";
import ParticipantPanel from "./components/ParticipantPanel";
import PlotCanvas from "./components/PlotCanvas";
import LeaderboardPanel from "./components/LeaderboardPanel";
import ExportPanel from "./components/ExportPanel";
import StatusBar from "./components/StatusBar";
import PointsListPanel from "./components/PointsListPanel";
import StatsPanel from "./components/StatsPanel";

import type { FunctionSpec, Point, SessionSnapshot, ExportData } from "./types";

const LS_VIEW = "opt2d_view";
const LS_CODE = "opt2d_code";
const LS_NAME = "opt2d_name";
const LS_CREATED_CODE = "opt2d_created_code";
const LS_ADMIN_TOKEN = "opt2d_admin_token";
const LS_SESSION_CTX = "opt2d_session_ctx";

type SessionCtx = {
  code: string;
  participantId: string;
};

function loadSessionCtx(): SessionCtx | null {
  try {
    const raw = sessionStorage.getItem(LS_SESSION_CTX);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (
      typeof parsed.code === "string" &&
      typeof parsed.participantId === "string"
    ) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

function saveSessionCtx(ctx: SessionCtx | null) {
  if (!ctx) {
    sessionStorage.removeItem(LS_SESSION_CTX);
    return;
  }
  sessionStorage.setItem(LS_SESSION_CTX, JSON.stringify(ctx));
}

export default function App() {
  const [error, setError] = useState<string | null>(null);

  const [activeView, setActiveView] = useState<"teacher" | "participant">(
    () =>
      (sessionStorage.getItem(LS_VIEW) as "teacher" | "participant" | null) ??
      "participant",
  );

  const [createdCode, setCreatedCode] = useState<string>(
    () => sessionStorage.getItem(LS_CREATED_CODE) ?? "",
  );
  const [adminToken, setAdminToken] = useState<string>(
    () => sessionStorage.getItem(LS_ADMIN_TOKEN) ?? "",
  );

  const [inspectPid, setInspectPid] = useState<string>("");
  const [teacherSnapshot, setTeacherSnapshot] =
    useState<SessionSnapshot | null>(null);

  const [code, setCode] = useState<string>(
    () => sessionStorage.getItem(LS_CODE) ?? "",
  );
  const [name, setName] = useState<string>(
    () => sessionStorage.getItem(LS_NAME) ?? "",
  );
  const [participantId, setParticipantId] = useState<string | null>(null);

  const [sessionStatus, setSessionStatus] = useState<string>("running");
  const [participantsCount, setParticipantsCount] = useState<number>(0);
  const [sessionMaxSteps, setSessionMaxSteps] = useState<number>(30);

  const [functions, setFunctions] = useState<FunctionSpec[]>([]);
  const [selectedFunctionId, setSelectedFunctionId] =
    useState("sphere_shifted");
  const [selectedGoal, setSelectedGoal] = useState<"min" | "max">("min");

  const [draftFunctionId, setDraftFunctionId] = useState("sphere_shifted");

  const [draftGoal, setDraftGoal] = useState<"min" | "max">("min");
  const [draftMaxSteps, setDraftMaxSteps] = useState<number>(30);

  const [points, setPoints] = useState<Point[]>([]);
  const [leaderboard, setLeaderboard] = useState<any>(null);
  const [exportData, setExportData] = useState<ExportData | null>(null);
  const [revealed, setRevealed] = useState(false);

  const [showOnlyBots, setShowOnlyBots] = useState(false);
  const [snapshot, setSnapshot] = useState<SessionSnapshot | null>(null);

  const [activeSessionCode, setActiveSessionCode] = useState<string>("");
  const [collapseSignal, setCollapseSignal] = useState(0);

  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [isEndingSession, setIsEndingSession] = useState(false);
  const [isStartingBot, setIsStartingBot] = useState(false);
  const [isStartingHillClimbBot, setIsStartingHillClimbBot] = useState(false);

  const activeFunction = useMemo(
    () => functions.find((f) => f.id === selectedFunctionId) ?? null,
    [functions, selectedFunctionId],
  );

  const draftFunction = useMemo(
    () => functions.find((f) => f.id === draftFunctionId) ?? null,
    [functions, draftFunctionId],
  );

  const sessionFunction = useMemo(
    () => functions.find((f) => f.id === selectedFunctionId) ?? null,
    [functions, selectedFunctionId],
  );

  const draftBounds = useMemo(
    () => draftFunction?.bounds ?? { xmin: -5, xmax: 5, ymin: -5, ymax: 5 },
    [draftFunction],
  );

  const activeBounds = useMemo(
    () => sessionFunction?.bounds ?? { xmin: -5, xmax: 5, ymin: -5, ymax: 5 },
    [sessionFunction],
  );
  const hasTeacherSession = Boolean(createdCode.trim() && adminToken.trim());

  const publicAppUrl =
    import.meta.env.VITE_PUBLIC_APP_URL ?? window.location.origin;
  const joinLink = createdCode ? `${publicAppUrl}/?code=${createdCode}` : "";

  function getFunctionDescription(functionId: string | null) {
    switch (functionId) {
      case "sphere_shifted":
        return "Einfache glatte Testfunktion mit verschobenem globalem Minimum.";
      case "booth":
        return "Quadratische Benchmark-Funktion mit eindeutigem globalem Minimum.";
      case "himmelblau":
        return "Multimodale Funktion mit mehreren gleich guten globalen Minima.";
      case "rosenbrock":
        return 'Klassische "Bananenfunktion" mit schmalem Tal.';
      case "eggholder":
        return "Sehr unruhige, multimodale Benchmark-Funktion.";
      case "rastrigin_shifted":
        return "Multimodale Benchmark-Funktion mit vielen lokalen Minima.";
      case "schwefel":
        return "Schwierige Benchmark-Funktion mit globalem Minimum fern vom Zentrum.";
      case "levy":
        return "Wellige Benchmark-Funktion mit globalem Minimum bei (1,1).";
      case "griewank_negated_shifted":
        return "Negierte und verschobene Griewank-Funktion als Maximierungsproblem.";
      case "easom":
        return "Funktion mit sehr scharfem globalem Minimum bei (π, π).";
      default:
        return "Keine Beschreibung verfügbar.";
    }
  }

  function resetForNewSession() {
    setParticipantId(null);
    setPoints([]);
    setLeaderboard(null);
    setExportData(null);
    setRevealed(false);
    setSnapshot(null);
    setTeacherSnapshot(null);
    setInspectPid("");
    setShowOnlyBots(false);
    setError(null);
    saveSessionCtx(null);
  }

  function clearTeacherState() {
    setCreatedCode("");
    setAdminToken("");
    setTeacherSnapshot(null);
    setInspectPid("");
    setExportData(null);
    setRevealed(false);

    sessionStorage.removeItem(LS_CREATED_CODE);
    sessionStorage.removeItem(LS_ADMIN_TOKEN);
  }

  function leaveSession() {
    setParticipantId(null);
    setPoints([]);
    setSnapshot(null);
    setShowOnlyBots(false);
    setError(null);
    saveSessionCtx(null);
    setExportData(null);
    setRevealed(false);
  }

  async function onCreateSession() {
    setError(null);
    setIsCreatingSession(true);

    try {
      const r = await createSession(draftFunctionId, draftGoal, draftMaxSteps);
      resetForNewSession();
      setCreatedCode(r.session_code);
      setAdminToken(r.admin_token);
      setCode(r.session_code);
      setActiveSessionCode(r.session_code);
      setCollapseSignal((v) => v + 1);
      setActiveView("teacher");
      setSessionStatus("running");
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsCreatingSession(false);
    }
  }
  async function onToggleReveal() {
    setError(null);

    try {
      if (revealed) {
        setRevealed(false);
        setExportData(null);
        return;
      }

      const data = await exportSession(code.trim(), adminToken.trim());
      setExportData(data);
      setRevealed(true);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onEndSession() {
    setError(null);
    setIsEndingSession(true);

    try {
      await endSession(code.trim(), adminToken.trim());
      setSessionStatus("ended");
      setRevealed(false);
      setExportData(null);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsEndingSession(false);
    }
  }

  async function onJoin() {
    setError(null);
    setIsJoining(true);

    try {
      const r = await joinSession(code.trim(), name.trim());

      clearTeacherState();

      setParticipantId(r.participant_id);
      saveSessionCtx({ code: code.trim(), participantId: r.participant_id });
      setPoints([]);
      setExportData(null);
      setRevealed(false);
      setActiveSessionCode(code.trim());
      setActiveView("participant");
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsJoining(false);
    }
  }

  async function handleEvaluate(x: number, y: number) {
    if (!participantId) return;
    setError(null);

    try {
      const r = await evaluatePoint(code.trim(), participantId, x, y);
      setPoints((prev) => [...prev, { x: r.x, y: r.y, z: r.z, step: r.step }]);
    } catch (e: any) {
      const msg = e?.message ?? String(e);
      if (msg.includes("max steps reached")) {
        setError("Klick-Limit erreicht – keine weiteren Klicks möglich.");
      } else {
        setError(msg);
      }
    }
  }

  async function onStartRandomBot(n: number, seed?: number, delayMs?: number) {
    setError(null);
    setIsStartingBot(true);

    try {
      await startRandomBot(code.trim(), adminToken.trim(), n, seed, delayMs);
      const lb = await getLeaderboard(code.trim());
      setLeaderboard(lb);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsStartingBot(false);
    }
  }

  async function onStartHillClimbBot(
    n: number,
    stepSize: number,
    seed?: number,
    delayMs?: number,
  ) {
    setError(null);
    setIsStartingHillClimbBot(true);

    try {
      await startHillClimbBot(
        code.trim(),
        adminToken.trim(),
        n,
        stepSize,
        seed,
        delayMs,
      );
      const lb = await getLeaderboard(code.trim());
      setLeaderboard(lb);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setIsStartingHillClimbBot(false);
    }
  }

  useEffect(() => {
    async function load() {
      try {
        const data = await getFunctions();
        setFunctions(data.functions);

        if (data.functions.length > 0) {
          const first = data.functions[0];
          setDraftFunctionId(first.id);
          setDraftGoal(first.allowed_goals[0] as "min" | "max");
        }
      } catch (e: any) {
        setError(e?.message ?? String(e));
      }
    }

    load();
  }, []);

  useEffect(() => {
    const fn = functions.find((f) => f.id === draftFunctionId);
    if (!fn) return;
    if (!fn.allowed_goals.includes(draftGoal)) {
      setDraftGoal(fn.allowed_goals[0] as "min" | "max");
    }
  }, [functions, draftFunctionId, draftGoal]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const codeFromUrl = params.get("code");
    if (codeFromUrl) {
      setActiveView("participant");
      setCode(codeFromUrl);
      setActiveSessionCode(codeFromUrl);
    }
  }, []);

  useEffect(() => {
    const ctx = loadSessionCtx();
    if (!ctx) return;

    setCode(ctx.code);
    setParticipantId(ctx.participantId);
    setActiveView("participant");
    setActiveSessionCode(ctx.code);
  }, []);

  useEffect(() => {
    if (activeView !== "teacher") return;
    if (!createdCode) return;

    if (code !== createdCode) setCode(createdCode);
    if (activeSessionCode !== createdCode) setActiveSessionCode(createdCode);
  }, [activeView, createdCode, code, activeSessionCode]);

  useEffect(() => {
    async function sync() {
      if (!code.trim()) return;

      try {
        const info = await getSessionInfo(code.trim());
        setSessionMaxSteps(info.max_steps ?? 30);
        setParticipantsCount(info.participants ?? 0);
        setSessionStatus(info.status);
        setSelectedFunctionId(info.function_id);
        if (info.goal === "min" || info.goal === "max") {
          setSelectedGoal(info.goal);
        }
      } catch {
        // ignore
      }
    }

    sync();
  }, [code]);

  useEffect(() => {
    if (!activeSessionCode.trim()) return;

    const id = setInterval(async () => {
      try {
        const c = activeSessionCode.trim();

        const lb = await getLeaderboard(c);
        setLeaderboard(lb);

        const info = await getSessionInfo(c);
        if (activeView === "teacher" && revealed && adminToken.trim()) {
          try {
            const data = await exportSession(c, adminToken.trim());
            setExportData(data);
          } catch {
            // ignore
          }
        }
        setSessionMaxSteps(info.max_steps ?? 30);
        setParticipantsCount(info.participants ?? 0);
        setSessionStatus(info.status);
        setSelectedFunctionId(info.function_id);
        if (info.goal === "min" || info.goal === "max") {
          setSelectedGoal(info.goal);
        }

        const needSnapshot =
          activeView === "teacher" ||
          (activeView === "participant" && showOnlyBots);

        if (needSnapshot) {
          const snap = await getSessionSnapshot(c);
          if (activeView === "teacher") setTeacherSnapshot(snap);
          if (activeView === "participant") setSnapshot(snap);
        }
      } catch {
        // ignore
      }
    }, 3000); // Increased from 1500 to 3000ms

    return () => clearInterval(id);
  }, [activeSessionCode, activeView, showOnlyBots]);

  useEffect(() => {
    async function restore() {
      if (!code.trim() || !participantId) return;

      try {
        const snap = await getSessionSnapshot(code.trim());
        const me = snap.participants.find(
          (p) => p.participant_id === participantId,
        );

        if (!me) {
          saveSessionCtx(null);
          setParticipantId(null);
          setPoints([]);
          return;
        }

        const restored = me.clicks.map((c, idx) => ({
          x: c.x,
          y: c.y,
          z: c.z,
          step: idx + 1,
        }));
        setPoints(restored);
      } catch {
        // ignore
      }
    }

    restore();
  }, [code, participantId]);

  useEffect(() => {
    sessionStorage.setItem(LS_VIEW, activeView);
  }, [activeView]);

  useEffect(() => {
    sessionStorage.setItem(LS_CODE, code);
  }, [code]);

  useEffect(() => {
    sessionStorage.setItem(LS_NAME, name);
  }, [name]);

  useEffect(() => {
    sessionStorage.setItem(LS_CREATED_CODE, createdCode);
  }, [createdCode]);

  useEffect(() => {
    sessionStorage.setItem(LS_ADMIN_TOKEN, adminToken);
  }, [adminToken]);

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 16,
        padding: 16,
        fontFamily: "system-ui, sans-serif",
        alignItems: "flex-start",
      }}
    >
      <div style={{ flex: "1 1 0", minWidth: 420 }}>
        <h2>2D Optimization (Frontend MVP)</h2>

        <div style={{ marginBottom: 12 }}>
          <button
            onClick={() => setActiveView("teacher")}
            disabled={activeView === "teacher"}
          >
            Dozent
          </button>

          <button
            onClick={() => setActiveView("participant")}
            disabled={activeView === "participant"}
            style={{ marginLeft: 8 }}
          >
            Teilnehmer
          </button>
        </div>

        {activeView === "teacher" && hasTeacherSession && (
          <StatusBar
            mode="teacher"
            participantsCount={participantsCount}
            goal={selectedGoal}
            sessionStatus={sessionStatus}
            maxSteps={sessionMaxSteps}
          />
        )}

        {activeView === "participant" && participantId && (
          <StatusBar
            mode="participant"
            participantsCount={participantsCount}
            goal={selectedGoal}
            sessionStatus={sessionStatus}
            stepsUsed={points.length}
            maxSteps={sessionMaxSteps}
          />
        )}

        {activeView === "teacher" && (
          <>
            <TeacherCreatePanel
              functions={functions}
              selectedFunctionId={draftFunctionId}
              selectedGoal={draftGoal}
              selectedFunction={draftFunction}
              bounds={draftBounds}
              collapseSignal={collapseSignal}
              functionDescription={getFunctionDescription(
                draftFunction?.id ?? null,
              )}
              maxSteps={draftMaxSteps}
              onChangeMaxSteps={setDraftMaxSteps}
              teacherPin={import.meta.env.VITE_TEACHER_PIN}
              onChangeFunction={setDraftFunctionId}
              onChangeGoal={setDraftGoal}
              onCreateSession={onCreateSession}
              isCreatingSession={isCreatingSession}
            />

            {hasTeacherSession && (
              <TeacherActiveSessionPanel
                createdCode={createdCode}
                isAdmin={Boolean(adminToken)}
                joinLink={joinLink}
                revealed={revealed}
                onEndSession={onEndSession}
                onToggleReveal={onToggleReveal}
                isEndingSession={isEndingSession}
                onStartRandomBot={onStartRandomBot}
                isStartingBot={isStartingBot}
                onStartHillClimbBot={onStartHillClimbBot}
                isStartingHillClimbBot={isStartingHillClimbBot}
              />
            )}
          </>
        )}

        {activeView === "participant" && (
          <>
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

                <div style={{ marginBottom: 10, fontSize: 12 }}>
                  <label>
                    <input
                      type="checkbox"
                      checked={showOnlyBots}
                      onChange={(e) => setShowOnlyBots(e.target.checked)}
                    />{" "}
                    Bot-Pfade anzeigen
                  </label>
                </div>

                <div
                  style={{ display: "flex", gap: 16, alignItems: "flex-start" }}
                >
                  <div style={{ flex: "0 0 auto" }}>
                    <PlotCanvas
                      code={code}
                      hideDetails={true}
                      participantId={participantId}
                      sessionStatus={sessionStatus}
                      bounds={activeBounds}
                      points={points}
                      onEvaluate={handleEvaluate}
                      extraParticipants={
                        showOnlyBots && snapshot
                          ? snapshot.participants
                              .filter((p) => p.participant_id !== participantId)
                              .filter((p) => p.is_bot)
                              .map((p) => ({
                                name: p.name,
                                isBot: p.is_bot,
                                color: undefined,
                                clicks: p.clicks.map((c, idx) => ({
                                  x: c.x,
                                  y: c.y,
                                  z: c.z,
                                  step: idx + 1,
                                })),
                              }))
                          : []
                      }
                    />
                  </div>

                  <div style={{ flex: 1, minWidth: 280 }}>
                    <StatsPanel
                      points={points}
                      targetZ={activeFunction?.target_z ?? 0}
                      tolerance={activeFunction?.tolerance ?? 0.01}
                    />

                    <div
                      style={{
                        marginTop: 12,
                        maxHeight: 460,
                        overflow: "auto",
                        border: "1px solid #333",
                        padding: 8,
                      }}
                    >
                      <PointsListPanel points={points} />
                    </div>
                  </div>
                </div>
              </>
            )}
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

      {activeView === "teacher" && hasTeacherSession && (
        <div
          style={{
            width: 780,
            minWidth: 680,
            display: "flex",
            flexDirection: "column",
            gap: 12,
            alignSelf: "flex-start",
          }}
        >
          <div style={{ maxHeight: 260, overflow: "auto" }}>
            <LeaderboardPanel
              leaderboard={leaderboard}
              onSelectParticipant={setInspectPid}
            />
          </div>

          <div>
            <TeacherInspectPanel
              sessionCode={createdCode}
              sessionStatus={sessionStatus}
              bounds={activeBounds}
              snapshot={teacherSnapshot}
              selectedPid={inspectPid}
              onSelectPid={setInspectPid}
              revealFunctionId={exportData?.reveal?.function_id ?? null}
              revealed={revealed}
            />
          </div>
        </div>
      )}
    </div>
  );
}
