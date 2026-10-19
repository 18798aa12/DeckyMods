# 动作 / Unreal / RE 安装方式详细研究

核查日期：2026-10-19。返回 [113 款游戏索引](INSTALL_METHODS.md)。

未进行 Steam Deck 实机验证。下列“可实现候选”仅表示研究建议，不代表代码已实现或包一定兼容；真正能否部署由插件当前受限方案与安装预览决定。来源只用于参考公开行为与协议，不复制第三方实现，不捆绑闭源管理器或游戏/MOD 资源。

<a id="game-residentevil22019"></a>

## Resident Evil 2 (2019)

`residentevil22019` · Steam 883710

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil22019/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil22019/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil22019/index.js) |
| 旧非 RT 分支加载器<br>`reframework-legacy-nonrt` · 手动说明 | 旧非 RT 分支；RE2 TDB66 / RE3 TDB67 / RE7 TDB49<br>旧 per-game/TDB DLL + Lua | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；单体 nightly 明确不支持旧非 RT；必须选择旧版匹配发行，不自动升级为单体版。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- RT / 非 RT 是独立兼容路线，不能将相同 MOD 页面视为跨分支通用。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevil32020"></a>

## Resident Evil 3 (2020)

`residentevil32020` · Steam 952060

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil32020/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil32020/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil32020/index.js) |
| 旧非 RT 分支加载器<br>`reframework-legacy-nonrt` · 手动说明 | 旧非 RT 分支；RE2 TDB66 / RE3 TDB67 / RE7 TDB49<br>旧 per-game/TDB DLL + Lua | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；单体 nightly 明确不支持旧非 RT；必须选择旧版匹配发行，不自动升级为单体版。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- RT / 非 RT 是独立兼容路线，不能将相同 MOD 页面视为跨分支通用。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevil42023"></a>

## Resident Evil 4 (2023)

`residentevil42023` · Steam 2050650

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil42023/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil42023/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil42023/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevil7"></a>

## Resident Evil 7

`residentevil7` · Steam 418370

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil7/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil7/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevil7/index.js) |
| 旧非 RT 分支加载器<br>`reframework-legacy-nonrt` · 手动说明 | 旧非 RT 分支；RE2 TDB66 / RE3 TDB67 / RE7 TDB49<br>旧 per-game/TDB DLL + Lua | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；单体 nightly 明确不支持旧非 RT；必须选择旧版匹配发行，不自动升级为单体版。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- RT / 非 RT 是独立兼容路线，不能将相同 MOD 页面视为跨分支通用。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevilvillage"></a>

## Resident Evil Village

`residentevilvillage` · Steam 1196590

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilvillage/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilvillage/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilvillage/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevilrequiem"></a>

## Resident Evil Requiem

`residentevilrequiem` · Steam 3764200

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilrequiem/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilrequiem/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-residentevilrequiem/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-devilmaycry5"></a>

## Devil May Cry 5

`devilmaycry5` · Steam 601150

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-devilmaycry5/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-devilmaycry5/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-devilmaycry5/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-streetfighter6"></a>

## Street Fighter 6

