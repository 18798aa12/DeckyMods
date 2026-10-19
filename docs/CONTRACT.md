# Implementation contract — 2026-10-19

Approved scope: Decky native UI, >=50 distinct series catalog with honest capability levels, RE and Stellar Blade priority, free Nexus browser-confirmed downloads/NXM handoff plus local ZIP/7z/RAR import, reversible deployment. No root plugin, no password/cookie collection, no third-party mod redistribution.

## Backend RPC (async wrappers in main.py; service implementation synchronous)

`get_status()` -> `{version, platform_supported, auth: Auth, jobs: Job[], handler: Handler, error: string|null}`

`list_games()` -> `Game[]`; all catalog entries, installed flags and capability levels. `get_game(game_id)` -> `{game: Game, mods: Mod[], recovery_error: string|null}`.

`bind_account(api_key)` / `disconnect_account()` -> Auth.

`resolve_mod(game_id, reference)` -> NexusMod. Only a selected game gives meaning to a bare mod number. URLs must belong to that game's Nexus domain.

`begin_download(game_id, mod_id, file_id)` -> Job. Free users: `awaiting_browser`, `browser_url` opens the specific normal Nexus file page. Premium: background download. `accept_nxm(uri)` -> Job. Validate user, expiry, identity; the regular website must have generated free-user permission.

`import_archive(game_id, path, name)` -> Job. Native picker selects a regular user-owned archive in Downloads/Documents/Desktop (including XDG). Background inspection produces `ready` job and plan.

`get_import_directory()` -> string. Current user's existing XDG download directory, an existing standard import folder, or their home. No fixed `/home/deck` assumption.

`get_plan(plan_id)` -> Plan. `install_plan(plan_id, allow_conflicts)` -> Job. Explicit installation preview; conflicts need acknowledgement. `set_mod_enabled(game_id, mod_id, enabled)` and `uninstall_mod(game_id, mod_id)` -> GameView. These can be bounded synchronous operations through async RPC wrappers.

`get_jobs()` -> Job[]. `cancel_job(job_id)` -> Job. `set_nxm_handler(enabled)` -> Handler. Handler registration must preserve and restore any previous association; no activation on first launch.

`get_launch_setup(game_id)` -> LaunchSetup; `set_launch_auto(game_id, enabled)` -> LaunchSetup. Only reviewed REFramework adapters with a regular root dinput8.dll require known override configuration. Detection never executes archive metadata or arbitrary commands.

`prepare_launch_options(game_id, current, restore=false)` -> LaunchChange. Validates current options, detects conflicting/ambiguous shell syntax, persists original backup and pending intent before returning a write proposal. `finish_launch_options(game_id, change_id, observed)` -> LaunchSetup; requires exact verified readback. The frontend uses native Steam APIs, compares the current value again immediately before writing, and never rewrites localconfig.vdf. A changed=false proposal needs no finish. Restore disables automatic configuration and refuses to overwrite intervening external edits.

## Public shapes

0.2.0 focuses on 13 Steam Resident Evil titles. `re_legacy` maps explicitly anchored replacements of existing files; modern `re_engine` implements REFramework scripts, reviewed natives resources, RE4 patch numbering and RE9-specific pak_mods.

`get_resident_status(game_id)` -> ResidentStatus (family, Build ID, loader/config presence and previous-run TDB/renderer evidence). `prepare_resident_settings(game_id, enable_pak)` and `restore_resident_settings(game_id)` use a separate journaled configuration deployment. Active resource MODs block config restore. Resource file disable/uninstall is independent from the global loader flags; external config rewrites are preserved.

`get_update_status()`, `set_update_options(source, auto_check)`, `check_update()` -> UpdateStatus. `prepare_update()` -> `{artifact:fileURI,version,sha256}` for Decky's existing native install connection and confirmation modal. Automatic mode checks every six hours; unattended installation is not implemented. Only configured private-LAN HTTP or the fixed future GitHub release feed is accepted, signatures pin identity/namespace, packages may not request root or remote binaries. Native uninstall restores external NXM association, retained private preference reactivates it on next start; account removal is explicit.

Auth: `{connected: boolean, name: string|null, premium: boolean, user_id: number|null, error: string|null}`. Never return API key or signed download grant.

Game: `{id, name, series, series_name, nexus_domain, steam_app_ids: string[], adapter, support: 'automatic'|'needs_setup'|'catalog', requirements: string[], sources: string[], installed: boolean, path: string|null, app_id: string|null, build_id: string|null, running: boolean}`. Automatic means implemented format mapping with synthetic tests, NOT in-game hardware validation.

Mod: `{id, name, enabled, installed_at, files_count, nexus_mod_id: number|null, nexus_file_id: number|null, source_url: string|null}`.

NexusMod: `{game_id, mod_id, name, author, summary, page_url, files: [{file_id, name, version, category, size_bytes, description, primary: boolean}]}`. Multiple files require user choice.

Job: `{id, game_id, name, phase: 'queued'|'awaiting_browser'|'downloading'|'scanning'|'ready'|'installing'|'complete'|'failed'|'cancelled', bytes_done, bytes_total, error: string|null, plan_id: string|null, browser_url: string|null}`. Browser URLs contain no tokens. Incomplete jobs after restart become failed/retryable.

Plan: `{id, game_id, name, files_count, bytes, conflicts: string[], warnings: string[], requirements: string[], blocked_reason: string|null, can_install: boolean}`. Internal plan pins source hashes, target root and build.

Handler: `{enabled: boolean, supported: boolean, previous: string|null, message: string|null}`.

