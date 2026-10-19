import { Focusable, GamepadButton, type GamepadEvent } from "@decky/ui";
import { useQuickAccessVisible } from "@decky/api";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { styles } from "./styles";

interface CancelEvent {
  preventDefault(): void;
  stopPropagation(): void;
}

export function EditingBoundary({
  children,
}: {
  readonly children: ReactNode;
}) {
  const boundary = useRef<HTMLDivElement>(null);
  const releasedEditor = useRef<Element | null>(null);
  const deadline = useRef(0);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [confirmExit, setConfirmExit] = useState(false);
  const visible = useQuickAccessVisible();

  const resetExit = useCallback((): void => {
    clearTimeout(timer.current);
    timer.current = undefined;
    deadline.current = 0;
    setConfirmExit(false);
  }, []);

  useEffect(
    () => () => {
      clearTimeout(timer.current);
    },
    [],
  );
  useEffect(() => {
    if (!visible) resetExit();
  }, [visible, resetExit]);

  const finishEditing = useCallback(
    (event: CancelEvent): boolean => {
      const editing = document.activeElement;
      if (
        !(
          editing instanceof HTMLInputElement ||
          editing instanceof HTMLTextAreaElement
        ) ||
        !boundary.current?.contains(editing) ||
        releasedEditor.current === editing
      )
        return false;
      if (
        editing.disabled ||
        editing.readOnly ||
        (editing instanceof HTMLInputElement &&
          ![
            "text",
            "password",
            "url",
            "search",
            "email",
            "tel",
            "number",
          ].includes(editing.type))
      )
        return false;
      event.preventDefault();
      event.stopPropagation();
      resetExit();
      // Steam may restore the same input's DOM focus after blur. It must not
      // trap every subsequent B as another request to finish the same edit.
      releasedEditor.current = editing;
      editing.blur();
      (
        editing.closest<HTMLElement>("[data-text-editor]") ?? boundary.current
      ).focus();
      return true;
    },
    [resetExit],
  );

  const handleBack = useCallback(
    (event: Event): void => {
      if ((event as GamepadEvent).detail?.is_repeat) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      if (finishEditing(event)) return;
      if (deadline.current > Date.now()) {
        resetExit();
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      clearTimeout(timer.current);
      deadline.current = Date.now() + 2000;
      setConfirmExit(true);
      timer.current = setTimeout(resetExit, 2000);
    },
    [finishEditing, resetExit],
  );

  useEffect(() => {
    if (!visible) return;
    const element = boundary.current;
    const buttonDown = (event: Event): void => {
      const button = (event as GamepadEvent).detail?.button;
      if (button === GamepadButton.OK) releasedEditor.current = null;
      if (
        typeof button === "number" &&
        button > 0 &&
        button !== GamepadButton.CANCEL
      )
        resetExit();
    };
    // QAM does not reliably wire FooterLegend callbacks on wrapper Focusables.
    // Listen to Steam's native bubbling event, without registering another
    // cancel callback that could consume the second B before Decky sees it.
    element?.addEventListener("vgp_oncancel", handleBack);
    element?.addEventListener("vgp_onbuttondown", buttonDown);
    return () => {
      element?.removeEventListener("vgp_oncancel", handleBack);
      element?.removeEventListener("vgp_onbuttondown", buttonDown);
    };
  }, [handleBack, resetExit, visible]);

  return (
    <Focusable
      ref={boundary}
      tabIndex={-1}
      onClickCapture={resetExit}
      onPointerDownCapture={() => {
        releasedEditor.current = null;
        resetExit();
      }}
      onInputCapture={() => {
        releasedEditor.current = null;
        resetExit();
      }}
      onKeyDownCapture={(event) => {
        if (
          visible &&
          !["Escape", "BrowserBack", "GoBack", "b", "B"].includes(event.key)
        )
          resetExit();
      }}
      onKeyDown={(event) => {
        if (visible && event.key === "Escape") finishEditing(event);
      }}
    >
      {confirmExit && (
        <div role="status" aria-live="polite" style={styles.backHint}>
          再次按 B 返回 Decky
        </div>
      )}
      {children}
    </Focusable>
  );
}
