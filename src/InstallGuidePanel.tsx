import { PanelSection } from "@decky/ui";
import { useEffect, useRef, useState } from "react";
import { Action, Note } from "./controls";
import { openGuideLink, safeGuideLink } from "./guideLinks";
import { backend } from "./rpc";
import { safeError } from "./state";
import { styles } from "./styles";
import type { Game, InstallGuide, InstallMode } from "./types";

interface Props {
  readonly game: Game;
  readonly busy: boolean;
  readonly selectedMode: InstallMode;
  readonly onSelectMode: (mode: InstallMode) => void;
}

export function InstallGuidePanel(props: Props) {
  const identity = JSON.stringify([
    props.game.id, props.game.installed, props.game.path, props.game.app_id,
    props.game.build_id, props.game.adapter,
  ]);
  const previous = useRef(identity);
  useEffect(() => {
    if (previous.current !== identity) {
      previous.current = identity;
      props.onSelectMode("auto");
    }
  }, [identity, props.onSelectMode]);
  return <GuideDetails key={identity} {...props} />;
}

function GuideDetails({ game, busy, selectedMode, onSelectMode }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [guide, setGuide] = useState<InstallGuide | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);
  const pending = useRef(false);
  const revision = useRef(0);
  const blocked = busy || !game.installed || !game.path?.startsWith("/") ||
    game.running || Boolean(game.updating) || Boolean(game.root_error);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; revision.current += 1; };
  }, []);

  const load = async (): Promise<void> => {
    if (pending.current) return;
    pending.current = true;
    const current = ++revision.current;
    setLoading(true);
    setError(null);
    try {
      const next = await backend.getInstallGuide(game.id);
      if (next.game_id !== game.id) throw new Error("游戏信息已变化，请重试。");
      if (mounted.current && current === revision.current) setGuide(next);
    } catch (caught) {
      if (mounted.current && current === revision.current)
        setError(`无法读取安装指南：${safeError(caught)}`);
    } finally {
      if (mounted.current && current === revision.current) {
        pending.current = false;
        setLoading(false);
      }
    }
  };

  const toggle = (): void => {
    if (!expanded && !guide) void load();
    setExpanded((value) => !value);
  };

  return (
    <PanelSection title="MOD 安装指南">
      <Action onClick={toggle}>{expanded ? "收起安装指南" : "展开安装指南"}</Action>
      {expanded && <>
        {loading && <Note>正在读取安装指南…</Note>}
        {error && <>
          <div role="alert" style={styles.error}>{error}</div>
          <Action disabled={loading} onClick={() => { void load(); }}>重试读取安装指南</Action>
        </>}
        {guide && <>
          <Note>资料核查：{guide.checked_at}</Note>
          <Note>按 MOD 作者注明的游戏版本、加载器与依赖选择路线。资料适配不代表已在你的游戏版本验证。</Note>
          {guide.notes.map((note, index) => <Note key={`${index}:${note}`}>{note}</Note>)}
          {guide.methods.length === 0 && <Note>此游戏尚无已核实的专用安装路线，请先查看作者说明。</Note>}
          {guide.methods.map((method, index) => (
            <MethodDetails key={`${index}:${method.id}`} method={method} selectedMode={selectedMode}
              blocked={blocked || loading} onSelectMode={(mode) => {
                if (mounted.current && !blocked && !loading) onSelectMode(mode);
              }} />
          ))}
          <GuideSources urls={guide.sources} />
        </>}
      </>}
    </PanelSection>
  );
}

function MethodDetails({ method, blocked, selectedMode, onSelectMode }: {
  readonly method: InstallGuide["methods"][number];
  readonly blocked: boolean;
  readonly selectedMode: InstallMode;
  readonly onSelectMode: (mode: InstallMode) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const selectable = method.can_install && method.install_mode !== null;
  const choose = (): void => {
    if (!blocked && selectable && method.install_mode !== null) onSelectMode(method.install_mode);
  };
  return <>
    <Action onClick={() => { setExpanded((value) => !value); }}>{expanded ? "收起" : "展开"}：{method.label}</Action>
    {expanded && <>
      <Note>版本：{method.versions.join("；") || "按作者发布说明选择"}</Note>
      <Note>格式：{method.format}</Note>
      <Note>目标：{method.destination}</Note>
      {method.requirements.map((requirement, index) => <Note key={`${index}:${requirement}`}>{requirement}</Note>)}
      {selectable ? <>
        {selectedMode === method.install_mode && <Note>当前安装方式：{method.label}</Note>}
        <Action disabled={blocked} onClick={choose}>选择安装方式：{method.label}</Action>
        <Note>选择后仍需选择压缩包、检查预览并确认安装。不会自动安装加载器或改写启动项。</Note>
      </> : <Note>需按作者说明手动安装或使用外部工具。此路线不会由插件自动执行。</Note>}
      <GuideSources urls={method.source_urls} />
    </>}
  </>;
}

function GuideSources({ urls }: { readonly urls: readonly string[] }) {
  const [error, setError] = useState(false);
  const links = [...new Set(urls)].flatMap((value) => {
    const url = safeGuideLink(value);
    return url ? [url] : [];
  });
  const open = (url: string): void => {
    try {
      setError(!openGuideLink(url));
    } catch {
      setError(true);
    }
  };
  return <>
    {links.map((url) => <Action key={url} onClick={() => { open(url); }}>打开来源：{new URL(url).hostname}</Action>)}
    {links.length < new Set(urls).size && <Note>部分来源链接不符合官方 HTTPS 资料要求，已停止打开。</Note>}
    {error && <div role="alert" style={styles.error}>无法打开资料网页，请稍后重试。</div>}
  </>;
}