LaunchSetup: `{supported: boolean, required: boolean, reason: string, app_id: string|null, auto_enabled: boolean, backup_available: boolean}`. Reason contains safe user-facing text, never raw launch options. LaunchChange: `{id, app_id, before, after, changed: boolean}`; before/after stay within the local authenticated Decky flow and private backup files, never rendered or logged. IDs are empty for no-op proposals.

## Module ownership / interfaces

Root: errors.py, paths.py, archive reading, objects/SQLite deployment/journal/recovery, service/jobs, main.py, release scripts and docs.

Game worker: `catalog.py`, `steam.py`, `adapters.py` (split modules as needed), `data/games.json`, related tests/docs. `load_catalog(plugin_dir: Path) -> list[dict]`; `SteamDiscovery(catalog: list[dict], home: Path|None=None)`, `.discover() -> list[dict]`, `.resolve(game_id: str) -> dict` (installed game, raises ModsError if unavailable); `plan_files(game: dict, extracted: Path) -> dict` returns `{files: [{source: str, target: str, kind?: 're_pak'}], warnings: str[], requirements: str[], blocked_reason: str|null}`. Paths relative. RE PAK `kind` is renumbered by deployment across enabled packs; adapter must not mutate games. Registry owns extra verified adapter config fields. Unverified games block deployment.

Nexus worker: `nexus.py`, `network.py`, `nxm.py`, helper script and related tests. `NexusClient(directory: Path)`: `.status()`, `.bind(key)`, `.disconnect()`, `.resolve(domain: str, reference: str) -> dict` (NexusMod without game_id), `.download(domain: str, mod_id: int, file_id: int, destination: Path, cancel: threading.Event, progress: Callable[[int,int],None], nxm_uri: str|None=None) -> None`, `.browser_url(domain, mod_id, file_id) -> str`, `.parse_nxm(uri) -> dict` (identity+account+expiry validation). Free download without valid nxm grant must fail actionably, no scrape. `NxmHandler(directory: Path, plugin_dir: Path, home: Path|None=None)`: `.status()`, `.set_enabled(bool)`, `.drain() -> list[str]`, `.close()`. Helper private queue; do not persist signed URIs beyond consumed transient input. Other modules use `ModsError` from `.errors`.

Frontend worker: all src and frontend config only. Root owns package metadata/build shell. Typed @decky/api callable RPC, native controls, collapsed/searchable game/mod lists, native file picker and alwaysRender lifecycle, first-B hint/second-B propagation as already proven in DeckyProxy. Manual game-folder selection is explicit and validated by GameRoots; archive targets remain relative and registry/selected-root confined. Display free-account instructions and capabilities honestly.

All workers are sharing this checkout; never revert other workers' changes. Tests first, inspect RED, implement GREEN. No commits from workers.

## 0.2.1 explicit root mode and descriptions

`set_game_root(game_id, mode: auto|manual, path="")` -> GameView; catalog games only, current-user game EXE directory, no symlinks/protected containers/shared or overlapping game roots. In-flight jobs or managed MODs prevent relocation. Manual processes are detected from cwd/exe/cmdline even without a catalog Steam AppID.

`import_archive` and `begin_download` accept optional `install_mode="auto"|"game_root"`. The selected mode is persisted with each private job; browser NXM handoff retains that mode. Explicit root `accept_nxm(uri, "game_root", expected_game_id)` must match selected game; unsolicited NXM defaults to auto.

`get_mod_details(game_id, internal_mod_id)` -> `{name,author,version,description,source_url,origin,error}`; called only on expansion, local notes fallback, official game-scoped Nexus API only. Private embedded metadata is excluded from list/poll responses. Public Plan now includes `targets` for folded paginated preview.

## 已安装 Steam 游戏身份

专用目录外的已安装作品从受校验的 Steam manifest 建立 `steam-APPID` 身份，适配器为 `catalog`，Nexus 域名为空；仅显式根目录本地导入可部署。未知游戏与已有游戏根目录相同或重叠时不建立第二身份。已有部署、事务、安装预览、任务或手动目录引用的 `steam-APPID` 会持久保留原身份；目录新增适配时仍沿用旧根目录模式，不自动升级适配器或猜测 Nexus 域名。兼容层仅使用新校验的 Steam 目录证据，不将历史部署路径当作自动定位许可；原 ID、MOD 层、备份、任务与启动项记录不重命名。需要切换至新适配器时仍须另行实现明确的安全迁移。

启动恢复在游戏运行或 Steam 更新/验证期间延期，不将临时忙碌状态记为恢复失败；原恢复事务与备份保留，待游戏空闲后由安全恢复流程处理。主 MOD 与前置配置两类恢复均成功后，才清除此游戏的旧恢复错误。

## 十轮加固后的补充约束

- 每次启动尚未取得可验证更新清单时，重新检查一次；本会话检查失败仍按检查间隔退避。更新来源配置先落盘，再替换内存。
- Nexus 账号绑定以最新请求及解绑意图为准。重复 NXM 回调复用活跃任务、安装模式和预览，不重复下载。
- 运行必需文件由 `package_layout.py` 共用清单检查；新增模块必须更新清单。未来删除或改名需兼容已安装版本的最小文件检查。
- 资源 MOD 的启用和前置恢复串行；恢复不能关闭活跃 MOD 依赖的资源加载开关。
- 取消初始化须等待不可取消的线程结束并清理。兼容 Decky 先 `_unload` 再 `_uninstall` 的删除顺序，保留协议恢复能力，不删除个人账户。
- 单项轮询失败保留其他成功结果；失效游戏视图停止操作，手动扫描与自动扫描采用一致的选择清理。启动项状态按游戏身份、安装状态、路径、AppID、Build ID 重新判断。
