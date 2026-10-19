import {
  PanelSection,
  PanelSectionRow,
  TextField,
  ToggleField,
} from "@decky/ui";
import { useState } from "react";
import { Action, Note } from "./controls";
import { capability } from "./state";
import type { Game } from "./types";
interface Props {
  readonly games: readonly Game[];
  readonly selected: string;
  readonly busy: boolean;
  readonly onSelect: (id: string) => void;
  readonly onRefresh: () => void;
}
export function GamePanel({
  games,
  selected,
  busy,
  onSelect,
  onRefresh,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [installedOnly, setInstalledOnly] = useState(true);
  const [residentOnly, setResidentOnly] = useState(false);
  const scoped = residentOnly
    ? games.filter((game) => game.series === "resident-evil")
    : games;
  const filtered = scoped.filter(
    (game) =>
      (!installedOnly || game.installed) &&
      `${game.name} ${game.series_name} ${game.series} ${game.nexus_domain}`
        .toLocaleLowerCase()
        .includes(query.trim().toLocaleLowerCase()),
  );
  const pageCount = Math.max(1, Math.ceil(filtered.length / 10));
  const currentPage = Math.min(page, pageCount - 1);
  const pageGames = filtered.slice(currentPage * 10, currentPage * 10 + 10);
  return (
    <PanelSection title="选择游戏">
      <Note>
        当前筛选匹配 {filtered.length} 个游戏 · 已安装 {filtered.filter((game) => game.installed).length} 个
      </Note>
      <Action onClick={() => setExpanded(!expanded)}>
        {expanded ? "收起游戏列表" : `展开游戏列表（${filtered.length}）`}
      </Action>
      {expanded && (
        <>
          <PanelSectionRow>
            <TextField
              label="搜索游戏或系列"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setPage(0);
              }}
            />
          </PanelSectionRow>
          <PanelSectionRow>
            <ToggleField
              label="只显示生化危机"
              checked={residentOnly}
              onChange={(enabled) => {
                setResidentOnly(enabled);
                setPage(0);
              }}
            />
          </PanelSectionRow>
          <PanelSectionRow>
            <ToggleField
              label="只显示已安装游戏"
              checked={installedOnly}
              onChange={(enabled) => {
                setInstalledOnly(enabled);
                setPage(0);
              }}
            />
          </PanelSectionRow>
          {filtered.length === 0 && (
            <Note>
              未找到匹配游戏。
              {query.trim() && "请修改搜索词。"}
              {residentOnly && "关闭“只显示生化危机”可查看其他游戏。"}
              {installedOnly && "关闭“只显示已安装游戏”可查看目录。"}
              {!residentOnly && !query.trim() && "若游戏已安装，请重新扫描 Steam 游戏。"}
            </Note>
          )}
          {pageGames.map((game) => (
            <div key={game.id}>
              <Action
                disabled={busy || (!game.installed && game.adapter !== "catalog")}
                onClick={() => onSelect(game.id)}
              >
                {selected === game.id ? "当前：" : "选择 "}
                {game.name}
              </Action>
              <Note>
                {game.series_name} ·{" "}
                {game.installed ? "已安装" : "未检测到安装"}
                {game.updating && " · Steam 更新中"}
                <br />
                {capability(game)}
                {game.requirements.length > 0 && (
                  <>
                    <br />
                    {game.requirements.join("；")}
                  </>
                )}
              </Note>
            </div>
          ))}
          {pageCount > 1 && (
            <>
              <Note>
                第 {currentPage + 1} / {pageCount} 页 · 匹配 {filtered.length}{" "}
                个游戏
              </Note>
              <Action
                disabled={currentPage === 0}
                onClick={() => setPage(currentPage - 1)}
              >
                上一页游戏
              </Action>
              <Action
                disabled={currentPage + 1 === pageCount}
                onClick={() => setPage(currentPage + 1)}
              >
                下一页游戏
              </Action>
            </>
          )}
          <Action disabled={busy} onClick={onRefresh}>
            重新扫描 Steam 游戏
          </Action>
        </>
      )}
    </PanelSection>
  );
}
