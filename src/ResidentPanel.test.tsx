import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { GameView, ResidentStatus, RunAction } from "./types";

const mocks = vi.hoisted(() => ({
  getResidentStatus: vi.fn(),
  prepareResidentSettings: vi.fn(),
  restoreResidentSettings: vi.fn(),
}));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/ui", () => ({
  PanelSection: ({ title, children }: { title: string; children: ReactNode }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
}));
import { ResidentPanel } from "./ResidentPanel";

const status: ResidentStatus = {
  supported: true, family: "re_engine", build_id: "22773795", runtime_tdb: 70,
  renderer: "D3D12", runtime_evidence: true, script_count: 1,
  last_run_at: "2026-10-19T09:00:00Z", loader_present: true,
  config_exists: true, config_valid: true, loose_enabled: false,
  pak_directory_enabled: false, config_backup_available: false,
  warnings: ["游戏更新后需要重新核对 MOD 版本"],
};
const view: GameView = {
  game: {
    id: "residentevil7", name: "Resident Evil 7", series: "resident-evil", series_name: "生化危机",
    nexus_domain: "residentevil7", steam_app_ids: ["418370"], adapter: "reframework",
    support: "needs_setup", requirements: [], sources: [], installed: true,
    path: "/games/re7", app_id: "418370", build_id: "22773795", running: false,
  }, mods: [], recovery_error: null,
};
const run: RunAction = async (_label, operation, onSuccess) => {
  const result = await operation();
  onSuccess?.(result);
  return result;
};
function panel(next = view, busy = false) {
  return <ResidentPanel view={next} busy={busy} run={run} />;
}
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}
beforeEach(() => {
  mocks.getResidentStatus.mockResolvedValue(status);
  mocks.prepareResidentSettings.mockResolvedValue({ ...status, loose_enabled: true, config_backup_available: true });
  mocks.restoreResidentSettings.mockResolvedValue({ ...status, config_backup_available: false });
});
afterEach(() => { cleanup(); vi.resetAllMocks(); });

