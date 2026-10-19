import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { game, gameView, mocks, selectGame, status } from "./test/AppHarness";
import { App } from "./App";

describe("independent polling and selection availability", () => {
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
