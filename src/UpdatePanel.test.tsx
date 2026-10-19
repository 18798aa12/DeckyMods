import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StrictMode, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { RunAction, UpdateStatus } from "./types";
import { unwrap } from "./state";

const mocks = vi.hoisted(() => ({ getUpdateStatus: vi.fn(), setUpdateOptions: vi.fn(), checkUpdate: vi.fn(), prepareUpdate: vi.fn(), install: vi.fn() }));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("./deckyUpdate", () => ({ requestPluginUpdate: mocks.install }));
vi.mock("@decky/ui", () => ({
  PanelSection: ({ title, children }: { title: string; children: ReactNode }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
  ToggleField: ({ label, checked, disabled, onChange }: { label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) => <label>{label}<input aria-label={label} type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} /></label>,
  TextField: ({ label, value, disabled, onChange }: { label: string; value: string; disabled: boolean; onChange: (event: { target: { value: string } }) => void }) => <label>{label}<input aria-label={label} value={value} disabled={disabled} onChange={onChange} /></label>,
}));
import { UpdatePanel } from "./UpdatePanel";
const status: UpdateStatus = { current_version: "0.1.3", latest_version: null, available: false, checked_at: null, error: null, source: null, auto_check: true, source_label: "尚未配置更新来源" };
const available: UpdateStatus = { ...status, latest_version: "0.2.0", available: true, source: "http://192.168.50.10:8767", source_label: "局域网签名更新" };
const run: RunAction = async (_label, operation, onSuccess) => { const result = await operation(); onSuccess?.(result); return result; };
beforeEach(() => {
  mocks.getUpdateStatus.mockResolvedValue(status);
  mocks.setUpdateOptions.mockImplementation(async (source: string, auto_check: boolean) => ({ ...status, source: source || null, auto_check }));
  mocks.checkUpdate.mockResolvedValue(available);
  mocks.prepareUpdate.mockResolvedValue({ artifact: "file:///tmp/DeckyMods-v0.2.0.zip", version: "0.2.0", sha256: "a".repeat(64) });
  mocks.install.mockResolvedValue(undefined);
});
afterEach(() => { cleanup(); vi.resetAllMocks(); vi.useRealTimers(); });

describe("signed plugin updates", () => {
  it("shows a redacted backend reason instead of hiding every preparation failure", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    mocks.prepareUpdate.mockImplementation(async () => unwrap({ ok: false, error: "游戏正在运行，请退出后重试；token=synthetic-secret" }));
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("可更新至 0.2.0");
    fireEvent.click(screen.getByRole("button", { name: "安装已验证更新" }));
    expect((await screen.findByRole("alert")).textContent).toContain("游戏正在运行，请退出后重试");
    expect(document.body.textContent).not.toContain("synthetic-secret");
    expect(mocks.install).not.toHaveBeenCalled();
  });
  it("clears a failed status read after polling recovers", async () => {
    vi.useFakeTimers();
    mocks.getUpdateStatus.mockRejectedValueOnce(new Error("temporary outage")).mockResolvedValue(available);
    render(<UpdatePanel busy={false} run={run} />);
    await act(async () => { await Promise.resolve(); });
    expect(screen.getByRole("alert").textContent).toContain("无法读取更新状态");
    await act(async () => { await vi.advanceTimersByTimeAsync(30000); });
    expect(screen.getByText("可更新至 0.2.0")).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
  });
  it("unlocks when the shared action guard declines a pending operation", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    const declined: RunAction = async () => null;
    render(<UpdatePanel busy={false} run={declined} />);
    await screen.findByText("可更新至 0.2.0");
    fireEvent.click(screen.getByRole("button", { name: "检查插件更新" }));
    await waitFor(() => expect((screen.getByRole("button", { name: "检查插件更新" }) as HTMLButtonElement).disabled).toBe(false));
  });
  it("ignores a stale StrictMode initial read after a fresher status response", async () => {
    let resolveOld: ((value: UpdateStatus) => void) | undefined;
    mocks.getUpdateStatus.mockImplementationOnce(() => new Promise<UpdateStatus>((resolve) => { resolveOld = resolve; })).mockResolvedValue(available);
    render(<StrictMode><UpdatePanel busy={false} run={run} /></StrictMode>);
    await screen.findByText("可更新至 0.2.0");
    await act(async () => { resolveOld?.(status); });
    expect(screen.getByText("可更新至 0.2.0")).toBeTruthy();
    expect((screen.getByLabelText("更新来源") as HTMLInputElement).value).toBe(available.source);
  });
  it("clearly says unconfigured and checks automatically rather than silently installing", async () => {
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("尚未配置更新来源");
    expect(screen.getByLabelText("自动检查更新（每 6 小时）")).toBeTruthy();
    expect(mocks.prepareUpdate).not.toHaveBeenCalled();
    expect(mocks.install).not.toHaveBeenCalled();
    expect((screen.getByRole("button", { name: "检查插件更新" }) as HTMLButtonElement).disabled).toBe(true);
  });
  it("saves the source then manually checks a signed release", async () => {
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("尚未配置更新来源");
    fireEvent.change(screen.getByLabelText("更新来源"), { target: { value: available.source } });
    fireEvent.click(screen.getByRole("button", { name: "保存更新设置" }));
    await waitFor(() => expect(mocks.setUpdateOptions).toHaveBeenCalledWith(available.source, true));
    fireEvent.click(screen.getByRole("button", { name: "检查插件更新" }));
    await screen.findByText("可更新至 0.2.0");
    expect(mocks.install).not.toHaveBeenCalled();
  });
  it("prepares then opens native confirmation, never reports update complete", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("可更新至 0.2.0");
    fireEvent.click(screen.getByRole("button", { name: "安装已验证更新" }));
    await screen.findByText("已打开 Decky 更新确认窗口，请确认安装；完成后重新打开插件核对版本。");
    expect(mocks.prepareUpdate).toHaveBeenCalledTimes(1);
    expect(mocks.install).toHaveBeenCalledWith(await mocks.prepareUpdate.mock.results[0].value);
    expect(screen.queryByText("更新完成")).toBeNull();
  });
  it("shows checked signature failure without offering install", async () => {
    mocks.getUpdateStatus.mockResolvedValue({ ...available, available: false, error: "更新签名验证失败" });
    render(<UpdatePanel busy={false} run={run} />);
    expect((await screen.findByRole("alert")).textContent).toContain("更新签名验证失败");
    expect(screen.queryByRole("button", { name: "安装已验证更新" })).toBeNull();
  });
  it("does not leak RPC exceptions or open installer after failed preparation", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    mocks.prepareUpdate.mockRejectedValue(new Error("PRIVATE auth token"));
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("可更新至 0.2.0");
    fireEvent.click(screen.getByRole("button", { name: "安装已验证更新" }));
    expect((await screen.findByRole("alert")).textContent).toContain("无法准备已验证的更新");
    expect(document.body.textContent).not.toContain("PRIVATE");
    expect(mocks.install).not.toHaveBeenCalled();
  });
  it("persists the auto-check toggle independently of an unsaved edited source", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    render(<UpdatePanel busy={false} run={run} />);
    await screen.findByText("可更新至 0.2.0");
    fireEvent.change(screen.getByLabelText("更新来源"), { target: { value: "http://192.168.1.4:8767" } });
    fireEvent.click(screen.getByLabelText("自动检查更新（每 6 小时）"));
    await waitFor(() => expect(mocks.setUpdateOptions).toHaveBeenCalledWith(available.source, false));
  });
  it("blocks controls during shared plugin operations", async () => {
    mocks.getUpdateStatus.mockResolvedValue(available);
    render(<UpdatePanel busy={true} run={run} />);
    await screen.findByText("可更新至 0.2.0");
    expect((screen.getByRole("button", { name: "检查插件更新" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "安装已验证更新" }) as HTMLButtonElement).disabled).toBe(true);
  });
  it("refreshes background auto-check status while retaining source edits", async () => {
    vi.useFakeTimers();
    mocks.getUpdateStatus.mockResolvedValueOnce(available).mockResolvedValueOnce({ ...available, latest_version: "0.2.1" });
    render(<UpdatePanel busy={false} run={run} />);
    await act(async () => {});
    fireEvent.change(screen.getByLabelText("更新来源"), { target: { value: "http://192.168.1.4:8767" } });
    await act(async () => { vi.advanceTimersByTime(30000); });
    expect((screen.getByLabelText("更新来源") as HTMLInputElement).value).toBe("http://192.168.1.4:8767");
    expect(screen.getByText("可更新至 0.2.1")).toBeTruthy();
  });
});
