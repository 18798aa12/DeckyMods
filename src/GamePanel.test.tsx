import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Game } from "./types";

vi.mock("@decky/ui", () => ({
  PanelSection: ({ title, children }: { title: string; children: ReactNode }) => <section aria-label={title}>{children}</section>,
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
  ToggleField: ({ label, checked, disabled, onChange }: { label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) => <label>{label}<input aria-label={label} type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} /></label>,
  TextField: ({ label, value, onChange }: { label: string; value: string; onChange: React.ChangeEventHandler<HTMLInputElement> }) => <input aria-label={label} value={value} onChange={onChange} />,
}));
import { GamePanel } from "./GamePanel";

const resident: Game = {
  id: "residentevil7", name: "Resident Evil 7", series: "resident-evil", series_name: "生化危机",
  nexus_domain: "residentevil7", steam_app_ids: ["418370"], adapter: "reframework",
  support: "needs_setup", requirements: [], sources: [], installed: true,
  path: "/games/re7", app_id: "418370", build_id: "22773795", running: false,
};
const stellar: Game = { ...resident, id: "stellarblade", name: "Stellar Blade", series: "stellar-blade", series_name: "剑星" };
afterEach(cleanup);

describe("installed Steam game selection", () => {
  it("defaults to every installed game and keeps the list folded", () => {
    render(<GamePanel games={[resident, stellar, { ...stellar, id: "missing", name: "未安装游戏", installed: false }]} selected="" busy={false} onSelect={vi.fn()} onRefresh={vi.fn()} />);
    expect(screen.queryByText("选择 Stellar Blade")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（2）" }));
    expect((screen.getByLabelText("只显示生化危机") as HTMLInputElement).checked).toBe(false);
    expect((screen.getByLabelText("只显示已安装游戏") as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText("选择 Resident Evil 7")).toBeTruthy();
    expect(screen.getByText("选择 Stellar Blade")).toBeTruthy();
    expect(screen.queryByText("选择 未安装游戏")).toBeNull();
    expect(screen.getByText("当前筛选匹配 2 个游戏 · 已安装 2 个")).toBeTruthy();
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    expect(screen.queryByText("选择 Stellar Blade")).toBeNull();
    expect(screen.getByText("当前筛选匹配 1 个游戏 · 已安装 1 个")).toBeTruthy();
  });
  it("shows only applicable empty-filter guidance", () => {
    render(<GamePanel games={[stellar]} selected="" busy={false} onSelect={vi.fn()} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    expect(screen.getByText(/关闭“只显示生化危机”可查看其他游戏/)).toBeTruthy();
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    fireEvent.change(screen.getByLabelText("搜索游戏或系列"), { target: { value: "不存在" } });
    expect(screen.getByText(/请修改搜索词/)).toBeTruthy();
    expect(screen.queryByText(/关闭“只显示生化危机”可查看其他游戏/)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "收起游戏列表" }));
    expect(screen.getByRole("button", { name: "展开游戏列表（0）" })).toBeTruthy();
  });
  it("permits selecting discovered unmapped games and uninstalled catalog entries", () => {
    const onSelect = vi.fn();
    const unknown: Game = { ...stellar, id: "steam-2358720", name: "Black Myth: Wukong", nexus_domain: "", adapter: "catalog", support: "catalog" };
    render(<GamePanel games={[resident, unknown, { ...unknown, id: "missing", name: "手动游戏", installed: false }]} selected="" busy={false} onSelect={onSelect} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（2）" }));
    fireEvent.click(screen.getByText("选择 Black Myth: Wukong"));
    expect(onSelect).toHaveBeenCalledWith("steam-2358720");
    fireEvent.click(screen.getByLabelText("只显示已安装游戏"));
    expect((screen.getByText("选择 手动游戏") as HTMLButtonElement).disabled).toBe(false);
    expect(screen.getAllByText(/可手动按作者目录安装/)).toHaveLength(2);
  });
});
