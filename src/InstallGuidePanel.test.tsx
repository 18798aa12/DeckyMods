import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StrictMode, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Game, InstallGuide } from "./types";

const mocks = vi.hoisted(() => ({ getInstallGuide: vi.fn(), external: vi.fn() }));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: mocks.external },
  PanelSection: ({ title, children }: { title: string; children: ReactNode }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
}));
import { InstallGuidePanel } from "./InstallGuidePanel";

const game: Game = { id: "stardewvalley", name: "Stardew Valley", series: "stardew", series_name: "Stardew", nexus_domain: "stardewvalley", steam_app_ids: ["413150"], adapter: "smapi", support: "automatic", requirements: [], sources: [], installed: true, path: "/games/Stardew", app_id: "413150", build_id: "100", running: false };
const guide: InstallGuide = {
  game_id: game.id, name: game.name, checked_at: "2026-10-19", notes: ["尚未进行游戏内验证"], sources: ["https://github.com/Pathoschild/SMAPI"],
  methods: [
    { id: "smapi", label: "SMAPI 内容包", versions: ["SMAPI 4.x / 游戏 1.6"], format: "manifest.json", destination: "Mods/<Mod>/", requirements: ["先安装匹配的 SMAPI", "检查 ContentPackFor 依赖"], source_urls: ["https://github.com/Pathoschild/SMAPI/blob/develop/docs/README.md"], can_install: true, install_mode: "game_root" },
    { id: "legacy", label: "旧版 XNB 替换", versions: ["作者指定的旧版"], format: "XNB", destination: "作者指定的 Content 子目录", requirements: ["先备份"], source_urls: [], can_install: false, install_mode: null },
  ],
};

beforeEach(() => { mocks.getInstallGuide.mockResolvedValue(guide); });
afterEach(() => { cleanup(); vi.resetAllMocks(); });
const expand = async (): Promise<void> => {
  fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
  await screen.findByText("资料核查：2026-10-19");
};

