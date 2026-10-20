import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { forwardRef, StrictMode, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { GameView, ModDetails, RunAction } from "./types";
const mocks = vi.hoisted(() => ({ getModDetails: vi.fn(), setModEnabled: vi.fn(), uninstallMod: vi.fn(), external: vi.fn() }));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/api", () => ({ useQuickAccessVisible: () => true }));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: mocks.external },
  Focusable: forwardRef<HTMLDivElement, { children: ReactNode }>(function Focus({ children }, ref) { return <div ref={ref}>{children}</div>; }),
  PanelSection: ({ children }: { children: ReactNode }) => <section>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
}));
import { ModPanel } from "./ModPanel";
const view: GameView = { game: { id: "re7", name: "Resident Evil 7", series: "resident_evil", series_name: "生化危机", nexus_domain: "residentevil7", steam_app_ids: ["418370"], adapter: "reframework", support: "needs_setup", requirements: [], sources: [], installed: true, path: "/games/RE7", app_id: "418370", build_id: "1", running: false }, mods: [{ id: "m1", name: "测试 MOD", enabled: true, installed_at: "2026-10-19", files_count: 2, nexus_mod_id: 7, nexus_file_id: 9, source_url: "https://www.nexusmods.com/residentevil7/mods/7" }], recovery_error: null };
const details: ModDetails = { name: "测试 MOD", author: "示例作者", version: "1.2", description: "第一行说明\n第二行说明", source_url: view.mods[0].source_url, error: null, origin: "local" };
const run: RunAction = async (_label, operation, onSuccess) => { const result = await operation(); onSuccess?.(result); return result; };
const renderPanel = () => render(<ModPanel view={view} busy={false} run={run} onView={vi.fn()} />);
const expand = () => { fireEvent.click(screen.getByRole("button", { name: "展开已安装 MOD（1）" })); fireEvent.click(screen.getByRole("button", { name: "展开“测试 MOD”" })); };
beforeEach(() => { mocks.getModDetails.mockResolvedValue(details); mocks.setModEnabled.mockResolvedValue(view); mocks.uninstallMod.mockResolvedValue(view); });
afterEach(() => { cleanup(); vi.resetAllMocks(); });
describe("lazy folded installed MOD descriptions", () => {
  it.each([
    { installed: false },
    { path: null },
    { root_error: "游戏目录已断开" },
  ])("blocks MOD writes when the installation becomes unavailable: %j", async (change) => {
    const rendered = renderPanel(); expand();
    await screen.findByText(/第一行说明/);
    fireEvent.click(screen.getByRole("button", { name: "卸载 MOD" }));
    rendered.rerender(<ModPanel view={{ ...view, game: { ...view.game, ...change } }} busy={false} run={run} onView={vi.fn()} />);
    for (const name of ["禁用 MOD", "卸载 MOD", "确认卸载“测试 MOD”"]) {
      const button = screen.getByRole("button", { name }) as HTMLButtonElement;
      expect(button.disabled).toBe(true);
      fireEvent.click(button);
    }
    expect(mocks.setModEnabled).not.toHaveBeenCalled();
    expect(mocks.uninstallMod).not.toHaveBeenCalled();
    expect((screen.getByRole("button", { name: "刷新 MOD 说明" }) as HTMLButtonElement).disabled).toBe(false);
  });
  it("does not fetch until the individual MOD is expanded", async () => {
    renderPanel();
    expect(mocks.getModDetails).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "展开已安装 MOD（1）" }));
    expect(mocks.getModDetails).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "展开“测试 MOD”" }));
    await screen.findByText(/第一行说明/);
    expect(mocks.getModDetails).toHaveBeenCalledWith("re7", "m1");
    expect(screen.getByText("作者：示例作者")).toBeTruthy();
    expect(screen.getByText("版本：1.2")).toBeTruthy();
  });
  it("keeps fetched details across normal status polls and individual folding", async () => {
    const rendered = renderPanel(); expand(); await screen.findByText(/第一行说明/);
    rendered.rerender(<ModPanel view={{ ...view, mods: view.mods.map((mod) => ({ ...mod })) }} busy={false} run={run} onView={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "收起“测试 MOD”" }));
    fireEvent.click(screen.getByRole("button", { name: "展开“测试 MOD”" }));
    expect(screen.getByText(/第一行说明/)).toBeTruthy();
    expect(mocks.getModDetails).toHaveBeenCalledTimes(1);
  });
  it("refreshes details explicitly and opens only the Nexus source page", async () => {
    renderPanel(); expand(); await screen.findByText(/第一行说明/);
    mocks.getModDetails.mockResolvedValue({ ...details, description: "更新后的说明" });
    fireEvent.click(screen.getByRole("button", { name: "刷新 MOD 说明" }));
    await screen.findByText("更新后的说明");
    expect(mocks.getModDetails).toHaveBeenCalledTimes(2);
    fireEvent.click(screen.getByRole("button", { name: "查看 MOD 来源" }));
    await waitFor(() => expect(mocks.external).toHaveBeenCalledWith(details.source_url));
  });
  it("unlocks a cancelled refresh when cached details are reopened", async () => {
    let finishRefresh: ((value: ModDetails) => void) | undefined;
    renderPanel(); expand(); await screen.findByText(/第一行说明/);
    mocks.getModDetails.mockImplementationOnce(() => new Promise<ModDetails>((resolve) => { finishRefresh = resolve; }));
    fireEvent.click(screen.getByRole("button", { name: "刷新 MOD 说明" }));
    await waitFor(() => expect(mocks.getModDetails).toHaveBeenCalledTimes(2));
    fireEvent.click(screen.getByRole("button", { name: "收起“测试 MOD”" }));
    fireEvent.click(screen.getByRole("button", { name: "展开“测试 MOD”" }));
    expect((screen.getByRole("button", { name: "刷新 MOD 说明" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.queryByText("正在检索 MOD 说明…")).toBeNull();
    await act(async () => { finishRefresh?.({ ...details, description: "过期刷新说明" }); });
    expect(screen.queryByText("过期刷新说明")).toBeNull();
    mocks.getModDetails.mockResolvedValue({ ...details, description: "再次刷新成功" });
    fireEvent.click(screen.getByRole("button", { name: "刷新 MOD 说明" }));
    await screen.findByText("再次刷新成功");
  });
  it("does not use the global mutation guard for description reads", async () => {
    const declined = vi.fn(async () => null) as unknown as RunAction;
    render(<ModPanel view={view} busy={true} run={declined} onView={vi.fn()} />);
    expand(); await screen.findByText(/第一行说明/);
    expect(declined).not.toHaveBeenCalled();
  });
  it("keeps management available after a description read fails", async () => {
    mocks.getModDetails.mockRejectedValue(new Error("private token"));
    renderPanel(); expand();
    await screen.findByText("暂时无法读取 MOD 说明，请重试。");
    expect(document.body.textContent).not.toContain("private token");
    fireEvent.click(screen.getByRole("button", { name: "禁用 MOD" }));
    await waitFor(() => expect(mocks.setModEnabled).toHaveBeenCalledWith("re7", "m1", false));
  });
  it("shows local metadata and an honest missing-description message without requiring an account", async () => {
    mocks.getModDetails.mockResolvedValue({ ...details, description: "", source_url: null, author: null, version: null, origin: "none", error: "没有可检索的 Nexus 来源信息。" });
    renderPanel(); expand();
    await screen.findByText("尚未找到此 MOD 的说明，可查看来源页面或稍后刷新。");
    expect(screen.getByText("没有可检索的 Nexus 来源信息。")).toBeTruthy();
  });
  it("ignores a response from an earlier expansion after folding and reopening", async () => {
    let finishOld: ((value: ModDetails) => void) | undefined;
    mocks.getModDetails.mockImplementationOnce(() => new Promise<ModDetails>((resolve) => { finishOld = resolve; })).mockResolvedValue({ ...details, description: "新说明" });
    renderPanel(); expand();
    expect(screen.getByText("正在检索 MOD 说明…")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "收起“测试 MOD”" }));
    fireEvent.click(screen.getByRole("button", { name: "展开“测试 MOD”" }));
    await screen.findByText("新说明");
    await act(async () => { finishOld?.({ ...details, description: "过期说明" }); });
    expect(screen.queryByText("过期说明")).toBeNull();
  });
  it("discards pending descriptions when the selected game changes", async () => {
    let finishOld: ((value: ModDetails) => void) | undefined;
    mocks.getModDetails.mockImplementationOnce(() => new Promise<ModDetails>((resolve) => { finishOld = resolve; })).mockResolvedValue({ ...details, description: "另一游戏说明" });
    const rendered = renderPanel(); expand();
    rendered.rerender(<ModPanel view={{ ...view, game: { ...view.game, id: "re8" } }} busy={false} run={run} onView={vi.fn()} />);
    expect(screen.getByRole("button", { name: "展开已安装 MOD（1）" })).toBeTruthy();
    expand(); await screen.findByText("另一游戏说明");
    await act(async () => { finishOld?.({ ...details, description: "过期说明" }); });
    expect(screen.queryByText("过期说明")).toBeNull();
  });
  it("discards responses after the installed list unmounts its items", async () => {
    let finishOld: ((value: ModDetails) => void) | undefined;
    mocks.getModDetails.mockImplementationOnce(() => new Promise<ModDetails>((resolve) => { finishOld = resolve; })).mockResolvedValue({ ...details, description: "重新展开的说明" });
    renderPanel(); expand();
    await waitFor(() => expect(mocks.getModDetails).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole("button", { name: "收起已安装 MOD" }));
    await act(async () => { finishOld?.({ ...details, description: "已卸载组件的说明" }); });
    expect(screen.queryByText("已卸载组件的说明")).toBeNull();
    expand(); await screen.findByText("重新展开的说明");
    expect(mocks.getModDetails).toHaveBeenCalledTimes(2);
  });
  it("renders description content as text and never injects HTML", async () => {
    mocks.getModDetails.mockResolvedValue({ ...details, description: '<img src=x onerror="alert(1)">' });
    render(<StrictMode><ModPanel view={view} busy={false} run={run} onView={vi.fn()} /></StrictMode>); expand();
    await screen.findByText('<img src=x onerror="alert(1)">');
    expect(document.querySelector("img")).toBeNull();
  });
});
