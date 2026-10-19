import { PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { useCallback, useEffect, useRef, useState } from "react";
import { Action, Note } from "./controls";
import { synchronizeLaunchOptions } from "./launchFlow";
import { backend } from "./rpc";
import { styles } from "./styles";
import type { GameView, Job, LaunchSetup, RunAction } from "./types";

interface Props {
  readonly view: GameView;
  readonly jobs: readonly Job[];
  readonly busy: boolean;
  readonly run: RunAction;
}

export function LaunchPanel({ view, jobs, busy, run }: Props) {
  const gameId = view.game.id;
  const installation = JSON.stringify([
    gameId, view.game.installed, view.game.path, view.game.app_id, view.game.build_id,
  ]);
  const [setup, setSetup] = useState<LaunchSetup | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const currentGame = useRef({ id: gameId, installation, generation: 0 });
  const alive = useRef(true);
  const attempted = useRef("");
  const setupRevision = useRef(0);
  const unavailable = !view.game.installed || !view.game.path;
  const blocked = Boolean(unavailable || view.game.running || view.game.updating || view.recovery_error);
  const signature = JSON.stringify([
    installation,
    view.mods.filter((mod) => mod.enabled).map((mod) => mod.id).sort(),
    jobs.filter((job) => job.game_id === gameId && job.phase === "complete").map((job) => job.id).sort(),
    blocked,
  ]);
  if (currentGame.current.installation !== installation) {
    currentGame.current = { id: gameId, installation, generation: currentGame.current.generation + 1 };
  }
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);
  const isCurrent = useCallback((id: string, generation: number): boolean =>
    alive.current && currentGame.current.id === id && currentGame.current.generation === generation, []);

  useEffect(() => {
    let active = true;
    const generation = currentGame.current.generation;
    const revision = ++setupRevision.current;
    setSetup(null);
    setMessage(null);
    setError(null);
    setPending(false);
    void backend.getLaunchSetup(gameId).then((next) => {
      if (active && isCurrent(gameId, generation) && setupRevision.current === revision) setSetup(next);
    }).catch(() => {
      if (active && isCurrent(gameId, generation) && setupRevision.current === revision) setError("无法读取启动项要求，请重新检查。");
    });
    return () => { active = false; };
  }, [gameId, isCurrent, signature]);

  const synchronize = useCallback((restore = false, automatic = false): void => {
    if (busy || blocked || pending) return;
    const id = gameId;
    const generation = currentGame.current.generation;
    void run("启动项检查已完成", async () => {
      if (automatic) attempted.current = signature;
      setupRevision.current += 1;
      if (isCurrent(id, generation)) {
        setPending(true);
        setError(null);
        setMessage(null);
      }
      try {
        const result = await synchronizeLaunchOptions(id, restore);
        if (isCurrent(id, generation)) {
          setupRevision.current += 1;
          setSetup(result.setup);
          setMessage(result.restored ? "启动项已恢复，自动配置已关闭" : result.configured ? "启动项已检查并配置" : null);
        }
        return result.configured || result.restored ? true : null;
      } catch (caught) {
        if (isCurrent(id, generation)) setError(caught instanceof Error ? caught.message : "启动项检查失败，请重试。");
        return null;
      } finally {
        if (isCurrent(id, generation)) setPending(false);
      }
    });
  }, [busy, blocked, pending, gameId, isCurrent, run, signature]);

  useEffect(() => {
    if (busy || blocked || pending || attempted.current === signature) return;
    if (!setup?.supported || !setup.required || !setup.auto_enabled) return;
    synchronize(false, true);
  }, [busy, blocked, pending, signature, synchronize, setup]);

  const toggle = (enabled: boolean): void => {
    if (busy || blocked || pending) return;
    const id = gameId;
    const generation = currentGame.current.generation;
    void run(enabled ? "已开启自动启动项配置" : "已关闭自动启动项配置", async () => {
      setupRevision.current += 1;
      setPending(true);
      setError(null);
      try {
        const next = await backend.setLaunchAuto(id, enabled);
        if (isCurrent(id, generation)) {
          setSetup(next);
          setMessage(null);
        }
        if (enabled && isCurrent(id, generation)) {
          attempted.current = signature;
          const result = await synchronizeLaunchOptions(id);
          if (isCurrent(id, generation)) {
            setSetup(result.setup);
            setMessage(result.configured ? "启动项已检查并配置" : null);
          }
        }
        return true;
      } catch {
        if (isCurrent(id, generation)) setError("自动配置设置未完成，请重新检查；若仍失败，请核对 Steam 启动项。");
        return null;
      } finally {
        if (isCurrent(id, generation)) setPending(false);
      }
    });
  };

  return (
    <PanelSection title="MOD 启动项">
      <Note>{setup?.reason ?? "正在识别启动项要求…"}</Note>
      {unavailable && <Note>游戏未安装或目录暂不可用，请连接存储设备后重新扫描。</Note>}
      {view.game.running && <Note>请先退出游戏，退出后会自动检查启动项。</Note>}
      {view.game.updating && <Note>Steam 更新中，完成后会自动检查启动项。</Note>}
      {view.recovery_error && <Note>先处理文件恢复问题，再配置启动项。</Note>}
      {setup?.supported && (
        <>
          <PanelSectionRow>
            <ToggleField label="自动配置已识别的启动项" checked={setup.auto_enabled} disabled={busy || blocked || pending} onChange={toggle} />
          </PanelSectionRow>
          {!setup.auto_enabled && <Note>自动配置已关闭；现有启动项会保留。</Note>}
          <Note>识别到加载器后合并必要参数，并保留插帧等原有设置。未知要求请核对 MOD 作者说明。</Note>
        </>
      )}
      {message && <Note>{message}</Note>}
      {error && <div role="alert" style={styles.error}>{error}</div>}
      {pending && <Note>正在检查启动项…</Note>}
      <Action disabled={busy || blocked || pending} onClick={() => synchronize()}>重新检查启动项</Action>
      {setup?.backup_available && <Action disabled={busy || blocked || pending} onClick={() => synchronize(true)}>恢复首次自动配置前的启动项</Action>}
    </PanelSection>
  );
}
