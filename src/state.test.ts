import { describe, expect, it, vi } from "vitest";
const { external } = vi.hoisted(() => ({ external: vi.fn() }));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: external },
}));
import { formatBytes, mergeJob, openNexus, safeError, unwrap } from "./state";
import type { Job } from "./types";
describe("public state boundaries", () => {
  it("hides signed URLs and credentials from errors", () => {
    const error = safeError(
      new Error(
        "下载失败 nxm://game/mods/42/files/1?key=private&expires=1 token=secret api_key=private https://api.nexusmods.com/private",
      ),
    );
    expect(error).not.toContain("private");
    expect(error).not.toContain("secret");
    expect(error).toContain("[已隐藏");
  });
  it("accepts only secure official Nexus browser destinations", () => {
    openNexus(
      "https://www.nexusmods.com/residentevil42023/mods/42?tab=files&file_id=10",
    );
    expect(external).toHaveBeenCalledOnce();
    for (const url of [
      "https://www.nexusmods.com.evil.invalid/",
      "javascript:alert(1)",
      "http://www.nexusmods.com/",
      "https://user:password@www.nexusmods.com/",
    ])
      expect(() => openNexus(url)).toThrow();
    expect(external).toHaveBeenCalledOnce();
  });
  it("unwraps RPC errors without allowing a failed result into UI state", () => {
    expect(unwrap({ ok: true, data: 3 })).toBe(3);
    expect(() => unwrap({ ok: false, error: "失败 token=private" })).toThrow(
      "[已隐藏]",
    );
  });
  it("merges queue updates immutably without duplicating an id", () => {
    const job: Job = {
      id: "one",
      game_id: "game",
      name: "mod",
      phase: "downloading",
      bytes_done: 1,
      bytes_total: 2,
      error: null,
      plan_id: null,
      browser_url: null,
    };
    const current = Object.freeze([Object.freeze(job)]);
    const next = mergeJob(current, { ...job, phase: "complete" });
    expect(next).toHaveLength(1);
    expect(next[0].phase).toBe("complete");
    expect(current[0].phase).toBe("downloading");
  });
  it("formats bounded download progress", () => {
    expect(formatBytes(1024)).toBe("1.0 KiB");
    expect(formatBytes(-1)).toBe("未知");
    expect(formatBytes(Number.NaN)).toBe("未知");
  });
});
