# RPG / Bethesda / FromSoftware 安装方式详细研究

核查日期：2026-10-19。返回 [113 款游戏索引](INSTALL_METHODS.md)。

未进行 Steam Deck 实机验证。下列“可实现候选”仅表示研究建议，不代表代码已实现或包一定兼容；真正能否部署由插件当前受限方案与安装预览决定。来源只用于参考公开行为与协议，不复制第三方实现，不捆绑闭源管理器或游戏/MOD 资源。

<a id="game-skyrimspecialedition"></a>

## Skyrim Special Edition

`skyrimspecialedition` · Steam 489830

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | SE 1.5.97；AE 1.6.x；Steam AE 1.7.104；GOG AE 单独匹配<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrimse/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | SE 1.5.97；AE 1.6.x；Steam AE 1.7.104；GOG AE 单独匹配<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrimse/src/index.js) |
| SKSE64按运行时安装<br>`skse64-runtime` · 外部工具 | SE1.5.97→SKSE2.0.20；历史Steam1.6.1170→2.2.6；当前Steam1.7.104→2.3.1；GOG: 官网1.6.1179与README1.6.1170冲突需人工确认<br>SKSE64 loader EXE/DLL + Data/Scripts | `游戏根目录 + Data/Scripts`<br>当前官方分发页优先于陈旧GitHub Releases；SKSE自定义分发限制：不随插件再分发，用户从作者官方源获取；现有启动项、DLL代理和Address Library必须保留并核对 | [源1](https://github.com/ianpatt/skse64/blob/25b72352adb6543fa6d0bd3795780672b2e238e0/skse64_readme.txt)、[源2](https://skse.silverlock.org/) |

- SE/AE共用489830，只计一个游戏；GitHub稳定tag2.2.6不等于当前官网2.3.1；官网GOG版本与仓库README存在冲突。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ianpatt/skse64](https://github.com/ianpatt/skse64/releases/tag/v2.2.6)：`{"repo":"ianpatt/skse64","ref":"25b72352adb6543fa6d0bd3795780672b2e238e0","release":"v2.2.6","published_at":"2024-01-17T20:28:38Z","license":"NOASSERTION","archived":false,"latest_prerelease":{"release":"v2.1.3","published_at":"2021-11-23T00:58:02Z","prerelease":true,"url":"https://github.com/ianpatt/skse64/releases/tag/v2.1.3"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-skyrim"></a>

## The Elder Scrolls V: Skyrim (Classic / Legendary)

`skyrim` · Steam 72850

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | Classic / Legendary 1.9.32<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrim/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | Classic / Legendary 1.9.32<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrim/src/index.js) |
| Classic SKSE<br>`skse-classic` · 外部工具 | 运行时1.9.32→SKSE1.7.3<br>32位SKSE EXE/DLL + scripts | `游戏根目录及Data/Scripts`<br>仅Classic/LE；不使用64位SKSE或VR构建；作者分发限制 | [源1](https://skse.silverlock.org/)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrim/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-skyrimvr"></a>

## The Elder Scrolls V: Skyrim VR

`skyrimvr` · Steam 611670

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | VR 1.4.15；与SE/AE区分<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrimvr/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | VR 1.4.15；与SE/AE区分<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrimvr/src/index.js) |
| SKSE VR<br>`skse-vr` · 外部工具 | VR1.4.15→SKSEVR2.0.12<br>SKSEVR loader EXE/DLL + scripts | `游戏根目录及Data/Scripts`<br>仅VR构建；SE/AE DLL不可混入VR | [源1](https://skse.silverlock.org/)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-skyrimvr/src/index.js) |

- Nexus从skyrimspecialedition共享页面下载时必须人工选择VR兼容文件。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-enderal"></a>

## Enderal: Forgotten Stories (Classic)

`enderal` · Steam 933480

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | Classic standalone / Skyrim LE-based<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-enderal/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | Classic standalone / Skyrim LE-based<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-enderal/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-fallout4"></a>

## Fallout 4

`fallout4` · Steam 377160

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | 旧版1.10.163；次世代1.10.984；当前1.11.240<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout4/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | 旧版1.10.163；次世代1.10.984；当前1.11.240<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout4/src/index.js) |
| F4SE运行时分支<br>`f4se-runtime` · 外部工具 | 1.10.163→0.6.23；1.10.984→0.7.2；1.11.240→0.7.9；VR1.2.72→VR0.6.21<br>对应运行时F4SE EXE/DLL + Data | `游戏根目录 + Data`<br>标准/VR分开；只安装与当前选定游戏运行时对应的分支；GitHubReleases停0.6.23，不能据此判断当前版本；不随插件重新分发加载器 | [源1](https://github.com/ianpatt/f4se/blob/6f6a7caa9aeaebc957a70d934b6ab6b80eb768b2/f4se_readme.txt)、[源2](https://f4se.silverlock.org/) |

- 新旧BA2格式、F4SE DLL与Address Library需分别匹配；更新游戏不表示旧MOD仍兼容。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ianpatt/f4se](https://github.com/ianpatt/f4se/releases/tag/v0.6.23)：`{"repo":"ianpatt/f4se","ref":"6f6a7caa9aeaebc957a70d934b6ab6b80eb768b2","release":"v0.6.23","published_at":"2022-06-21T01:44:27Z","license":null,"archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-fallout4vr"></a>

## Fallout 4 VR

`fallout4vr` · Steam 611660

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | VR1.2.72；不与标准FO4混装<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout4vr/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | VR1.2.72；不与标准FO4混装<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout4vr/src/index.js) |
| F4SE运行时分支<br>`f4se-runtime` · 外部工具 | 1.10.163→0.6.23；1.10.984→0.7.2；1.11.240→0.7.9；VR1.2.72→VR0.6.21<br>对应运行时F4SE EXE/DLL + Data | `游戏根目录 + Data`<br>标准/VR分开；只安装与当前选定游戏运行时对应的分支；GitHubReleases停0.6.23，不能据此判断当前版本；不随插件重新分发加载器 | [源1](https://github.com/ianpatt/f4se/blob/6f6a7caa9aeaebc957a70d934b6ab6b80eb768b2/f4se_readme.txt)、[源2](https://f4se.silverlock.org/) |

- 新旧BA2格式、F4SE DLL与Address Library需分别匹配；更新游戏不表示旧MOD仍兼容。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ianpatt/f4se](https://github.com/ianpatt/f4se/releases/tag/v0.6.23)：`{"repo":"ianpatt/f4se","ref":"6f6a7caa9aeaebc957a70d934b6ab6b80eb768b2","release":"v0.6.23","published_at":"2022-06-21T01:44:27Z","license":null,"archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-fallout3"></a>

## Fallout 3 / Game of the Year

`fallout3` · Steam 22300, 22370

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | Standard / GOTY；FOSE按运行时匹配<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout3/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | Standard / GOTY；FOSE按运行时匹配<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-fallout3/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-falloutnv"></a>

## Fallout: New Vegas

`falloutnv` · Steam 22380

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | Standard / Ultimate；NVSE按运行时匹配<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-falloutnv/src/index.ts) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | Standard / Ultimate；NVSE按运行时匹配<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-falloutnv/src/index.ts) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-oblivion"></a>

## The Elder Scrolls IV: Oblivion (2006)

