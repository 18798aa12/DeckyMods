import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { forwardRef, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Game, GameView, Job, RunAction } from "./types";
const mocks = vi.hoisted(() => ({ getImportDirectory: vi.fn(), importArchive: vi.fn(), resolveMod: vi.fn(), beginDownload: vi.fn(), acceptNxm: vi.fn(), setGameRoot: vi.fn(), picker: vi.fn(), external: vi.fn() }));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/api", () => ({ useQuickAccessVisible: () => true, openFilePicker: mocks.picker, FileSelectionType: { FILE: 0, FOLDER: 1 } }));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: mocks.external },
  Focusable: forwardRef<HTMLDivElement, { children: ReactNode }>(function Focus({ children }, ref) { return <div ref={ref}>{children}</div>; }),
  PanelSection: ({ children }: { children: ReactNode }) => <section>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
  ToggleField: ({ label, checked, disabled, onChange }: { label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) => <label>{label}<input aria-label={label} type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} /></label>,
  TextField: ({ label, value, disabled, onChange }: { label: string; value: string; disabled: boolean; onChange: (event: { target: { value: string } }) => void }) => <label>{label}<input aria-label={label} value={value} disabled={disabled} onChange={onChange} /></label>,
  DropdownItem: () => <div />,
}));
import { SourcePanel } from "./SourcePanel";
const game: Game = { id: "other", name: "未适配游戏", series: "other", series_name: "其他", nexus_domain: "other", steam_app_ids: ["10"], adapter: "catalog", support: "catalog", requirements: [], sources: [], installed: true, path: "/games/Other", app_id: "10", build_id: "1", running: false };
const job: Job = { id: "job", game_id: game.id, name: "demo", phase: "queued", bytes_done: 0, bytes_total: 0, error: null, plan_id: null, browser_url: null };
const run: RunAction = async (_label, operation, onSuccess) => { const result = await operation(); onSuccess?.(result); return result; };
const renderPanel = (selected = game) => render(<SourcePanel game={selected} busy={false} run={run} onJob={vi.fn()} />);
beforeEach(() => {
  mocks.getImportDirectory.mockResolvedValue("/home/deck/Downloads");
  mocks.picker.mockResolvedValue({ path: "/home/deck/Downloads/demo.zip" });
  mocks.importArchive.mockResolvedValue(job);
  mocks.beginDownload.mockResolvedValue(job);
  mocks.acceptNxm.mockResolvedValue(job);
  mocks.setGameRoot.mockResolvedValue({ game, mods: [], recovery_error: null });
  mocks.resolveMod.mockResolvedValue({ game_id: game.id, mod_id: 7, name: "示例", author: "作者", summary: "说明", page_url: "https://www.nexusmods.com/other/mods/7", files: [{ file_id: 9, name: "demo", version: "1", category: "main", size_bytes: 1, description: "", primary: true }] });
});
afterEach(() => { cleanup(); vi.resetAllMocks(); });
describe("explicit generic root archive installation", () => {
  it("defaults to reviewed adapter mode and shows a root option only for catalog games", () => {
    const rendered = renderPanel();
    expect((screen.getByLabelText("按游戏根目录安装（未适配游戏）") as HTMLInputElement).checked).toBe(false);
    rendered.rerender(<SourcePanel game={{ ...game, adapter: "reframework", support: "needs_setup" }} busy={false} run={run} onJob={vi.fn()} />);
    expect(screen.queryByLabelText("按游戏根目录安装（未适配游戏）")).toBeNull();
  });
  it("preserves the existing import contract by default", async () => {
    renderPanel();
    fireEvent.click(screen.getByRole("button", { name: "选择本地 MOD 压缩包" }));
    await waitFor(() => expect(mocks.importArchive).toHaveBeenCalledWith(game.id, "/home/deck/Downloads/demo.zip", "demo"));
  });
  it("uses root mapping only after explicit choice and explains its limits", async () => {
    renderPanel();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    expect(document.body.textContent).toContain("保留压缩包内的目录");
    expect(document.body.textContent).toContain("不会自动安装前置");
    fireEvent.click(screen.getByRole("button", { name: "选择本地 MOD 压缩包" }));
    await waitFor(() => expect(mocks.importArchive).toHaveBeenCalledWith(game.id, "/home/deck/Downloads/demo.zip", "demo", "game_root"));
  });
  it("applies the explicit mode to Nexus downloads and manual NXM handoff", async () => {
    renderPanel();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    fireEvent.change(screen.getByLabelText("MOD 编号或 Nexus 网址"), { target: { value: "7" } });
    fireEvent.click(screen.getByRole("button", { name: "查找 MOD" }));
    fireEvent.click(await screen.findByRole("button", { name: "获取所选文件" }));
    await waitFor(() => expect(mocks.beginDownload).toHaveBeenCalledWith(game.id, 7, 9, "game_root"));
    fireEvent.change(screen.getByLabelText("手动接收 NXM 链接（可选）"), { target: { value: "nxm://other/mods/7/files/9" } });
    fireEvent.click(screen.getByRole("button", { name: "接收 NXM 下载" }));
    await waitFor(() => expect(mocks.acceptNxm).toHaveBeenCalledWith("nxm://other/mods/7/files/9", "game_root", game.id));
  });
  it("does not authorize root mode for default Nexus downloads or NXM links", async () => {
    renderPanel();
    fireEvent.change(screen.getByLabelText("MOD 编号或 Nexus 网址"), { target: { value: "7" } });
    fireEvent.click(screen.getByRole("button", { name: "查找 MOD" }));
    fireEvent.click(await screen.findByRole("button", { name: "获取所选文件" }));
    await waitFor(() => expect(mocks.beginDownload).toHaveBeenCalledWith(game.id, 7, 9));
    fireEvent.change(screen.getByLabelText("手动接收 NXM 链接（可选）"), { target: { value: "nxm://other/mods/7/files/9" } });
    fireEvent.click(screen.getByRole("button", { name: "接收 NXM 下载" }));
    await waitFor(() => expect(mocks.acceptNxm).toHaveBeenCalledWith("nxm://other/mods/7/files/9"));
  });
  it("does not carry a root choice into a different game", async () => {
    const rendered = renderPanel();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    rendered.rerender(<SourcePanel game={{ ...game, id: "second" }} busy={false} run={run} onJob={vi.fn()} />);
    expect((screen.getByLabelText("按游戏根目录安装（未适配游戏）") as HTMLInputElement).checked).toBe(false);
    fireEvent.click(screen.getByRole("button", { name: "选择本地 MOD 压缩包" }));
    await waitFor(() => expect(mocks.importArchive).toHaveBeenCalledWith("second", "/home/deck/Downloads/demo.zip", "demo"));
  });
  it("blocks root choice while the game is running", () => {
    renderPanel({ ...game, running: true });
    expect((screen.getByLabelText("按游戏根目录安装（未适配游戏）") as HTMLInputElement).disabled).toBe(true);
  });
  it("shows the detected root only after explicit root choice and can locate it again", async () => {
    const onView = vi.fn();
    render(<SourcePanel game={game} busy={false} run={run} onJob={vi.fn()} onView={onView} />);
    expect(screen.queryByRole("button", { name: "自动定位 Steam 游戏根目录" })).toBeNull();
    expect(mocks.setGameRoot).not.toHaveBeenCalled();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    expect(screen.getByText("当前安装目录：/games/Other（Steam 自动定位）")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "自动定位 Steam 游戏根目录" }));
    await waitFor(() => expect(mocks.setGameRoot).toHaveBeenCalledWith(game.id, "auto"));
    await waitFor(() => expect(onView).toHaveBeenCalledWith({ game, mods: [], recovery_error: null }));
  });
  it("uses the folder picker and server-side root validation before updating the view", async () => {
    const onView = vi.fn();
    const next: GameView = { game: { ...game, path: "/games/Manual", manual_root: true }, mods: [], recovery_error: null };
    mocks.picker.mockResolvedValue({ path: "/games/Manual" });
    mocks.setGameRoot.mockResolvedValue(next);
    render(<SourcePanel game={game} busy={false} run={run} onJob={vi.fn()} onView={onView} />);
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect(mocks.picker).toHaveBeenCalledWith(1, "/games/Other", false, true, undefined, undefined, false, false));
    await waitFor(() => expect(mocks.setGameRoot).toHaveBeenCalledWith(game.id, "manual", "/games/Manual"));
    expect(onView).toHaveBeenCalledWith(next);
  });
  it("starts in Downloads for missing games and blocks imports until a valid root is selected", async () => {
    renderPanel({ ...game, installed: false, path: null, root_error: "尚未选择游戏目录" });
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    expect(screen.getByText("尚未选择游戏目录")).toBeTruthy();
    expect((screen.getByRole("button", { name: "选择本地 MOD 压缩包" }) as HTMLButtonElement).disabled).toBe(true);
    mocks.picker.mockResolvedValue({ path: "/games/Manual" });
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect(mocks.picker).toHaveBeenCalledWith(1, "/home/deck/Downloads", false, true, undefined, undefined, false, false));
  });
  it("releases the shared picker lock after cancellation and does not change the root", async () => {
    mocks.picker.mockRejectedValueOnce("User canceled").mockResolvedValue({ path: "/games/Manual" });
    renderPanel();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect((screen.getByRole("button", { name: "手动选择游戏根目录" }) as HTMLButtonElement).disabled).toBe(false));
    expect(mocks.setGameRoot).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect(mocks.setGameRoot).toHaveBeenCalledWith(game.id, "manual", "/games/Manual"));
  });
  it("releases root controls when the shared mutation guard declines the operation", async () => {
    const declined: RunAction = async () => null;
    render(<SourcePanel game={game} busy={false} run={declined} onJob={vi.fn()} />);
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect((screen.getByRole("button", { name: "手动选择游戏根目录" }) as HTMLButtonElement).disabled).toBe(false));
    expect(mocks.picker).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "自动定位 Steam 游戏根目录" }));
    await waitFor(() => expect((screen.getByRole("button", { name: "自动定位 Steam 游戏根目录" }) as HTMLButtonElement).disabled).toBe(false));
  });
  it("shares the picker lock between archive and root selectors and ignores unmounted results", async () => {
    let finishPicker: ((value: { path: string }) => void) | undefined;
    mocks.picker.mockImplementationOnce(() => new Promise<{ path: string }>((resolve) => { finishPicker = resolve; }));
    const rendered = renderPanel();
    fireEvent.click(screen.getByLabelText("按游戏根目录安装（未适配游戏）"));
    fireEvent.click(screen.getByRole("button", { name: "手动选择游戏根目录" }));
    await waitFor(() => expect(mocks.picker).toHaveBeenCalledTimes(1));
    expect((screen.getByRole("button", { name: "选择本地 MOD 压缩包" }) as HTMLButtonElement).disabled).toBe(true);
    rendered.unmount();
    await act(async () => { finishPicker?.({ path: "/games/Manual" }); });
    expect(mocks.setGameRoot).not.toHaveBeenCalled();
  });
});