describe("per-game installation guides", () => {
  it("defaults to folded and fetches only when opened; each method is folded too", async () => {
    render(<InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={vi.fn()} />);
    expect(mocks.getInstallGuide).not.toHaveBeenCalled();
    await expand();
    expect(mocks.getInstallGuide).toHaveBeenCalledWith(game.id);
    expect(screen.queryByText("Mods/<Mod>/")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "展开：SMAPI 内容包" }));
    expect(screen.getByText("版本：SMAPI 4.x / 游戏 1.6")).toBeTruthy();
    expect(screen.getByText("目标：Mods/<Mod>/")).toBeTruthy();
    expect(screen.getByText("格式：manifest.json")).toBeTruthy();
    expect(screen.getByText("检查 ContentPackFor 依赖")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "收起安装指南" }));
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    expect(mocks.getInstallGuide).toHaveBeenCalledTimes(1);
  });

  it("selects an implemented method explicitly and leaves external tools manual", async () => {
    const select = vi.fn();
    const ui = render(<InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={select} />);
    await expand();
    fireEvent.click(screen.getByRole("button", { name: "展开：SMAPI 内容包" }));
    fireEvent.click(screen.getByRole("button", { name: "选择安装方式：SMAPI 内容包" }));
    expect(select).toHaveBeenCalledWith("game_root");
    ui.rerender(<InstallGuidePanel game={game} busy={false} selectedMode="game_root" onSelectMode={select} />);
    expect(screen.getByText("当前安装方式：SMAPI 内容包")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "展开：旧版 XNB 替换" }));
    expect(screen.getByText("需按作者说明手动安装或使用外部工具。此路线不会由插件自动执行。")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "选择安装方式：旧版 XNB 替换" })).toBeNull();
  });

  it.each([
    { busy: true, changed: {} },
    { busy: false, changed: { installed: false, path: null } },
    { busy: false, changed: { running: true } },
    { busy: false, changed: { updating: true } },
    { busy: false, changed: { root_error: "目录失效" } },
  ])("blocks method selection when installation is unavailable: %j", async ({ busy, changed }) => {
    const select = vi.fn();
    render(<InstallGuidePanel game={{ ...game, ...changed }} busy={busy} selectedMode="auto" onSelectMode={select} />);
    await expand();
    fireEvent.click(screen.getByRole("button", { name: "展开：SMAPI 内容包" }));
    const button = screen.getByRole("button", { name: "选择安装方式：SMAPI 内容包" }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    fireEvent.click(button);
    expect(select).not.toHaveBeenCalled();
  });

  it("allows retry after a redacted failure without losing the folded structure", async () => {
    mocks.getInstallGuide.mockRejectedValueOnce(new Error("token=synthetic-secret https://private.example/grant"));
    render(<InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    expect((await screen.findByRole("alert")).textContent).toContain("无法读取安装指南");
    expect(document.body.textContent).not.toContain("synthetic-secret");
    expect(document.body.textContent).not.toContain("private.example");
    fireEvent.click(screen.getByRole("button", { name: "重试读取安装指南" }));
    await screen.findByText("资料核查：2026-10-19");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByText("Mods/<Mod>/")).toBeNull();
  });

  it("discards an old game's delayed response and resets a previous explicit choice", async () => {
    let old: ((value: InstallGuide) => void) | undefined;
    mocks.getInstallGuide.mockImplementationOnce(() => new Promise<InstallGuide>((resolve) => { old = resolve; }));
    const select = vi.fn();
    const ui = render(<InstallGuidePanel game={game} busy={false} selectedMode="game_root" onSelectMode={select} />);
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    const next = { ...game, id: "other", name: "Other" };
    ui.rerender(<InstallGuidePanel game={next} busy={false} selectedMode="game_root" onSelectMode={select} />);
    expect(select).toHaveBeenCalledWith("auto");
    await act(async () => { old?.(guide); });
    expect(screen.queryByText("资料核查：2026-10-19")).toBeNull();
    expect(screen.queryByRole("button", { name: "展开：SMAPI 内容包" })).toBeNull();
    expect(mocks.getInstallGuide).toHaveBeenCalledTimes(1);
  });

  it.each([
    { path: "/games/OtherRoot" },
    { build_id: "101" },
    { installed: false, path: null },
  ])("invalidates old guide and selected mode when installation identity changes: %j", async (changed) => {
    const select = vi.fn();
    const ui = render(<InstallGuidePanel game={game} busy={false} selectedMode="game_root" onSelectMode={select} />);
    await expand();
    fireEvent.click(screen.getByRole("button", { name: "展开：SMAPI 内容包" }));
    ui.rerender(<InstallGuidePanel game={{ ...game, ...changed }} busy={false} selectedMode="game_root" onSelectMode={select} />);
    expect(screen.queryByText("目标：Mods/<Mod>/")).toBeNull();
    expect(select).toHaveBeenCalledWith("auto");
    expect(screen.getByRole("button", { name: "展开安装指南" })).toBeTruthy();
  });

  it("rejects a mismatched guide response instead of enabling methods for another game", async () => {
    mocks.getInstallGuide.mockResolvedValue({ ...guide, game_id: "wrong" });
    render(<InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    expect((await screen.findByRole("alert")).textContent).toContain("无法读取安装指南");
    expect(screen.queryByRole("button", { name: "展开：SMAPI 内容包" })).toBeNull();
  });

  it("opens only vetted sources and never renders credential-bearing links", async () => {
    mocks.getInstallGuide.mockResolvedValue({ ...guide, sources: [...guide.sources, "https://github.com/x?token=synthetic-secret", "https://127.0.0.1/private"] });
    render(<InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={vi.fn()} />);
    await expand();
    fireEvent.click(screen.getByRole("button", { name: "打开来源：github.com" }));
    expect(mocks.external).toHaveBeenCalledWith("https://github.com/Pathoschild/SMAPI");
    expect(document.body.textContent).not.toContain("synthetic-secret");
    expect(document.body.textContent).not.toContain("127.0.0.1");
  });

  it("does not leave duplicate reads or unhandled callbacks after StrictMode unmount", async () => {
    let finish: ((value: InstallGuide) => void) | undefined;
    mocks.getInstallGuide.mockImplementation(() => new Promise<InstallGuide>((resolve) => { finish = resolve; }));
    const ui = render(<StrictMode><InstallGuidePanel game={game} busy={false} selectedMode="auto" onSelectMode={vi.fn()} /></StrictMode>);
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    fireEvent.click(screen.getByRole("button", { name: "收起安装指南" }));
    fireEvent.click(screen.getByRole("button", { name: "展开安装指南" }));
    expect(mocks.getInstallGuide).toHaveBeenCalledTimes(1);
    ui.unmount();
    await act(async () => { finish?.(guide); });
    await waitFor(() => expect(mocks.getInstallGuide).toHaveBeenCalledTimes(1));
  });
});