`oblivion` · Steam 22330

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data资源文件<br>`bethesda-data` · 可实现候选 | 原版 / GOTY；不兼容Remastered<br>已明确以Data为根的散装textures/meshes/scripts及资源归档 | `Data`<br>确认游戏与MOD版本匹配；保留Data相对路径；DLL/EXE不作为普通资源处理；有FOMOD安装器或多个可选版本时必须选择分支，禁止全部解压 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-oblivion/src/index.js) |
| ESP/ESM/ESL与加载顺序<br>`bethesda-plugins` · 外部工具 | 原版 / GOTY；不兼容Remastered<br>esp/esm/esl + bsa/ba2（按具体游戏） | `Data + 当前游戏用户配置目录中的plugins.txt/loadorder`<br>先解析依赖、主文件和负载顺序；未实现相应格式前交由MO2/Vortex/LOOT外部流程；Classic/VR/新版本对ESL、归档头和原生扩展的支持不能互推 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-oblivion/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-enderalspecialedition"></a>

## Enderal: Forgotten Stories (Special Edition)

`enderalspecialedition` · Steam 976620

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Enderal SE数据层<br>`enderal-se-data` · 可实现候选 | Enderal SE Steam / GOG 独立分支<br>Enderal适用esp/esm/esl、bsa及textures/meshes/scripts | `Data`<br>Enderal专用MOD，不把SkyrimSE MOD默认视为兼容；不覆盖基础Enderal master | [源1](https://github.com/ModOrganizer2/modorganizer-game_enderalse/blob/51373ce843b3916ca0cf117cea41d47170bb9b77/src/gameenderalse.cpp)、[源2](https://github.com/ModOrganizer2/modorganizer-game_enderalse/blob/51373ce843b3916ca0cf117cea41d47170bb9b77/src/enderalsemoddatachecker.h) |
| 独立配置和SKSE入口<br>`enderal-se-profile` · 外部工具 | EnderalSE Steam / GOG<br>plugins.txt、loadorder及Enderal.ini | `Enderal Special Edition用户配置 / skse64_loader.exe`<br>该MO2插件仓库已归档且未检测到明确开源许可证，不复制代码；保持Enderal master与SkyUI主文件、Steam/GOG配置分开；当前运行时以游戏包为准 | [源1](https://github.com/ModOrganizer2/modorganizer-game_enderalse/blob/51373ce843b3916ca0cf117cea41d47170bb9b77/src/gameenderalse.cpp) |

- 976620与Classic933480独立识别；加载器不得因Skyrim官网更新而自动替换。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-game_enderalse](https://github.com/ModOrganizer2/modorganizer-game_enderalse/releases/tag/1.0.0b)：`{"repo":"ModOrganizer2/modorganizer-game_enderalse","ref":"51373ce843b3916ca0cf117cea41d47170bb9b77","release":"1.0.0b","published_at":"2021-02-24T21:53:30Z","license":null,"archived":true,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-oblivionremastered"></a>

## The Elder Scrolls IV: Oblivion Remastered

`oblivionremastered` · Steam 2623190

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 重制版Bethesda数据<br>`obvr-data` · 可实现候选 | Remastered；原版2006包不自动兼容<br>esp/esm及textures/meshes等 | `OblivionRemastered/Content/Dev/ObvData/Data`<br>ObvData是独立目标；插件加载顺序另行管理；依赖OBSE64时需专用配置 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_oblivion_remaster.py)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/oblivion_remaster/mod_data_checker.py) |
| 重制版Unreal资源<br>`obvr-paks` · 可实现候选 | Remastered按游戏更新匹配<br>pak，保留同名ucas/utoc成套文件 | `OblivionRemastered/Content/Paks/~mods`<br>仅资源包；同名成套文件必须完整；脚本/LogicMods不当作资源包 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_oblivion_remaster.py)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/oblivion_remaster/mod_data_checker.py) |
| 重制版UE4SS脚本<br>`obvr-ue4ss` · 外部工具 | MO2 basic_games 当前适配模型0.1.0-b.1；UE4SS按游戏构建<br>UE4SS Lua/C++及代理DLL | `OblivionRemastered/Binaries/Win64/ue4ss/Mods`<br>先安装对应构建UE4SS；合并DLL覆盖启动项；mod启用清单单独保存 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_oblivion_remaster.py)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/oblivion_remaster/mod_data_checker.py)、[源3](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 不能把Data、Paks、UE4SS三种归档统一解压到同一个根目录。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT","archived":false,"latest_prerelease":{"release":"experimental-latest","published_at":"2024-12-29T23:57:31Z","prerelease":true,"url":"https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental-latest"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-morrowind"></a>

## The Elder Scrolls III: Morrowind GOTY

`morrowind` · Steam 22320

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 原版Data Files<br>`morrowind-data` · 可实现候选 | 原版Morrowind/GOTY<br>esm/esp/bsa及textures/meshes等 | `Data Files`<br>MWSE与OpenMW Lua不是同一种脚本；插件配置另行管理 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-morrowind/src/index.ts) |
| OpenMW独立数据目录<br>`openmw` · 外部工具 | OpenMW0.51.0稳定；0.50及更旧需按MOD说明<br>目录型资源 + esp/esm/omwaddon/omwscripts等 | `用户选择的MOD目录 + openmw.cfg 的data/content配置`<br>先安装OpenMW；保留多data目录顺序；不改原版Morrowind.ini冒充OpenMW配置 | [源1](https://github.com/OpenMW/openmw/blob/e1b3589f169275af8264437c4e314fa8abdd6ba1/docs/source/reference/modding/mod-install.rst) |

- 原版游戏与OpenMW是不同运行方式；同AppID不能推定MWSE MOD兼容OpenMW。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[OpenMW/openmw](https://github.com/OpenMW/openmw/releases/tag/openmw-0.51.0)：`{"repo":"OpenMW/openmw","ref":"e1b3589f169275af8264437c4e314fa8abdd6ba1","release":"openmw-0.51.0","published_at":"2026-06-19T19:58:46Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"openmw-51-rc2","published_at":"2026-04-29T00:12:16Z","prerelease":true,"url":"https://github.com/OpenMW/openmw/releases/tag/openmw-51-rc2"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-starfield"></a>

## Starfield

`starfield` · Steam 1716740

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Starfield Data资源<br>`starfield-data` · 可实现候选 | 当前Steam/GOG安装，按具体游戏构建匹配<br>Data树、ba2、资源及插件 | `Data；另有Documents/My Games/Starfield/Data覆盖层`<br>先识别用户数据覆盖目录，不自动创建Windows junction到Linux路径；资源启用需Archive配置；esp/esm/esl加载顺序与SFSE另外处理 | [源1](https://github.com/Nexus-Mods/game-starfield/blob/ebea0bf2aa1e41f96f0c3fba8e5a58855466f3b7/src/index.ts)、[源2](https://github.com/Nexus-Mods/game-starfield/blob/ebea0bf2aa1e41f96f0c3fba8e5a58855466f3b7/src/common.ts) |
| SFSE / ASI / 加载顺序<br>`starfield-loader` · 外部工具 | SFSE按运行时分支；商店发行版不同<br>SFSE DLL/EXE、ASI、plugins.txt | `游戏根目录或Data/SFSE/Plugins，按包类型`<br>只用明确游戏版本的加载器；不自动执行归档中的程序；FOMOD和可选分支需要选择；不覆盖原配置 | [源1](https://github.com/Nexus-Mods/game-starfield/blob/ebea0bf2aa1e41f96f0c3fba8e5a58855466f3b7/src/index.ts)、[源2](https://github.com/Nexus-Mods/game-starfield/blob/ebea0bf2aa1e41f96f0c3fba8e5a58855466f3b7/src/common.ts) |

- Vortex monorepo中的Starfield只是跳转stub，实际安装证据取独立game-starfield源码。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/game-starfield](https://github.com/Nexus-Mods/game-starfield/releases/tag/v1.10.4)：`{"repo":"Nexus-Mods/game-starfield","ref":"ebea0bf2aa1e41f96f0c3fba8e5a58855466f3b7","release":"v1.10.4","published_at":"2024-12-12T11:00:05Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v0.6.2","published_at":"2023-12-04T09:22:26Z","prerelease":true,"url":"https://github.com/Nexus-Mods/game-starfield/releases/tag/v0.6.2"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-cyberpunk2077"></a>

## Cyberpunk 2077

`cyberpunk2077` · Steam 1091500

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 原生archive资源<br>`cp-archive` · 可实现候选 | 1.6.x旧版与2.x当前分支分开；依作者游戏版本<br>archive及ArchiveXL xl | `archive/pc/mod`<br>旧archive/pc/patch教程仅供历史；XL文件需要对应ArchiveXL依赖；2.x引擎更新可能改变archive内容；仅复制不证明兼容 | [源1](https://github.com/Nexus-Mods/game-cyberpunk2077/blob/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b/src/installer.archive.ts)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_cyberpunk2077.py) |
| 明确的脚本及原生目录包<br>`cp-canonical` · 外部工具 | CET/redscript/RED4ext各版本需匹配游戏运行时<br>CET init.lua / .reds / RED4ext DLL | `bin/x64/plugins/cyber_engine_tweaks/mods；r6/scripts；red4ext/plugins`<br>识别规范目录才能保留树部署，不能把任意Lua/DLL猜成CET/RED4ext；前置组件、启动项和DLL冲突先检查；同包可含多类型 | [源1](https://github.com/Nexus-Mods/game-cyberpunk2077/blob/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b/src/installer.cet.ts)、[源2](https://github.com/Nexus-Mods/game-cyberpunk2077/blob/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b/src/installer.redscript.ts)、[源3](https://github.com/Nexus-Mods/game-cyberpunk2077/blob/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b/src/installer.red4ext.ts) |
| REDmod部署<br>`cp-redmod` · 外部工具 | 支持REDmod的游戏版本；区别于普通archive模组<br>mods/<name>/info.json及assets | `mods/<name> + REDmod部署输出`<br>需REDmod DLC与部署编译，不是复制info.json即生效；不将REDmod与legacy archive重复安装 | [源1](https://github.com/Nexus-Mods/game-cyberpunk2077/blob/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b/src/installer.redmod.ts) |

- 独立Cyberpunk扩展当前代码比Vortex内置stub详细；规范目录之外的可选布局不能猜。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/game-cyberpunk2077](https://github.com/Nexus-Mods/game-cyberpunk2077/commit/0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b)：`{"repo":"Nexus-Mods/game-cyberpunk2077","ref":"0ddc3e8a9c593dd6cf144d67739d9a9986d95f3b","release":null,"published_at":null,"license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"source_only"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-witcher3"></a>

## The Witcher 3

`witcher3` · Steam 292030

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Mods与DLC资源<br>`w3-resources` · 可实现候选 | Classic1.x(含1.32)；Next-Gen4.x；Remastered5.0<br>mod<name>/content及dlc<name>树 | `Mods/mod<name>；DLC/dlc<name>`<br>先判别版本；相同目录/资源冲突需预览；版本分支不能混装；Remastered5.0目录和游戏内MOD总开关不同，目录名称最多63字符按当前适配器处理 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher3/src/index.ts)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher3/src/edition.ts)、[源3](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher3/src/installers.ts) |
| 脚本、菜单和配置合并<br>`w3-scriptmerge` · 外部工具 | 1.x/4.x legacy分支；5.0 remastered分支<br>ws脚本、配置matrix XML及input配置 | `Mods/DLC/bin/config及用户Documents配置`<br>需Script Merger或版本对应的合并器；禁止纯覆盖脚本文件解决冲突；5.0没有DX11及graphicsdx11.xml；不能继续硬编码bin/x64启动 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher3/src/edition.ts)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher3/src/scriptmerger.ts) |

- Steam官方appdetails已显示Remastered；不能把“最新”固定为4.04。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-witcher2"></a>

## The Witcher 2: Assassins of Kings Enhanced Edition

`witcher2` · Steam 20920

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| CookedPC资源<br>`w2-cooked` · 可实现候选 | Enhanced Edition；包需匹配游戏版本<br>dzip及原生CookedPC资源 | `CookedPC`<br>保持包要求的相对目录；脚本/配置安装不能任意覆盖用户ini | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher2/src/index.js)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_witcher2.py) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-witcher"></a>

## The Witcher: Enhanced Edition

`witcher` · Steam 20900

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Data Override<br>`w1-override` · 可实现候选 | Enhanced Edition<br>作者规定的override资源目录 | `Data/Override`<br>只处理明确override资源；附加冒险和整包替换走作者流程 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-witcher/src/index.js)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_witcher1.py) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-baldursgate3"></a>

