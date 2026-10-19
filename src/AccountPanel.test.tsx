import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Auth, Handler, RunAction } from "./types";

const mocks = vi.hoisted(() => ({ bindAccount: vi.fn(), disconnectAccount: vi.fn(), setNxmHandler: vi.fn(), external: vi.fn() }));
vi.mock("./rpc", () => ({ backend: mocks }));
vi.mock("@decky/ui", () => ({
  Navigation: { NavigateToExternalWeb: mocks.external },
  PanelSection: ({ children }: { children: ReactNode }) => <section>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
  TextField: ({ label, value, disabled, bIsPassword, onChange }: { label: string; value: string; disabled: boolean; bIsPassword: boolean; onChange: React.ChangeEventHandler<HTMLInputElement> }) => <label>{label}<input aria-label={label} type={bIsPassword ? "password" : "text"} value={value} disabled={disabled} onChange={onChange} /></label>,
  ToggleField: ({ label, checked, disabled, onChange }: { label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) => <label>{label}<input aria-label={label} type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} /></label>,
}));
import { AccountPanel } from "./AccountPanel";
const auth: Auth = { connected: false, name: null, premium: false, user_id: null, error: null };
const connected: Auth = { ...auth, connected: true, name: "玩家", user_id: 1 };
const handler: Handler = { enabled: false, supported: true, previous: null, message: null };
const run: RunAction = async (_label, operation, onSuccess) => { const result = await operation(); onSuccess?.(result); return result; };
const renderPanel = (account = auth, onAuth = vi.fn()) => render(<AccountPanel auth={account} handler={handler} busy={false} run={run} onAuth={onAuth} onHandler={vi.fn()} />);
const expand = () => fireEvent.click(screen.getByRole("button", { name: "展开 Nexus 账号" }));
beforeEach(() => { mocks.bindAccount.mockResolvedValue(connected); });
afterEach(() => { cleanup(); vi.resetAllMocks(); });

describe("Nexus personal API key help", () => {
  it("keeps account controls folded and local import available without binding", () => {
    renderPanel();
    expect(screen.getByText("未绑定 Nexus 账号 · 本地压缩包无需登录")).toBeTruthy();
    expect(screen.queryByLabelText("Nexus API Key")).toBeNull();
    expect(screen.queryByRole("button", { name: "打开 Nexus API Key 设置" })).toBeNull();
  });
  it("opens the official API Access account tab using the exact working URL", async () => {
    renderPanel(); expand();
    fireEvent.click(screen.getByRole("button", { name: "打开 Nexus API Key 设置" }));
    await waitFor(() => expect(mocks.external).toHaveBeenCalledWith("https://www.nexusmods.com/users/myaccount?tab=api%20access"));
  });
  it("explains ordinary membership, the personal key section, and downloading without binding", () => {
    renderPanel(); expand();
    expect(document.body.textContent).toContain("普通会员也可使用个人 API Key");
    expect(document.body.textContent).toContain("API Access");
    expect(document.body.textContent).toContain("Personal API Key");
    expect(document.body.textContent).toContain("生成或显示个人密钥");
    expect(document.body.textContent).toContain("已授权应用");
    expect(document.body.textContent).toContain("继续往下找");
    expect(document.body.textContent).toContain("不绑定也可在网页下载后导入本地压缩包");
  });
  it("submits a trimmed key and clears the masked input after successful binding", async () => {
    const onAuth = vi.fn();
    renderPanel(auth, onAuth); expand();
    const input = screen.getByLabelText("Nexus API Key") as HTMLInputElement;
    expect(input.type).toBe("password");
    fireEvent.change(input, { target: { value: "  sample-personal-key  " } });
    fireEvent.click(screen.getByRole("button", { name: "绑定账号" }));
    await waitFor(() => expect(mocks.bindAccount).toHaveBeenCalledWith("sample-personal-key"));
    expect(onAuth).toHaveBeenCalledWith(connected);
    expect(input.value).toBe("");
  });
  it("never fills or renders a stored key from account status", () => {
    const statusWithUnexpectedField = { ...connected, api_key: "stored-secret-sentinel" };
    renderPanel(statusWithUnexpectedField); expand();
    expect((screen.getByLabelText("Nexus API Key") as HTMLInputElement).value).toBe("");
    expect(document.body.textContent).not.toContain("stored-secret-sentinel");
    expect(document.querySelector('[value="stored-secret-sentinel"]')).toBeNull();
    expect(mocks.bindAccount).not.toHaveBeenCalled();
  });
});
