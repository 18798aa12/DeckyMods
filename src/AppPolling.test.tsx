import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { game, gameView, mocks, selectGame, status } from "./test/AppHarness";
import { App } from "./App";

describe("independent polling and selection availability", () => {
  it("blocks existing MOD controls immediately after a rescan loses the game directory", async () => {
    render(<App />); await selectGame();
    fireEvent.click(screen.getByRole("button", { name: "展开已安装 MOD（1）" }));
    fireEvent.click(screen.getByRole("button", { name: "展开“示例服装”" }));
    mocks.listGames.mockResolvedValue([{ ...game, installed: false, path: null, root_error: "目录断开" }]);
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新扫描 Steam 游戏" })); });
    expect((screen.getByRole("button", { name: "禁用 MOD" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "卸载 MOD" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("drops old MOD controls after a manual rescan finds a different installation", async () => {
    render(<App />); await selectGame();
    mocks.listGames.mockResolvedValue([{ ...game, path: "/games/reinstalled-RE4", build_id: "2" }]);
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新扫描 Steam 游戏" })); });
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
    expect(screen.queryByRole("button", { name: "选择本地 MOD 压缩包" })).toBeNull();
  });

  it("does not trust an available scan when the parallel game read reports a disconnected directory", async () => {
    vi.useFakeTimers(); render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" })); });
    mocks.getGame.mockResolvedValue({ ...gameView, game: { ...game, installed: false, path: null } });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.queryByRole("button", { name: "选择本地 MOD 压缩包" })).toBeNull();
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
  });

  it("still refreshes a valid selected game when only the game-list request fails", async () => {
    vi.useFakeTimers(); render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" })); });
    mocks.listGames.mockRejectedValue(new Error("游戏列表读取失败"));
    mocks.getGame.mockResolvedValue({ ...gameView, mods: [] });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.getByRole("button", { name: "展开已安装 MOD（0）" })).toBeTruthy();
    expect(screen.getByText("刷新失败：游戏列表读取失败")).toBeTruthy();
  });

  it.each([
    { installed: false, path: null },
    { path: "/games/another-install" },
    { app_id: "254700" },
    { build_id: "2" },
    { root_error: "目录断开" },
  ])("discards a conflicting polled game view until installation identity agrees: %j", async (change) => {
    vi.useFakeTimers(); render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" })); });
    const scanned = { ...game, ...change };
    mocks.listGames.mockResolvedValue([scanned]);
    mocks.getGame.mockResolvedValue(gameView);
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.queryByRole("button", { name: "选择本地 MOD 压缩包" })).toBeNull();
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
    mocks.getGame.mockResolvedValue({ ...gameView, game: scanned });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.getByRole("button", { name: "展开已安装 MOD（1）" })).toBeTruthy();
  });

  it.each(["running", "updating"] as const)("keeps %s protection if either polling result reports it", async (flag) => {
    vi.useFakeTimers(); render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" })); });
    mocks.listGames.mockResolvedValue([{ ...game, [flag]: true }]);
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect((screen.getByRole("button", { name: "选择本地 MOD 压缩包" }) as HTMLButtonElement).disabled).toBe(true);
    mocks.listGames.mockResolvedValue([game]);
    mocks.getGame.mockResolvedValue({ ...gameView, game: { ...game, [flag]: true } });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect((screen.getByRole("button", { name: "选择本地 MOD 压缩包" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it.each([false, true])("refreshes global state when selected game fails (removed: %s)", async (removed) => {
    vi.useFakeTimers();
    render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" }));
    });
    expect(screen.getByText("当前游戏：Resident Evil 4")).toBeTruthy();
    mocks.getStatus.mockResolvedValue({ ...status, version: "0.2.14" });
    mocks.listGames.mockResolvedValue(removed ? [] : [game]);
    mocks.getGame.mockRejectedValue(new Error("未找到所选游戏，请刷新 Steam 游戏库后重试"));
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(mocks.getGame.mock.calls.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("DeckyMods 0.2.14")).toBeTruthy();
    expect(screen.queryByText("当前游戏：Resident Evil 4")).toBeNull();
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
    mocks.getGame.mockResolvedValue(gameView);
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(Boolean(screen.queryByText("当前游戏：Resident Evil 4"))).toBe(!removed);
  });

  it("clears missing-game controls immediately after a manual rescan", async () => {
    render(<App />);
    await selectGame();
    mocks.listGames.mockResolvedValue([]);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "重新扫描 Steam 游戏" }));
    });
    expect(screen.queryByText("当前游戏：Resident Evil 4")).toBeNull();
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
  });
});