## Baldur's Gate 3

`baldursgate3` · Steam 1086940

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| PAK与模组元数据<br>`bg3-paks` · 外部工具 | Patch6及更旧格式；Patch7格式；Patch8格式<br>Larian PAK、meta.lsx UUID/dependency metadata | `Proton用户LocalAppData/Larian Studios/Baldur's Gate 3/Mods`<br>必须读取PAK元数据及依赖；不能把UE PAK安装器用于Larian PAK；按Patch生成modsettings.lsx并保留既有项目；未实现前交由BG3MM/MO2/Vortex | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-baldursgate3/src/index.tsx)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-baldursgate3/src/util.ts)、[源3](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/baldursgate3/bg3_file_mapper.py) |
| Native DLL与Script Extender<br>`bg3-native` · 外部工具 | 按游戏Patch和构建；原生Linux/macOS版本另行验证<br>DWrite.dll / NativeMods / Data loose | `bin及Data等作者指定目录`<br>Script Extender DLL不放到用户Mods目录；需对应版本及Proton DLL覆盖；Patch7/8游戏内管理器、Steam Workshop与外部清单不能互相清空 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-baldursgate3/src/index.tsx)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-baldursgate3/src/installers.ts) |

- 当前上游明确区分Patch6/7/8；不能统一套旧modsettings模板。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-divinityoriginalsin2"></a>

## Divinity Original Sin 2

`divinityoriginalsin2` · Steam 435150

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Definitive PAK<br>`dos2-de` · 外部工具 | Definitive Edition<br>Larian .pak + 模组/依赖元数据 | `Proton Documents/Larian Studios/Divinity Original Sin 2 Definitive Edition/Mods`<br>需要在对应Profile中启用；modsettings.lsx备份合并，不能照搬BG3 Patch8格式 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-divinityoriginalsin2/src/index.js) |
| Classic PAK<br>`dos2-classic` · 外部工具 | Classic/original分支；与DE分别下载<br>Larian .pak | `Proton Documents/Larian Studios/Divinity Original Sin 2/Mods`<br>Classic Nexus域名divinityoriginalsin2；与DE域名divinityoriginalsin2definitiveedition区分；二者共用435150，不能创建冲突的自动识别条目 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-divinityoriginalsin2/src/index.js) |

- 本项只计一款游戏，包含同AppID的Classic/Definitive方法分支。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 此发行版研究归入已有 divinityoriginalsin2 身份；保留原游戏 ID、Nexus 域名与 MOD 记录。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-divinityoriginalsinenhancededition"></a>

## Divinity: Original Sin Enhanced Edition

`divinityoriginalsinenhancededition` · Steam 373420

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Enhanced游戏Data层<br>`dos-ee-data` · 可实现候选 | Enhanced Edition；不与原版Classic混用<br>pak与Public/Localization/Engine等规范目录 | `Data`<br>不同类型包可能为文档Mods安装，不强制所有pak去同一目录 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_divinityoriginalsinee.py) |
| 文档Mods层<br>`dos-ee-docmods` · 外部工具 | Enhanced Edition<br>MO2 DOCS_MOD包装的内容型mod | `Documents/Larian Studios/Divinity Original Sin Enhanced Edition/Mods`<br>需要对应用户配置与依赖，先识别DOCS_MOD/作者说明；不猜裸pak性质 | [源1](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_divinityoriginalsinee.py) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-eldenring"></a>

