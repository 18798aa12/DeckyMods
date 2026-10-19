import type { CSSProperties } from "react";

export const styles = {
  status: {
    padding: "12px 14px",
    background: "#202A35",
    borderLeft: "3px solid #1A9FFF",
    borderRadius: 3,
    marginBottom: 6,
  } satisfies CSSProperties,
  statusName: {
    fontSize: 19,
    fontWeight: 700,
    marginBottom: 5,
  } satisfies CSSProperties,
  detail: {
    fontSize: 12,
    lineHeight: 1.6,
    color: "#BAC8D6",
    overflowWrap: "anywhere",
  } satisfies CSSProperties,
  error: {
    padding: "9px 14px",
    marginBottom: 8,
    color: "#F5A7AE",
    background: "#35272E",
    fontSize: 13,
    lineHeight: 1.5,
    overflowWrap: "anywhere",
  } satisfies CSSProperties,
  notice: {
    padding: "6px 14px",
    color: "#67D9BF",
    fontSize: 12,
    lineHeight: 1.5,
  } satisfies CSSProperties,
  backHint: {
    position: "sticky",
    top: 0,
    zIndex: 2,
    padding: "10px 14px",
    color: "#67D9BF",
    background: "#202A35",
    fontSize: 13,
    lineHeight: 1.5,
    pointerEvents: "none",
  } satisfies CSSProperties,
  note: {
    fontSize: 12,
    color: "#BAC8D6",
    lineHeight: 1.6,
    margin: "4px 0 10px",
    overflowWrap: "anywhere",
  } satisfies CSSProperties,
};
