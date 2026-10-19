import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StrictMode, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { GameView, Job, LaunchChange, LaunchSetup, RunAction } from "./types";

const mocks = vi.hoisted(() => ({
  getLaunchSetup: vi.fn(), setLaunchAuto: vi.fn(), prepareLaunchOptions: vi.fn(),
  finishLaunchOptions: vi.fn(), read: vi.fn(), write: vi.fn(),
}));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("./steamLaunch", () => ({ readLaunchOptions: mocks.read, writeLaunchOptions: mocks.write }));
vi.mock("@decky/ui", () => ({
  PanelSection: ({ title, children }: { title: string; children: ReactNode }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
  ToggleField: ({ label, checked, disabled, onChange }: { label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) => <label>{label}<input aria-label={label} type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} /></label>,
}));
import { LaunchPanel } from "./LaunchPanel";
import { synchronizeLaunchOptions } from "./launchFlow";

const setup: LaunchSetup = {
  supported: true, required: true, reason: "已识别 REFramework 加载器",
  app_id: "418370", auto_enabled: true, backup_available: false,
};
const view: GameView = {
  game: {
    id: "re7", name: "Resident Evil 7", series: "resident-evil", series_name: "生化危机",
    nexus_domain: "residentevil7", steam_app_ids: ["418370"], adapter: "reframework",
    support: "needs_setup", requirements: [], sources: [], installed: true,
    path: "/games/re7", app_id: "418370", build_id: "1", running: false,
  }, mods: [], recovery_error: null,
};
const change: LaunchChange = { id: "change1", app_id: "418370", before: "PRIVATE original", after: "PRIVATE merged", changed: true };
const run: RunAction = async (_label, operation, onSuccess) => {
  const result = await operation();
  onSuccess?.(result);
  return result;
};
function panel(next = view, jobs: readonly Job[] = [], busy = false) {
  return <LaunchPanel view={next} jobs={jobs} busy={busy} run={run} />;
}
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}
beforeEach(() => {
  mocks.getLaunchSetup.mockResolvedValue(setup);
  mocks.setLaunchAuto.mockImplementation(async (_id, enabled: boolean) => ({ ...setup, auto_enabled: enabled }));
  mocks.prepareLaunchOptions.mockResolvedValue(change);
  mocks.finishLaunchOptions.mockResolvedValue({ ...setup, backup_available: true });
  mocks.read.mockResolvedValue(change.before);
  mocks.write.mockResolvedValue(change.after);
});
afterEach(() => { cleanup(); vi.resetAllMocks(); });