## ELDEN RING

`eldenring` · Steam 1245620

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| me3隔离Profile<br>`me3-profile` · 外部工具 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对<br>TOML .me3：packages目录 + natives DLL列表 | `独立mod目录与.me3文件；不覆盖游戏原档`<br>先安装官方me3 Linux版本并用该游戏profile启动；packages和natives明确区分；不默认合并同名regulation.bin或相同资产；保持官方服务器离线默认；保存文件可用独立savefile；不自动改为online | [源1](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/configuration-reference.md)、[源2](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/crates/mod-protocol/src/game.rs)、[源3](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/user-guide/installation.md) |
| 历史ModEngine2方案<br>`modengine2-legacy` · 外部工具 | ModEngine2 release-2.1.0；维护已停止<br>TOML配置 + mod目录 + external DLL | `ModEngine2独立目录并通过launcher启动`<br>只用于明确要求ME2的MOD；不称为最新；按作者配置启动；ME2 README支持列表与某些发行包AC6差异需按具体包核实，不默认泛用 | [源1](https://github.com/soulsmods/ModEngine2/blob/4f701ccd0e2f6ddb106f17050dfd7fca036bb244/README.md) |

- me3当前源码明确支持DS3/Sekiro/ER/AC6/Nightreign五款；不据此推定DSR或DS2受支持。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[garyttierney/me3](https://github.com/garyttierney/me3/releases/tag/v0.13.0)：`{"repo":"garyttierney/me3","ref":"5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5","release":"v0.13.0","published_at":"2026-08-11T22:32:19Z","license":"Apache-2.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`；[soulsmods/ModEngine2](https://github.com/soulsmods/ModEngine2/releases/tag/release-2.1.0)：`{"repo":"soulsmods/ModEngine2","ref":"4f701ccd0e2f6ddb106f17050dfd7fca036bb244","release":"release-2.1.0","published_at":"2023-09-01T04:29:34Z","license":"MIT","archived":true,"latest_prerelease":{"release":"preview4","published_at":"2022-08-26T17:07:25Z","prerelease":true,"url":"https://github.com/soulsmods/ModEngine2/releases/tag/preview4"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-eldenringnightreign"></a>

## ELDEN RING NIGHTREIGN

`eldenringnightreign` · Steam 2622380

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| me3隔离Profile<br>`me3-profile` · 外部工具 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对<br>TOML .me3：packages目录 + natives DLL列表 | `独立mod目录与.me3文件；不覆盖游戏原档`<br>先安装官方me3 Linux版本并用该游戏profile启动；packages和natives明确区分；不默认合并同名regulation.bin或相同资产；保持官方服务器离线默认；保存文件可用独立savefile；不自动改为online | [源1](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/configuration-reference.md)、[源2](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/crates/mod-protocol/src/game.rs)、[源3](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/user-guide/installation.md) |

- me3当前源码明确支持DS3/Sekiro/ER/AC6/Nightreign五款；不据此推定DSR或DS2受支持。
- Nightreign独立Steam2622380及Nexus域名；不能把EldenRing1245620的regulation.bin或DLL直接安装过去。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[garyttierney/me3](https://github.com/garyttierney/me3/releases/tag/v0.13.0)：`{"repo":"garyttierney/me3","ref":"5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5","release":"v0.13.0","published_at":"2026-08-11T22:32:19Z","license":"Apache-2.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-darksouls3"></a>

## DARK SOULS III

`darksouls3` · Steam 374320

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| me3隔离Profile<br>`me3-profile` · 外部工具 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对<br>TOML .me3：packages目录 + natives DLL列表 | `独立mod目录与.me3文件；不覆盖游戏原档`<br>先安装官方me3 Linux版本并用该游戏profile启动；packages和natives明确区分；不默认合并同名regulation.bin或相同资产；保持官方服务器离线默认；保存文件可用独立savefile；不自动改为online | [源1](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/configuration-reference.md)、[源2](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/crates/mod-protocol/src/game.rs)、[源3](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/user-guide/installation.md) |
| 历史ModEngine2方案<br>`modengine2-legacy` · 外部工具 | ModEngine2 release-2.1.0；维护已停止<br>TOML配置 + mod目录 + external DLL | `ModEngine2独立目录并通过launcher启动`<br>只用于明确要求ME2的MOD；不称为最新；按作者配置启动；ME2 README支持列表与某些发行包AC6差异需按具体包核实，不默认泛用 | [源1](https://github.com/soulsmods/ModEngine2/blob/4f701ccd0e2f6ddb106f17050dfd7fca036bb244/README.md) |

- me3当前源码明确支持DS3/Sekiro/ER/AC6/Nightreign五款；不据此推定DSR或DS2受支持。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[garyttierney/me3](https://github.com/garyttierney/me3/releases/tag/v0.13.0)：`{"repo":"garyttierney/me3","ref":"5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5","release":"v0.13.0","published_at":"2026-08-11T22:32:19Z","license":"Apache-2.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`；[soulsmods/ModEngine2](https://github.com/soulsmods/ModEngine2/releases/tag/release-2.1.0)：`{"repo":"soulsmods/ModEngine2","ref":"4f701ccd0e2f6ddb106f17050dfd7fca036bb244","release":"release-2.1.0","published_at":"2023-09-01T04:29:34Z","license":"MIT","archived":true,"latest_prerelease":{"release":"preview4","published_at":"2022-08-26T17:07:25Z","prerelease":true,"url":"https://github.com/soulsmods/ModEngine2/releases/tag/preview4"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-sekiro"></a>

## Sekiro Shadows Die Twice

`sekiro` · Steam 814380

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| me3隔离Profile<br>`me3-profile` · 外部工具 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对<br>TOML .me3：packages目录 + natives DLL列表 | `独立mod目录与.me3文件；不覆盖游戏原档`<br>先安装官方me3 Linux版本并用该游戏profile启动；packages和natives明确区分；不默认合并同名regulation.bin或相同资产；保持官方服务器离线默认；保存文件可用独立savefile；不自动改为online | [源1](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/configuration-reference.md)、[源2](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/crates/mod-protocol/src/game.rs)、[源3](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/user-guide/installation.md) |
| 历史Sekiro ModEngine<br>`sekiro-legacy` · 外部工具 | 旧版0.1.x加载器；me3迁移需作者确认<br>dinput8.dll、modengine.ini、mods目录 | `游戏根目录 + mods`<br>不可与另一dinput8代理直接覆盖；已有启动项需合并；上游旧源码无明确许可证不复制实现 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-sekiro/src/index.js)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_sekiroshadowsdietwice.py) |

- me3当前源码明确支持DS3/Sekiro/ER/AC6/Nightreign五款；不据此推定DSR或DS2受支持。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[garyttierney/me3](https://github.com/garyttierney/me3/releases/tag/v0.13.0)：`{"repo":"garyttierney/me3","ref":"5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5","release":"v0.13.0","published_at":"2026-08-11T22:32:19Z","license":"Apache-2.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`；[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-armoredcore6"></a>

## ARMORED CORE VI FIRES OF RUBICON

`armoredcore6` · Steam 1888160

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| me3隔离Profile<br>`me3-profile` · 外部工具 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对<br>TOML .me3：packages目录 + natives DLL列表 | `独立mod目录与.me3文件；不覆盖游戏原档`<br>先安装官方me3 Linux版本并用该游戏profile启动；packages和natives明确区分；不默认合并同名regulation.bin或相同资产；保持官方服务器离线默认；保存文件可用独立savefile；不自动改为online | [源1](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/configuration-reference.md)、[源2](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/crates/mod-protocol/src/game.rs)、[源3](https://github.com/garyttierney/me3/blob/5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5/docs/user-guide/installation.md) |

- me3当前源码明确支持DS3/Sekiro/ER/AC6/Nightreign五款；不据此推定DSR或DS2受支持。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[garyttierney/me3](https://github.com/garyttierney/me3/releases/tag/v0.13.0)：`{"repo":"garyttierney/me3","ref":"5f4fa47fad537b915fa9dbc01a9fb91b8a081bb5","release":"v0.13.0","published_at":"2026-08-11T22:32:19Z","license":"Apache-2.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-darksoulsremastered"></a>

## DARK SOULS REMASTERED

`darksoulsremastered` · Steam 570940

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| DSR纹理覆盖重打包<br>`dsr-textures` · 外部工具 | DSR；工具历史稳定1.5，仓库已归档<br>Texture Override/<chr\|map\|obj\|...>纹理 | `外部工具重打包原游戏资源并备份`<br>用DSR-TPUP指定含DarkSoulsRemastered.exe的目录；修改会触及原资源，需备份与Restore；不把DS1 PTDE的UnpackDarkSoulsForModding流程套用到Remastered | [源1](https://github.com/JKAnderson/DSR-TPUP/blob/844ed9336d528d9aa6704a28338599b29451dd48/readme.md) |
| 作者指定整包/根目录方案<br>`dsr-author-root` · 手动说明 | 具体整合包的当前版本<br>作者明确要求的目录、DLL、资源 | `用户确认的游戏根目录`<br>仅手动根目录模式；不声称me3/ME2支持该游戏；不能从任意parts/chr文件猜是否无需解包即可生效 | [源1](https://github.com/JKAnderson/DSR-TPUP/blob/844ed9336d528d9aa6704a28338599b29451dd48/readme.md)、[源2](https://github.com/soulsmods/ModEngine2/blob/4f701ccd0e2f6ddb106f17050dfd7fca036bb244/README.md) |

- 当前没有在me3稳定支持列表发现DSR，保持外部工具与手动路径。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[JKAnderson/DSR-TPUP](https://github.com/JKAnderson/DSR-TPUP/releases/tag/1.5)：`{"repo":"JKAnderson/DSR-TPUP","ref":"844ed9336d528d9aa6704a28338599b29451dd48","release":"1.5","published_at":"2018-07-14T11:58:19Z","license":"GPL-3.0","archived":true,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[soulsmods/ModEngine2](https://github.com/soulsmods/ModEngine2/releases/tag/release-2.1.0)：`{"repo":"soulsmods/ModEngine2","ref":"4f701ccd0e2f6ddb106f17050dfd7fca036bb244","release":"release-2.1.0","published_at":"2023-09-01T04:29:34Z","license":"MIT","archived":true,"latest_prerelease":{"release":"preview4","published_at":"2022-08-26T17:07:25Z","prerelease":true,"url":"https://github.com/soulsmods/ModEngine2/releases/tag/preview4"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-darksouls2"></a>

## Dark Souls II

`darksouls2` · Steam 236430

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 已证实的Game目录资源替换<br>`ds2-known-files` · 可实现候选 | 32位原版/DX9<br>完整规范Game目录或明确的enc_regulation.bnd.dcx | `Game`<br>保持Game前缀仅一层，避免Game/Game；需要当前游戏分支对应的MOD；普通模型bnd/原始dds不可当成原生loose replacer | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/index.ts)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/installers.ts) |
| 注入器、纹理和内容加载器<br>`ds2-loader` · 外部工具 | 32位原版/DX9<br>ModEngine / LightingEngine / iGP11 / GeDoSaTo等各自格式 | `Game或特定工具的tex_override/modoverride配置目录`<br>原版与Scholar架构和渲染器不同；先确认对应加载器已安装；me3没有该游戏；DX9 GeDoSaTo不能泛用于Scholar；同名DLL不可互相覆盖 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/installers.ts)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_darksouls2sotfs.py) |

- 同Nexus域名但236430与335300必须独立识别；下载文件版本不能仅凭MOD编号决定。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-darksouls2sotfs"></a>

## DARK SOULS II Scholar of the First Sin

`darksouls2sotfs` · Steam 335300

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 已证实的Game目录资源替换<br>`ds2-known-files` · 可实现候选 | 64位Scholar/DX11<br>完整规范Game目录或明确的enc_regulation.bnd.dcx | `Game`<br>保持Game前缀仅一层，避免Game/Game；需要当前游戏分支对应的MOD；普通模型bnd/原始dds不可当成原生loose replacer | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/index.ts)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/installers.ts) |
| 注入器、纹理和内容加载器<br>`ds2-loader` · 外部工具 | 64位Scholar/DX11<br>ModEngine / LightingEngine / iGP11 / GeDoSaTo等各自格式 | `Game或特定工具的tex_override/modoverride配置目录`<br>原版与Scholar架构和渲染器不同；先确认对应加载器已安装；me3没有该游戏；DX9 GeDoSaTo不能泛用于Scholar；同名DLL不可互相覆盖 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-darksouls2/src/installers.ts)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_darksouls2sotfs.py) |

- 同Nexus域名但236430与335300必须独立识别；下载文件版本不能仅凭MOD编号决定。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-dragonage"></a>

## Dragon Age Origins

`dragonage` · Steam 17450, 47810

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 用户文档Override<br>`da-override` · 手动说明 | 对应原版/Ultimate<br>明确override文件树 | `Proton Documents/BioWare/Dragon Age/packages/core/override`<br>目标在游戏Proton用户目录，不在游戏根目录；解析实际用户Documents映射；依赖erf/dazip和manifest的包不可按loose override处理 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragonage/src/index.js) |
| DAZIP/AddIns注册<br>`da-dazip` · 外部工具 | 按游戏和DLC版本<br>dazip、manifest.xml及AddIns元数据 | `Documents/BioWare/Dragon Age的AddIns/Settings及对应安装结构`<br>需解析和合并AddIns.xml；保持已装DLC和用户清单；DAZIP不是重命名ZIP后全解压；禁用/卸载应回滚注册信息 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragonage/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-dragonage2"></a>

