import { PanelSection, PanelSectionRow, TextField, ToggleField } from "@decky/ui";
import { useEffect, useRef, useState } from "react";
import { Action, Note } from "./controls";
import { requestPluginUpdate } from "./deckyUpdate";
import { backend } from "./rpc";
import { styles } from "./styles";
import type { RunAction, UpdateStatus } from "./types";

interface Props {
  readonly busy: boolean;
  readonly run: RunAction;
}

export function UpdatePanel({ busy, run }: Props) {
  const [status, setStatus] = useState<UpdateStatus | null>(null);
  const [source, setSource] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const alive = useRef(true);
  const edited = useRef(false);
  const revision = useRef(0);
  const locked = useRef(false);

  useEffect(() => {
    alive.current = true;
    const refresh = async (): Promise<void> => {
      if (locked.current) return;
      const generation = ++revision.current;
      try {
        const next = await backend.getUpdateStatus();
        if (!alive.current || generation !== revision.current) return;
        setStatus(next);
        if (!edited.current) setSource(next.source ?? "");
      } catch {
        if (alive.current && generation === revision.current) setError("无法读取更新状态，请重新打开插件后重试。");
      }
    };
    void refresh();
    const timer = setInterval(() => { void refresh(); }, 30000);
    return () => { alive.current = false; revision.current += 1; clearInterval(timer); };
  }, []);

  const perform = (label: string, failure: string, operation: () => Promise<void>): void => {
    if (busy || locked.current) return;
    locked.current = true;
    revision.current += 1;
    setPending(true);
    setError(null);
    setMessage(null);
    void run(label, async () => {
      try {
        await operation();
        return null;
      } catch {
        if (alive.current) setError(failure);
        return null;
      }
    }).catch(() => {
      if (alive.current) setError(failure);
    }).finally(() => {
      revision.current += 1;
      locked.current = false;
      if (alive.current) setPending(false);
    });
  };

  const save = (automatic: boolean, saveEditedSource: boolean): void => {
    const nextSource = saveEditedSource ? source.trim() : status?.source ?? "";
    perform("更新设置已保存", "无法保存更新设置，请核对来源地址和网络后重试。", async () => {
      const next = await backend.setUpdateOptions(nextSource, automatic);
      if (!alive.current) return;
      setStatus(next);
      if (saveEditedSource) { edited.current = false; setSource(next.source ?? ""); }
      setMessage("更新设置已保存。");
    });
  };

  const check = (): void => {
    perform("更新检查已完成", "检查更新失败，请检查网络后重试。", async () => {
      const next = await backend.checkUpdate();
      if (!alive.current) return;
      setStatus(next);
      if (!next.error) setMessage(next.available ? "签名已验证，可以安装更新。" : "当前已是更新来源中的最新版本。");
    });
  };

  const install = (): void => {
    perform("已请求 Decky 更新确认", "无法准备已验证的更新。请先退出游戏、等待 MOD 任务结束，再重新检查更新；也可从 ZIP 安装。", async () => {
      const artifact = await backend.prepareUpdate();
      if (!alive.current) return;
      await requestPluginUpdate(artifact);
      if (alive.current) setMessage("已打开 Decky 更新确认窗口，请确认安装；完成后重新打开插件核对版本。");
    });
  };

  const disabled = busy || pending || !status;
  const visibleError = error ?? status?.error;
  return (
    <PanelSection title="插件更新">
      <Note>当前版本：{status?.current_version ?? "正在读取…"}</Note>
      <Note>{status?.source_label ?? "正在读取更新来源…"}</Note>
      {status?.available && <Note>可更新至 {status.latest_version}</Note>}
      {status?.checked_at && <Note>上次检查：{new Date(status.checked_at).toLocaleString()}</Note>}
      <PanelSectionRow>
        <ToggleField label="自动检查更新（每 6 小时）" checked={status?.auto_check ?? true} disabled={disabled} onChange={(enabled) => save(enabled, false)} />
      </PanelSectionRow>
      <Note>自动检查新版并提示。安装时由 Decky 弹窗确认；请先退出游戏并等待 MOD 任务结束。更新保留个人设置和 MOD 数据。</Note>
      <PanelSectionRow>
        <TextField label="更新来源" value={source} disabled={disabled} description="填写发布来源或局域网服务器地址；来源未配置时不会自动联网。" onChange={(event) => { edited.current = true; setSource(event.target.value); }} />
      </PanelSectionRow>
      <Note>局域网下载需要 Mac 上的更新服务保持运行，且两台设备连接同一 Wi-Fi。</Note>
      <Action disabled={disabled} onClick={() => save(status?.auto_check ?? true, true)}>保存更新设置</Action>
      <Action disabled={disabled || !status?.source} onClick={check}>检查插件更新</Action>
      {status?.available && <Action disabled={disabled} onClick={install}>安装已验证更新</Action>}
      {pending && <Note>正在处理更新请求…</Note>}
      {message && <Note>{message}</Note>}
      {visibleError && <div role="alert" style={styles.error}>{visibleError}</div>}
    </PanelSection>
  );
}
