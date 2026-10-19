import {
  PanelSection,
  PanelSectionRow,
  TextField,
  ToggleField,
} from "@decky/ui";
import { useState } from "react";
import { backend } from "./rpc";
import { Action, Note } from "./controls";
import { openNexus, safeError } from "./state";
import type { Auth, Handler, RunAction } from "./types";
interface Props {
  readonly auth: Auth;
  readonly handler: Handler;
  readonly busy: boolean;
  readonly run: RunAction;
  readonly onAuth: (auth: Auth) => void;
  readonly onHandler: (handler: Handler) => void;
}
export function AccountPanel({
  auth,
  handler,
  busy,
  run,
  onAuth,
  onHandler,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [key, setKey] = useState("");
  return (
    <PanelSection title="Nexus 账号">
      <Note>
        {auth.connected
          ? `${auth.name ?? "账号已验证"} · ${auth.premium ? "Premium" : "普通会员"}`
          : "未绑定 Nexus 账号 · 本地压缩包无需登录"}
      </Note>
      {auth.connected && <Note>API 已绑定 · 网页登录由浏览器管理</Note>}
      <Action
        onClick={() => {
          setExpanded(!expanded);
          if (expanded) setKey("");
        }}
      >
        {expanded ? "收起 Nexus 账号" : "展开 Nexus 账号"}
      </Action>
      {expanded && (
        <>
          <Note>
            普通会员也可使用个人 API Key。在 Nexus 官方网页登录后，
            打开 API Access 页面，找到 Personal API Key，生成或显示个人密钥。
            如果顶部只有已授权应用，请继续往下找个人密钥区域。
          </Note>
          <Note>
            不绑定也可在网页下载后导入本地压缩包。插件不收集账号密码或浏览器 Cookie。
          </Note>
          <Note>
            API Key 用于验证账号和查询 MOD 信息，不会替浏览器登录 Nexus。
            普通会员还需在网页授权所选文件；Premium 可通过 API 获取下载链接。
            网页请登录与 API 绑定相同的 Nexus 账号。
          </Note>
          <Action
            onClick={() => {
              void run("已打开 Nexus 登录页", async () => {
                openNexus("https://users.nexusmods.com/auth/sign_in");
                return true;
              });
            }}
          >
            打开 Nexus 登录页
          </Action>
          <Action
            onClick={() => {
              void run("已打开 API Key 设置", async () => {
                openNexus("https://www.nexusmods.com/users/myaccount?tab=api%20access");
                return true;
              });
            }}
          >
            打开 Nexus API Key 设置
          </Action>
          <PanelSectionRow>
            <TextField
              label="Nexus API Key"
              value={key}
              bIsPassword
              bShowCopyAction={false}
              disabled={busy}
              onChange={(event) => setKey(event.target.value)}
            />
          </PanelSectionRow>
          <Action
            disabled={busy || !key.trim()}
            onClick={() => {
              void run(
                "API 已绑定",
                () => backend.bindAccount(key.trim()),
                (next) => {
                  setKey("");
                  onAuth(next);
                },
              );
            }}
          >
            绑定账号
          </Action>
          {auth.connected && (
            <Action
              disabled={busy}
              onClick={() => {
                void run("账号已断开", backend.disconnectAccount, (next) => {
                  setKey("");
                  onAuth(next);
                });
              }}
            >
              断开账号
            </Action>
          )}
          {auth.error && <Note>{safeError(auth.error)}</Note>}
          <PanelSectionRow>
            <ToggleField
              label="接收 Nexus 的 NXM 下载链接"
              checked={handler.enabled}
              disabled={busy || !handler.supported}
              onChange={(enabled) => {
                void run(
                  enabled ? "NXM 接收已启用" : "NXM 接收已关闭",
                  () => backend.setNxmHandler(enabled),
                  onHandler,
                );
              }}
            />
          </PanelSectionRow>
          <Note>
            首次请在桌面模式打开 Firefox，登录并点击 MOD Manager
            Download；浏览器提示时允许用 DeckyMods 打开
            nxm。关闭接收会恢复原关联。
          </Note>
          {handler.message && <Note>{handler.message}</Note>}
          {handler.previous && <Note>原 NXM 处理程序：{handler.previous}</Note>}
        </>
      )}
    </PanelSection>
  );
}