## Dragon Age II / Ultimate

`dragonage2` · Steam 1238040

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 用户文档Override<br>`da-override` · 手动说明 | 对应原版/Ultimate<br>明确override文件树 | `Proton Documents/BioWare/Dragon Age 2/packages/core/override`<br>目标在游戏Proton用户目录，不在游戏根目录；解析实际用户Documents映射；依赖erf/dazip和manifest的包不可按loose override处理 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragonage2/src/index.js) |
| DAZIP/AddIns注册<br>`da-dazip` · 外部工具 | 按游戏和DLC版本<br>dazip、manifest.xml及AddIns元数据 | `Documents/BioWare/Dragon Age 2的AddIns/Settings及对应安装结构`<br>需解析和合并AddIns.xml；保持已装DLC和用户清单；DAZIP不是重命名ZIP后全解压；禁用/卸载应回滚注册信息 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-dragonage2/src/index.js) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-dragonageinquisition"></a>

## Dragon Age: Inquisition

`dragonageinquisition` · Steam 1222690

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Frosty稳定外部工具<br>`frosty-stable` · 外部工具 | 旧Frosty1.0.6.3；按游戏profile<br>fbmod/fbarchive | `Frosty库 → 生成ModData`<br>fbmod需处理资源合并及生成ModData，不可直接解压到根目录；EA启动器、Proton依赖及游戏profile需外部配置；当前没有设备验证 | [源1](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/README.md)、[源2](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/README.md)、[源3](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/Profiles/DragonAgeInquisition.json) |
| Frosty .NET8开发CLI<br>`frosty-next` · 外部工具 | 未正式发布的master重写；不默认安装<br>新版fbmod；旧1.0.x须update-mod转换 | `FrostyCli mod生成ModData + -dataPath或GAME_DATA_DIR`<br>新仓库README明确开发状态，没有正式release或功能完整UI；Linux依游戏Frostbite版本需bcrypt.dll覆写；仅给出研究入口，未实装自动编译/启动修改 | [源1](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/README.md)、[源2](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/README.md)、[源3](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/Profiles/DragonAgeInquisition.json) |
| 历史DAIMod分支<br>`dai-legacy` · 外部工具 | 只适用于.daimod作者指定的DAI构建/补丁<br>daimod | `DAI Mod Manager合并补丁目录`<br>与fbmod为不同工具格式，不把后缀改名；该类保留外部工具入口；本轮未找到可充分核验且可直接复用的当前开源DAIMod安装器，不自动安装 | [源1](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/README.md)、[源2](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/README.md) |

