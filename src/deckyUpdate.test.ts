import { afterEach, describe, expect, it, vi } from "vitest";
import { requestPluginUpdate } from "./deckyUpdate";

const artifact = {
  artifact: "file:///home/deck/homebrew/settings/DeckyMods/updates/DeckyMods-v0.2.0.zip",
  version: "0.2.0", sha256: "a".repeat(64),
};
afterEach(() => { vi.unstubAllGlobals(); });

describe("native Decky update confirmation", () => {
  it("opens the official confirmation using the existing connection and pinned hash", async () => {
    const call = vi.fn().mockResolvedValue(true);
    vi.stubGlobal("window", { DeckyBackend: { call } });
    await requestPluginUpdate(artifact);
    expect(call).toHaveBeenCalledExactlyOnceWith("utilities/install_plugin", artifact.artifact, "DeckyMods", "0.2.0", artifact.sha256, 2);
  });
  it.each([
    { artifact: "https://example.com/DeckyMods-v0.2.0.zip" },
    { artifact: "file://remote/path/DeckyMods-v0.2.0.zip" },
    { artifact: "file:///tmp/Other.zip" },
    { artifact: "file:///tmp/../DeckyMods-v0.2.0.zip" },
    { artifact: "file:///tmp/%2e%2e/DeckyMods-v0.2.0.zip" },
    { artifact: "file:///tmp/DeckyMods-v0.2.0.zip?token=PRIVATE" },
    { version: "not-a-version" }, { sha256: "bad" },
  ])("rejects malformed backend handoff: %j", async (override) => {
    const call = vi.fn();
    vi.stubGlobal("window", { DeckyBackend: { call } });
    await expect(requestPluginUpdate({ ...artifact, ...override })).rejects.toThrow("更新安装包信息无效");
    expect(call).not.toHaveBeenCalled();
  });
  it("explains the missing Decky interface", async () => {
    vi.stubGlobal("window", {});
    await expect(requestPluginUpdate(artifact)).rejects.toThrow("Decky 更新接口暂不可用");
  });
  it("sanitizes native failure without pretending installation succeeded", async () => {
    vi.stubGlobal("window", { DeckyBackend: { call: vi.fn().mockRejectedValue(new Error("PRIVATE token")) } });
    await expect(requestPluginUpdate(artifact)).rejects.toThrow("无法打开 Decky 更新确认窗口");
  });
  it("handles explicit loader rejection", async () => {
    vi.stubGlobal("window", { DeckyBackend: { call: vi.fn().mockResolvedValue(false) } });
    await expect(requestPluginUpdate(artifact)).rejects.toThrow("无法打开 Decky 更新确认窗口");
  });
});
