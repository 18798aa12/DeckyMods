import { useState } from "react";
import { Action, Note } from "./controls";

const PAGE_SIZE = 50;
interface Props {
  readonly targets: readonly string[];
}
export function PlanTargets({ targets }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [page, setPage] = useState(0);
  if (targets.length === 0) return null;
  const pages = Math.ceil(targets.length / PAGE_SIZE);
  const current = Math.min(page, pages - 1);
  const start = current * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, targets.length);
  return (
    <>
      <Action onClick={() => {
        setExpanded(!expanded);
        setPage(0);
      }}>
        {expanded ? "收起安装文件路径" : `查看安装文件路径（${targets.length}）`}
      </Action>
      {expanded && (
        <>
          <Note>第 {current + 1} / {pages} 页 · 文件 {start + 1}–{end} / {targets.length}</Note>
          {targets.slice(start, end).map((path, index) => (
            <Note key={`${start + index}:${path}`}>游戏根目录/{path}</Note>
          ))}
          <Action disabled={current === 0} onClick={() => setPage(current - 1)}>
            上一页文件路径
          </Action>
          <Action disabled={current + 1 === pages} onClick={() => setPage(current + 1)}>
            下一页文件路径
          </Action>
        </>
      )}
    </>
  );
}
