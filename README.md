# DeckyMods

SteamOS / Steam Deck 上的 Decky MOD 管理插件。当前版本 **0.2.10，预发布测试版**。

[下载预发布安装包](https://github.com/18798aa12/DeckyMods/releases/download/v0.2.10/DeckyMods-v0.2.10.zip) · [当前正式发布 v0.2.3](https://github.com/18798aa12/DeckyMods/releases/tag/v0.2.3) · [发布记录](https://github.com/18798aa12/DeckyMods/releases)

默认显示所有已安装的 Steam 游戏，另有可选的“只显示生化危机”筛选。生化危机目录覆盖 RE0 至 RE9 的 13 款 Steam 作品，包括 HD、重制版与启示录。提供 MOD 查询/导入、安装预览、冲突确认、启用、禁用、卸载、前置状态和中断恢复。

## 游戏覆盖范围

专用目录有 **72 款游戏、60 个不同系列**，包括 13 款生化危机 PC 游戏。另扫描已登记 Steam 游戏库中的其他已安装游戏，跳过 Proton、Steam Linux Runtime 等运行工具。未收录作品使用本地压缩包和显式根目录安装，不会猜测 Nexus 游戏域名或专用适配。识别目录不等于所有游戏都可以自动安装：

| 等级 | 数量 | 当前能力 |
| --- | ---: | --- |
| 自动映射已实现 | 12 款 | 7 款旧引擎生化危机的现有资源替换，以及原有 5 款 UE PAK 游戏 |
| 需要额外加载器 | 7 款 | 已适配 REFramework 文件结构；加载器须另行安装，支持自动检查并合并启动项 |
| 仅识别/查询目录 | 53 款 | 展示游戏及 Nexus 资料；可显式选择通用根目录模式，自动适配仍待验证 |

**已在 Steam Deck 验证 RE7 的 Item Unlocker 脚本加载，其他游戏内效果仍待实测。** 不同版本、可选文件、FOMOD、脚本安装器、复杂前置和反作弊游戏不能通用处理；无法确定的布局会提示原因并阻止安装。完整映射及逐项来源见 [兼容表](docs/COMPATIBILITY.md)。

剑星支持 `.pak`，以及相同文件名的 `.pak/.utoc/.ucas` 完整组合，目标是 `SB/Content/Paks/~mods`。RE2/3/4 重制版、RE7、Village、Requiem 支持 REFramework 脚本/插件和 natives 资源；RE4 重制版保留补丁 PAK 自动编号，RE9 使用独立 pak_mods 规则。RE0、1 HD、4 原版、5、6、启示录 1/2 仅处理明确目录内已存在的资源文件替换，不能自动执行安装器或解包/重打原版归档。

## 安装与添加 MOD

1. 安装 Decky Loader，在 Decky 设置的开发者选项里选择“从 ZIP 安装插件”，选完整 `DeckyMods-v0.2.10.zip`。不要单独拷贝 `main.py`。插件不申请 root 权限。
2. 打开 DeckyMods，扫描 Steam 游戏库并选择游戏。支持 Steam 主库和在库清单中登记的 SD 卡库。
3. 已有压缩包：在“添加 MOD”选择本地压缩包，文件放在当前用户的下载、文档或桌面目录（支持 XDG 配置）。先看安装预览，再确认。
4. 下载 Nexus MOD：在账户区域打开 Nexus 登录和 API Access 页面，找到 Personal API Key 区域（普通会员也可生成），再将**个人 API Key**输入插件绑定。插件不接收 Nexus 密码或浏览器 Cookie。
5. 有已核实 Nexus 游戏映射的条目，可以输入 MOD 编号或对应 Nexus 网址，查询并明确选择文件。仅从 Steam 发现的未知条目提供本地导入，暂不提供 Nexus 查询。
6. 普通会员：插件打开文件网页，你在网站完成登录及下载确认。可选开启“接收 NXM 下载”，将浏览器的 `nxm://` 链接交给本插件；也可以正常下载压缩包，再用本地导入。NXM 接收需要浏览器/桌面协议关联正常，游戏模式中不生效时请切桌面模式。

API 绑定与网页登录是两套状态。API Key 可验证账号、查询 MOD 说明和文件列表；普通会员仍须在网页确认所选文件，取得临时下载授权。网页需使用与 API 绑定相同的 Nexus 账号，Steam 内置浏览器与 Chrome / Firefox 的登录状态可能独立。官方 [下载授权说明](https://github.com/Nexus-Mods/node-nexus-api/blob/master/docs/classes/_nexus_.nexus.md#getdownloadurls) 介绍了网页产生的 NXM 下载授权。也可直接下载压缩包后本地导入。

## 未适配游戏的根目录安装

在默认的已安装游戏列表中选择游戏。未检测到安装的目录条目也可以选择，再手动指定游戏文件夹。勾选“按游戏根目录安装”后，提供两个定位选项：从 Steam 自动定位，或用文件夹选择器手动选择。手动目录须为当前用户所有、包含游戏 EXE 的具体游戏目录，禁止链接、资料目录、Proton 容器及与其他游戏相互重叠的目录。已有管理中的 MOD 或未完成任务时禁止换目录。

只有作者明确要求解压到根目录时使用；所有压缩包相对路径保持原样，不自动去掉外层文件夹，也不执行安装器、合并配置或代装前置。预览可以展开并翻页查看所有目标文件；路径大小写与 Linux 游戏目录不同会阻止安装。确认后仍使用备份、分层部署和可撤销管理。复杂可选包、FOMOD、安装脚本需先按作者说明处理。

## MOD 说明

“已安装 MOD”和每个 MOD 均默认折叠。展开某个 MOD 时才读取包内 modinfo.ini / README，并对有明确 Nexus 来源的 MOD 查询官方描述；支持刷新和打开来源网页。没有账号或网络失败时保留本地说明，启用、禁用和卸载不依赖描述查询。没有来源信息的本地包不会凭文件名猜 MOD 编号。

## 自动启动项

选择游戏后，“启动项”区域会显示是否识别到已适配的加载器、是否需要配置及操作结果。已适配的 REFramework 游戏检测到根目录 `dinput8.dll` 后，默认自动检查；安装或启用 MOD 后会再次检查。其他游戏完成安装后，选择对应游戏即可触发检查。

- 仅补齐已知的 `dinput8.dll=n,b` 覆盖，保留插帧的 `dxgi`、其他环境变量和原有参数；已经满足要求时不重复添加。
- 首次修改前保存私有备份，写入后回读验证。游戏运行、Steam 更新、文件恢复未完成时阻止修改。
- 可以关闭自动配置，并恢复首次修改前的启动项。若之后手动改过启动项，恢复会停止并提示，避免覆盖新设置。
- 复杂 Shell 命令、同名 DLL 的冲突和未知加载器需要人工检查。插件不会执行 MOD 说明中的命令，也不会只凭压缩包里有任意 DLL 就添加参数。

规则依据为 [REFramework 官方安装说明](https://github.com/praydog/REFramework#protonlinux)。检测到加载器文件和参数不代表加载器版本一定匹配，仍需核对游戏内日志。

## 生化危机状态与资源配置

选择游戏后显示 Build ID、前置文件、资源开关和上次运行日志中的 TDB/渲染器。文件存在与上次成功加载不是当前版本兼容性保证；没有日志时不会凭 EXE 中的 DLL 字符串猜 RT/非 RT 分支。

现代作品共用 `re2_fw_config.txt`。安装 natives 资源时，确认安装会备份并启用 `LooseFileLoader_Enabled`；RE9 PAK 另启用 `IntegrityCheckBypass_LoadPakDirectory`。原配置必须由匹配的 REFramework 运行生成，损坏/重复键会阻止修改。配置作为独立前置偏好保存；禁用和卸载资源 MOD 只撤销对应文件，不关闭其他 MOD 仍可能需要的开关。

可以在状态面板准备或恢复资源配置；恢复前必须先禁用相关资源 MOD。游戏改写了配置后，恢复会保留新内容并提示人工核对。RT/非 RT、DLC、模型替换前置、脚本与游戏补丁的对应关系仍以作者要求为准。

## 插件更新

提供每 6 小时自动检查、手动检查、下载校验及 Decky 原生确认安装。新安装默认使用本仓库 GitHub Release 签名来源，已有来源和开关会保留。也可以填写局域网来源；局域网方式需要 Mac 下载服务保持运行。大陆网络访问 GitHub 受阻时可继续使用局域网 ZIP。

更新清单经固定公钥验证，安装包校验大小、SHA256、版本、普通用户权限和完整文件结构；拒绝额外远程二进制下载。账户、配置与 MOD 数据保留。卸载原生协议绑定后，新版按已保存的用户意图恢复 NXM；只有主动“停用账户”才删除个人 API Key。

预发布版本供手动测试，不替换正式更新源中的版本。安装操作仍由 Decky 确认，当前没有无人值守自动安装功能。Decky 原生替换失败后可重新从已验证 ZIP 安装，不承诺启动失败后的自动回滚。

TUN 虚拟 DNS 兼容：只有官方 Nexus / GitHub 域名的 DNS 结果全部为 198.18.0.0/15 虚拟地址时，才向固定 Cloudflare HTTPS 解析器查询真实公网 IP；保留目标网站 TLS 校验，拒绝私网或混合结果。解析请求只包含域名。Decky 冻结 Python 的默认证书库为空时，读取 SteamOS 系统 CA 证书；始终验证 HTTPS 证书与主机名。

## 管理与恢复

已由通用 Steam 识别并产生管理记录的游戏，在后续目录增加专用适配时保留原身份和根目录模式，已有 MOD、备份、手动路径与安装预览继续归属原游戏；不会自动切换适配器。存储暂不可用时保留记录并阻止写入，重新连接后重新校验。切换到新适配器需要单独的安全迁移流程。

- MOD、游戏目录默认折叠，支持搜索和分页。不同 MOD 覆盖相同文件时，预览会列出冲突；后安装且启用的层优先。
- 禁用或卸载上层 MOD 会恢复下层；最后一层卸载后恢复原文件。仅删除本插件有记录且当前校验相符的文件。
- 检测到游戏运行、Steam 更新或文件被外部工具修改时会阻止修改。Steam 更新后出现冲突时先保留现状，勿强行删除备份。
- 安装操作记录恢复日志。插件重新启动时尝试恢复未完成操作；存储设备不在或文件外部变化时保留文件并提示。
- 原压缩包在私有工作目录中的临时副本会在任务结束后删除；你自己的下载包不会删除。MOD 对象与备份会保留在 Decky 私有设置目录，暂未提供自动清理旧对象的界面，请预留空间。
- NXM 接收默认关闭；开启前保存已有协议关联，关闭或正常卸载时恢复。停用账户会删除本地 API Key。
- 卸载 Decky 插件前，先在本插件里卸载所管理的 MOD。卸载插件不会擅自批量改动游戏，也不会抹掉恢复记录。

此预览版使用个人 API Key，适合自用验证。公开商店发行前需按 Nexus 要求登记独立应用及自己的 SSO 标识，并完成实机兼容测试；本包尚未提交 Decky 商店。

## 开发与验证

需要 Node.js 22/24、pnpm 10.33.0、Python 3.11+ 和系统 libarchive。Decky 安装包附带固定版本 libarchive-c 纯 Python 包，启动不联网安装依赖。

```bash
pnpm install --frozen-lockfile
pnpm test
pnpm typecheck
pnpm build
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt -r requirements.txt
.venv/bin/python -m pytest --cov=decky_mods
.venv/bin/ruff check main.py py_modules scripts tests
.venv/bin/python -m scripts.package
.venv/bin/python -m scripts.verify_release release/DeckyMods-v0.2.10.zip
```

构建输入在 `data/dependencies.json` 固定版本及 SHA256；输出安装 ZIP、对应源码包和 SHA256SUMS。测试使用合成的游戏目录，不修改真实游戏或下载第三方 MOD。实机检查步骤见 [测试清单](docs/STEAM_DECK_TESTING.md)。

GPL-3.0-only；依赖与参考资料见 [第三方说明](THIRD_PARTY_NOTICES.md)。插件不是 Nexus Mods 或 Valve 的官方产品。