- 稳定旧版与未发布新重写必须分开；不将存在源码等同于能在SteamOS自动安装。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[FrostyToolsuite/FrostyToolsuite](https://github.com/FrostyToolsuite/FrostyToolsuite/commit/ee2a587af394fc784b309bb7990dab051065330f)：`{"repo":"FrostyToolsuite/FrostyToolsuite","ref":"ee2a587af394fc784b309bb7990dab051065330f","release":null,"published_at":null,"license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"source_only"}`；[CadeEvs/FrostyToolsuite](https://github.com/CadeEvs/FrostyToolsuite/releases/tag/v1.0.6.3)：`{"repo":"CadeEvs/FrostyToolsuite","ref":"e400dcb283ad743071263ea7b34ff86780ffe910","release":"v1.0.6.3","published_at":"2023-09-29T11:45:15Z","license":null,"archived":false,"latest_prerelease":{"release":"v1.0.6.3-beta2","published_at":"2023-09-17T17:04:35Z","prerelease":true,"url":"https://github.com/CadeEvs/FrostyToolsuite/releases/tag/v1.0.6.3-beta2"},"checked_at":"2026-10-19","source_branch":"1.0.6.3","channel":"stable_and_source"}`

<a id="game-masseffectandromeda"></a>

## Mass Effect: Andromeda

`masseffectandromeda` · Steam 1238000

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Frosty稳定外部工具<br>`frosty-stable` · 外部工具 | 旧Frosty1.0.6.3；按游戏profile<br>fbmod/fbarchive | `Frosty库 → 生成ModData`<br>fbmod需处理资源合并及生成ModData，不可直接解压到根目录；EA启动器、Proton依赖及游戏profile需外部配置；当前没有设备验证 | [源1](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/README.md)、[源2](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/README.md)、[源3](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/Profiles/Mea.json) |
| Frosty .NET8开发CLI<br>`frosty-next` · 外部工具 | 未正式发布的master重写；不默认安装<br>新版fbmod；旧1.0.x须update-mod转换 | `FrostyCli mod生成ModData + -dataPath或GAME_DATA_DIR`<br>新仓库README明确开发状态，没有正式release或功能完整UI；Linux依游戏Frostbite版本需bcrypt.dll覆写；仅给出研究入口，未实装自动编译/启动修改 | [源1](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/README.md)、[源2](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/README.md)、[源3](https://github.com/FrostyToolsuite/FrostyToolsuite/blob/ee2a587af394fc784b309bb7990dab051065330f/FrostyCli/Profiles/Mea.json) |

- 稳定旧版与未发布新重写必须分开；不将存在源码等同于能在SteamOS自动安装。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[FrostyToolsuite/FrostyToolsuite](https://github.com/FrostyToolsuite/FrostyToolsuite/commit/ee2a587af394fc784b309bb7990dab051065330f)：`{"repo":"FrostyToolsuite/FrostyToolsuite","ref":"ee2a587af394fc784b309bb7990dab051065330f","release":null,"published_at":null,"license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"source_only"}`；[CadeEvs/FrostyToolsuite](https://github.com/CadeEvs/FrostyToolsuite/releases/tag/v1.0.6.3)：`{"repo":"CadeEvs/FrostyToolsuite","ref":"e400dcb283ad743071263ea7b34ff86780ffe910","release":"v1.0.6.3","published_at":"2023-09-29T11:45:15Z","license":null,"archived":false,"latest_prerelease":{"release":"v1.0.6.3-beta2","published_at":"2023-09-17T17:04:35Z","prerelease":true,"url":"https://github.com/CadeEvs/FrostyToolsuite/releases/tag/v1.0.6.3-beta2"},"checked_at":"2026-10-19","source_branch":"1.0.6.3","channel":"stable_and_source"}`

<a id="game-masseffectlegendaryedition"></a>

## Mass Effect Legendary Edition (LE1 / LE2 / LE3)

`masseffectlegendaryedition` · Steam 1328670

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ME3Tweaks内容安装<br>`me3tweaks` · 外部工具 | M3稳定9.2.1.137；LE1/LE2/LE3分别选择<br>moddesc.ini及DLC内容/配置合并 | `按moddesc目标LE1/LE2/LE3生成DLC与对应游戏数据`<br>必须读取Game/安装目标/替代项；不能把三作混到统一根目录；Mod Manager负责备份、整合和原档恢复；不以普通文件禁用承诺复原所有二进制合并 | [源1](https://github.com/ME3Tweaks/ME3TweaksModManager/blob/1c98d93e410c589cf48624e7e13aec02079d3bcd/README.md)、[源2](https://github.com/ME3Tweaks/ME3TweaksModManager/blob/1c98d93e410c589cf48624e7e13aec02079d3bcd/MassEffectModManagerCore/modmanager/installer/ModInstaller.cs)、[源3](https://github.com/ME3Tweaks/ME3TweaksModManager/blob/staticfiles/documentation/moddesc.ini.md) |
| MEM纹理安装<br>`mass-effect-mem` · 外部工具 | MEM稳定534；LE1/LE2/LE3分开<br>mem纹理包与替换资源 | `由MEM重打包到对应游戏资源`<br>纹理修改会改写游戏资产，必须完整备份；安装顺序依MOD要求；与内容MOD部署阶段不同，不提供虚假的无损toggle | [源1](https://github.com/MassEffectModder/MassEffectModder/blob/4364093b2d6c1bbeaf6d3ee40f1a0a9b56b5b2c1/README.md) |

- MO2 basic_games的ME Legendary条目在quarantine目录，不把它视为完成可用的最新适配。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ME3Tweaks/ME3TweaksModManager](https://github.com/ME3Tweaks/ME3TweaksModManager/releases/tag/9.2.1.137)：`{"repo":"ME3Tweaks/ME3TweaksModManager","ref":"1c98d93e410c589cf48624e7e13aec02079d3bcd","release":"9.2.1.137","published_at":"2026-07-26T03:16:44Z","license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"M3Core","channel":"stable_and_source"}`；[MassEffectModder/MassEffectModder](https://github.com/MassEffectModder/MassEffectModder/releases/tag/534)：`{"repo":"MassEffectModder/MassEffectModder","ref":"4364093b2d6c1bbeaf6d3ee40f1a0a9b56b5b2c1","release":"534","published_at":"2026-04-02T20:46:15Z","license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-dragonsdogma2"></a>

## Dragon's Dogma 2

`dragonsdogma2` · Steam 2054970

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework Lua脚本<br>`reframework-lua` · 可实现候选 | 对应游戏的REFramework构建；稳定/开发nightly分开<br>Lua脚本与显式reframework目录 | `reframework/autorun`<br>需要该游戏专用REFramework dinput8.dll，启动项保留并合并；不把MHR/MHWilds/DD2 DLL互换；有脚本前置库需一并核验 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/ScriptRunner.cpp) |
| REFramework原生插件<br>`reframework-native` · 外部工具 | 按游戏更新/REF版本/插件ABI匹配<br>dll插件和对应依赖 | `reframework/plugins`<br>先确定x64架构及目标游戏；任何DLL都不自动执行；与插帧、ReShade或其他dinput8代理需冲突处理，不能覆写 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md) |
| RE Engine资源包<br>`reengine-resource` · 外部工具 | Rise基础/Sunbreak、Wilds更新、DD2更新分别选择<br>natives资源树、RE PAK / Fluffy包 | `由作者规定的资源加载器/Fluffy部署目标决定`<br>RE资源PAK不是Unreal PAK；不使用UE的~mods算法；本轮未核验可安全泛化的原生RE资源自动激活路线，保留外部工具和显式根目录预览 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md) |

- REFramework稳定v1.5.9.1与2026 nightly分开：旧stable可能没有新游戏更新支持，不能自动选旧stable。
- nightly仓库GitHub prerelease标志为false仍是开发通道，必须按仓库/发行名称标明nightly。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework/releases/tag/v1.5.9.1)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly/releases/tag/nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee)：`{"repo":"praydog/REFramework-nightly","ref":"0436e043af6f81a5d3fef49ae27d35e63431e566","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"nightly"}`

