import { useQuickAccessVisible } from "@decky/api";
import { Focusable, PanelSection } from "@decky/ui";
import { useEffect, useRef, useState } from "react";
import { backend } from "./rpc";
import { Action, Note } from "./controls";
import { openNexus, safeError } from "./state";
import type { GameView, Mod, ModDetails, RunAction } from "./types";
interface ItemProps {
  readonly view: GameView;
  readonly mod: Mod;
  readonly busy: boolean;
  readonly run: RunAction;
  readonly onView: (view: GameView) => void;
}
function ModItem({ view, mod, busy, run, onView }: ItemProps) {
  const [expanded, setExpanded] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [details, setDetails] = useState<ModDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [readError, setReadError] = useState<string | null>(null);
  const revision = useRef(0);
  const active = useRef(false);
  const boundary = useRef<HTMLDivElement>(null);
  const visible = useQuickAccessVisible();
  const readDetails = (): void => {
    const request = ++revision.current;
    setLoading(true);
    setReadError(null);
    void Promise.resolve()
      .then(() => backend.getModDetails(view.game.id, mod.id))
      .then((next) => {
        if (active.current && revision.current === request) setDetails(next);
      })
      .catch(() => {
        if (active.current && revision.current === request)
          setReadError("暂时无法读取 MOD 说明，请重试。");
      })
      .finally(() => {
        if (active.current && revision.current === request) setLoading(false);
      });
  };
  useEffect(() => {
    active.current = expanded;
    if (!expanded) setLoading(false);
    else if (!details) readDetails();
    return () => {
      active.current = false;
      revision.current += 1;
    };
  }, [expanded, view.game.id, mod.id]);
  useEffect(() => {
    if (!visible || !confirm) return;
    const element = boundary.current;
    const cancel = (event: Event): void => {
      event.preventDefault();
      event.stopPropagation();
      setConfirm(false);
    };
    element?.addEventListener("vgp_oncancel", cancel);
    return () => element?.removeEventListener("vgp_oncancel", cancel);
  }, [confirm, visible]);
  const disabled =
    busy || !view.game.installed || !view.game.path?.startsWith("/") ||
    Boolean(view.game.root_error) || view.game.running || view.game.updating ||
    Boolean(view.recovery_error);
  const sourceUrl = details?.source_url || mod.source_url;
  return (
    <Focusable ref={boundary}>
      <Action
        onClick={() => {
          setExpanded(!expanded);
          setConfirm(false);
        }}
      >
        {expanded ? `收起“${mod.name}”` : `展开“${mod.name}”`}
      </Action>
      {expanded && (
        <>
          <Note>
            {mod.enabled ? "已启用" : "已禁用"} · {mod.files_count} 个文件
          </Note>
          {loading && <Note>正在检索 MOD 说明…</Note>}
          {details?.author && <Note>作者：{details.author}</Note>}
          {details?.version && <Note>版本：{details.version}</Note>}
          {details?.description ? (
            <Note><div style={{ whiteSpace: "pre-wrap" }}>{details.description}</div></Note>
          ) : !loading && !readError && (
            <Note>尚未找到此 MOD 的说明，可查看来源页面或稍后刷新。</Note>
          )}
          {(readError || details?.error) && (
            <Note>{readError || safeError(details?.error)}</Note>
          )}
          <Action disabled={loading} onClick={readDetails}>
            刷新 MOD 说明
          </Action>
          <Action
            disabled={disabled}
            onClick={() => {
              void run(
                mod.enabled ? "MOD 已禁用" : "MOD 已启用",
                () => backend.setModEnabled(view.game.id, mod.id, !mod.enabled),
                onView,
              );
            }}
          >
            {mod.enabled ? "禁用 MOD" : "启用 MOD"}
          </Action>
          {sourceUrl && (
            <Action
              onClick={() => {
                void run("已打开 MOD 原始页面", async () => {
                  openNexus(sourceUrl);
                  return true;
                });
              }}
            >
              查看 MOD 来源
            </Action>
          )}
          <Action disabled={disabled} onClick={() => setConfirm(!confirm)}>
            卸载 MOD
          </Action>
          {confirm && (
            <>
              <Note>卸载将撤销此 MOD 的部署，并恢复由它覆盖的文件备份。</Note>
              <Action
                disabled={disabled}
                onClick={() => {
                  void run(
                    "MOD 已卸载",
                    () => backend.uninstallMod(view.game.id, mod.id),
                    onView,
                  );
                }}
              >
                确认卸载“{mod.name}”
              </Action>
              <Action onClick={() => setConfirm(false)}>取消卸载</Action>
            </>
          )}
        </>
      )}
    </Focusable>
  );
}
export function ModPanel({ view, busy, run, onView }: Omit<ItemProps, "mod">) {
  const [expanded, setExpanded] = useState(false);
  useEffect(() => { setExpanded(false); }, [view.game.id]);
  return (
    <PanelSection title="已安装 MOD">
      {view.recovery_error && <Note>{safeError(view.recovery_error)}</Note>}
      <Action onClick={() => setExpanded(!expanded)}>
        {expanded ? "收起已安装 MOD" : `展开已安装 MOD（${view.mods.length}）`}
      </Action>
      {expanded && (
        <>
          {view.mods.length === 0 && (
            <Note>此游戏还没有由 DeckyMods 管理的 MOD。</Note>
          )}
          {view.mods.map((mod) => (
            <ModItem
              key={`${view.game.id}:${mod.id}`}
              view={view}
              mod={mod}
              busy={busy}
              run={run}
              onView={onView}
            />
          ))}
        </>
      )}
      <Note>
        只管理通过 DeckyMods
        安装的文件。启用、禁用和卸载前请退出游戏；外部修改会触发冲突检查。
      </Note>
    </PanelSection>
  );
}