describe("Resident Evil runtime and resource setup", () => {
  it("labels runtime observations as last-run evidence without promising compatibility", async () => {
    render(panel());
    expect(await screen.findByText(/上次运行日志：TDB 70 · D3D12 · 1 个脚本/)).toBeTruthy();
    expect(screen.getByText(/Build ID：22773795/)).toBeTruthy();
    expect(screen.getByText(/日志仅说明上次加载情况/)).toBeTruthy();
    expect(screen.getByText("游戏更新后需要重新核对 MOD 版本")).toBeTruthy();
    expect(mocks.prepareResidentSettings).not.toHaveBeenCalled();
  });
  it("can refresh observations without a polling loop or writing settings", async () => {
    const rendered = render(panel());
    await screen.findByText(/上次运行日志/);
    rendered.rerender(panel({ ...view, game: { ...view.game }, mods: [] }));
    await act(async () => {});
    expect(mocks.getResidentStatus).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", { name: "刷新生化危机状态" }));
    await waitFor(() => expect(mocks.getResidentStatus).toHaveBeenCalledTimes(2));
    expect(mocks.prepareResidentSettings).not.toHaveBeenCalled();
  });
  it("refreshes after a build or managed-mod change", async () => {
    const rendered = render(panel());
    await screen.findByText(/上次运行日志/);
    rendered.rerender(panel({ ...view, game: { ...view.game, build_id: "2" } }));
    await waitFor(() => expect(mocks.getResidentStatus).toHaveBeenCalledTimes(2));
    rendered.rerender(panel({ ...view, mods: [{ id: "m1", name: "New", enabled: true, installed_at: "now", files_count: 1, nexus_mod_id: null, nexus_file_id: null, source_url: null }] }));
    await waitFor(() => expect(mocks.getResidentStatus).toHaveBeenCalledTimes(3));
  });
  it("prepares only loose files on existing modern titles and exposes backup recovery", async () => {
    render(panel());
    await screen.findByText(/上次运行日志/);
    fireEvent.click(screen.getByRole("button", { name: "配置资源 MOD 加载" }));
    await waitFor(() => expect(mocks.prepareResidentSettings).toHaveBeenCalledWith("residentevil7", false));
    await screen.findByText("资源 MOD 设置已检查并配置");
    expect(screen.getByRole("button", { name: "恢复资源 MOD 配置备份" })).toBeTruthy();
  });
  it("enables PAK-directory settings only for canonical Requiem", async () => {
    render(panel({ ...view, game: { ...view.game, id: "residentevilrequiem" } }));
    await screen.findByText(/上次运行日志/);
    fireEvent.click(screen.getByRole("button", { name: "配置资源 MOD 加载" }));
    await waitFor(() => expect(mocks.prepareResidentSettings).toHaveBeenCalledWith("residentevilrequiem", true));
  });
  it("restores the matching configuration backup through the guarded action", async () => {
    mocks.getResidentStatus.mockResolvedValue({ ...status, config_backup_available: true });
    render(panel());
    fireEvent.click(await screen.findByRole("button", { name: "恢复资源 MOD 配置备份" }));
    await screen.findByText("资源 MOD 配置已恢复");
    expect(mocks.restoreResidentSettings).toHaveBeenCalledWith("residentevil7");
    expect(screen.queryByRole("button", { name: "恢复资源 MOD 配置备份" })).toBeNull();
  });
  it.each(["running", "updating", "recovery", "busy"])("blocks configuration changes while %s", async (block) => {
    const blocked = { ...view, game: { ...view.game, running: block === "running", updating: block === "updating" }, recovery_error: block === "recovery" ? "recovery" : null };
    render(panel(blocked, block === "busy"));
    await screen.findByText(/上次运行日志/);
    expect((screen.getByRole("button", { name: "配置资源 MOD 加载" }) as HTMLButtonElement).disabled).toBe(true);
    expect(mocks.prepareResidentSettings).not.toHaveBeenCalled();
  });
  it("keeps legacy resource replacements separate from REFramework configuration", async () => {
    mocks.getResidentStatus.mockResolvedValue({ ...status, family: "mt_framework", runtime_evidence: false, loader_present: false });
    render(panel({ ...view, game: { ...view.game, id: "residentevil5", adapter: "re_legacy" } }));
    await screen.findByText(/旧引擎资源替换/);
    expect(screen.queryByRole("button", { name: "配置资源 MOD 加载" })).toBeNull();
    expect(screen.getByText(/资源替换无需额外启动项/)).toBeTruthy();
  });
  it("makes absent logs explicit and does not infer compatibility from a DLL", async () => {
    mocks.getResidentStatus.mockResolvedValue({ ...status, runtime_evidence: false, runtime_tdb: null, renderer: null, script_count: 0 });
    render(panel());
    await screen.findByText(/尚无可核对的上次运行日志/);
    expect(screen.getByText(/发现加载器文件不代表加载成功/)).toBeTruthy();
    expect(screen.queryByText(/TDB 70/)).toBeNull();
  });
  it("hides this panel entirely for other series", async () => {
    render(panel({ ...view, game: { ...view.game, series: "other-series" } }));
    await act(async () => {});
    expect(mocks.getResidentStatus).not.toHaveBeenCalled();
    expect(screen.queryByRole("region", { name: "生化危机 MOD 状态" })).toBeNull();
  });
  it("sanitizes backend error details and permits an explicit retry", async () => {
    mocks.getResidentStatus.mockRejectedValueOnce(new Error("网络失败 https://private.example/sub?token=secret"));
    render(panel());
    const alert = await screen.findByRole("alert");
    expect(alert.textContent).not.toContain("private.example");
    expect(alert.textContent).not.toContain("secret");
    fireEvent.click(screen.getByRole("button", { name: "刷新生化危机状态" }));
    await screen.findByText(/上次运行日志：TDB 70/);
  });
  it("does not report configuration success after a rejected update", async () => {
    mocks.prepareResidentSettings.mockRejectedValueOnce(new Error("配置文件已被修改 key=private"));
    render(panel());
    await screen.findByText(/上次运行日志/);
    fireEvent.click(screen.getByRole("button", { name: "配置资源 MOD 加载" }));
    expect((await screen.findByRole("alert")).textContent).not.toContain("private");
    expect(screen.queryByText("资源 MOD 设置已检查并配置")).toBeNull();
  });
  it("discards a late old-game status response after changing games", async () => {
    const first = deferred<ResidentStatus>();
    mocks.getResidentStatus.mockReturnValueOnce(first.promise).mockResolvedValueOnce({ ...status, runtime_tdb: 71 });
    const rendered = render(panel());
    rendered.rerender(panel({ ...view, game: { ...view.game, id: "residentevil22019" } }));
    await screen.findByText(/TDB 71/);
    await act(async () => { first.resolve(status); });
    expect(screen.queryByText(/TDB 70/)).toBeNull();
    expect(screen.getByText(/TDB 71/)).toBeTruthy();
  });
  it("discards old-game mutation completion after switching selection", async () => {
    const pending = deferred<ResidentStatus>();
    mocks.prepareResidentSettings.mockReturnValueOnce(pending.promise);
    const rendered = render(panel());
    await screen.findByText(/上次运行日志/);
    fireEvent.click(screen.getByRole("button", { name: "配置资源 MOD 加载" }));
    await waitFor(() => expect(mocks.prepareResidentSettings).toHaveBeenCalledOnce());
    rendered.rerender(panel({ ...view, game: { ...view.game, id: "residentevil22019" } }));
    await screen.findByText(/上次运行日志/);
    await act(async () => { pending.resolve({ ...status, config_backup_available: true }); });
    expect(screen.queryByText("资源 MOD 设置已检查并配置")).toBeNull();
    expect(screen.queryByRole("button", { name: "恢复资源 MOD 配置备份" })).toBeNull();
  });
});
