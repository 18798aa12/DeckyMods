import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  StrictMode,
  forwardRef,
  type HTMLAttributes,
  type ReactNode,
} from "react";

const { quickAccessVisible } = vi.hoisted(() => ({
  quickAccessVisible: vi.fn(),
}));

interface MockFocusableProps extends HTMLAttributes<HTMLDivElement> {
  readonly children: ReactNode;
  readonly onCancelButton?: unknown;
  readonly onButtonDown?: unknown;
  readonly onGamepadDirection?: unknown;
}

vi.mock("@decky/api", () => ({ useQuickAccessVisible: quickAccessVisible }));
vi.mock("@decky/ui", () => ({
  GamepadButton: { OK: 1, CANCEL: 2 },
  // Steam's QAM can deliver native events without wiring FooterLegend callbacks.
  Focusable: forwardRef<HTMLDivElement, MockFocusableProps>(
    function MockFocusable(
      {
        children,
        onCancelButton: _onCancelButton,
        onButtonDown: _onButtonDown,
        onGamepadDirection: _onGamepadDirection,
        ...props
      },
      ref,
    ) {
      return (
        <div ref={ref} {...props}>
          {children}
        </div>
      );
    },
  ),
}));

import { EditingBoundary } from "./EditingBoundary";

function back(target: HTMLElement, repeat = false): CustomEvent {
  const event = new CustomEvent("vgp_oncancel", {
    bubbles: true,
    cancelable: true,
    detail: { button: 2, is_repeat: repeat },
  });
  fireEvent(target, event);
  return event;
}

beforeEach(() => {
  quickAccessVisible.mockReturnValue(true);
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.resetAllMocks();
});

