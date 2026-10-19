import { ButtonItem, PanelSectionRow } from "@decky/ui";
import type { ReactNode } from "react";
import { styles } from "./styles";
export function Action({
  children,
  disabled = false,
  onClick,
}: {
  readonly children: ReactNode;
  readonly disabled?: boolean;
  readonly onClick: () => void;
}) {
  return (
    <PanelSectionRow>
      <ButtonItem layout="below" disabled={disabled} onClick={onClick}>
        {children}
      </ButtonItem>
    </PanelSectionRow>
  );
}
export function Note({ children }: { readonly children: ReactNode }) {
  return (
    <PanelSectionRow>
      <div style={styles.note}>{children}</div>
    </PanelSectionRow>
  );
}