describe("automatic Steam launch setup", () => {
  it.each([
    { installed: false, path: null },
    { path: "/games/re7-new" },
    { app_id: "other-app" },
    { build_id: "new-build" },
  ])("refreshes launch controls when installation identity changes: %j", async (identity) => {
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, auto_enabled: false });
    const rendered = render(panel());
    await screen.findByText(setup.reason);
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, supported: false, required: false, reason: "安装状态已重新核对" });
    rendered.rerender(panel({ ...view, game: { ...view.game, ...identity } }));
    await screen.findByText("安装状态已重新核对");
    expect(mocks.getLaunchSetup).toHaveBeenCalledTimes(2);
    expect(mocks.write).not.toHaveBeenCalled();
    if (identity.installed === false) {
      expect((screen.getByRole("button", { name: "重新检查启动项" }) as HTMLButtonElement).disabled).toBe(true);
    }
  });
  it("does not reserve the shared action guard for unrecognized requirements", async () => {
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, supported: false, required: false });
    const invoked = vi.fn();
    const shared: RunAction = (label, operation, onSuccess) => {
      invoked();
      return run(label, operation, onSuccess);
    };
    render(<LaunchPanel view={view} jobs={[]} busy={false} run={shared} />);
    await screen.findByText(setup.reason);
    await act(async () => {});
    expect(invoked).not.toHaveBeenCalled();
  });
  it("refreshes requirements when the first loader is installed after selection", async () => {
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, required: false });
    const rendered = render(panel());
    await screen.findByText(setup.reason);
    expect(mocks.write).not.toHaveBeenCalled();
    mocks.getLaunchSetup.mockResolvedValue(setup);
    rendered.rerender(panel({ ...view, mods: [{ id: "loader", name: "REFramework", enabled: true, installed_at: "now", files_count: 1, nexus_mod_id: null, nexus_file_id: null, source_url: null }] }));
    await screen.findByText("启动项已检查并配置");
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it("merges recognized requirements on selection and confirms readback", async () => {
    render(panel());
    expect(await screen.findByText("启动项已检查并配置" )).toBeTruthy();
    expect(mocks.prepareLaunchOptions).toHaveBeenCalledWith("re7", change.before, false);
    expect(mocks.write).toHaveBeenCalledWith("418370", change.before, change.after);
    expect(mocks.finishLaunchOptions).toHaveBeenCalledWith("re7", "change1", change.after);
    expect(document.body.textContent).not.toContain("PRIVATE");
  });
  it.each([false, true])("does not mutate unknown or missing-loader games (supported: %s)", async (supported) => {
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, supported, required: false, reason: "需要手动核对作者说明" });
    render(panel());
    expect(await screen.findByText("需要手动核对作者说明")).toBeTruthy();
    expect(mocks.read).not.toHaveBeenCalled();
    expect(mocks.prepareLaunchOptions).not.toHaveBeenCalled();
  });
  it.each(["running", "updating", "recovery"])("waits while %s blocks changes", async (block) => {
    const blocked = { ...view, game: { ...view.game, running: block === "running", updating: block === "updating" }, recovery_error: block === "recovery" ? "recovery failure" : null };
    render(panel(blocked));
    await screen.findByText("已识别 REFramework 加载器");
    expect(mocks.prepareLaunchOptions).not.toHaveBeenCalled();
    expect(mocks.write).not.toHaveBeenCalled();
  });
  it("waits for the App operation guard before automatic setup", async () => {
    const rendered = render(panel(view, [], true));
    expect(mocks.write).not.toHaveBeenCalled();
    rendered.rerender(panel(view));
    await screen.findByText("启动项已检查并配置");
  });
  it("does not repeat on polling identities, but syncs a newly enabled MOD", async () => {
    const rendered = render(panel());
    await screen.findByText("启动项已检查并配置");
    rendered.rerender(panel({ ...view, game: { ...view.game }, mods: [] }));
    await act(async () => {});
    expect(mocks.write).toHaveBeenCalledTimes(1);
    rendered.rerender(panel({ ...view, mods: [{ id: "m1", name: "New", enabled: true, installed_at: "now", files_count: 1, nexus_mod_id: null, nexus_file_id: null, source_url: null }] }));
    await waitFor(() => expect(mocks.write).toHaveBeenCalledTimes(2));
  });
  it("checks again for a completed selected-game install, not unrelated jobs", async () => {
    const job: Job = { id: "j1", game_id: "other", name: "Other", phase: "complete", bytes_done: 1, bytes_total: 1, error: null, plan_id: null, browser_url: null };
    const rendered = render(panel());
    await screen.findByText("启动项已检查并配置");
    rendered.rerender(panel(view, [job]));
    await act(async () => {});
    expect(mocks.write).toHaveBeenCalledTimes(1);
    rendered.rerender(panel(view, [{ ...job, game_id: "re7" }]));
    await waitFor(() => expect(mocks.write).toHaveBeenCalledTimes(2));
  });
  it("makes native errors actionable, hides raw commands, retries only explicitly", async () => {
    mocks.write.mockRejectedValueOnce(new Error('PRIVATE token=secret WINEDLLOVERRIDES="bad"'));
    const rendered = render(panel());
    expect((await screen.findByRole("alert")).textContent).toContain("Steam 启动项写入未确认");
    expect(document.body.textContent).not.toContain("PRIVATE");
    expect(document.body.textContent).not.toContain("secret");
    rendered.rerender(panel({ ...view }));
    await act(async () => {});
    expect(mocks.write).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", { name: "重新检查启动项" }));
    await screen.findByText("启动项已检查并配置");
    expect(mocks.write).toHaveBeenCalledTimes(2);
  });
  it("surfaces backend preparation failures without marking configured", async () => {
    mocks.prepareLaunchOptions.mockRejectedValueOnce(new Error("PRIVATE command"));
    render(panel());
    expect((await screen.findByRole("alert")).textContent).toContain("无法安全合并启动项");
    expect(mocks.write).not.toHaveBeenCalled();
    expect(screen.queryByText("启动项已检查并配置")).toBeNull();
  });
  it("tells users to open the Steam details page when the native read is unavailable", async () => {
    mocks.read.mockRejectedValueOnce(new Error("PRIVATE command"));
    render(panel());
    expect((await screen.findByRole("alert")).textContent).toContain("Steam 打开该游戏详情页");
    expect(mocks.prepareLaunchOptions).not.toHaveBeenCalled();
  });
  it("marks configured only after the backend confirms the observed command", async () => {
    mocks.finishLaunchOptions.mockRejectedValueOnce(new Error("PRIVATE saved command"));
    render(panel());
    expect((await screen.findByRole("alert")).textContent).toContain("启动项已提交，但记录确认失败");
    expect(screen.queryByText("启动项已检查并配置")).toBeNull();
  });
  it("can turn auto off without removing existing user launch settings", async () => {
    render(panel());
    await screen.findByText("启动项已检查并配置");
    fireEvent.click(screen.getByLabelText("自动配置已识别的启动项"));
    await waitFor(() => expect(mocks.setLaunchAuto).toHaveBeenCalledWith("re7", false));
    await screen.findByText("自动配置已关闭；现有启动项会保留。");
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it("checks requirements immediately when automatic configuration is enabled", async () => {
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, auto_enabled: false });
    render(panel());
    await screen.findByText("自动配置已关闭；现有启动项会保留。");
    expect(mocks.write).not.toHaveBeenCalled();
    mocks.getLaunchSetup.mockResolvedValue(setup);
    fireEvent.click(screen.getByLabelText("自动配置已识别的启动项"));
    await screen.findByText("启动项已检查并配置");
    expect(mocks.setLaunchAuto).toHaveBeenCalledWith("re7", true);
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it("lets users restore the backed-up command and disables auto", async () => {
    mocks.finishLaunchOptions.mockResolvedValueOnce({ ...setup, backup_available: true }).mockResolvedValueOnce({ ...setup, auto_enabled: false, backup_available: false });
    render(panel());
    await screen.findByText("启动项已检查并配置");
    fireEvent.click(screen.getByRole("button", { name: "恢复首次自动配置前的启动项" }));
    await screen.findByText("启动项已恢复，自动配置已关闭");
    expect(mocks.prepareLaunchOptions).toHaveBeenLastCalledWith("re7", change.before, true);
  });
  it("explains a refused restore without exposing private launch settings", async () => {
    render(panel());
    await screen.findByText("启动项已检查并配置");
    mocks.prepareLaunchOptions.mockRejectedValueOnce(new Error("PRIVATE external options"));
    fireEvent.click(screen.getByRole("button", { name: "恢复首次自动配置前的启动项" }));
    expect((await screen.findByRole("alert")).textContent).toContain("无法安全恢复启动项");
    expect(document.body.textContent).not.toContain("PRIVATE");
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it("deduplicates StrictMode mount effects", async () => {
    render(<StrictMode>{panel()}</StrictMode>);
    await screen.findByText("启动项已检查并配置");
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it("waits for identified requirements before acquiring the action guard", async () => {
    const initial = deferred<LaunchSetup>();
    mocks.getLaunchSetup.mockReturnValueOnce(initial.promise);
    render(panel());
    await act(async () => {});
    expect(mocks.write).not.toHaveBeenCalled();
    initial.resolve(setup);
    await screen.findByText("启动项已检查并配置");
    expect(screen.getByRole("button", { name: "恢复首次自动配置前的启动项" })).toBeTruthy();
  });
  it.each(["game", "installation"])("ignores completion after changing %s", async (context) => {
    const pending = deferred<string>();
    mocks.write.mockReturnValueOnce(pending.promise);
    const rendered = render(panel());
    await waitFor(() => expect(mocks.write).toHaveBeenCalledTimes(1));
    mocks.getLaunchSetup.mockResolvedValue({ ...setup, supported: false, required: false, reason: "此游戏请手动核对", app_id: "2" });
    rendered.rerender(panel({ ...view, game: { ...view.game,
      id: context === "game" ? "other" : view.game.id, path: "/games/new-install", app_id: "2" } }));
    await act(async () => { pending.resolve(change.after); });
    expect(await screen.findByText("此游戏请手动核对")).toBeTruthy();
    expect(screen.queryByText("启动项已检查并配置")).toBeNull();
  });
});

describe("serialized launch flow", () => {
  it("serializes different games and deduplicates overlapping same-game actions", async () => {
    const pending = deferred<string>();
    mocks.write.mockReturnValueOnce(pending.promise);
    const first = synchronizeLaunchOptions("re7");
    const duplicate = synchronizeLaunchOptions("re7");
    const second = synchronizeLaunchOptions("other");
    await waitFor(() => expect(mocks.write).toHaveBeenCalledTimes(1));
    expect(mocks.read).toHaveBeenCalledTimes(1);
    pending.resolve(change.after);
    await Promise.all([first, duplicate, second]);
    expect(mocks.write).toHaveBeenCalledTimes(2);
  });
  it("skips writes and finish for an already correct command", async () => {
    mocks.prepareLaunchOptions.mockResolvedValue({ ...change, changed: false, after: change.before });
    const result = await synchronizeLaunchOptions("re7");
    expect(result.configured).toBe(true);
    expect(mocks.write).not.toHaveBeenCalled();
    expect(mocks.finishLaunchOptions).not.toHaveBeenCalled();
  });
  it("returns a newly detected external-edit warning after a no-op check", async () => {
    const warning = { ...setup, reason: "检测到后续更改，已保留设置，禁止恢复旧备份。" };
    mocks.getLaunchSetup.mockResolvedValueOnce(setup).mockResolvedValueOnce(warning);
    mocks.prepareLaunchOptions.mockResolvedValue({ ...change, changed: false, after: change.before });
    const result = await synchronizeLaunchOptions("re7");
    expect(result.setup.reason).toBe(warning.reason);
    expect(mocks.write).not.toHaveBeenCalled();
  });
});