describe("Steam native QAM back events", () => {
  it("consumes the first native B and allows the second event to reach Decky", () => {
    const view = render(
      <StrictMode>
        <EditingBoundary>
          <button>控制</button>
        </EditingBoundary>
      </StrictMode>,
    );
    const deckyBack = vi.fn();
    view.container.addEventListener("vgp_oncancel", deckyBack);
    const control = screen.getByRole("button", { name: "控制" });
    expect(back(control).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(deckyBack).not.toHaveBeenCalled();
    expect(back(control).defaultPrevented).toBe(false);
    expect(deckyBack).toHaveBeenCalledTimes(1);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
  });

  it("does not let a held B count as a second press", () => {
    const view = render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const deckyBack = vi.fn();
    view.container.addEventListener("vgp_oncancel", deckyBack);
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    expect(back(control, true).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(deckyBack).not.toHaveBeenCalled();
    expect(back(control).defaultPrevented).toBe(false);
    expect(deckyBack).toHaveBeenCalledTimes(1);
  });

  it("ignores a repeat arriving before the first normal B", () => {
    render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    expect(back(control, true).defaultPrevented).toBe(true);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
    expect(back(control).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
  });

  it("treats a focused checkbox as a main-page control rather than a text editor", () => {
    render(
      <EditingBoundary>
        <input type="checkbox" aria-label="代理开关" />
      </EditingBoundary>,
    );
    const control = screen.getByLabelText("代理开关");
    control.focus();
    expect(back(control).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(back(control).defaultPrevented).toBe(false);
  });

  it.each(["input", "textarea"])(
    "uses native B to finish %s editing without clearing its content",
    (kind) => {
      const view = render(
        <EditingBoundary>
          <div data-text-editor tabIndex={0}>
            {kind === "input" ? (
              <input aria-label="编辑内容" defaultValue="我的线路 🇨🇳" />
            ) : (
              <textarea
                aria-label="编辑内容"
                defaultValue="proxies: []\nrules: []\n"
              />
            )}
          </div>
        </EditingBoundary>,
      );
      const deckyBack = vi.fn();
      view.container.addEventListener("vgp_oncancel", deckyBack);
      const editor = screen.getByLabelText("编辑内容") as
        | HTMLInputElement
        | HTMLTextAreaElement;
      const content = editor.value;
      editor.focus();
      expect(back(editor).defaultPrevented).toBe(true);
      expect(document.activeElement).toBe(editor.parentElement);
      expect(editor.value).toBe(content);
      expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
      expect(deckyBack).not.toHaveBeenCalled();
    },
  );

  it("clears the pending exit confirmation when another native button is pressed", () => {
    render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    fireEvent(
      control,
      new CustomEvent("vgp_onbuttondown", {
        bubbles: true,
        detail: { button: 1 },
      }),
    );
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
    expect(back(control).defaultPrevented).toBe(true);
  });

  it("preserves the pending confirmation for native CANCEL buttondown", () => {
    render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    fireEvent(
      control,
      new CustomEvent("vgp_onbuttondown", {
        bubbles: true,
        detail: { button: 2 },
      }),
    );
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(back(control).defaultPrevented).toBe(false);
  });

  it("does not reset confirmation for a neutral native button report", () => {
    render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    fireEvent(
      control,
      new CustomEvent("vgp_onbuttondown", {
        bubbles: true,
        detail: { button: 0 },
      }),
    );
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(back(control).defaultPrevented).toBe(false);
  });

  it("does not disarm the B confirmation for a mirrored keyboard B event", () => {
    render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    fireEvent.keyDown(control, { key: "b", code: "KeyB" });
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(back(control).defaultPrevented).toBe(false);
  });

  it("allows the exit confirmation if Steam restores focus to the just-released input", () => {
    render(
      <EditingBoundary>
        <input
          aria-label="订阅地址"
          defaultValue="https://provider.example/sub"
        />
      </EditingBoundary>,
    );
    const editor = screen.getByLabelText("订阅地址");
    editor.focus();
    expect(back(editor).defaultPrevented).toBe(true);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
    editor.focus();
    expect(back(editor).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    expect(back(editor).defaultPrevented).toBe(false);
  });

  it("finishes a new editing session after actual typing in the same restored input", () => {
    render(
      <EditingBoundary>
        <input aria-label="配置名称" defaultValue="线路" />
      </EditingBoundary>,
    );
    const editor = screen.getByLabelText("配置名称");
    editor.focus();
    back(editor);
    editor.focus();
    fireEvent.input(editor, { target: { value: "线路更新" } });
    expect(back(editor).defaultPrevented).toBe(true);
    expect(document.activeElement).not.toBe(editor);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
  });

  it("allows A to start a new editing session on a previously released input", () => {
    render(
      <EditingBoundary>
        <input aria-label="配置名称" defaultValue="线路" />
      </EditingBoundary>,
    );
    const editor = screen.getByLabelText("配置名称");
    editor.focus();
    back(editor);
    editor.focus();
    fireEvent(
      editor,
      new CustomEvent("vgp_onbuttondown", {
        bubbles: true,
        detail: { button: 1 },
      }),
    );
    expect(back(editor).defaultPrevented).toBe(true);
    expect(document.activeElement).not.toBe(editor);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
  });

  it("requires a fresh two-press confirmation after the QAM hides and reopens", () => {
    const content = (
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>
    );
    const view = render(content);
    const control = screen.getByRole("button", { name: "控制" });
    back(control);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
    quickAccessVisible.mockReturnValue(false);
    view.rerender(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
    expect(back(control).defaultPrevented).toBe(false);
    expect(screen.queryByText("再次按 B 返回 Decky")).toBeNull();
    quickAccessVisible.mockReturnValue(true);
    view.rerender(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    expect(back(control).defaultPrevented).toBe(true);
    expect(screen.getByText("再次按 B 返回 Decky")).toBeTruthy();
  });

  it("removes native listeners and the confirmation timer on true unmount", () => {
    vi.useFakeTimers();
    const view = render(
      <EditingBoundary>
        <button>控制</button>
      </EditingBoundary>,
    );
    const control = screen.getByRole("button", { name: "控制" });
    expect(back(control).defaultPrevented).toBe(true);
    expect(vi.getTimerCount()).toBe(1);
    view.unmount();
    expect(vi.getTimerCount()).toBe(0);
    expect(back(control).defaultPrevented).toBe(false);
  });

  it("does not consume Escape from an old input while the QAM is hidden", () => {
    quickAccessVisible.mockReturnValue(false);
    render(
      <EditingBoundary>
        <input aria-label="订阅地址" />
      </EditingBoundary>,
    );
    const editor = screen.getByLabelText("订阅地址");
    editor.focus();
    expect(fireEvent.keyDown(editor, { key: "Escape" })).toBe(true);
  });
});
