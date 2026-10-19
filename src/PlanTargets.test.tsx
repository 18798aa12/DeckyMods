import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@decky/ui", () => ({
  PanelSectionRow: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ButtonItem: ({ children, disabled, onClick }: { children: ReactNode; disabled: boolean; onClick: () => void }) => <button disabled={disabled} onClick={onClick}>{children}</button>,
}));
import { PlanTargets } from "./PlanTargets";

afterEach(cleanup);
const targets = Array.from({ length: 121 }, (_, index) => `mods/file-${index + 1}.bin`);

describe("folded installation target preview", () => {
  it("shows nothing when the plan has no target paths", () => {
    const { container } = render(<PlanTargets targets={[]} />);
    expect(container.textContent).toBe("");
  });
  it("keeps paths collapsed until explicitly requested", () => {
    render(<PlanTargets targets={targets} />);
    expect(screen.getByRole("button", { name: "查看安装文件路径（121）" })).toBeTruthy();
    expect(screen.queryByText("游戏根目录/mods/file-1.bin")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（121）" }));
    expect(screen.getByText("游戏根目录/mods/file-1.bin")).toBeTruthy();
    expect(screen.getByText("游戏根目录/mods/file-50.bin")).toBeTruthy();
    expect(screen.queryByText("游戏根目录/mods/file-51.bin")).toBeNull();
    expect((screen.getByRole("button", { name: "上一页文件路径" }) as HTMLButtonElement).disabled).toBe(true);
  });
  it("pages through all paths fifty at a time without dropping the last page", () => {
    render(<PlanTargets targets={targets} />);
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（121）" }));
    fireEvent.click(screen.getByRole("button", { name: "下一页文件路径" }));
    expect(screen.getByText("游戏根目录/mods/file-51.bin")).toBeTruthy();
    expect(screen.getByText("游戏根目录/mods/file-100.bin")).toBeTruthy();
    expect(screen.queryByText("游戏根目录/mods/file-50.bin")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "下一页文件路径" }));
    expect(screen.getByText("游戏根目录/mods/file-101.bin")).toBeTruthy();
    expect(screen.getByText("游戏根目录/mods/file-121.bin")).toBeTruthy();
    expect((screen.getByRole("button", { name: "下一页文件路径" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "上一页文件路径" }));
    expect(screen.getByText("游戏根目录/mods/file-51.bin")).toBeTruthy();
  });
  it("folds and resets pagination when the selected plan changes", () => {
    const rendered = render(<PlanTargets key="plan-one" targets={targets} />);
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（121）" }));
    fireEvent.click(screen.getByRole("button", { name: "下一页文件路径" }));
    rendered.rerender(<PlanTargets key="plan-two" targets={["new/file.bin"]} />);
    expect(screen.getByRole("button", { name: "查看安装文件路径（1）" })).toBeTruthy();
    expect(screen.queryByText("游戏根目录/new/file.bin")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（1）" }));
    expect(screen.getByText("游戏根目录/new/file.bin")).toBeTruthy();
  });
  it("renders arbitrary path characters as plain text", () => {
    const path = '<img src=x onerror="alert(1)">.bin';
    render(<PlanTargets targets={[path]} />);
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（1）" }));
    expect(screen.getByText(`游戏根目录/${path}`)).toBeTruthy();
    expect(document.querySelector("img")).toBeNull();
  });
  it("can collapse a displayed list without leaving file rows visible", () => {
    render(<PlanTargets targets={["mod.bin"]} />);
    fireEvent.click(screen.getByRole("button", { name: "查看安装文件路径（1）" }));
    fireEvent.click(screen.getByRole("button", { name: "收起安装文件路径" }));
    expect(screen.queryByText("游戏根目录/mod.bin")).toBeNull();
  });
});
