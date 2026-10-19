import { PanelSection } from "@decky/ui";
import { useCallback, useEffect, useRef, useState } from "react";
import { Action, Note } from "./controls";
import { backend } from "./rpc";
import { safeError } from "./state";
import { styles } from "./styles";
import type { GameView, ResidentStatus, RunAction } from "./types";

interface Props {
  readonly view: GameView;
  readonly busy: boolean;
  readonly run: RunAction;
}

export function ResidentPanel(props: Props) {
  return props.view.game.series === "resident-evil"
    ? <ResidentDetails key={props.view.game.id} {...props} />
    : null;
}

function ResidentDetails({ view, busy, run }: Props) {
  const gameId = view.game.id;
  const [status, setStatus] = useState<ResidentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const alive = useRef(true);
  const request = useRef(0);
  const operation = useRef(false);
  const blocked = Boolean(view.game.running || view.game.updating || view.recovery_error);
  const signature = JSON.stringify([
    view.game.build_id,
    view.mods.map((mod) => [mod.id, mod.enabled]).sort(),
    view.game.running,
    view.game.updating,
  ]);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; request.current += 1; };
  }, []);

  const refresh = useCallback(async (): Promise<void> => {
    if (operation.current) return;
    const revision = ++request.current;
    setLoading(true);
    setError(null);
    try {
      const next = await backend.getResidentStatus(gameId);
      if (alive.current && revision === request.current) setStatus(next);
    } catch (caught) {
      if (alive.current && revision === request.current) {
        setError(`无法读取生化危机状态：${safeError(caught)}`);
      }
    } finally {
      if (alive.current && revision === request.current) setLoading(false);
    }
  }, [gameId]);

  useEffect(() => {
    void refresh();
  }, [refresh, signature]);

  const configure = (restore = false): void => {
    if (busy || blocked || loading || operation.current || !status?.supported) return;
    operation.current = true;
    request.current += 1;
    setPending(true);
    setMessage(null);
    setError(null);
    const label = restore ? "资源 MOD 配置已恢复" : "资源 MOD 设置已检查并配置";
    void run(label, async () => {
      try {
        const next = restore
          ? await backend.restoreResidentSettings(gameId)
          : await backend.prepareResidentSettings(gameId, gameId === "residentevilrequiem");
        if (alive.current) {
          setStatus(next);
          setMessage(label);
        }
        return next;
      } catch (caught) {
        if (alive.current) setError(`资源 MOD 配置未完成：${safeError(caught)}`);
        return null;
      }
    }).finally(() => {
        operation.current = false;
        if (alive.current) setPending(false);
    });
  };

  const modern = view.game.adapter === "reframework" || status?.family === "re_engine";
  const disabled = busy || blocked || loading || pending;
  return (
    <PanelSection title="生化危机 MOD 状态">
      <Note>{modern ? "RE Engine · REFramework" : "旧引擎资源替换"} · Build ID：{status?.build_id ?? view.game.build_id ?? "未知"}</Note>
      {loading && <Note>正在读取生化危机状态…</Note>}
      {status && modern && (
        <>
          <Note>REFramework 加载器：{status.loader_present ? "已发现文件" : "未发现文件"}。发现加载器文件不代表加载成功。</Note>
          {status.runtime_evidence ? (
            <Note>上次运行日志：TDB {status.runtime_tdb ?? "未知"} · {status.renderer ?? "渲染器未知"} · {status.script_count} 个脚本{status.last_run_at ? ` · ${status.last_run_at}` : ""}</Note>
          ) : <Note>尚无可核对的上次运行日志；请使用匹配版本的 REFramework 启动游戏一次。</Note>}
          <Note>日志仅说明上次加载情况，不保证所有 MOD 与当前游戏版本兼容。</Note>
          <Note>资源配置：{!status.config_exists ? "尚未生成" : status.config_valid ? "可读取" : "需人工检查"} · 松散资源：{status.loose_enabled ? "已开启" : "未开启"}{gameId === "residentevilrequiem" ? ` · PAK 目录：${status.pak_directory_enabled ? "已开启" : "未开启"}` : ""}</Note>
        </>
      )}
      {status && !modern && <Note>资源替换无需额外启动项；DLL、脚本、归档解包和其他前置仍按作者说明检查。</Note>}
      {status?.warnings.map((warning, index) => <Note key={`${index}:${warning}`}>{safeError(warning)}</Note>)}
      {view.game.running && <Note>请完全退出游戏后再修改资源加载配置。</Note>}
      {view.game.updating && <Note>Steam 更新或验证完成后才能修改配置。</Note>}
      {view.recovery_error && <Note>请先处理 MOD 文件恢复问题。</Note>}
      {message && <Note>{message}</Note>}
      {error && <div role="alert" style={styles.error}>{error}</div>}
      {pending && <Note>正在更新资源加载配置…</Note>}
      <Action disabled={busy || loading || pending} onClick={() => { void refresh(); }}>刷新生化危机状态</Action>
      {status?.supported && modern && (
        <>
          <Action disabled={disabled || !status.loader_present} onClick={() => configure()}>配置资源 MOD 加载</Action>
          {status.config_backup_available && <Action disabled={disabled} onClick={() => configure(true)}>恢复资源 MOD 配置备份</Action>}
        </>
      )}
    </PanelSection>
  );
}
