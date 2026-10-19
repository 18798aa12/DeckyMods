import {
  FileSelectionType,
  openFilePicker,
  useQuickAccessVisible,
} from "@decky/api";
import {
  DropdownItem,
  Focusable,
  PanelSection,
  PanelSectionRow,
  TextField,
  ToggleField,
} from "@decky/ui";
import { useEffect, useRef, useState } from "react";
import { backend } from "./rpc";
import { Action, Note } from "./controls";
import { InstallGuidePanel } from "./InstallGuidePanel";
import { capability, formatBytes, openNexus, safeError } from "./state";
import type { Game, GameView, InstallMode, Job, NexusMod, RunAction } from "./types";
interface Props {
  readonly game: Game;
  readonly busy: boolean;
  readonly run: RunAction;
  readonly onJob: (job: Job) => void;
  readonly onView?: (view: GameView) => void;
}
export function SourcePanel(props: Props) {
  const game = props.game;
  const identity = JSON.stringify([game.id, game.installed, game.path, game.app_id, game.build_id, game.adapter, game.nexus_domain]);
  return <SourceDetails key={identity} {...props} />;
}
function SourceDetails({ game, busy, run, onJob, onView }: Props) {
  const [reference, setReference] = useState("");
  const [nxm, setNxm] = useState("");
  const [mod, setMod] = useState<NexusMod | null>(null);
  const [file, setFile] = useState<number | null>(null);
  const [picking, setPicking] = useState<"archive" | "root" | "auto" | null>(null);
  const [rootInstall, setRootInstall] = useState(false);
  const [methodMode, setMethodMode] = useState<InstallMode>("auto");
  const pickerLock = useRef(false);
  const fileControl = useRef<HTMLDivElement>(null);
  const restoreFocus = useRef(false);
  const mounted = useRef(true);
  const visible = useQuickAccessVisible();
  const writeBlocked = busy || game.running || Boolean(game.updating);
  const hasNexusMapping = Boolean(game.nexus_domain.trim());
  const installBlocked = writeBlocked || Boolean(picking) || !game.installed ||
    !game.path?.startsWith("/") || Boolean(game.root_error) ||
    (!hasNexusMapping && game.adapter === "catalog" && !rootInstall && methodMode === "auto");
  const useGameRoot = game.adapter === "catalog" && rootInstall;
  const installMode: InstallMode = useGameRoot ? "game_root" : methodMode;
  useEffect(() => {
    setRootInstall(false);
    setMod(null);
    setFile(null);
    setReference("");
    setNxm("");
  }, [game.id, game.adapter, game.nexus_domain]);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  useEffect(() => {
    if (visible && !picking && restoreFocus.current) {
      restoreFocus.current = false;
      fileControl.current?.focus();
    }
  }, [picking, visible]);
  const finishSelection = (): void => {
    pickerLock.current = false;
    if (mounted.current) {
      restoreFocus.current = true;
      setPicking(null);
    }
  };
  const chooseRoot = async (mode: "auto" | "manual"): Promise<void> => {
    if (writeBlocked || pickerLock.current) return;
    pickerLock.current = true;
    setPicking(mode === "auto" ? "auto" : "root");
    try {
      await run("游戏目录已更新", async () => {
        if (mode === "auto") return backend.setGameRoot(game.id, "auto");
        const directory = game.path || await backend.getImportDirectory();
        if (!mounted.current) return null;
        if (typeof directory !== "string" || !directory.startsWith("/"))
          throw new Error("无法读取目录，请重新扫描游戏或重试。");
        let selected: { path: string };
        try {
          selected = await openFilePicker(
            FileSelectionType.FOLDER, directory, false, true,
            undefined, undefined, false, false,
          );
        } catch (caught) {
          if (caught === "User canceled") return null;
          throw caught;
        }
        if (!mounted.current) return null;
        if (!selected || typeof selected.path !== "string" || !selected.path.startsWith("/"))
          throw new Error("请选择具体的游戏根目录。");
        return backend.setGameRoot(game.id, "manual", selected.path);
      }, (next) => {
        if (next && mounted.current) onView?.(next);
      });
    } finally {
      finishSelection();
    }
  };
  const lookup = (): void => {
    if (!hasNexusMapping) return;
    void run(
      "已获取 MOD 信息",
      () => backend.resolveMod(game.id, reference.trim()),
      (next) => {
        setMod(next);
        setFile(next.files.length === 1 ? next.files[0].file_id : null);
      },
    );
  };
  const download = (): void => {
    if (!hasNexusMapping || installBlocked || !mod || file === null) return;
    void run(
      "下载任务已创建",
      () => installMode !== "auto"
        ? backend.beginDownload(game.id, mod.mod_id, file, installMode)
        : backend.beginDownload(game.id, mod.mod_id, file),
      (job) => {
        onJob(job);
        if (job.browser_url) openNexus(job.browser_url);
      },
    );
  };
  const importFile = async (): Promise<void> => {
    if (installBlocked || pickerLock.current) return;
    pickerLock.current = true;
    setPicking("archive");
    try {
      await run(
        "压缩包已加入检查队列",
        async () => {
          let directory: string;
          try {
            directory = await backend.getImportDirectory();
          } catch (caught) {
            throw new Error(`无法读取导入目录，请重试：${safeError(caught)}`);
          }
          if (!mounted.current) return null;
          if (typeof directory !== "string" || !directory.startsWith("/"))
            throw new Error("导入目录无效，请重试。");
          let selected: { path: string };
          try {
            selected = await openFilePicker(
              FileSelectionType.FILE,
              directory,
              true,
              true,
              undefined,
              ["zip", "7z", "rar"],
              false,
              false,
            );
          } catch (caught) {
            if (caught === "User canceled") return null;
            throw caught;
          }
          if (!mounted.current) return null;
          if (
            !selected ||
            typeof selected.path !== "string" ||
            !/\.(zip|7z|rar)$/i.test(selected.path)
          )
            throw new Error("请选择具体的 ZIP、7z 或 RAR 压缩包。");
          const name =
            selected.path
              .split("/")
              .pop()
              ?.replace(/\.(zip|7z|rar)$/i, "") || "本地 MOD";
          const title = [...name].slice(0, 120).join("");
          return installMode !== "auto"
            ? backend.importArchive(game.id, selected.path, title, installMode)
            : backend.importArchive(game.id, selected.path, title);
        },
        (job) => {
          if (job) onJob(job);
        },
      );
    } finally {
      finishSelection();
    }
  };
  return (
    <>
    <InstallGuidePanel game={game} busy={writeBlocked || Boolean(picking)} selectedMode={installMode} onSelectMode={(mode) => {
      setMethodMode(mode);
      setRootInstall(false);
    }} />
    <PanelSection title="添加 MOD">
      <Note>当前游戏：{game.name}</Note>
      {methodMode !== "auto" && <>
        <Note>已选择指南中的专用安装方式，请导入对应格式并核对安装预览。</Note>
        <Action disabled={writeBlocked || Boolean(picking)} onClick={() => setMethodMode("auto")}>恢复默认安装方式</Action>
      </>}
      <Note>
        {capability(game)}
        {game.running && (
          <>
            <br />
            游戏正在运行，请先退出游戏再安装或更改 MOD。
          </>
        )}
        {game.updating && (
          <>
            <br />
            Steam 更新中，请等待更新完成后再安装或更改 MOD。
          </>
        )}
      </Note>
      {game.requirements.length > 0 && (
        <Note>{game.requirements.join("；")}</Note>
      )}
      {game.adapter === "catalog" && (
        <>
          <PanelSectionRow>
            <ToggleField
              label="按游戏根目录安装（未适配游戏）"
              checked={rootInstall}
              disabled={writeBlocked || Boolean(picking)}
              onChange={(enabled) => { setRootInstall(enabled); setMethodMode("auto"); }}
            />
          </PanelSectionRow>
          <Note>
            仅在作者明确要求解压到游戏根目录时开启。保留压缩包内的目录，
            检查文件预览后再确认安装；安装后可禁用或卸载。不会自动安装前置、
            执行安装程序或合并配置。默认关闭，不会将未知格式自动放入游戏。
          </Note>
          {rootInstall && (
            <>
              <Note>
                {game.path
                  ? `当前安装目录：${game.path}（${game.manual_root ? "手动选择" : "Steam 自动定位"}）`
                  : "当前安装目录：尚未定位，请自动扫描或手动选择游戏根目录。"}
              </Note>
              {game.root_error && <Note>{safeError(game.root_error)}</Note>}
              <Action disabled={writeBlocked || Boolean(picking)} onClick={() => { void chooseRoot("auto"); }}>
                自动定位 Steam 游戏根目录
              </Action>
              <Action disabled={writeBlocked || Boolean(picking)} onClick={() => { void chooseRoot("manual"); }}>
                手动选择游戏根目录
              </Action>
              <Note>请选择包含游戏主程序的目录。目录会先验证；已有受管 MOD 时不能更换目录。</Note>
            </>
          )}
        </>
      )}
      {hasNexusMapping ? <>
      <PanelSectionRow>
        <TextField
          label="MOD 编号或 Nexus 网址"
          value={reference}
          disabled={busy}
          description={`编号仅在 ${game.nexus_domain} 内查找。`}
          onChange={(event) => {
            setReference(event.target.value);
            setMod(null);
            setFile(null);
          }}
        />
      </PanelSectionRow>
      <Action disabled={busy || !reference.trim()} onClick={lookup}>
        查找 MOD
      </Action>
      {mod && (
        <>
          <Note>{mod.name}</Note>
          <Note>作者：{mod.author}</Note>
          <Note>{mod.summary}</Note>
          <Action
            onClick={() => {
              void run("已打开 MOD 原始页面", async () => {
                openNexus(mod.page_url);
                return true;
              });
            }}
          >
            查看原始 MOD 页面
          </Action>
          {mod.files.length === 0 ? (
            <Note>没有可下载文件，请查看原始页面说明。</Note>
          ) : (
            <PanelSectionRow>
              <DropdownItem
                label="选择下载文件"
                disabled={busy}
                selectedOption={file ?? ""}
                rgOptions={[
                  { data: "", label: "请选择文件" },
                  ...mod.files.map((item) => ({
                    data: item.file_id,
                    label: `${item.name} · ${item.version} · ${formatBytes(item.size_bytes)}`,
                  })),
                ]}
                onChange={(option: { data: unknown }) =>
                  setFile(typeof option.data === "number" ? option.data : null)
                }
              />
            </PanelSectionRow>
          )}
          {file !== null && (
            <Note>
              {mod.files.find((item) => item.file_id === file)?.description}
            </Note>
          )}
          <Action disabled={installBlocked || file === null} onClick={download}>
            获取所选文件
          </Action>
        </>
      )}
      <Note>
        普通会员需在 Nexus 网页确认下载：请登录与 API 绑定相同的 Nexus 账号，
        选 Slow Download / MOD Manager Download，等待完成后允许 NXM
        打开；也可手动下载压缩包后导入。下载与检查完成后仍需确认安装预览。
      </Note>
      <Note>
        绑定 API 不会替网页登录。Steam 内置浏览器与 Chrome / Firefox
        可能不共享登录状态，网页仍可能要求登录。Premium 可通过 API 获取下载链接。
      </Note>
      </> : <Note>
        尚未验证此游戏的 Nexus 对应页面，暂不提供编号、网址或 NXM 下载。
        请先按 MOD 作者说明下载压缩包；需要解压到游戏根目录时，
        开启上方选项，核对游戏目录，再选择本地 MOD 压缩包并查看安装预览。
      </Note>}
      <PanelSectionRow>
        <Focusable ref={fileControl} tabIndex={-1}>
          <Action
            disabled={installBlocked}
            onClick={() => {
              void importFile();
            }}
          >
            {picking === "archive" ? "正在选择压缩包…" : "选择本地 MOD 压缩包"}
          </Action>
        </Focusable>
      </PanelSectionRow>
      {hasNexusMapping && <>
      <PanelSectionRow>
        <TextField
          label="手动接收 NXM 链接（可选）"
          value={nxm}
          bIsPassword
          bShowCopyAction={false}
          disabled={busy}
          onChange={(event) => setNxm(event.target.value)}
        />
      </PanelSectionRow>
      <Action
        disabled={installBlocked || !nxm.trim()}
        onClick={() => {
          const uri = nxm.trim();
          setNxm("");
          void run("NXM 下载任务已接收", () => installMode !== "auto"
            ? backend.acceptNxm(uri, installMode, game.id)
            : backend.acceptNxm(uri), onJob);
        }}
      >
        接收 NXM 下载
      </Action>
      </>}
    </PanelSection>
    </>
  );
}
