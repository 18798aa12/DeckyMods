const MAX_COMMAND_BYTES = 16 * 1024;
const RETRY_DELAY_MS = 100;
const READ_ATTEMPTS = 5;
const VERIFY_ATTEMPTS = 20;

type DetailsStore = {
  GetAppDetails: (appId: number) => unknown;
};

type NativeApps = {
  SetAppLaunchOptions: (appId: number, command: string) => unknown;
};

type SteamWindow = {
  appDetailsStore?: Partial<DetailsStore>;
  SteamClient?: { Apps?: Partial<NativeApps> };
};

function numericAppId(appId: string): number {
  if (
    typeof appId !== "string" ||
    !/^[1-9]\d{0,9}$/.test(appId) ||
    Number(appId) > 0xffffffff
  ) {
    throw new Error("游戏编号无效，无法读取 Steam 启动选项。");
  }
  return Number(appId);
}

function validateCommand(command: string): void {
  if (
    typeof command !== "string" ||
    /[\0\r\n]/.test(command) ||
    command.length > MAX_COMMAND_BYTES ||
    new TextEncoder().encode(command).byteLength > MAX_COMMAND_BYTES
  ) {
    throw new Error("启动选项格式无效：不得包含换行、空字符或超过 16 KiB。");
  }
}

function steamWindow(): SteamWindow {
  if (typeof window === "undefined") {
    throw new Error("Steam 界面尚未就绪，请在游戏模式中打开插件后重试。");
  }
  return window as unknown as SteamWindow;
}

function detailsStore(): DetailsStore {
  const store = steamWindow().appDetailsStore;
  if (!store || typeof store.GetAppDetails !== "function") {
    throw new Error("无法连接 Steam 游戏详情，请打开游戏详情页后重试。");
  }
  return store as DetailsStore;
}

function readCachedOptions(store: DetailsStore, appId: number): string | null {
  let details: unknown;
  try {
    details = store.GetAppDetails(appId);
  } catch {
    throw new Error("无法读取 Steam 启动选项，请打开游戏详情页后重试。");
  }
  if (
    typeof details !== "object" ||
    details === null ||
    !("strLaunchOptions" in details) ||
    typeof details.strLaunchOptions !== "string"
  ) {
    return null;
  }
  validateCommand(details.strLaunchOptions);
  return details.strLaunchOptions;
}

async function delay(): Promise<void> {
  await new Promise<void>((resolve) => setTimeout(resolve, RETRY_DELAY_MS));
}

/** Read Steam's actual custom options; an unavailable value is never empty. */
export async function readLaunchOptions(appId: string): Promise<string> {
  const numericId = numericAppId(appId);
  const store = detailsStore();
  for (let attempt = 0; attempt < READ_ATTEMPTS; attempt += 1) {
    const command = readCachedOptions(store, numericId);
    if (command !== null) return command;
    if (attempt < READ_ATTEMPTS - 1) await delay();
  }
  throw new Error("Steam 尚未提供启动选项，请打开该游戏的详情页后重试。");
}

/** Compare before writing; merging and a durable backup belong to the caller. */
export async function writeLaunchOptions(
  appId: string,
  before: string,
  after: string,
): Promise<string> {
  const numericId = numericAppId(appId);
  validateCommand(before);
  validateCommand(after);
  const current = await readLaunchOptions(appId);
  if (current !== before) {
    throw new Error("Steam 启动选项已变化，请刷新后重新检查，已保留当前设置。");
  }
  if (before === after) return current;

  const apps = steamWindow().SteamClient?.Apps;
  if (!apps || typeof apps.SetAppLaunchOptions !== "function") {
    throw new Error("Steam 启动选项写入接口不可用，请在游戏模式中重试。");
  }
  try {
    const result = await apps.SetAppLaunchOptions(numericId, after);
    if (result === false) throw new Error("Native setter rejected the change.");
  } catch {
    throw new Error("Steam 未能保存启动选项，请检查该游戏的启动选项后重试。");
  }

  const store = detailsStore();
  for (let attempt = 0; attempt < VERIFY_ATTEMPTS; attempt += 1) {
    const observed = readCachedOptions(store, numericId);
    if (observed === after) return observed;
    if (observed !== null && observed !== before) {
      throw new Error("启动选项出现其他改动，已停止自动写入，请检查 Steam 设置。");
    }
    if (attempt < VERIFY_ATTEMPTS - 1) await delay();
  }
  throw new Error("无法确认 Steam 已保存启动选项，请检查该游戏的设置后刷新。");
}
