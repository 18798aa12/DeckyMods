import { act, cleanup, fireEvent, screen } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";
import { forwardRef, type ReactNode } from "react";
import type { Auth, Game, GameView, Job, Plan, Status } from "../types";

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
vi.mock("../rpc", () => ({ backend: mocks }));
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

export { mocks, auth, game, gameView, job, plan, status, selectGame };
