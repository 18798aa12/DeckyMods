import { Navigation } from "@decky/ui";
import type { Game, Job, Result } from "./types";
export function safeError(error: unknown): string {
  const value =
    error instanceof Error
      ? error.message
      : typeof error === "string"
        ? error
        : "操作失败，请稍后重试。";
  return value
    .replace(/(?:https?|nxm):\/\/[^\s<>"']+/gi, "[已隐藏地址]")
    .replace(
      /(api[_ -]?key|key|token|signature)\s*[:=]\s*[^\s,;]+/gi,
      "$1 [已隐藏]",
    )
    .slice(0, 500);
}
export function unwrap<T>(result: Result<T>): T {
  if (!result.ok) throw new Error(safeError(result.error));
  return result.data;
}
export function capability(game: Game): string {
  return game.support === "automatic"
    ? "已实现格式适配 · 未实机验证"
    : game.support === "needs_setup"
      ? "需要额外加载器或设置"
      : "可手动按作者目录安装";
}
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return "未知";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / 1048576).toFixed(1)} MiB`;
}
export function mergeJob(jobs: readonly Job[], next: Job): readonly Job[] {
  return [next, ...jobs.filter((job) => job.id !== next.id)];
}
export function openNexus(url: string): void {
  const parsed = new URL(url);
  if (
    parsed.protocol !== "https:" ||
    !["nexusmods.com", "www.nexusmods.com", "users.nexusmods.com"].includes(
      parsed.hostname,
    ) ||
    parsed.username ||
    parsed.password
  )
    throw new Error("无法打开非 Nexus 官方网页。");
  Navigation.NavigateToExternalWeb(parsed.href);
}