`streetfighter6` · Steam 1364780

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework 脚本与插件<br>`reframework-lua` · 可实现候选 | Steam 当前分支；nightly 01432 单体包<br>reframework/autorun/*.lua; reframework/plugins/*.dll | `reframework/`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；使用官方匹配加载器；非 VR 仅取 dinput8.dll；Proton 合并 dinput8 原生 DLL override。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md)、[源3](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-streetfighter6/index.js) |
| RE Engine 明确路径资源覆盖<br>`re-loose-resources` · 可实现候选 | 仅作者声明支持的当前分支<br>natives/... 或明确命名的补丁 PAK | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；须由对应版本 LooseFileLoader 支持并开启所需开关；不推断包内命名空间。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/LooseFileLoader.cpp)、[源2](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-streetfighter6/index.js) |
| Fluffy 元数据或资源归档<br>`fluffy-package` · 外部工具 | 按 MOD 作者声明的游戏分支<br>modinfo.ini + natives/...; .pak | `由专用工具/作者说明决定，不猜路径`<br>Fluffy 为外部工具，不能把其二进制或闭源实现当作 MIT 源码复制。；涉及归档失效、合并与特殊选项时留给外部管理器。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-streetfighter6/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- REFramework 最新开发路线与旧 stable v1.5.9.1 分开记录；nightly 仓库虽然 API prerelease=false，产品仍按开发构建展示。
- 新 REFramework.zip 统一取代旧 per-game ZIP；禁止按 latest 盲取旧资产名。
- 联机与反作弊风险须按作者与游戏规则检查；不能承诺 MOD 可在联网对战使用。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly)：`{"repo":"praydog/REFramework-nightly","ref":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT (REFramework source)"}`；[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-residentevil0biohazard0hdremaster"></a>

## Resident Evil 0 HD

`residentevil0biohazard0hdremaster` · Steam 339340

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil0.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re0)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil0.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re0)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevilbiohazardhdremaster"></a>

## Resident Evil HD

`residentevilbiohazardhdremaster` · Steam 304240

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re1)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re1)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevil4"></a>

## Resident Evil 4 (2005)

`residentevil4` · Steam 254700

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil4.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re4)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil4.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re4)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevil5"></a>

## Resident Evil 5

`residentevil5` · Steam 21690

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil5.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re5)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil5.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re5)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevil6"></a>

## Resident Evil 6

`residentevil6` · Steam 221040

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil6.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re6)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvil6.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/re6)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevilrevelations"></a>

## Resident Evil Revelations

`residentevilrevelations` · Steam 222480

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvilRevelations.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/rerev)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvilRevelations.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/rerev)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| RERevFix 独立 DLL 修复<br>`rerevfix` · 手动说明 | 该修复声明支持的 Steam 版本<br>RERevFix 发布包 | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；上游警告 Raid 多人模式使用 VAC，不带此钩子进入该模式。 | [源1](https://github.com/Lyall/RERevFix/blob/master/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-residentevilrevelations2"></a>

## Resident Evil Revelations 2

`residentevilrevelations2` · Steam 287290

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 修复包（按官方发行结构）<br>`asi-fusionfix` · 手动说明 | PC Steam 对应作品；匹配该作品发布标签<br>.asi/.ini + 对应位数代理 DLL | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；从该作品官方 ZIP 保留结构；32/64 位和代理 DLL 必须匹配，不自动覆盖已有加载器。；Proton override 依据实际代理 DLL 合并；不为所有作品硬套 dinput8。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvilRevelations2.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/rerev2)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| 旧引擎完整相对路径覆盖<br>`legacy-exact-overlay` · 手动说明 | 仅明确标注兼容的 PC Steam 版本<br>含游戏相对资源目录的 ZIP | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先验证真实游戏目录、目标文件和完整相对路径；原始 ARC/DAT/EXE 补丁、自动安装器须转手动。 | [源1](https://github.com/ThirteenAG/WidescreenFixesPack/blob/708f7528fb8b54c79d4ac3c6071ea7ccc01ae162/source/ResidentEvilRevelations2.FusionFix/dllmain.cpp)、[源2](https://github.com/ThirteenAG/WidescreenFixesPack/releases/tag/rerev2)、[源3](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 这些作品不是 RE Engine，不得为它们安装 REFramework。
- WidescreenFixesPack 使用各作品独立可滚动标签，不能以全仓库 latest 标签判断该作品修复版本。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack)：`{"repo":"ThirteenAG/WidescreenFixesPack","ref":"708f7528fb8b54c79d4ac3c6071ea7ccc01ae162","release":null,"published_at":null,"license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-stellarblade"></a>

## Stellar Blade

`stellarblade` · Steam 3489700

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak + 对应同名 .ucas/.utoc | `SB/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-stellarblade/index.js) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-stellarblade/index.js)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-tekken8"></a>

## TEKKEN 8

`tekken8` · Steam 1778820

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak + 对应同名 .ucas/.utoc | `Polaris/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-tekken8/index.js) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-tekken8/index.js)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-finalfantasy7rebirth"></a>

## Final Fantasy VII Rebirth

`finalfantasy7rebirth` · Steam 2909400

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak + 对应同名 .ucas/.utoc | `End/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-finalfantasy7rebirth/index.js) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-finalfantasy7rebirth/index.js)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-codevein"></a>

## Code Vein

`codevein` · Steam 678960

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `CodeVein/content/paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-codevein/src/common.ts) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-codevein/src/common.ts)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-bloodstainedritualofthenight"></a>

## Bloodstained Ritual of the Night

`bloodstainedritualofthenight` · Steam 692850

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `BloodstainedRotN/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-bloodstainedritualofthenight/src/common.ts) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-bloodstainedritualofthenight/src/common.ts)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-spyroreignitedtrilogy"></a>

## Spyro Reignited Trilogy

`spyroreignitedtrilogy` · Steam 996580

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `falcon/content/paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-spyroreignitedtrilogy/src/common.ts) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-spyroreignitedtrilogy/src/common.ts)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-finalfantasy7remake"></a>

## Final Fantasy VII Remake Intergrade

`finalfantasy7remake` · Steam 1462040

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `End/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_finalfantasy7remake.py) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_finalfantasy7remake.py)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-guiltygearstrive"></a>

## Guilty Gear -Strive-

`guiltygearstrive` · Steam 1384160

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `RED/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/UI/MainWindow.xaml.cs)、[源2](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/Setup.cs) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/UI/MainWindow.xaml.cs)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- Unverum 可为本游戏提供资源部署及特殊补丁；它有构建时清理自有 ~mods 子目录行为，不得复制为清空用户目录的逻辑。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[TekkaGB/Unverum](https://github.com/TekkaGB/Unverum)：`{"repo":"TekkaGB/Unverum","ref":"e41b135e8900187b9a7a06f52bf723f4a7ba35e1","release":"2.6.5","published_at":"2025-01-22T20:39:40Z","license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-talesofarise"></a>

## Tales of Arise

`talesofarise` · Steam 740130

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal 资源包<br>`ue-resource-pak` · 可实现候选 | Steam PC；仅作者声明匹配当前更新的 cooked 资源<br>.pak；作者提供时保留 .sig | `Arise/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留文件名、配套文件和依赖；不重排 IO Store 配对名称。；拒绝把 LogicMods/UE4SS/配置/加载器混为普通资源 PAK。 | [源1](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/UI/MainWindow.xaml.cs)、[源2](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/Setup.cs) |
| UE4SS / Blueprint / Text Patch 专用路线<br>`ue-logic-or-script` · 外部工具 | 依作者要求的 UE、游戏及加载器版本<br>LogicMods; UE4SS Lua/C++; text.json | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要对应版本加载器、启用登记或文本合并；不能只复制到 ~mods 即声称成功。 | [源1](https://github.com/TekkaGB/Unverum/blob/e41b135e8900187b9a7a06f52bf723f4a7ba35e1/Unverum/UI/MainWindow.xaml.cs)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Linux 按真实目录逐段匹配并保留大小写；源代码 Windows 路径常量不能直接代表 Linux 文件系统大小写。
- Unverum 可为本游戏提供资源部署及特殊补丁；它有构建时清理自有 ~mods 子目录行为，不得复制为清空用户目录的逻辑。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[TekkaGB/Unverum](https://github.com/TekkaGB/Unverum)：`{"repo":"TekkaGB/Unverum","ref":"e41b135e8900187b9a7a06f52bf723f4a7ba35e1","release":"2.6.5","published_at":"2025-01-22T20:39:40Z","license":"GPL-3.0"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT"}`

<a id="game-palworld"></a>

## Palworld

`palworld` · Steam 1623730

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 普通资源 PAK<br>`ue-resource-pak` · 可实现候选 | Steam/Win64；与当前 Palworld 更新兼容的资源<br>.pak/.ucas/.utoc | `Pal/Content/Paks/~mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。 | [源1](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/common.ts)、[源2](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/installers.ts) |
| LogicMods 蓝图包<br>`ue-blueprint` · 手动说明 | 需要 BPModLoader/作者指定加载器的版本<br>.pak + 蓝图元数据 | `Pal/Content/Paks/LogicMods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；按包内明确标记分类，不能仅按 .pak 扩展名猜测。 | [源1](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/common.ts)、[源2](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/installers.ts) |
| 当前 UE4SS 目录布局<br>`ue4ss-new` · 手动说明 | Okaetsu 2281fa31 / experimental-palworld；按游戏更新核验<br>ue4ss/Mods/<mod>/Scripts/main.lua 或 dlls/main.dll | `Pal/Binaries/Win64/ue4ss/Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；现有 UE4SS 必须检测；不同版本布局不可混装；按 mods.txt 或 enabled.txt 登记。；不要同时启用 Workshop UE4SS 和手工代理 DLL；Steam 客户端与 dedicated server 分开。 | [源1](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/common.ts)、[源2](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/installers.ts)、[源3](https://github.com/Okaetsu/RE-UE4SS/blob/5418fa4ed9f1e8379d28ee7bbc3235c7e0c71b09/README.md) |
| 旧 UE4SS 平铺 Mods 布局<br>`ue4ss-legacy` · 手动说明 | 旧 UE4SS 2.5.2 / 3.0.0 发行结构<br>Mods/<mod> + UE4SS-settings.ini | `Pal/Binaries/Win64/Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；只为已检测到的旧平铺加载器提供；不能将新 ue4ss 子目录删掉以迁就旧布局。 | [源1](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/common.ts)、[源2](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/installers.ts) |
| PalSchema 子模块<br>`palschema` · 手动说明 | 已安装兼容 PalSchema 的当前 UE4SS<br>.json/.jsonc 数据子目录，可伴随 PAK | `Pal/Binaries/Win64/ue4ss/Mods/PalSchema/mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；完整识别 PalSchema 元数据与子模块；混合 PAK 与数据须同一事务管理。 | [源1](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/common.ts)、[源2](https://github.com/Nexus-Mods/game-palworld/blob/16850505152c67b0a4322a4c1ae4cdb5fd69d9e5/src/installers.ts) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Game Pass 为 WinGDK 及不同代理 DLL 路线，不能把 Steam 安装路径直接套到它；本插件先做 Steam 自动化。
- 上游 0.4.x 源码已更新到 2026-08，而 GitHub 最后扩展 stable tag 仍 0.1.7；当前源码与已打包发行必须区分。
- Okaetsu rolling asset 的发布时间可能很旧但内容更新；以完整 ref/资产 updated_at/digest 核查，不能仅看 tag。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/game-palworld](https://github.com/Nexus-Mods/game-palworld)：`{"repo":"Nexus-Mods/game-palworld","ref":"16850505152c67b0a4322a4c1ae4cdb5fd69d9e5","release":"v0.1.7","published_at":"2024-02-21T12:04:01Z","license":"GPL-3.0"}`；[Okaetsu/RE-UE4SS](https://github.com/Okaetsu/RE-UE4SS)：`{"repo":"Okaetsu/RE-UE4SS","ref":"5418fa4ed9f1e8379d28ee7bbc3235c7e0c71b09","release":"2281fa31","published_at":"2026-09-03T21:06:13Z","license":"MIT"}`

<a id="game-dragonsdogma"></a>

## Dragon's Dogma: Dark Arisen

`dragonsdogma` · Steam 367500

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| nativePC 完整路径覆盖<br>`nativepc-overlay` · 可实现候选 | Steam Dark Arisen；非 Dragon's Dogma 2<br>nativePC/... 文件树 | `nativePC`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留 ROM 外的合法资源；不要重犯旧 Vortex 只截取 nativePC/rom 的漏文件问题。 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_dragonsdogmadarkarisen.py)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragons-dogma/src/index.js) |
| ARC 合并或补丁安装<br>`arc-merge` · 外部工具 | 作者指定的游戏版本<br>.arc/.arcs 或工具输入 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；有归档内部合并、冲突资源时使用作者指定工具；不按扩展名猜装。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragons-dogma/src/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`；[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-granbluefantasyrelink"></a>

## Granblue Fantasy: Relink

`granbluefantasyrelink` · Steam 881020

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Reloaded-II + GBFR Mod Manager<br>`gbfr-reloaded` · 外部工具 | 原版 1.x；Endless Ragnarok 2.x 须兼容的新 manager<br>ModConfig.json + GBFR/data/... | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；先安装 Reloaded-II 与 gbfrelink.utility.manager；2.0 系列资产与表格式不同，不能承诺旧模组兼容。；Proton 使用官方 Linux 指南；ASI 注入时 Windows 映射盘和当前工作目录必须吻合，不能仅成功显示日志就声称载入。 | [源1](https://github.com/WistfulHopes/gbfrelink.utility.manager/blob/d30815669df03018be06fa426f6615235ca0c90b/README.md)、[源2](https://github.com/Nenkai/relink-modding/blob/main/docs/modding/installing_mods.md) |
| GBFRDataTools 手工资源工具链<br>`gbfr-tools` · 外部工具 | 按游戏 1.x / 2.x 架构匹配工具<br>data.i / extracted assets | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要原始资源解析与重新构建；保留外部工具，不自动修改原始 data.i。 | [源1](https://github.com/WistfulHopes/gbfrelink.utility.manager/blob/d30815669df03018be06fa426f6615235ca0c90b/README.md)、[源2](https://github.com/Nenkai/relink-modding/blob/main/docs/modding/installing_mods.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 截至核查 manager stable 2.1.0；上游 2026 年公开 issue 906 记录 Steam ASI 启动与映射盘问题，属于 Proton 未验证限制。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[WistfulHopes/gbfrelink.utility.manager](https://github.com/WistfulHopes/gbfrelink.utility.manager)：`{"repo":"WistfulHopes/gbfrelink.utility.manager","ref":"d30815669df03018be06fa426f6615235ca0c90b","release":"2.1.0","published_at":"2026-08-18T15:12:38Z","license":"MIT"}`；[Reloaded-Project/Reloaded-II](https://github.com/Reloaded-Project/Reloaded-II)：`{"repo":"Reloaded-Project/Reloaded-II","ref":"458987f26bc8d78fdc0f86b73fc0d6fd4b673d01","release":"1.31.0","published_at":"2026-09-23T00:49:27Z","license":"GPL-3.0"}`

<a id="game-finalfantasy15"></a>

## Final Fantasy XV Windows Edition

`finalfantasy15` · Steam 637650

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Flagrum 管理器包<br>`flagrum-package` · 外部工具 | FFXV Windows Edition；不同 Flagrum/游戏版本按作者校验<br>.fmod 或 Flagrum 明确声明的模组包 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；Flagrum 会处理数据归档与安装状态；不得把管理器源目录或模型源文件直接解压进根目录。 | [源1](https://github.com/Kizari/Flagrum/blob/c9e27a5bcfc9e12c49a2f3a5c24346c9543d7703/.github/README.md)、[源2](https://github.com/Kizari/Flagrum/wiki) |
| Steam Workshop 模组<br>`steam-workshop` · 外部工具 | Steam Workshop 支持的项目<br>Steam Workshop manifest | `由专用工具/作者说明决定，不猜路径`<br>由 Steam 订阅管理；Nexus ZIP 与 Workshop 内容不是相同安装协议。 | [源1](https://github.com/Kizari/Flagrum/blob/c9e27a5bcfc9e12c49a2f3a5c24346c9543d7703/.github/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- Flagrum 为 Windows .NET GUI 工具；本次没有证明其 GUI 或自动归档修改在 Steam Deck 上可用。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Kizari/Flagrum](https://github.com/Kizari/Flagrum)：`{"repo":"Kizari/Flagrum","ref":"c9e27a5bcfc9e12c49a2f3a5c24346c9543d7703","release":"v1.6.5","published_at":"2025-08-20T13:54:42Z","license":"GPL-3.0"}`

<a id="game-finalfantasy16"></a>

## Final Fantasy XVI

`finalfantasy16` · Steam 2515020

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Reloaded-II + FFXVI Loader<br>`ff16-reloaded` · 外部工具 | Steam 完整版；loader 1.2.1 按游戏当前更新核验<br>ModConfig.json + FF16 loader 数据 | `Reloaded/Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需外部 Reloaded-II 注册 ffxvi.exe 和兼容 loader；不能只解压 ModConfig.json 即标记游戏可用。 | [源1](https://github.com/Nenkai/ff16.utility.modloader/blob/566e1d378a0ed5d0f45673de49e863d7934b79ce/README.md) |
| FF16Tools 差异资源包<br>`ff16-diff-pac` · 手动说明 | FFXVI 当前机制；不泛化到 FFT 等其它游戏<br>*.diff.pac | `data`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；仅作者已构建完成且清楚标注的 diff.pac；相同 PAC 的多个模组可能冲突，应优先官方 loader。；语言包伴随 diff 主包、嵌套 .path 信息必须按作者说明保持。 | [源1](https://github.com/Nenkai/FF16Tools/blob/14361aefa1e1265096b42cad95cd9f01550a0457/README.md)、[源2](https://github.com/Nenkai/ff16.utility.modloader/blob/566e1d378a0ed5d0f45673de49e863d7934b79ce/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nenkai/ff16.utility.modloader](https://github.com/Nenkai/ff16.utility.modloader)：`{"repo":"Nenkai/ff16.utility.modloader","ref":"566e1d378a0ed5d0f45673de49e863d7934b79ce","release":"1.2.1","published_at":"2026-05-17T16:31:45Z","license":"MIT"}`；[Nenkai/FF16Tools](https://github.com/Nenkai/FF16Tools)：`{"repo":"Nenkai/FF16Tools","ref":"14361aefa1e1265096b42cad95cd9f01550a0457","release":"1.13.3","published_at":"2026-07-04T21:27:28Z","license":"MIT"}`；[Reloaded-Project/Reloaded-II](https://github.com/Reloaded-Project/Reloaded-II)：`{"repo":"Reloaded-Project/Reloaded-II","ref":"458987f26bc8d78fdc0f86b73fc0d6fd4b673d01","release":"1.31.0","published_at":"2026-09-23T00:49:27Z","license":"GPL-3.0"}`

<a id="game-nierautomata"></a>

## NieR:Automata

`nierautomata` · Steam 524220

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 明确游戏相对路径资源<br>`nier-root-layout` · 手动说明 | Steam 版本；不能自动视为 Game Pass 兼容<br>data/... 或明确根目录包 | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；不同版本的 FAR/Special K/LodMod 需求不同，不能混装代理 DLL。 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_nierautomata.py) |
| ASI 插件包<br>`nier-asi` · 手动说明 | 对应当前 Steam build 的插件<br>.asi + winmm.dll 等已声明加载器 | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；上游示例明确要求 winmm.dll；Proton override 必须依据实际代理名。 | [源1](https://github.com/illusionyy/Windows-Game-Patches/blob/c027e140e2b8a59a49e0a4824ac82e77938bf7c5/.github/README.md)、[源2](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-nierreplicant"></a>

## NieR Replicant ver.1.22474487139

`nierreplicant` · Steam 1113560

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 与独立配置<br>`replicant-asi` · 手动说明 | 作者匹配的 Steam build；示例为 v1.224 输入修复<br>.asi + .ini + winmm.dll | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；示例上游给出 winmm=n,b 的 Proton 设置，须与原启动参数合并；不能据此推定所有 MOD 都是该布局。 | [源1](https://github.com/teamawawa/nier-replicant-v1.224-simultaneous-input-fix/blob/main/README.md)、[源2](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| Special K 插件或独立启动器<br>`replicant-specialk` · 外部工具 | 按 MOD 的配置说明<br>.dll + Import 配置或自带 launcher | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；必须读取 MOD 明确需求；不自动运行未知注入器或修改原 EXE。 | [源1](https://github.com/ifa-ifa/NieR-Replicant-Hardcore-mod/blob/master/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-gta5"></a>

## Grand Theft Auto V (Legacy / Enhanced)

`gta5` · Steam 271590, 3240220

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI 插件与代理加载器<br>`gta-asi` · 手动说明 | Legacy 与 Enhanced 必须分别核对插件兼容<br>*.asi + 对应位数 ASI loader | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；不得覆盖已有 dinput8.dll；ScriptHookV 依赖及游戏 build 必须匹配。；仅单人使用说明须按具体 MOD 显示，不将任何客户端 MOD 用于 Online。 | [源1](https://github.com/Chiheb-Bacha/RageOpenV/blob/f742117a5e8ccc359bf3b4644c6bce7dad77cc7a/readme.md)、[源2](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| RageOpenV / RPF 资源覆盖<br>`gta-rpf` · 外部工具 | RageOpenV 自述支持 Legacy + Enhanced，具体资源仍须版本匹配<br>mods/... RPF 与资源 | `mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；RageOpenV 是开源替代加载器，但 README 明确要求链接官方发布而不要重分发其已编译二进制。；OpenIV 工具本身不能当作开源依赖；.oiv 安装清单、RPF 内部编辑需外部工具。 | [源1](https://github.com/Chiheb-Bacha/RageOpenV/blob/f742117a5e8ccc359bf3b4644c6bce7dad77cc7a/readme.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 同一游戏两个 AppID 属于发行版分支，不凑数计作两个游戏。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Chiheb-Bacha/RageOpenV](https://github.com/Chiheb-Bacha/RageOpenV)：`{"repo":"Chiheb-Bacha/RageOpenV","ref":"f742117a5e8ccc359bf3b4644c6bce7dad77cc7a","release":"v1.0","published_at":"2026-05-09T20:28:11Z","license":"GPL-3.0; upstream README additionally requests no binary redistribution"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-reddeadredemption2"></a>

## Red Dead Redemption 2

`reddeadredemption2` · Steam 1174180

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ASI / ScriptHookRDR2 包<br>`rdr2-asi` · 手动说明 | 作者明确支持的当前 RDR2 build<br>.asi + 对应 loader | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要匹配的 ScriptHook 等外部前置；不覆盖多个 MOD 共用代理 DLL。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-reddeadredemption2/index.js)、[源2](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| Lenny Mod Loader 资源<br>`rdr2-lml` · 外部工具 | 指定 LML 版本与游戏 build<br>lml/...; install.xml | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需外部 LML 解释 install.xml 和加载顺序；不能把 lml 文件任意改投 mods/。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-reddeadredemption2/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`；[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-bullyscholarshipedition"></a>

## Bully: Scholarship Edition

`bullyscholarshipedition` · Steam 12200

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| SilentPatch / ASI 包<br>`bully-asi` · 手动说明 | PC Scholarship Edition；按当前游戏 build 匹配<br>.asi + .ini + 对应 32 位代理 | `.`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留已有 ASI 共享加载器，位数必须匹配。 | [源1](https://github.com/CookiePLMonster/SilentPatchBully/blob/master/README.md)、[源2](https://github.com/ThirteenAG/Ultimate-ASI-Loader/blob/f9d13268f456076c9ff77201ed5a552e77ec559d/readme.md) |
| IMG/脚本资源外部编辑<br>`bully-resource` · 外部工具 | 作者指定的 Scholarship Edition 版本<br>.img/.lur/.lua 或第三方安装器 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；不能把任意散文件推断为可直接覆盖；使用作者指定的合并/导入工具。 | [源1](https://github.com/CookiePLMonster/SilentPatchBully/blob/master/README.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ThirteenAG/Ultimate-ASI-Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)：`{"repo":"ThirteenAG/Ultimate-ASI-Loader","ref":"f9d13268f456076c9ff77201ed5a552e77ec559d","release":"v9.7.4","published_at":"2026-08-16T12:01:51Z","license":"MIT"}`

<a id="game-kingdomcomedeliverance"></a>

## Kingdom Come Deliverance

`kingdomcomedeliverance` · Steam 379430

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 自包含资源 MOD 目录<br>`kcd-folder` · 可实现候选 | Steam PC；一代/二代包不能互换<br><mod>/mod.manifest + Data/*.pak | `Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；仅按明确的 mod 根目录安装，保留清单、Data、Localization；不将每个 .pak 拆成独立 MOD。；mod.manifest 为 XML；旧一代亦有无清单 pak/cfg，但新自动路线可保守要求有效清单。；一代 mod_order.txt 使用目录名，靠后的 MOD 覆盖优先；不要套用二代 modid 顺序规则。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-kingdomcome-deliverance/src/index.ts) |
| 加载顺序 / 配置 / 原文件替换<br>`kcd-order` · 手动说明 | 对应本作 mod_order.txt 机制<br>mod_order.txt/.cfg 或原文件补丁 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；顺序配置要保留非本插件条目，未实现事务化合并前只提供手动说明。；Game Pass KCD2 使用用户文档 kingdomcome_mods；不能套 Steam 根目录路径。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-kingdomcome-deliverance/src/index.ts) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`

<a id="game-kingdomcomedeliverance2"></a>

## Kingdom Come: Deliverance II

`kingdomcomedeliverance2` · Steam 1771300

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 自包含资源 MOD 目录<br>`kcd-folder` · 可实现候选 | Steam PC；一代/二代包不能互换<br><mod>/mod.manifest + Data/*.pak | `Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；仅按明确的 mod 根目录安装，保留清单、Data、Localization；不将每个 .pak 拆成独立 MOD。；标准文件名为 mod.manifest（XML）；优先解析 modid，缺失时不可猜测 ID 直接安装。；KCD2 的 mod_order.txt 使用 modid；必须识别并保留现存手工/Workshop 条目。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-kingdomcomedeliverance2/index.js) |
| 加载顺序 / 配置 / 原文件替换<br>`kcd-order` · 手动说明 | 对应本作 mod_order.txt 机制<br>mod_order.txt/.cfg 或原文件补丁 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；顺序配置要保留非本插件条目，未实现事务化合并前只提供手动说明。；Game Pass KCD2 使用用户文档 kingdomcome_mods；不能套 Steam 根目录路径。 | [源1](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games/blob/1e7bb7bd8afc93ba8d78d73e844cda62336552e7/game-kingdomcomedeliverance2/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ChemGuy1611/ChemBoy1-Vortex-Games](https://github.com/ChemGuy1611/ChemBoy1-Vortex-Games)：`{"repo":"ChemGuy1611/ChemBoy1-Vortex-Games","ref":"1e7bb7bd8afc93ba8d78d73e844cda62336552e7","release":null,"published_at":null,"license":"GPL-3.0"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`

<a id="game-mountandblade2bannerlord"></a>

## Mount & Blade II: Bannerlord

`mountandblade2bannerlord` · Steam 261550

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| SubModule 模块目录<br>`bannerlord-module` · 可实现候选 | Steam/GOG/Epic PC 版本；按 SubModule 依赖版本约束<br><Module>/SubModule.xml + bin/ModuleData/... | `Modules`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；识别 SubModule.xml 才路由到 Modules；名称、依赖与版本顺序不可丢失。；部署不代表启用：通过兼容启动器启用模块；不能自动误称插件排序已经生效。 | [源1](https://github.com/Nexus-Mods/NexusMods.App/blob/main/docs/developers/games/0004-MountAndBlade2Bannerlord.md)、[源2](https://github.com/Bannerlord-Modding/Documentation/blob/master/docs/_tutorials/packing_mods_for_vortex.md) |
| BLSE / Harmony 与启动器<br>`bannerlord-blse` · 外部工具 | 不同游戏 build 与 .NET 运行时；Xbox 与其它商店不同<br>BLSE launcher / bin helper | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；保留外部启动器和依赖安装；Steam 为 bin/Win64_Shipping_Client，Xbox 为 Gaming.Desktop.x64_Shipping_Client。 | [源1](https://github.com/Nexus-Mods/NexusMods.App/blob/main/docs/developers/games/0004-MountAndBlade2Bannerlord.md) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-kenshi"></a>

## Kenshi

`kenshi` · Steam 233860

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Kenshi .mod 同名目录<br>`kenshi-mod-folder` · 可实现候选 | Steam PC Kenshi；按作者当前版本要求<br><name>/<name>.mod + 资源 | `mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；以 .mod 所在目录为整体，不丢配套资源；目录名与模块名称要求必须校验。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-kenshi/src/index.js) |
| 启用与排序<br>`kenshi-load-order` · 手动说明 | Kenshi 启动器 / mods.cfg 机制<br>mods.cfg | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需要保存用户已有启用顺序；未实现并测试配置合并前由游戏启动器确认。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-kenshi/src/index.js) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-xcom2"></a>

## XCOM 2

`xcom2` · Steam 268500

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 原版模块<br>`xcom2-base` · 可实现候选 | XCOM 2 Base；排除 WotC 专用包<br><mod>/<mod>.XComMod + Config/Content | `XComGame/Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；读取 .XComMod；保留文件结构。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-xcom2/src/index.js) |
| War of the Chosen 模块<br>`xcom2-wotc` · 可实现候选 | XCOM 2 War of the Chosen；与原版独立兼容<br><mod>/<mod>.XComMod + Config/Content | `XCom2-WarOfTheChosen/XComGame/Mods`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；需确认 DLC 实际存在和 MOD 分支，不能仅按相同主 AppID 猜测安装位置。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-xcom2/src/index.js) |
| XComModOptions 启用 / AML<br>`xcom2-options` · 外部工具 | Steam Windows/Proton 与 Linux 原生配置位置不同<br>XComModOptions.ini 或 AML 配置 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；部署与启用分开；兼容 Feral Linux 原生版前不可使用 Windows 路径规则。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-xcom2/src/index.js)、[源2](https://github.com/X2CommunityCore/xcom2-launcher) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`

<a id="game-nomanssky"></a>

## No Man's Sky

`nomanssky` · Steam 275850

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 当前松散 MOD 数据目录<br>`nms-current` · 可实现候选 | 当前 Vortex/MO2 2026 源码路线；以具体 MOD 作者的资源版本为准<br>当前 MOD 数据树 | `GAMEDATA/MODS`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；新目录不能静默接收旧 .pak 并假称兼容。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-nomanssky/src/index.ts)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_nomanssky.py) |
| 旧 PAK MOD 路线<br>`nms-legacy-pak` · 可实现候选 | 历史 .pak 包；上游已标 deprecated<br>*.pak | `GAMEDATA/PCBANKS/MODS`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；检查匹配游戏版本与 DISABLEMODS.TXT；对开关改名必须备份、可撤销。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-nomanssky/src/index.ts) |
| MBIN 生成 / 资源冲突合并<br>`nms-merge` · 外部工具 | 按当前 MBINCompiler / AMUMSS 支持版本<br>.lua/.exml/.mbin 源或生成工具 | `由专用工具/作者说明决定，不猜路径`<br>MOD 必须匹配当前游戏发行版、更新和作者前置；不凭编号推定兼容性。；安装前预览文件并备份，禁用只撤销本插件拥有的文件。；源码与游戏就绪资源不同，不能把构建脚本当 MOD 直接解压启用。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-nomanssky/src/index.ts) |

- 核查日期 2026-10-19；只调研公开源码和官方 Steam 身份，未在游戏内验证。
- 已用当前源码证实新旧路径；没有凭印象标注某个游戏更新版本号作为切换阈值，须依包类型与作者声明选择。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":null,"published_at":null,"license":"GPL-3.0"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT"}`

