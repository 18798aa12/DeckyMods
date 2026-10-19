import { backend } from "./rpc";
import { readLaunchOptions, writeLaunchOptions } from "./steamLaunch";
import type { LaunchSetup } from "./types";

export interface LaunchOutcome {
  readonly setup: LaunchSetup;
  readonly configured: boolean;
  readonly restored: boolean;
}

// Steam exposes process-wide state. Serialize operations, including reads and the
// backend intent journal, so another panel cannot interleave a command update.
let queue: Promise<void> = Promise.resolve();
const inFlight = new Map<string, Promise<LaunchOutcome>>();

async function synchronize(gameId: string, restore: boolean): Promise<LaunchOutcome> {
  const setup = await backend.getLaunchSetup(gameId).catch(() => {
    throw new Error("无法读取启动项要求，请重新检查；若仍失败，请重新打开 DeckyMods。");
  });
  if (!restore && (!setup.supported || !setup.required || !setup.auto_enabled)) {
    return { setup, configured: false, restored: false };
  }
  if (!setup.app_id || (!restore && !setup.supported)) {
    throw new Error("未识别可配置的 Steam 游戏，请重新扫描游戏。");
  }
  const before = await readLaunchOptions(setup.app_id).catch(() => {
    throw new Error("无法读取 Steam 启动项，请先在 Steam 打开该游戏详情页，然后重试。");
  });
  const change = await backend.prepareLaunchOptions(gameId, before, restore).catch(() => {
    throw new Error(restore
      ? "无法安全恢复启动项：若自动配置后又改过启动项，插件会保留新设置并阻止恢复。请退出游戏、等待更新完成后，在 Steam 属性中核对；原始备份仍保留。"
      : "无法安全合并启动项，请先退出游戏、等待 Steam 更新完成；复杂或重复命令需要手动核对。");
  });
  if (change.app_id !== setup.app_id || change.before !== before) {
    throw new Error("Steam 游戏或启动项已变化，请重新扫描后重试。");
  }
  if (!change.changed) {
    const latest = await backend.getLaunchSetup(gameId).catch(() => {
      throw new Error("最新启动项状态读取失败，请重新检查启动项。");
    });
    return { setup: latest, configured: !restore, restored: restore };
  }
  const observed = await writeLaunchOptions(change.app_id, before, change.after).catch(() => {
    throw new Error("Steam 启动项写入未确认，请重新检查；原始设置已备份，不要在操作期间编辑启动项。");
  });
  if (observed !== change.after) {
    throw new Error("Steam 返回的启动项不一致，请重新检查；不会继续覆盖。");
  }
  const confirmed = await backend.finishLaunchOptions(gameId, change.id, observed).catch(() => {
    throw new Error("启动项已提交，但记录确认失败。请重新检查，暂时不要手动编辑启动项。");
  });
  return { setup: confirmed, configured: !restore, restored: restore };
}

export function synchronizeLaunchOptions(gameId: string, restore = false): Promise<LaunchOutcome> {
  const key = `${gameId}:${restore ? "restore" : "merge"}`;
  const existing = inFlight.get(key);
  if (existing) return existing;
  const task = queue.then(() => synchronize(gameId, restore));
  queue = task.then(() => undefined, () => undefined);
  inFlight.set(key, task);
  void task.finally(() => {
    if (inFlight.get(key) === task) inFlight.delete(key);
  }).catch(() => undefined); // The caller receives the original rejection.
  return task;
}