<a id="game-monsterhunterrise"></a>

## MONSTER HUNTER RISE / Sunbreak

`monsterhunterrise` · Steam 1446780

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework Lua脚本<br>`reframework-lua` · 可实现候选 | 对应游戏的REFramework构建；稳定/开发nightly分开<br>Lua脚本与显式reframework目录 | `reframework/autorun`<br>需要该游戏专用REFramework dinput8.dll，启动项保留并合并；不把MHR/MHWilds/DD2 DLL互换；有脚本前置库需一并核验 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/ScriptRunner.cpp) |
| REFramework原生插件<br>`reframework-native` · 外部工具 | 按游戏更新/REF版本/插件ABI匹配<br>dll插件和对应依赖 | `reframework/plugins`<br>先确定x64架构及目标游戏；任何DLL都不自动执行；与插帧、ReShade或其他dinput8代理需冲突处理，不能覆写 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md) |
| RE Engine资源包<br>`reengine-resource` · 外部工具 | Rise基础/Sunbreak、Wilds更新、DD2更新分别选择<br>natives资源树、RE PAK / Fluffy包 | `由作者规定的资源加载器/Fluffy部署目标决定`<br>RE资源PAK不是Unreal PAK；不使用UE的~mods算法；本轮未核验可安全泛化的原生RE资源自动激活路线，保留外部工具和显式根目录预览 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_monsterhunterrise.py) |

- REFramework稳定v1.5.9.1与2026 nightly分开：旧stable可能没有新游戏更新支持，不能自动选旧stable。
- nightly仓库GitHub prerelease标志为false仍是开发通道，必须按仓库/发行名称标明nightly。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework/releases/tag/v1.5.9.1)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly/releases/tag/nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee)：`{"repo":"praydog/REFramework-nightly","ref":"0436e043af6f81a5d3fef49ae27d35e63431e566","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"nightly"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-monsterhunterwilds"></a>

## Monster Hunter Wilds

`monsterhunterwilds` · Steam 2246340

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| REFramework 非 VR 单 DLL 加载器<br>`reframework-loader` · 可实现候选 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建<br>REFramework.zip：dinput8.dll + 可选 reframework_revision.txt | `.`<br>仅部署官方非 VR dinput8.dll，保留已有文件冲突与备份确认；不安装 VR 或 C# API 包。；仅复制 DLL 不会自动配置 Proton 启动项或证明 MOD 生效；已有启动项及其它代理 DLL 必须保留。；游戏分支/版本需手动核对；新单体版不支持旧 RE2/RE3/RE7 非 RT 分支。 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/nightly-body.md) |
| REFramework Lua脚本<br>`reframework-lua` · 可实现候选 | 对应游戏的REFramework构建；稳定/开发nightly分开<br>Lua脚本与显式reframework目录 | `reframework/autorun`<br>需要该游戏专用REFramework dinput8.dll，启动项保留并合并；不把MHR/MHWilds/DD2 DLL互换；有脚本前置库需一并核验 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md)、[源2](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/src/mods/ScriptRunner.cpp) |
| REFramework原生插件<br>`reframework-native` · 外部工具 | 按游戏更新/REF版本/插件ABI匹配<br>dll插件和对应依赖 | `reframework/plugins`<br>先确定x64架构及目标游戏；任何DLL都不自动执行；与插帧、ReShade或其他dinput8代理需冲突处理，不能覆写 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md) |
| RE Engine资源包<br>`reengine-resource` · 外部工具 | Rise基础/Sunbreak、Wilds更新、DD2更新分别选择<br>natives资源树、RE PAK / Fluffy包 | `由作者规定的资源加载器/Fluffy部署目标决定`<br>RE资源PAK不是Unreal PAK；不使用UE的~mods算法；本轮未核验可安全泛化的原生RE资源自动激活路线，保留外部工具和显式根目录预览 | [源1](https://github.com/praydog/REFramework/blob/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee/README.md) |

- REFramework稳定v1.5.9.1与2026 nightly分开：旧stable可能没有新游戏更新支持，不能自动选旧stable。
- nightly仓库GitHub prerelease标志为false仍是开发通道，必须按仓库/发行名称标明nightly。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[praydog/REFramework](https://github.com/praydog/REFramework/releases/tag/v1.5.9.1)：`{"repo":"praydog/REFramework","ref":"d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","release":"v1.5.9.1","published_at":"2025-03-05T15:56:49Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[praydog/REFramework-nightly](https://github.com/praydog/REFramework-nightly/releases/tag/nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee)：`{"repo":"praydog/REFramework-nightly","ref":"0436e043af6f81a5d3fef49ae27d35e63431e566","release":"nightly-01432-d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee","published_at":"2026-10-11T01:59:23Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"nightly"}`；[Dytser/MH-Wilds-Vortex-Extension](https://github.com/Dytser/MH-Wilds-Vortex-Extension/commit/3839a10197490e0117dbb86d4b8dc831022ef942)：`{"repo":"Dytser/MH-Wilds-Vortex-Extension","ref":"3839a10197490e0117dbb86d4b8dc831022ef942","release":null,"published_at":null,"license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"source_only"}`

<a id="game-monsterhunterworld"></a>

## Monster Hunter World

`monsterhunterworld` · Steam 582010

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| nativePC资源<br>`mhw-nativepc` · 可实现候选 | World基础 / Iceborne及对应更新<br>显式nativePC目录树 | `nativePC`<br>保留nativePC相对路径，不生成nativePC/nativePC；所需加载器依MOD类型和版本；Stracker插件/DLL与普通资源区分；不猜裸二进制落点 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-monster-hunter-world/src/index.js)、[源2](https://github.com/ModOrganizer2/modorganizer-basic_games/blob/f1207d6398fbb4adda281f2bd5c563105391baaf/games/game_monsterhunterworld.py) |
| Stracker及插件<br>`mhw-loader` · 外部工具 | 对应当前World/Iceborne构建<br>Loader及nativePC/plugins等原生DLL | `作者指定根目录与插件目录`<br>加载器ABI、VC运行库和Proton DLL覆盖需外部配置；不自动覆写现有代理 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-monster-hunter-world/src/index.js) |

