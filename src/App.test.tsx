import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StrictMode, forwardRef, type ReactNode } from "react";
import type { Auth, Game, GameView, Job, Plan, Status } from "./types";

const { mocks } = vi.hoisted(() => ({
  mocks: {
    getStatus: vi.fn(),
    listGames: vi.fn(),
    getGame: vi.fn(),
    getLaunchSetup: vi.fn(),
    setLaunchAuto: vi.fn(),
    prepareLaunchOptions: vi.fn(),
    finishLaunchOptions: vi.fn(),
    getResidentStatus: vi.fn(),
    prepareResidentSettings: vi.fn(),
    restoreResidentSettings: vi.fn(),
    getUpdateStatus: vi.fn(),
    setUpdateOptions: vi.fn(),
    checkUpdate: vi.fn(),
    prepareUpdate: vi.fn(),
    bindAccount: vi.fn(),
    disconnectAccount: vi.fn(),
    resolveMod: vi.fn(),
    beginDownload: vi.fn(),
    acceptNxm: vi.fn(),
    getImportDirectory: vi.fn(),
    importArchive: vi.fn(),
    getPlan: vi.fn(),
    installPlan: vi.fn(),
    setModEnabled: vi.fn(),
    uninstallMod: vi.fn(),
    getJobs: vi.fn(),
    cancelJob: vi.fn(),
    setNxmHandler: vi.fn(),
    visible: vi.fn(),
    picker: vi.fn(),
    external: vi.fn(),
  },
}));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/api", () => ({
  useQuickAccessVisible: mocks.visible,
  openFilePicker: mocks.picker,
  FileSelectionType: { FILE: 0 },
  definePlugin: (fn: unknown) => fn,
}));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: mocks.external },
  staticClasses: { Title: "title" },
  GamepadButton: { OK: 1, CANCEL: 2 },
  Focusable: forwardRef<HTMLDivElement, { children: ReactNode }>(
    function MockFocusable({ children, ...props }, ref) {
      return (
        <div {...props} ref={ref}>
          {children}
        </div>
      );
    },
  ),
  PanelSection: ({
    title,
    children,
  }: {
    title: string;
    children: ReactNode;
  }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => (
    <div>{children}</div>
  ),
  ButtonItem: ({
    children,
    disabled,
    onClick,
  }: {
    children: ReactNode;
    disabled: boolean;
    onClick: () => void;
  }) => (
    <button disabled={disabled} onClick={onClick}>
      {children}
    </button>
  ),
  TextField: ({
    label,
    value,
    disabled,
    bIsPassword,
    onChange,
  }: {
    label: string;
    value: string;
    disabled: boolean;
    bIsPassword?: boolean;
    onChange: React.ChangeEventHandler<HTMLInputElement>;
  }) => (
    <label>
      {label}
      <input
        aria-label={label}
        value={value}
        disabled={disabled}
        type={bIsPassword ? "password" : "text"}
        onChange={onChange}
      />
    </label>
  ),
  ToggleField: ({
    label,
    checked,
    disabled,
    onChange,
  }: {
    label: string;
    checked: boolean;
    disabled: boolean;
    onChange: (value: boolean) => void;
  }) => (
    <label>
      {label}
      <input
        aria-label={label}
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
      />
    </label>
  ),
  DropdownItem: ({
    label,
    selectedOption,
    disabled,
    rgOptions,
    onChange,
  }: {
    label: string;
    selectedOption: string | number;
    disabled: boolean;
    rgOptions: { data: string | number; label: string }[];
    onChange: (value: { data: string | number }) => void;
  }) => (
    <label>
      {label}
      <select
        aria-label={label}
        disabled={disabled}
        value={selectedOption}
        onChange={(event) => {
          const option = rgOptions.find(
            (item) => String(item.data) === event.target.value,
          );
          if (option) onChange(option);
        }}
      >
        {rgOptions.map((option) => (
          <option value={option.data} key={option.data}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  ),
}));
import { App } from "./App";
const auth: Auth = {
  connected: false,
  name: null,
  premium: false,
  user_id: null,
  error: null,
};
const game: Game = {
  id: "re4",
  name: "Resident Evil 4",
  series: "resident-evil",
  series_name: "生化危机",
  nexus_domain: "residentevil42023",
  steam_app_ids: ["2050650"],
  adapter: "re_pak",
  support: "automatic",
  requirements: [],
  sources: [],
  installed: true,
  path: "/games/RE4",
  app_id: "2050650",
  build_id: "1",
  running: false,
};
const gameView: GameView = {
  game,
  mods: [
    {
      id: "m1",
      name: "示例服装",
      enabled: true,
      installed_at: "2026-10-19",
      files_count: 2,
      nexus_mod_id: 42,
      nexus_file_id: 9,
      source_url: "https://www.nexusmods.com/residentevil42023/mods/42",
    },
  ],
  recovery_error: null,
};
const job: Job = {
  id: "j1",
  game_id: "re4",
  name: "示例服装",
  phase: "ready",
  bytes_done: 100,
  bytes_total: 100,
  error: null,
  plan_id: "p1",
  browser_url: null,
};
const plan: Plan = {
  id: "p1",
  game_id: "re4",
  name: "示例服装",
  files_count: 2,
  bytes: 100,
  conflicts: ["example.pak"],
  warnings: ["请关闭游戏"],
  requirements: [],
  blocked_reason: null,
  can_install: true,
};
const status: Status = {
  version: "0.1.0",
  platform_supported: true,
  auth,
  jobs: [],
  handler: { enabled: false, supported: true, previous: null, message: null },
  error: null,
};
beforeEach(() => {
  mocks.visible.mockReturnValue(true);
  mocks.getStatus.mockResolvedValue(status);
  mocks.listGames.mockResolvedValue([game]);
  mocks.getJobs.mockResolvedValue([]);
  mocks.getGame.mockResolvedValue(gameView);
  mocks.getLaunchSetup.mockResolvedValue({
    supported: false,
    required: false,
    reason: "未识别额外启动项要求",
    app_id: game.app_id,
    auto_enabled: true,
    backup_available: false,
  });
  mocks.getResidentStatus.mockResolvedValue({
    supported: true,
    family: "RE Engine / REFramework",
    build_id: game.build_id,
    runtime_tdb: null,
    renderer: null,
    runtime_evidence: false,
    script_count: 0,
    last_run_at: null,
    loader_present: false,
    config_exists: false,
    config_valid: false,
    loose_enabled: false,
    pak_directory_enabled: false,
    config_backup_available: false,
    warnings: [],
  });
  mocks.getUpdateStatus.mockResolvedValue({
    current_version: status.version,
    latest_version: null,
    available: false,
    checked_at: null,
    error: null,
    source: null,
    auto_check: true,
    source_label: "更新来源尚未配置",
  });
  mocks.getImportDirectory.mockResolvedValue("/home/deck/Downloads");
});
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
  vi.useRealTimers();
});
async function selectGame(): Promise<void> {
  fireEvent.click(
    await screen.findByRole("button", { name: "展开游戏列表（1）" }),
  );
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" }));
  });
  await screen.findByText("当前游戏：Resident Evil 4");
}
describe("DeckyMods workflows", () => {
  it("keeps game and installed mod lists folded until requested", async () => {
    render(<App />);
    await screen.findByText("DeckyMods 0.1.0");
    expect(
      screen.queryByRole("button", { name: "选择 Resident Evil 4" }),
    ).toBeNull();
    await selectGame();
    expect(screen.queryByText("示例服装")).toBeNull();
    fireEvent.click(
      screen.getByRole("button", { name: "展开已安装 MOD（1）" }),
    );
    expect(await screen.findByRole("button", { name: "展开“示例服装”" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "禁用 MOD" })).toBeNull();
  });
  it("keeps a requested MOD list open after delayed game selection and polling", async () => {
    vi.useFakeTimers();
    let finishSelection: ((value: GameView) => void) | undefined;
    mocks.getGame.mockImplementationOnce(() => new Promise<GameView>((resolve) => {
      finishSelection = resolve;
    }));
    render(<App />);
    await act(async () => {});
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    fireEvent.click(screen.getByRole("button", { name: "选择 Resident Evil 4" }));
    expect(screen.queryByText("当前游戏：Resident Evil 4")).toBeNull();
    expect(screen.queryByRole("button", { name: "展开已安装 MOD（1）" })).toBeNull();
    await act(async () => { finishSelection?.(gameView); });
    expect(screen.getByText("当前游戏：Resident Evil 4")).toBeTruthy();
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "展开已安装 MOD（1）" }));
    });
    expect(screen.getByRole("button", { name: "展开“示例服装”" })).toBeTruthy();
    await act(async () => { vi.advanceTimersByTime(3000); });
    expect(mocks.getGame).toHaveBeenCalledTimes(2);
    expect(screen.getByRole("button", { name: "展开“示例服装”" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "禁用 MOD" })).toBeNull();
  });
  it("binds a masked API key and clears it after success", async () => {
    mocks.bindAccount.mockResolvedValue({
      ...auth,
      connected: true,
      name: "player",
    });
    render(<App />);
    fireEvent.click(
      await screen.findByRole("button", { name: "展开 Nexus 账号" }),
    );
    const key = screen.getByLabelText("Nexus API Key") as HTMLInputElement;
    expect(key.type).toBe("password");
    fireEvent.change(key, { target: { value: "private-key" } });
    fireEvent.click(screen.getByText("绑定账号"));
    await waitFor(() =>
      expect(mocks.bindAccount).toHaveBeenCalledWith("private-key"),
    );
    await waitFor(() => expect(key.value).toBe(""));
    expect(await screen.findByText("player · 普通会员")).toBeTruthy();
  });
  it("asks free members to confirm the selected file on the Nexus website", async () => {
    mocks.resolveMod.mockResolvedValue({
      game_id: "re4",
      mod_id: 42,
      name: "示例 MOD",
      author: "author",
      summary: "summary",
      page_url: "https://www.nexusmods.com/residentevil42023/mods/42",
      files: [
        {
          file_id: 9,
          name: "主文件",
          version: "1",
          category: "MAIN",
          size_bytes: 100,
          description: "",
          primary: true,
        },
        {
          file_id: 10,
          name: "可选文件",
          version: "1",
          category: "OPTIONAL",
          size_bytes: 10,
          description: "",
          primary: false,
        },
      ],
    });
    const browser =
      "https://www.nexusmods.com/residentevil42023/mods/42?tab=files&file_id=10";
    mocks.beginDownload.mockResolvedValue({
      ...job,
      phase: "awaiting_browser",
      browser_url: browser,
    });
    render(<App />);
    await selectGame();
    fireEvent.change(screen.getByLabelText("MOD 编号或 Nexus 网址"), {
      target: { value: "42" },
    });
    fireEvent.click(screen.getByText("查找 MOD"));
    await screen.findByText("作者：author");
    const download = screen.getByText("获取所选文件") as HTMLButtonElement;
    expect(download.disabled).toBe(true);
    fireEvent.change(screen.getByLabelText("选择下载文件"), {
      target: { value: "10" },
    });
    fireEvent.click(download);
    await waitFor(() =>
      expect(mocks.beginDownload).toHaveBeenCalledWith("re4", 42, 10),
    );
    expect(mocks.external).toHaveBeenCalledWith(browser);
    expect(
      await screen.findByText(/普通会员需在 Nexus 网页确认下载/),
    ).toBeTruthy();
  });
  it("keeps an archive picker result across the QAM hidden interval", async () => {
    let resolveFile: ((value: { path: string }) => void) | undefined;
    mocks.picker.mockImplementation(
      () =>
        new Promise<{ path: string }>((resolve) => {
          resolveFile = resolve;
        }),
    );
    mocks.importArchive.mockResolvedValue(job);
    const view = render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await waitFor(() => expect(mocks.picker).toHaveBeenCalled());
    mocks.visible.mockReturnValue(false);
    view.rerender(<App />);
    await act(async () => {
      resolveFile?.({ path: "/home/deck/Downloads/服装.zip" });
    });
    await waitFor(() =>
      expect(mocks.importArchive).toHaveBeenCalledWith(
        "re4",
        "/home/deck/Downloads/服装.zip",
        "服装",
      ),
    );
    mocks.visible.mockReturnValue(true);
    view.rerender(<App />);
    expect(await screen.findByText("压缩包已加入检查队列")).toBeTruthy();
  });
  it("uses the backend download directory for custom users and XDG locations", async () => {
    mocks.getImportDirectory.mockResolvedValue("/home/player/下载");
    mocks.picker.mockResolvedValue({ path: "/home/player/下载/服装.zip" });
    mocks.importArchive.mockResolvedValue(job);
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await waitFor(() =>
      expect(mocks.importArchive).toHaveBeenCalledWith(
        "re4",
        "/home/player/下载/服装.zip",
        "服装",
      ),
    );
    expect(mocks.getImportDirectory).toHaveBeenCalledOnce();
    expect(mocks.picker.mock.calls[0]?.[1]).toBe("/home/player/下载");
  });
  it("keeps the picker closed when its directory cannot be read and permits retry", async () => {
    mocks.getImportDirectory
      .mockRejectedValueOnce(new Error("下载目录暂时不可用，请重试"))
      .mockResolvedValueOnce("/home/player/Downloads");
    mocks.picker.mockResolvedValue({ path: "/home/player/Downloads/mod.7z" });
    mocks.importArchive.mockResolvedValue(job);
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await screen.findByText(/无法读取导入目录，请重试/);
    expect(mocks.picker).not.toHaveBeenCalled();
    expect(mocks.importArchive).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await waitFor(() => expect(mocks.importArchive).toHaveBeenCalledOnce());
    expect(mocks.picker.mock.calls[0]?.[1]).toBe("/home/player/Downloads");
  });
  it("does not open a stale picker when the plugin unmounts during directory lookup", async () => {
    let releaseDirectory: ((value: string) => void) | undefined;
    mocks.getImportDirectory.mockImplementation(
      () =>
        new Promise<string>((resolve) => {
          releaseDirectory = resolve;
        }),
    );
    const view = render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await waitFor(() => expect(releaseDirectory).toBeTypeOf("function"));
    expect(
      (screen.getByText("当前：Resident Evil 4") as HTMLButtonElement).disabled,
    ).toBe(true);
    view.unmount();
    await act(async () => {
      releaseDirectory?.("/home/player/Downloads");
    });
    expect(mocks.picker).not.toHaveBeenCalled();
    expect(mocks.importArchive).not.toHaveBeenCalled();
  });
  it("rejects a malformed directory response without guessing another location", async () => {
    mocks.getImportDirectory.mockResolvedValue("relative/downloads");
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await screen.findByText("导入目录无效，请重试。");
    expect(mocks.picker).not.toHaveBeenCalled();
    expect(mocks.importArchive).not.toHaveBeenCalled();
  });
  it("rejects picker folders without sending an import", async () => {
    mocks.picker.mockResolvedValue({ path: "/home/deck/Downloads/folder" });
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    expect(await screen.findByRole("alert")).toHaveProperty(
      "textContent",
      expect.stringContaining("ZIP、7z 或 RAR"),
    );
    expect(mocks.importArchive).not.toHaveBeenCalled();
  });
  it("requires conflict acknowledgement before installing a ready plan", async () => {
    mocks.getStatus.mockResolvedValue({ ...status, jobs: [job] });
    mocks.getPlan.mockResolvedValue(plan);
    mocks.installPlan.mockResolvedValue({ ...job, phase: "complete" });
    render(<App />);
    fireEvent.click(
      await screen.findByRole("button", { name: "展开下载与安装任务（1）" }),
    );
    fireEvent.click(screen.getByText("预览安装"));
    await screen.findByText("example.pak");
    const install = screen.getByText("确认安装") as HTMLButtonElement;
    expect(install.disabled).toBe(true);
    fireEvent.click(screen.getByLabelText("我确认覆盖上述冲突文件"));
    fireEvent.click(install);
    await waitFor(() =>
      expect(mocks.installPlan).toHaveBeenCalledWith("p1", true),
    );
  });
  it("can disable and uninstall only after explicit confirmation", async () => {
    mocks.setModEnabled.mockResolvedValue({
      ...gameView,
      mods: [{ ...gameView.mods[0], enabled: false }],
    });
    mocks.uninstallMod.mockResolvedValue({ ...gameView, mods: [] });
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("展开已安装 MOD（1）"));
    fireEvent.click(screen.getByText("展开“示例服装”"));
    fireEvent.click(screen.getByText("禁用 MOD"));
    await waitFor(() =>
      expect(mocks.setModEnabled).toHaveBeenCalledWith("re4", "m1", false),
    );
    await screen.findByText("启用 MOD");
    fireEvent.click(screen.getByText("卸载 MOD"));
    expect(mocks.uninstallMod).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText("确认卸载“示例服装”"));
    await waitFor(() =>
      expect(mocks.uninstallMod).toHaveBeenCalledWith("re4", "m1"),
    );
  });
  it("blocks deployment while Steam updates a game and keeps read-only lookup available", async () => {
    const updatingGame = { ...game, updating: true };
    mocks.listGames.mockResolvedValue([updatingGame]);
    mocks.getGame.mockResolvedValue({ ...gameView, game: updatingGame });
    mocks.getStatus.mockResolvedValue({ ...status, jobs: [job] });
    mocks.getPlan.mockResolvedValue({ ...plan, conflicts: [] });
    render(<App />);
    await selectGame();
    expect(screen.getByText(/已安装 · Steam 更新中/)).toBeTruthy();
    expect(
      (screen.getByText("选择本地 MOD 压缩包") as HTMLButtonElement).disabled,
    ).toBe(true);
    fireEvent.change(screen.getByLabelText("MOD 编号或 Nexus 网址"), {
      target: { value: "42" },
    });
    expect((screen.getByText("查找 MOD") as HTMLButtonElement).disabled).toBe(
      false,
    );
    fireEvent.click(screen.getByText("展开已安装 MOD（1）"));
    fireEvent.click(screen.getByText("展开“示例服装”"));
    expect((screen.getByText("禁用 MOD") as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByText("卸载 MOD") as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByText("展开下载与安装任务（1）"));
    fireEvent.click(screen.getByText("预览安装"));
    await screen.findByText(/安装预览：示例服装/);
    expect((screen.getByText("确认安装") as HTMLButtonElement).disabled).toBe(true);
    expect(mocks.installPlan).not.toHaveBeenCalled();
  });
  it("refreshes a ready task's game after switching to another game", async () => {
    const otherGame = {
      ...game,
      id: "stellar",
      name: "Stellar Blade",
      series: "stellar-blade",
      series_name: "剑星",
    };
    mocks.listGames.mockResolvedValue([
      { ...game, updating: true },
      otherGame,
    ]);
    mocks.getGame.mockResolvedValue({ ...gameView, game: otherGame });
    mocks.getStatus.mockResolvedValue({ ...status, jobs: [job] });
    mocks.getPlan.mockResolvedValue({ ...plan, conflicts: [] });
    const view = render(<App />);
    fireEvent.click(await screen.findByText("展开游戏列表（1）"));
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    fireEvent.click(screen.getByText("选择 Stellar Blade"));
    await screen.findByText("当前游戏：Stellar Blade");
    fireEvent.click(screen.getByText("展开下载与安装任务（1）"));
    fireEvent.click(screen.getByText("预览安装"));
    const install = (await screen.findByText("确认安装")) as HTMLButtonElement;
    expect(install.disabled).toBe(true);

    mocks.listGames.mockResolvedValue([game, otherGame]);
    mocks.visible.mockReturnValue(false);
    view.rerender(<App />);
    mocks.visible.mockReturnValue(true);
    view.rerender(<App />);
    await waitFor(() => expect(install.disabled).toBe(false));
    expect(screen.getByText("当前游戏：Stellar Blade")).toBeTruthy();
    expect(mocks.getGame).not.toHaveBeenCalledWith("re4");
  });
  it("preserves a failed action message when background state succeeds", async () => {
    mocks.bindAccount.mockRejectedValue(new Error("账号无效"));
    const view = render(<App />);
    fireEvent.click(await screen.findByText("展开 Nexus 账号"));
    fireEvent.change(screen.getByLabelText("Nexus API Key"), {
      target: { value: "bad" },
    });
    fireEvent.click(screen.getByText("绑定账号"));
    await screen.findByText("账号无效");
    mocks.visible.mockReturnValue(false);
    view.rerender(<App />);
    mocks.visible.mockReturnValue(true);
    view.rerender(<App />);
    await waitFor(() =>
      expect(mocks.getStatus.mock.calls.length).toBeGreaterThan(1),
    );
    expect(screen.getByText("账号无效")).toBeTruthy();
  });
  it("ignores a stale poll that completes after a successful account action", async () => {
    let releasePoll: ((value: Status) => void) | undefined;
    mocks.bindAccount.mockResolvedValue({
      ...auth,
      connected: true,
      name: "fresh-account",
    });
    const view = render(<App />);
    await screen.findByText("DeckyMods 0.1.0");
    await waitFor(() =>
      expect(mocks.getStatus.mock.calls.length).toBeGreaterThan(1),
    );
    mocks.getStatus.mockImplementationOnce(
      () =>
        new Promise<Status>((resolve) => {
          releasePoll = resolve;
        }),
    );
    mocks.visible.mockReturnValue(false);
    view.rerender(<App />);
    mocks.visible.mockReturnValue(true);
    view.rerender(<App />);
    await waitFor(() => expect(releasePoll).toBeTypeOf("function"));
    fireEvent.click(screen.getByText("展开 Nexus 账号"));
    fireEvent.change(screen.getByLabelText("Nexus API Key"), {
      target: { value: "private" },
    });
    fireEvent.click(screen.getByText("绑定账号"));
    await screen.findByText("fresh-account · 普通会员");
    await act(async () => {
      releasePoll?.(status);
    });
    expect(screen.getByText("fresh-account · 普通会员")).toBeTruthy();
  });
  it("does not duplicate an import when activated twice before the picker resolves", async () => {
    let releasePicker: ((value: { path: string }) => void) | undefined;
    mocks.picker.mockImplementation(
      () =>
        new Promise<{ path: string }>((resolve) => {
          releasePicker = resolve;
        }),
    );
    mocks.importArchive.mockResolvedValue(job);
    render(
      <StrictMode>
        <App />
      </StrictMode>,
    );
    await selectGame();
    const button = screen.getByText("选择本地 MOD 压缩包");
    fireEvent.click(button);
    fireEvent.click(button);
    await waitFor(() => expect(mocks.picker).toHaveBeenCalledOnce());
    await act(async () => {
      releasePicker?.({ path: "/home/deck/Downloads/test.7z" });
    });
    await waitFor(() => expect(mocks.importArchive).toHaveBeenCalledOnce());
  });
  it("treats native picker cancellation as cancellation and permits retry", async () => {
    mocks.picker
      .mockRejectedValueOnce("User canceled")
      .mockResolvedValueOnce({ path: "/home/deck/Downloads/test.rar" });
    mocks.importArchive.mockResolvedValue(job);
    render(<App />);
    await selectGame();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await screen.findByText("选择本地 MOD 压缩包");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(mocks.importArchive).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText("选择本地 MOD 压缩包"));
    await waitFor(() =>
      expect(mocks.importArchive).toHaveBeenCalledWith(
        "re4",
        "/home/deck/Downloads/test.rar",
        "test",
      ),
    );
  });
  it("clears a consumed signed NXM URI even when the download is rejected", async () => {
    mocks.acceptNxm.mockRejectedValue(new Error("NXM 已过期"));
    render(<App />);
    await selectGame();
    const input = screen.getByLabelText(
      "手动接收 NXM 链接（可选）",
    ) as HTMLInputElement;
    fireEvent.change(input, {
      target: { value: "nxm://game/mods/42/files/9?key=private" },
    });
    fireEvent.click(screen.getByText("接收 NXM 下载"));
    await screen.findByText("NXM 已过期");
    expect(input.value).toBe("");
    expect(mocks.acceptNxm).toHaveBeenCalledWith(
      "nxm://game/mods/42/files/9?key=private",
    );
  });
  it("blocks a plan that the adapter marked unsupported", async () => {
    mocks.getStatus.mockResolvedValue({ ...status, jobs: [job] });
    mocks.getPlan.mockResolvedValue({
      ...plan,
      conflicts: [],
      can_install: false,
      blocked_reason: "该安装布局尚未适配",
    });
    render(<App />);
    fireEvent.click(await screen.findByText("展开下载与安装任务（1）"));
    fireEvent.click(screen.getByText("预览安装"));
    await screen.findByText("该安装布局尚未适配");
    expect((screen.getByText("确认安装") as HTMLButtonElement).disabled).toBe(
      true,
    );
    expect(mocks.installPlan).not.toHaveBeenCalled();
  });
  it("searches uninstalled catalog entries while keeping them unselectable", async () => {
    mocks.listGames.mockResolvedValue([
      game,
      {
        ...game,
        id: "stellar",
        name: "Stellar Blade",
        series: "stellar-blade",
        series_name: "剑星",
        installed: false,
      },
    ]);
    render(<App />);
    fireEvent.click(await screen.findByText("展开游戏列表（1）"));
    expect(screen.queryByText("选择 Stellar Blade")).toBeNull();
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    fireEvent.click(screen.getByLabelText("只显示已安装游戏"));
    fireEvent.change(screen.getByLabelText("搜索游戏或系列"), {
      target: { value: "剑星" },
    });
    const stellar = screen.getByText("选择 Stellar Blade") as HTMLButtonElement;
    expect(stellar.disabled).toBe(true);
    expect(screen.queryByText("选择 Resident Evil 4")).toBeNull();
  });

  it("pages a large game catalog and resets pagination when searching", async () => {
    mocks.listGames.mockResolvedValue(
      Array.from({ length: 12 }, (_, index) => ({
        ...game,
        id: `game-${index}`,
        name: `Game ${index}`,
      })),
    );
    render(<App />);
    fireEvent.click(await screen.findByText("展开游戏列表（12）"));
    expect(screen.queryByText("选择 Game 11")).toBeNull();
    fireEvent.click(screen.getByText("下一页游戏"));
    expect(screen.getByText("选择 Game 11")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("搜索游戏或系列"), {
      target: { value: "Game 0" },
    });
    expect(screen.getByText("选择 Game 0")).toBeTruthy();
  });
});
