import { useQuickAccessVisible } from "@decky/api";
import { useCallback, useEffect, useRef, useState } from "react";
import { AccountPanel } from "./AccountPanel";
import { Action, Note } from "./controls";
import { EditingBoundary } from "./EditingBoundary";
import { GamePanel } from "./GamePanel";
import { JobPanel } from "./JobPanel";
import { LaunchPanel } from "./LaunchPanel";
import { ModPanel } from "./ModPanel";
import { ResidentPanel } from "./ResidentPanel";
import { UpdatePanel } from "./UpdatePanel";
import { backend } from "./rpc";
import { SourcePanel } from "./SourcePanel";
import { mergeJob, safeError } from "./state";
import { styles } from "./styles";
import type { Game, GameView, Job, RunAction, Status } from "./types";
export function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [games, setGames] = useState<readonly Game[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [view, setView] = useState<GameView | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backgroundError, setBackgroundError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const busyRef = useRef(false);
  const mounted = useRef(true);
  const revision = useRef(0);
  const selectedRef = useRef("");
  const visible = useQuickAccessVisible();
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      revision.current += 1;
    };
  }, []);
  const run: RunAction = useCallback(
    async <T,>(
      label: string,
      operation: () => Promise<T>,
      onSuccess?: (result: T) => void,
    ): Promise<T | null> => {
      if (busyRef.current) return null;
      busyRef.current = true;
      revision.current += 1;
      setBusy(true);
      setError(null);
      setNotice(null);
      try {
        const result = await operation();
        if (mounted.current) {
          onSuccess?.(result);
          if (result !== null) setNotice(label);
        }
        return result;
      } catch (caught) {
        if (mounted.current) setError(safeError(caught));
        return null;
      } finally {
        busyRef.current = false;
        revision.current += 1;
        if (mounted.current) setBusy(false);
      }
    },
    [],
  );
  const updateJob = useCallback((job: Job): void => {
    setStatus((current) =>
      current ? { ...current, jobs: mergeJob(current.jobs, job) } : current,
    );
  }, []);
  const updateView = useCallback((next: GameView): void => {
    if (selectedRef.current === next.game.id) {
      setView(next);
      setGames((current) =>
        current.map((game) => (game.id === next.game.id ? next.game : game)),
      );
    }
  }, []);
  useEffect(() => {
    if (!visible) return;
    let active = true;
    let pending = false;
    const poll = async (): Promise<void> => {
      if (pending || busyRef.current) return;
      pending = true;
      const token = revision.current;
      const gameId = selectedRef.current;
      try {
        const [nextStatus, nextGames, nextView] = await Promise.all([
          backend.getStatus(),
          backend.listGames(),
          gameId ? backend.getGame(gameId) : Promise.resolve(null),
        ]);
        if (
          active &&
          mounted.current &&
          revision.current === token &&
          !busyRef.current
        ) {
          setStatus(nextStatus);
          setGames(nextGames);
          if (nextView && selectedRef.current === gameId) updateView(nextView);
          setBackgroundError(null);
        }
      } catch (caught) {
        if (active && mounted.current && revision.current === token)
          setBackgroundError(safeError(caught));
      } finally {
        pending = false;
      }
    };
    void poll();
    const interval = setInterval(() => {
      void poll();
    }, 3000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [visible, games.length, updateView]);
  const select = (id: string): void => {
    void run(
      "游戏已选择",
      () => backend.getGame(id),
      (next) => {
        selectedRef.current = id;
        setSelectedId(id);
        setView(next);
      },
    );
  };
  return (
    <EditingBoundary>
      <div style={styles.status}>
        <div style={styles.statusName}>DeckyMods {status?.version ?? ""}</div>
        <div style={styles.detail}>Nexus MOD · 下载、预览与可撤销部署</div>
      </div>
      {error && (
        <div role="alert" style={styles.error}>
          {error}
        </div>
      )}
      {backgroundError && (
        <div role="alert" style={styles.error}>
          刷新失败：{backgroundError}
        </div>
      )}
      {error && <Action onClick={() => setError(null)}>关闭操作提示</Action>}
      {notice && (
        <div role="status" style={styles.notice}>
          {notice}
        </div>
      )}
      {!status && <Note>正在读取插件状态…</Note>}
      {status && (
        <>
          {!status.platform_supported && (
            <Note>此平台不支持文件部署。请在 SteamOS / Linux 上运行。</Note>
          )}
          {status.error && <Note>{safeError(status.error)}</Note>}
          <UpdatePanel busy={busy || !status.platform_supported} run={run} />
          <AccountPanel
            auth={status.auth}
            handler={status.handler}
            busy={busy}
            run={run}
            onAuth={(auth) =>
              setStatus((current) => (current ? { ...current, auth } : current))
            }
            onHandler={(handler) =>
              setStatus((current) =>
                current ? { ...current, handler } : current,
              )
            }
          />
          <GamePanel
            games={games}
            selected={selectedId}
            busy={busy}
            onSelect={select}
            onRefresh={() => {
              void run("Steam 游戏已重新扫描", backend.listGames, setGames);
            }}
          />
          {view && (
            <>
              <ResidentPanel key={`resident-${selectedId}`} view={view}
                busy={busy || !status.platform_supported} run={run} />
              <SourcePanel
                key={`source-${selectedId}`}
                game={view.game}
                busy={busy || !status.platform_supported}
                run={run}
                onJob={updateJob}
                onView={updateView}
              />
              <ModPanel
                key={`mods-${selectedId}`}
                view={view}
                busy={busy || !status.platform_supported}
                run={run}
                onView={updateView}
              />
              <LaunchPanel
                key={`launch-${selectedId}`}
                view={view}
                jobs={status.jobs}
                busy={busy || !status.platform_supported}
                run={run}
              />
            </>
          )}
          <JobPanel
            jobs={status.jobs}
            games={games}
            busy={busy || !status.platform_supported}
            run={run}
            onJob={updateJob}
          />
          <Note>
            安装完成后，选择对应游戏会自动检查已识别的启动项要求。
          </Note>
          <Note>
            自动适配表示已实现对应文件格式，并通过合成样例验证；各 MOD
            的版本、加载器要求和游戏内效果仍须核对作者说明。备份保存在插件数据目录。
          </Note>
        </>
      )}
    </EditingBoundary>
  );
}
