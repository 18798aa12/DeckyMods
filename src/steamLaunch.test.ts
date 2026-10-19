import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readLaunchOptions, writeLaunchOptions } from "./steamLaunch";

describe("native Steam launch options bridge", () => {
  const getDetails = vi.fn<(appId: number) => unknown>();
  const setOptions = vi.fn<(appId: number, command: string) => unknown>();

  beforeEach(() => {
    vi.useFakeTimers();
    getDetails.mockReset();
    setOptions.mockReset();
    vi.stubGlobal("appDetailsStore", { GetAppDetails: getDetails });
    vi.stubGlobal("SteamClient", {
      Apps: { SetAppLaunchOptions: setOptions },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("reads a real empty value without substituting a default", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "" });
    expect(await readLaunchOptions("418370")).toBe("");
    expect(getDetails).toHaveBeenCalledWith(418370);
  });

  it("preserves the exact native command string", async () => {
    const command = '  WINEDLLOVERRIDES="dxgi=n,b" %command% --option="x y"  ';
    getDetails.mockReturnValue({ strLaunchOptions: command });
    expect(await readLaunchOptions("418370")).toBe(command);
  });

  it("waits briefly for the native details cache to become ready", async () => {
    getDetails
      .mockReturnValueOnce(undefined)
      .mockReturnValueOnce({})
      .mockReturnValue({ strLaunchOptions: "%command%" });
    const result = readLaunchOptions("418370");
    await vi.runAllTimersAsync();
    expect(await result).toBe("%command%");
    expect(getDetails).toHaveBeenCalledTimes(3);
  });

  it.each(["", "0", "-1", "01", "1.1", "1e3", "418370x", "4294967296"])(
    "rejects an invalid Steam app ID %s before reading",
    async (appId) => {
      await expect(readLaunchOptions(appId)).rejects.toThrow("游戏编号");
      expect(getDetails).not.toHaveBeenCalled();
    },
  );

  it("fails explicitly when the native store is unavailable", async () => {
    vi.stubGlobal("appDetailsStore", undefined);
    await expect(readLaunchOptions("418370")).rejects.toThrow("Steam");
  });

  it("does not mistake missing details for empty launch options", async () => {
    getDetails.mockReturnValue({});
    const result = expect(readLaunchOptions("418370")).rejects.toThrow(
      "启动选项",
    );
    await vi.runAllTimersAsync();
    await result;
    expect(getDetails).toHaveBeenCalledTimes(5);
  });

  it("rejects native values with an unexpected type", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: null });
    const result = expect(readLaunchOptions("418370")).rejects.toThrow();
    await vi.runAllTimersAsync();
    await result;
  });

  it.each(["bad\ncommand", "bad\rcommand", "bad\0command", "a".repeat(16385)])(
    "rejects invalid command contents without writing",
    async (command) => {
      await expect(
        writeLaunchOptions("418370", "", command),
      ).rejects.toThrow("启动选项");
      expect(getDetails).not.toHaveBeenCalled();
      expect(setOptions).not.toHaveBeenCalled();
    },
  );

  it("bounds launch options by UTF-8 bytes", async () => {
    await expect(
      writeLaunchOptions("418370", "", "中".repeat(6000)),
    ).rejects.toThrow("启动选项");
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("rejects invalid previous commands and unsafe native contents", async () => {
    await expect(
      writeLaunchOptions("418370", "old\ncommand", ""),
    ).rejects.toThrow("启动选项");
    getDetails.mockReturnValue({ strLaunchOptions: "native\0command" });
    await expect(readLaunchOptions("418370")).rejects.toThrow("启动选项");
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("rejects concurrent user edits without calling the setter", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "user changed this" });
    await expect(
      writeLaunchOptions("418370", "%command%", "new %command%"),
    ).rejects.toThrow("已变化");
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("skips the setter for an exact no-op after checking current options", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "%command%" });
    vi.stubGlobal("SteamClient", undefined);
    expect(
      await writeLaunchOptions("418370", "%command%", "%command%"),
    ).toBe("%command%");
    expect(getDetails).toHaveBeenCalledOnce();
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("does not bypass concurrent edits for a no-op", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "changed" });
    await expect(
      writeLaunchOptions("418370", "%command%", "%command%"),
    ).rejects.toThrow("已变化");
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("writes exact strings and verifies a synchronous native setter", async () => {
    const before = 'WINEDLLOVERRIDES="dxgi=n,b" %command%';
    const after = 'WINEDLLOVERRIDES="dxgi=n,b;dinput8.dll=n,b" %command%';
    getDetails.mockReturnValue({ strLaunchOptions: before });
    setOptions.mockImplementation(() => {
      getDetails.mockReturnValue({ strLaunchOptions: after });
    });
    expect(await writeLaunchOptions("418370", before, after)).toBe(after);
    expect(setOptions).toHaveBeenCalledExactlyOnceWith(418370, after);
  });

  it("waits for a promise setter and delayed cache confirmation", async () => {
    getDetails
      .mockReturnValueOnce({ strLaunchOptions: "before" })
      .mockReturnValueOnce({ strLaunchOptions: "before" })
      .mockReturnValueOnce(undefined)
      .mockReturnValue({ strLaunchOptions: "after" });
    setOptions.mockResolvedValue(undefined);
    const result = writeLaunchOptions("418370", "before", "after");
    await vi.runAllTimersAsync();
    expect(await result).toBe("after");
    expect(setOptions).toHaveBeenCalledExactlyOnceWith(418370, "after");
  });

  it("fails with an actionable error after bounded readback failure", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "before" });
    const result = expect(
      writeLaunchOptions("418370", "before", "after"),
    ).rejects.toThrow("检查");
    await vi.advanceTimersByTimeAsync(2000);
    await result;
    expect(setOptions).toHaveBeenCalledOnce();
    expect(vi.getTimerCount()).toBe(0);
  });

  it("does not retry or overwrite a third-party value observed after writing", async () => {
    getDetails
      .mockReturnValueOnce({ strLaunchOptions: "before" })
      .mockReturnValue({ strLaunchOptions: "user edited after writing" });
    const result = expect(
      writeLaunchOptions("418370", "before", "after"),
    ).rejects.toThrow();
    await vi.runAllTimersAsync();
    await result;
    expect(setOptions).toHaveBeenCalledExactlyOnceWith(418370, "after");
  });

  it("fails before writing when the setter is unavailable", async () => {
    getDetails.mockReturnValue({ strLaunchOptions: "before" });
    vi.stubGlobal("SteamClient", { Apps: {} });
    await expect(
      writeLaunchOptions("418370", "before", "after"),
    ).rejects.toThrow("Steam");
    expect(setOptions).not.toHaveBeenCalled();
  });

  it("sanitizes getter and setter errors without leaking command contents", async () => {
    getDetails.mockImplementation(() => {
      throw new Error("private token=secret getter");
    });
    await expect(readLaunchOptions("418370")).rejects.not.toThrow("secret");
    getDetails.mockReturnValue({ strLaunchOptions: "before" });
    setOptions.mockRejectedValue(new Error("private token=secret setter"));
    await expect(
      writeLaunchOptions("418370", "before", "after"),
    ).rejects.not.toThrow("secret");
  });
});
