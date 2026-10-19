import type { UpdateArtifact } from "./types";
import { UserFacingError } from "./errors";

type DeckyWindow = { DeckyBackend?: { call?: (route: string, ...args: unknown[]) => Promise<unknown> } };

/** Uses Decky's existing connection and confirmation modal, without opening a second socket. */
export async function requestPluginUpdate(artifact: UpdateArtifact): Promise<void> {
  try {
    const raw = artifact.artifact;
    const uri = new URL(raw);
    const filename = `DeckyMods-v${artifact.version}.zip`;
    if (
      !/^(?:0|[1-9]\d{0,4})\.(?:0|[1-9]\d{0,4})\.(?:0|[1-9]\d{0,4})$/.test(artifact.version) ||
      !/^[0-9a-f]{64}$/.test(artifact.sha256) || uri.protocol !== "file:" || uri.host ||
      uri.search || uri.hash || !raw.startsWith("file:///") || /[\0\r\n\\]/.test(raw) ||
      decodeURIComponent(raw).split("/").some((part) => part === "." || part === "..") ||
      decodeURIComponent(uri.pathname).split("/").pop() !== filename
    ) throw new Error("Invalid handoff");
  } catch {
    throw new UserFacingError("更新安装包信息无效，请重新检查更新。");
  }
  const native = (window as unknown as DeckyWindow).DeckyBackend;
  if (!native || typeof native.call !== "function") {
    throw new UserFacingError("Decky 更新接口暂不可用，请在游戏模式中打开插件后重试。");
  }
  try {
    const result = await native.call("utilities/install_plugin", artifact.artifact, "DeckyMods", artifact.version, artifact.sha256, 2);
    if (result === false) throw new Error("Installation request rejected");
  } catch {
    throw new UserFacingError("无法打开 Decky 更新确认窗口，请重试或在 Decky 设置中从 ZIP 安装。");
  }
}