- World使用MT Framework，与Rise/Wilds的REFramework不通用。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","archived":false,"latest_prerelease":{"release":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","prerelease":true,"url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`；[ModOrganizer2/modorganizer-basic_games](https://github.com/ModOrganizer2/modorganizer-basic_games/releases/tag/v0.0.3)：`{"repo":"ModOrganizer2/modorganizer-basic_games","ref":"f1207d6398fbb4adda281f2bd5c563105391baaf","release":"v0.0.3","published_at":"2021-01-03T10:50:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"master","channel":"stable_and_source"}`

<a id="game-hogwartslegacy"></a>

## Hogwarts Legacy

`hogwartslegacy` · Steam 990080

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Unreal资源PAK<br>`hogwarts-pak` · 可实现候选 | 非官方传统MOD；按游戏更新与MOD版本选择<br>pak + 同名ucas/utoc成套资源 | `Phoenix/Content/Paks/~mods`<br>仅普通资源包；保留成套文件，不把Larian/RE Engine PAK混入；游戏官方MOD/Workshop来源不由插件直接接管或删除 | [源1](https://github.com/Nexus-Mods/game-hogwartslegacy/blob/10088b781d494f5190914f460291d979bb12a995/README.md)、[源2](https://github.com/Nexus-Mods/game-hogwartslegacy/blob/10088b781d494f5190914f460291d979bb12a995/src/index.ts) |
| 已存在BK2影片替换<br>`hogwarts-movie` · 手动说明 | 按游戏提供的影片文件匹配<br>bk2 | `Phoenix/Content/Movies中的精确现存目标`<br>要求唯一现存目标并备份；不能按文件名在多个目录乱猜 | [源1](https://github.com/Nexus-Mods/game-hogwartslegacy/blob/10088b781d494f5190914f460291d979bb12a995/README.md) |
| UE4SS Lua / Blueprint<br>`hogwarts-ue4ss` · 外部工具 | 旧扩展Mods/Mods.txt布局；UE4SS3.x/new ue4ss/Mods布局需按构建核对<br>Lua/C++脚本、LogicMods蓝图 | `Phoenix/Binaries/Win64中的对应UE4SS目录；Phoenix/Content/Paks/LogicMods`<br>UE4SS版本和配置按游戏版本；不能把LogicMods当普通~mods；旧扩展启用清单与新UE4SS结构不同，先读包结构和作者说明 | [源1](https://github.com/Nexus-Mods/game-hogwartslegacy/blob/10088b781d494f5190914f460291d979bb12a995/README.md)、[源2](https://github.com/Nexus-Mods/game-hogwartslegacy/blob/10088b781d494f5190914f460291d979bb12a995/src/index.ts)、[源3](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/game-hogwartslegacy](https://github.com/Nexus-Mods/game-hogwartslegacy/commit/10088b781d494f5190914f460291d979bb12a995)：`{"repo":"Nexus-Mods/game-hogwartslegacy","ref":"10088b781d494f5190914f460291d979bb12a995","release":null,"published_at":null,"license":"GPL-3.0","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"source_only"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT","archived":false,"latest_prerelease":{"release":"experimental-latest","published_at":"2024-12-29T23:57:31Z","prerelease":true,"url":"https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental-latest"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-blackmythwukong"></a>

## Black Myth: Wukong

`blackmythwukong` · Steam 2358720

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 资源PAK<br>`wukong-pak` · 可实现候选 | 游戏版本按MOD说明；WukongMM1.0.0记录布局<br>同stem的pak/utoc/ucas/sig作为同一个MOD | `b1/Content/Paks/~mods`<br>同stem文件一起启停；子目录作为一个MOD整体处理；普通pak与LogicMods脚本蓝图区分；不得从文件扩展名推断完整兼容 | [源1](https://github.com/aloneGtz/WukongMM/blob/20911873a4788d52cfed52c1c3e9cf6add6e4ad7/docs/USER_GUIDE.en.md) |
| UE4SS / LogicMods / C#<br>`wukong-script` · 外部工具 | UE4SS及CSharpLoader版本独立匹配当前游戏<br>Lua、Blueprint、C# loader mods | `b1/Binaries/Win64/ue4ss/Mods；b1/Content/Paks/LogicMods；b1/Binaries/Win64/CSharpLoader/Mods`<br>先安装对应加载器；不同加载器不能混为一个reframework目录；平台DLL覆盖和游戏更新兼容需另行验证；禁用不删除加载器被其他MOD共享的组件 | [源1](https://github.com/aloneGtz/WukongMM/blob/20911873a4788d52cfed52c1c3e9cf6add6e4ad7/docs/USER_GUIDE.en.md)、[源2](https://github.com/UE4SS-RE/RE-UE4SS/blob/97adba01e9fcb3c208376581e54edb9ef466f233/README.md) |

- WukongMM v1.0.0于2026-10-07发布，本轮只归纳目录/分组算法，不复用其存档修改功能。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[aloneGtz/WukongMM](https://github.com/aloneGtz/WukongMM/releases/tag/v1.0.0)：`{"repo":"aloneGtz/WukongMM","ref":"20911873a4788d52cfed52c1c3e9cf6add6e4ad7","release":"v1.0.0","published_at":"2026-10-07T10:03:00Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`；[UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1)：`{"repo":"UE4SS-RE/RE-UE4SS","ref":"97adba01e9fcb3c208376581e54edb9ef466f233","release":"v3.0.1","published_at":"2024-02-14T19:59:38Z","license":"MIT","archived":false,"latest_prerelease":{"release":"experimental-latest","published_at":"2024-12-29T23:57:31Z","prerelease":true,"url":"https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental-latest"},"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

<a id="game-ghostoftsushima"></a>

## Ghost of Tsushima DIRECTOR'S CUT

`ghostoftsushima` · Steam 2215430

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| PC DSAR/PSARC资源替换<br>`got-psarc` · 外部工具 | PC Director's Cut；按MOD对应版本<br>成品PSARC/DSAR或需要重打包的资源 | `cache_pc/psarc（仅明确完整成品包可预览部署）`<br>PC容器可能是DSAR包裹PSAR，不能把任意UnPSARC输出当可用MOD；原始sps/xpps需要重打包；修改主档必须备份；不自动运行包内bat/exe | [源1](https://github.com/mstww/Ghost-of-Tsushima-PSARC-Tool/blob/7cfa73600675714f049253ac8e87d2eb2c092656/README.md)、[源2](https://github.com/mstww/Ghost-Of-Tsushima-xpps-Localization-tool/blob/main/README.md) |
| 作者明确路径的成品包<br>`got-explicit-root` · 手动说明 | 与当前PC游戏更新匹配<br>已生成的规范cache_pc/psarc目录包 | `用户确认根目录下cache_pc/psarc`<br>仅手动根目录预览；不把PS4/PS5包或工具源码直接部署；工具作者的layout一致性声明不等于本插件已游戏实测 | [源1](https://github.com/mstww/Ghost-of-Tsushima-PSARC-Tool/blob/7cfa73600675714f049253ac8e87d2eb2c092656/README.md) |

- 排除无源码且只有“下载点击这里”的伪mod manager仓库；本项基于可读的真实MIT打包工具。
- 未进行 Steam Deck 或游戏内验证；方法记录不是跨版本兼容性保证。
- implemented_candidate 仅指可实现的受限文件部署，不代表本轮已实现或已自动激活。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[mstww/Ghost-of-Tsushima-PSARC-Tool](https://github.com/mstww/Ghost-of-Tsushima-PSARC-Tool/releases/tag/v1.1)：`{"repo":"mstww/Ghost-of-Tsushima-PSARC-Tool","ref":"7cfa73600675714f049253ac8e87d2eb2c092656","release":"v1.1","published_at":"2026-09-26T10:26:05Z","license":"MIT","archived":false,"latest_prerelease":null,"checked_at":"2026-10-19","source_branch":"main","channel":"stable_and_source"}`

