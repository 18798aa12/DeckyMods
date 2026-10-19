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

describe("Resident Evil game selection", () => {
  it("defaults to the actual Resident Evil count and can expose other catalog games", () => {
    render(<GamePanel games={[resident, stellar]} selected="" busy={false} onSelect={vi.fn()} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（1）" }));
    expect((screen.getByLabelText("只显示生化危机") as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText(/生化危机 1 款/)).toBeTruthy();
    expect(screen.getByText("选择 Resident Evil 7")).toBeTruthy();
    expect(screen.queryByText("选择 Stellar Blade")).toBeNull();
    fireEvent.click(screen.getByLabelText("只显示生化危机"));
    expect(screen.getByText("选择 Stellar Blade")).toBeTruthy();
    expect(screen.getByText(/已收录 2 个系列/)).toBeTruthy();
  });
  it("retains installed-only safety while viewing every Resident Evil catalog entry", () => {
    render(<GamePanel games={[resident, { ...resident, id: "re0", name: "RE0", installed: false }, stellar]} selected="" busy={false} onSelect={vi.fn()} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "展开游戏列表（2）" }));
    expect(screen.queryByText("选择 RE0")).toBeNull();
    fireEvent.click(screen.getByLabelText("只显示已安装游戏"));
    expect((screen.getByText("选择 RE0") as HTMLButtonElement).disabled).toBe(true);
    expect(screen.queryByText("选择 Stellar Blade")).toBeNull();
  });
});
