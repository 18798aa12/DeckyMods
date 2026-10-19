# Unity / 独立游戏 / 加载器 安装方式详细研究

核查日期：2026-10-19。返回 [113 款游戏索引](INSTALL_METHODS.md)。

未进行 Steam Deck 实机验证。下列“可实现候选”仅表示研究建议，不代表代码已实现或包一定兼容；真正能否部署由插件当前受限方案与安装预览决定。来源只用于参考公开行为与协议，不复制第三方实现，不捆绑闭源管理器或游戏/MOD 资源。

<a id="game-valheim"></a>

## Valheim

`valheim` · Steam 892970

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L18010)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-lethal-company"></a>

## Lethal Company

`lethal-company` · Steam 1966720

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L8494)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-riskofrain2"></a>

## Risk of Rain 2

`riskofrain2` · Steam 632360

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L12965)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-content-warning"></a>

## Content Warning

`content-warning` · Steam 2881650

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L3925)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-repo"></a>

## R.E.P.O.

`repo` · Steam 3241660

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L12524)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-dyson-sphere-program"></a>

## Dyson Sphere Program

`dyson-sphere-program` · Steam 1366540

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L5387)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-ultrakill"></a>

## ULTRAKILL

`ultrakill` · Steam 1229490

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L17758)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-inscryption"></a>

## Inscryption

`inscryption` · Steam 1092790

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L7955)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-hollow-knight-silksong"></a>

## Hollow Knight: Silksong

`hollow-knight-silksong` · Steam 1030300

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L27315)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- r2modman 的 profile 目录与游戏根目录是两种安装环境；不得覆盖现有 profile 或盲目复制整套加载器。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-stardewvalley"></a>

## Stardew Valley

`stardewvalley` · Steam 413150

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| SMAPI 代码 MOD / Content Patcher 内容包<br>`smapi-manifest` · 可实现候选 | 1.6.x: SMAPI 4.x；1.5.6 legacy: SMAPI 3.18.6<br>ZIP: <Mod>/manifest.json + EntryDll or ContentPackFor | `<game-root>/Mods/<Mod>/`<br>先安装与游戏版本匹配的 SMAPI；内容包还需 manifest 指定的框架。；保留多层内容包目录，检查 UniqueID、MinimumApiVersion、Dependencies；不把 XNB 包伪装成 SMAPI 包。；SMAPI 4.5.2 模型另有 MinimumGameVersion；EntryDll 与 ContentPackFor 必须二选一，不能两者同时指定。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-stardewvalley/src/installers/stardewValleyInstaller.ts)、[源2](https://stardewvalleywiki.com/Modding:Player_Guide/Getting_Started)、[源3](https://github.com/Pathoschild/SMAPI/blob/e5b8bf3d601bec0099252c8ee2f54e5571385f1a/src/SMAPI.Toolkit/Serialization/Models/Manifest.cs) |
| 安装 / 更新 SMAPI 本体<br>`smapi-install` · 外部工具 | SMAPI 4.5.2 stable; archived installers for older game branches<br>SMAPI platform-specific installer | `官方安装器所检测的游戏根目录`<br>Steam Deck 可用原生 Linux SMAPI；安装器及启动参数必须由用户按官方教程确认。 | [源1](https://stardewvalleywiki.com/Modding:Installing_SMAPI_on_Steam_Deck)、[源2](https://github.com/Pathoschild/SMAPI/blob/e5b8bf3d601bec0099252c8ee2f54e5571385f1a/docs/README.md) |
| 旧式 XNB 替换包<br>`xnb-replacement` · 手动说明 | 仅作者明确匹配的旧版/当前游戏资源<br>XNB resource replacement | `作者指定 Content 子目录`<br>需精确原文件与备份，优先使用 Content Patcher 替代，不猜贴图路径。 | [源1](https://stardewvalleywiki.com/Modding:Using_XNB_mods) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Pathoschild/SMAPI](https://github.com/Pathoschild/SMAPI)：`{"repo":"Pathoschild/SMAPI","ref":"e5b8bf3d601bec0099252c8ee2f54e5571385f1a","branch":"develop","release":"4.5.2","published_at":"2026-03-22T23:55:42Z","license":"LGPL-3.0","release_url":"https://github.com/Pathoschild/SMAPI/releases/tag/4.5.2","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","branch":"master","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","release_url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0","prerelease":{"version":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-terraria"></a>

## Terraria

`terraria` · Steam 105600

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 通过独立 tModLoader 管理代码 MOD<br>`tmodloader-workshop` · 外部工具 | 1.4.4 stable；1.4.3 legacy；1.3 legacy；1.4.5 development 按官方分支标记<br>tModLoader .tmod / Steam Workshop | `Linux: $XDG_DATA_HOME/Terraria/<tML-branch>/Mods/；不是 Terraria 游戏根目录`<br>需要合法 Terraria 和独立 tModLoader；版本分支、存档目录与模组必须一致。；建议由 tModLoader 游戏内 Workshop 下载、启用及重载；不写 Steam Workshop 缓存。 | [源1](https://github.com/tModLoader/tModLoader/wiki/Basic-tModLoader-Usage-Guide)、[源2](https://github.com/tModLoader/tModLoader/wiki/tModLoader-guide-for-players) |
| 原版资源包<br>`terraria-resource-pack` · 手动说明 | 游戏内资源包系统支持的版本<br>resource pack with pack.json | `游戏内 Workshop / Resource Packs 指定目录`<br>资源包与 .tmod 不是同一类型；不要向原版根目录释放 .tmod。 | [源1](https://terraria.wiki.gg/wiki/Resource_Pack) |
| tModLoader 本地 .tmod 与 Workshop<br>`tmodloader-manual` · 外部工具 | 1.4.4 stable；1.4.3: tModLoader-1.4.3；1.3: ModLoader；1.4.5 development 单独确认<br>*.tmod; enabled.json | `Linux: ${XDG_DATA_HOME:-~/.local/share}/Terraria/{tModLoader\|tModLoader-1.4.3\|ModLoader}/Mods/`<br>当前插件只管理游戏根目录，用户目录路径需要专用受限目标，暂由游戏内管理。；Proton Windows Documents 路径与原生 Linux XDG 路径不能混同。 | [源1](https://github.com/tModLoader/tModLoader/wiki/Basic-tModLoader-Usage-Guide)、[源2](https://github.com/tModLoader/tModLoader/wiki/tModLoader-guide-for-players) |

- tModLoader 是此游戏的加载平台；其独立 Steam 条目不会增加独立游戏作品数。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。
- independent_game_count=false；这是 Terraria 的独立加载器应用，不另算作品。
- tModLoader（Steam AppID 1281930）作为 Terraria 的加载器方法记录，不另计独立游戏，也不当作 Terraria 本体 AppID。

上游版本与许可：[tModLoader/tModLoader](https://github.com/tModLoader/tModLoader)：`{"repo":"tModLoader/tModLoader","ref":"fdcf523ec5c8f3fe613ce16d4eac6e07eef8de93","branch":"1.4.5","release":"v2026.08.3.0","published_at":"2026-10-01T00:08:55Z","license":"MIT","release_url":"https://github.com/tModLoader/tModLoader/releases/tag/v2026.08.3.0","prerelease":{"version":"v2026.09.2.1","published_at":"2026-10-01T05:03:02Z","url":"https://github.com/tModLoader/tModLoader/releases/tag/v2026.09.2.1"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-rimworld"></a>

## RimWorld

`rimworld` · Steam 294100

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| About.xml MOD 文件夹<br>`rimworld-about` · 可实现候选 | 支持版本由 About/About.xml supportedVersions 与 LoadFolders.xml 声明，例如 1.5/1.6<br>ZIP: <Mod>/About/About.xml plus Assemblies/Defs/Textures/version folders | `<game-root>/Mods/<Mod>/`<br>保留不同版本文件夹及 LoadFolders.xml，不只拷贝当前版本目录。；读取 packageId、modDependencies、loadBefore/loadAfter；复制不等于已调整游戏加载顺序。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-rimworld/src/index.js)、[源2](https://rimsort.github.io/RimSort/user-guide/basic-usage/) |
| 加载顺序 / Workshop 依赖管理<br>`rimsort` · 外部工具 | 当前 RimSort 及游戏版本<br>RimSort profile / Steam Workshop | `RimSort 检测的本地 Mods 和 Workshop 目录`<br>不重写第三方管理器配置；复杂依赖与排序由 RimSort 完成。 | [源1](https://github.com/RimSort/RimSort/blob/7f0a0249dae8f744a2abff2568c8e1ab7ab0d3a2/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[RimSort/RimSort](https://github.com/RimSort/RimSort)：`{"repo":"RimSort/RimSort","ref":"7f0a0249dae8f744a2abff2568c8e1ab7ab0d3a2","branch":"main","release":"v1.17.1","published_at":"2026-10-19T12:52:20Z","license":"GPL-3.0","release_url":"https://github.com/RimSort/RimSort/releases/tag/v1.17.1","prerelease":{"version":"Edge","published_at":"2026-10-19T12:40:30Z","url":"https://github.com/RimSort/RimSort/releases/tag/Edge"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","branch":"master","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","release_url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0","prerelease":{"version":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-factorio"></a>

## Factorio

`factorio` · Steam 427520

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Factorio 原生 ZIP / 文件夹 MOD<br>`factorio-native` · 外部工具 | info.json factorio_version 分别匹配 1.1、2.0、后续版本<br><name>_<version>.zip containing info.json | `Linux: ~/.factorio/mods/；Proton 则是其前缀 AppData/Roaming/Factorio/mods/`<br>MOD 主版本、dependencies、DLC/feature flags 必须匹配；mod-list.json 为启用状态。；此目标在用户数据目录而非游戏根目录，目前应由游戏内 MOD 菜单或专用管理器处理。 | [源1](https://wiki.factorio.com/Modding#Installing_mods)、[源2](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-factorio/src/index.js) |

- ModMyFactory2 最新只有 2022 beta，不能称为最新推荐维护方案；当前优先游戏原生 MOD 菜单。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","branch":"master","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","release_url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0","prerelease":{"version":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[Artentus/ModMyFactory2](https://github.com/Artentus/ModMyFactory2)：`{"repo":"Artentus/ModMyFactory2","ref":"871f2349300b27b265f6454e729a554cf807f35d","branch":"master","release":null,"published_at":null,"license":"GPL-3.0","release_url":null,"prerelease":{"version":"4.3.4.42-beta","published_at":"2022-07-28T19:24:33Z","url":"https://github.com/Artentus/ModMyFactory2/releases/tag/4.3.4.42-beta"},"archived":false,"checked_at":"2026-10-19","release_kind":"no_stable_release"}`

<a id="game-risk-of-rain-returns"></a>

## Risk of Rain Returns

`risk-of-rain-returns` · Steam 1337520

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Return Of Modding / Lua MOD<br>`return-of-modding` · 外部工具 | 由 MOD 声明的 RoRR game build 与 Return Of Modding 版本<br>version.dll loader; ReturnOfModding/plugins/<Author-Mod>/ | `<game-root>/version.dll and ReturnOfModding/plugins/`<br>GameMaker 游戏，不使用 Risk of Rain 2 的 BepInEx DLL 路线；先安装匹配加载器。；Proton DLL override 与自定义启动项需专门合并，当前只引导外部 r2modman。 | [源1](https://github.com/return-of-modding/ReturnOfModding/blob/f7eac6beb3f51000ecdfb1f4b3de43ca5b539a37/README.md)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/r2mm/launching/instructions/instructions/loader/ReturnOfModdingGameInstructions.ts) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[return-of-modding/ReturnOfModding](https://github.com/return-of-modding/ReturnOfModding)：`{"repo":"return-of-modding/ReturnOfModding","ref":"f7eac6beb3f51000ecdfb1f4b3de43ca5b539a37","branch":"master","release":"nightly","published_at":"2026-05-19T14:50:24Z","license":"MIT","release_url":"https://github.com/return-of-modding/ReturnOfModding/releases/tag/nightly","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"rolling_development_nightly"}`；[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-schedule-i"></a>

## Schedule I

`schedule-i` · Steam 3164500

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| MelonLoader MOD 与 Plugins<br>`melonloader-mods` · 外部工具 | 游戏默认 IL2CPP 与 alternate/Mono 分支需分别匹配；当前 MelonLoader stable 0.7.3 不代表所有旧 MOD 可直接升级<br>Mods/*.dll; Plugins/*.dll; UserData companions | `<game-root>/Mods/ or Plugins/ as author specifies`<br>r2modman 标记 recursive-melonloader；不得把所有 DLL 一律丢进 BepInEx/plugins。；加载器安装、.NET/IL2CPP 生成与 Proton 依赖先使用官方流程；插件不执行包内安装器。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L13653)、[源2](https://github.com/LavaGang/MelonLoader/blob/5aff4d9d7c16ae153aad2f1035114dbc2713bf99/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[LavaGang/MelonLoader](https://github.com/LavaGang/MelonLoader)：`{"repo":"LavaGang/MelonLoader","ref":"5aff4d9d7c16ae153aad2f1035114dbc2713bf99","branch":"master","release":"v0.7.3","published_at":"2026-05-14T20:20:01Z","license":"Apache-2.0","release_url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.7.3","prerelease":{"version":"v0.6.0","published_at":"2022-12-25T15:18:05Z","url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.6.0"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-sons-of-the-forest"></a>

## Sons Of The Forest

`sons-of-the-forest` · Steam 1326470

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L14701)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |
| RedLoader / RedManager<br>`redloader` · 外部工具 | 按 MOD 的 RedLoader / 游戏版本要求<br>RedLoader.zip; Mods/<Mod> manifest.json and DLL | `<game-root>/_Redloader/; MOD 按 RedLoader manifest 指定布局`<br>官方建议 RedManager；根目录需对应 SonsOfTheForest.exe。；Linux Wine 专服说明使用 version=n,b，不能据此自动覆盖客户端已有启动项。 | [源1](https://github.com/ToniMacaroni/RedLoader/blob/3b9f3551c7d2cbae11ea6a4354054a9f9c5777c8/README.md) |

- BepInEx 旧生态与 RedLoader MOD 不可仅凭 .dll 扩展名混装。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[ToniMacaroni/RedLoader](https://github.com/ToniMacaroni/RedLoader)：`{"repo":"ToniMacaroni/RedLoader","ref":"3b9f3551c7d2cbae11ea6a4354054a9f9c5777c8","branch":"rewrite","release":"0.8.6","published_at":"2025-02-26T00:07:35Z","license":"LGPL-2.1","release_url":"https://github.com/ToniMacaroni/RedLoader/releases/tag/0.8.6","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-the-forest"></a>

## The Forest

`the-forest` · Steam 242760

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ModAPI 管理器补丁安装<br>`modapi-v2` · 外部工具 | ModAPI v2.0.9623；v1 为旧版且不能覆盖安装<br>ModAPI .mod package | `<ModAPI-manager>/mods/TheForest/；不是 <game-root>/mods/TheForest/`<br>ModAPI 会按游戏程序集版本打补丁；单纯解压到游戏根目录无法完成。；SteamOS/Proton 需单独验证管理器，当前提供文档与外部工具入口。 | [源1](https://modapi.survivetheforest.net/faq/)、[源2](https://github.com/FluffyFishGames/ModAPI/blob/54f03aab476a4c5d4a5308f752f619203990f7f1/README.md) |

- ModAPI官网2026-09更新为v2；旧v1包和v2管理器不可无提示混用。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[FluffyFishGames/ModAPI](https://github.com/FluffyFishGames/ModAPI)：`{"repo":"FluffyFishGames/ModAPI","ref":"54f03aab476a4c5d4a5308f752f619203990f7f1","branch":"master","release":"ModAPI_v2.0.9623","published_at":"2026-09-19T17:17:22Z","license":"GPL-3.0","release_url":"https://github.com/FluffyFishGames/ModAPI/releases/tag/ModAPI_v2.0.9623","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-subnautica"></a>

## Subnautica

`subnautica` · Steam 264710

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 现代 BepInEx / Nautilus 插件<br>`bepinex-plugins` · 可实现候选 | Subnautica Living Large/2.0+ 对应 Nautilus；Below Zero 使用明确支持 BZ 的包<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。；Nautilus/BepInEx 与 QModManager/SMLHelper 旧包使用不同 API；先核实游戏分支和 MOD 发布页。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L15266)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md)、[源3](https://github.com/SubnauticaModding/Nautilus/blob/dce0680e8a1abcd0c2c76102f2641eb9d13ee53f/README.md) |
| QModManager / SMLHelper 旧分支<br>`qmod-legacy` · 手动说明 | Subnautica legacy/pre-Living-Large；Below Zero 仅 MOD 作者明确要求的旧 QMod 分支<br>QMods/<Mod>/mod.json and assemblies | `<game-root>/QMods/<Mod>/`<br>不把旧 QMod 包自动迁移到 Nautilus；QModManager 已停止更新。；必须保留游戏分支、QModManager、SMLHelper及mod.json依赖的组合。 | [源1](https://github.com/SubnauticaModding/QModManager/blob/77c42c4c2aaf0dff99cfd4657b191d2f7a606834/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[SubnauticaModding/Nautilus](https://github.com/SubnauticaModding/Nautilus)：`{"repo":"SubnauticaModding/Nautilus","ref":"dce0680e8a1abcd0c2c76102f2641eb9d13ee53f","branch":"master","release":"sml/2.15","published_at":"2023-05-13T04:36:25Z","license":"GPL-3.0","release_url":"https://github.com/SubnauticaModding/Nautilus/releases/tag/sml/2.15","prerelease":{"version":"1.0.0-pre.54","published_at":"2026-09-26T03:40:33Z","url":"https://github.com/SubnauticaModding/Nautilus/releases/tag/1.0.0-pre.54"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag","release_note":"sml/2.15 is historical SMLHelper stable inherited in this repo, not current Nautilus; current Nautilus is prerelease 1.0.0-pre.54"}`；[SubnauticaModding/QModManager](https://github.com/SubnauticaModding/QModManager)：`{"repo":"SubnauticaModding/QModManager","ref":"77c42c4c2aaf0dff99cfd4657b191d2f7a606834","branch":"master","release":"v4.4.4","published_at":"2022-10-31T17:56:12Z","license":"NOASSERTION","release_url":"https://github.com/SubnauticaModding/QModManager/releases/tag/v4.4.4","prerelease":null,"archived":true,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"stable_release_tag"}`

<a id="game-subnautica-below-zero"></a>

## Subnautica: Below Zero

`subnautica-below-zero` · Steam 848450

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 现代 BepInEx / Nautilus 插件<br>`bepinex-plugins` · 可实现候选 | Subnautica Living Large/2.0+ 对应 Nautilus；Below Zero 使用明确支持 BZ 的包<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。；Nautilus/BepInEx 与 QModManager/SMLHelper 旧包使用不同 API；先核实游戏分支和 MOD 发布页。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L15159)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md)、[源3](https://github.com/SubnauticaModding/Nautilus/blob/dce0680e8a1abcd0c2c76102f2641eb9d13ee53f/README.md) |
| QModManager / SMLHelper 旧分支<br>`qmod-legacy` · 手动说明 | Subnautica legacy/pre-Living-Large；Below Zero 仅 MOD 作者明确要求的旧 QMod 分支<br>QMods/<Mod>/mod.json and assemblies | `<game-root>/QMods/<Mod>/`<br>不把旧 QMod 包自动迁移到 Nautilus；QModManager 已停止更新。；必须保留游戏分支、QModManager、SMLHelper及mod.json依赖的组合。 | [源1](https://github.com/SubnauticaModding/QModManager/blob/77c42c4c2aaf0dff99cfd4657b191d2f7a606834/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[SubnauticaModding/Nautilus](https://github.com/SubnauticaModding/Nautilus)：`{"repo":"SubnauticaModding/Nautilus","ref":"dce0680e8a1abcd0c2c76102f2641eb9d13ee53f","branch":"master","release":"sml/2.15","published_at":"2023-05-13T04:36:25Z","license":"GPL-3.0","release_url":"https://github.com/SubnauticaModding/Nautilus/releases/tag/sml/2.15","prerelease":{"version":"1.0.0-pre.54","published_at":"2026-09-26T03:40:33Z","url":"https://github.com/SubnauticaModding/Nautilus/releases/tag/1.0.0-pre.54"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag","release_note":"sml/2.15 is historical SMLHelper stable inherited in this repo, not current Nautilus; current Nautilus is prerelease 1.0.0-pre.54"}`；[SubnauticaModding/QModManager](https://github.com/SubnauticaModding/QModManager)：`{"repo":"SubnauticaModding/QModManager","ref":"77c42c4c2aaf0dff99cfd4657b191d2f7a606834","branch":"master","release":"v4.4.4","published_at":"2022-10-31T17:56:12Z","license":"NOASSERTION","release_url":"https://github.com/SubnauticaModding/QModManager/releases/tag/v4.4.4","prerelease":null,"archived":true,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"stable_release_tag"}`

<a id="game-slime-rancher"></a>

## Slime Rancher

`slime-rancher` · Steam 433340

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| SRML 插件<br>`srml` · 外部工具 | 仅原版 Slime Rancher；按作者要求的 SRML/game 版本<br>SRML MOD DLL and companion files | `<game-root>/SRML/Mods/`<br>先通过 SRML 安装器完成加载器注入；不同游戏 Slime Rancher 2 不使用此目录。；需依赖加载及Linux/Proton路径验证，目前使用外部安装器。 | [源1](https://github.com/SlimeRancherModding/SRML/wiki/Getting-Started)、[源2](https://github.com/SlimeRancherModding/SRML/blob/11440f26938fed5b3cc6b32327fa268dea866e8f/README.md)、[源3](https://github.com/SlimeRancherModding/SRML/blob/11440f26938fed5b3cc6b32327fa268dea866e8f/SRML/FileSystem.cs) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[SlimeRancherModding/SRML](https://github.com/SlimeRancherModding/SRML)：`{"repo":"SlimeRancherModding/SRML","ref":"11440f26938fed5b3cc6b32327fa268dea866e8f","branch":"main","release":"v0.2.1","published_at":"2022-08-07T13:30:03Z","license":"GPL-3.0","release_url":"https://github.com/SlimeRancherModding/SRML/releases/tag/v0.2.1","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-slime-rancher-2"></a>

## Slime Rancher 2

`slime-rancher-2` · Steam 1657630

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| MelonLoader / Starlight<br>`melonloader-starlight` · 外部工具 | 按Starlight发布页的游戏与 MelonLoader 版本组合；旧 SR2E 与新 Starlight 不自动等同；当前作者Linux教程要求 MelonLoader >=0.7.3；Starlight stable v4.0.4<br>Mods/*.dll; Starlight expansion layout | `<game-root>/Mods/；前置与配置保留作者指定位置`<br>使用作者提供的 Linux Steam 安装教程；IL2CPP依赖和Proton环境须先准备。；Starlight 使用自定义 Starlight-SAL 许可，不将其源码或二进制直接再分发。 | [源1](https://github.com/ThatFinn/Starlight/blob/78197b71eb82129671a89b8811fcd3214a62b04c/README.md)、[源2](https://starlight.sr2.dev/docs/category/linux-installation-guide)、[源3](https://starlight.sr2.dev/docs/installation/linux/steam) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[LavaGang/MelonLoader](https://github.com/LavaGang/MelonLoader)：`{"repo":"LavaGang/MelonLoader","ref":"5aff4d9d7c16ae153aad2f1035114dbc2713bf99","branch":"master","release":"v0.7.3","published_at":"2026-05-14T20:20:01Z","license":"Apache-2.0","release_url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.7.3","prerelease":{"version":"v0.6.0","published_at":"2022-12-25T15:18:05Z","url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.6.0"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[ThatFinn/Starlight](https://github.com/ThatFinn/Starlight)：`{"repo":"ThatFinn/Starlight","ref":"78197b71eb82129671a89b8811fcd3214a62b04c","branch":"main","release":"v4.0.4","published_at":"2026-09-24T18:42:59Z","license":"LicenseRef-Starlight-SAL","release_url":"https://github.com/ThatFinn/Starlight/releases/tag/v4.0.4","prerelease":{"version":"v3.0.0b1","published_at":"2024-12-25T04:31:46Z","url":"https://github.com/ThatFinn/Starlight/releases/tag/v3.0.0b1"},"archived":false,"checked_at":"2026-10-19","license_note":"Source-available, not OSI open source; no source reuse, cloning, bundling, mirroring or redistribution. Link official author download only.","license_url":"https://github.com/ThatFinn/Starlight/blob/78197b71eb82129671a89b8811fcd3214a62b04c/LICENSE.md","release_kind":"stable_release_tag"}`

<a id="game-7daystodie"></a>

## 7 Days to Die

`7daystodie` · Steam 251570

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ModInfo.xml 模组文件夹<br>`modinfo-root` · 可实现候选 | 匹配 A20/A21/1.x/2.x 等明确发布分支；不跨版本假定兼容<br>Mods/<Mod>/ModInfo.xml; Config/XML/assets or DLL | `<game-root>/Mods/<Mod>/（仅该 MOD 明确使用根目录 Mods 时）`<br>XML-only、含自定义素材、含 C# DLL 三种 MOD 的客户端及 EAC 要求不同。；仅选择有 ModInfo.xml 的完整模组，不把多个可选版本混成一个安装。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-7daystodie/src/index.tsx)、[源2](https://github.com/magejosh/7D2D_v1_mods/blob/main/README.md) |
| 用户数据目录 MOD<br>`modinfo-userdata` · 外部工具 | 由当前版本设置及作者文档指定<br>ModInfo.xml MOD folder | `Linux 用户数据目录 / Proton %APPDATA%/7DaysToDie/Mods/；以游戏配置解析为准`<br>当前根目录部署引擎不能写用户数据目录；该模式需外部工具。 | [源1](https://github.com/Nexus-Mods/Vortex/blob/efc1370d768a5f5843c4ba9d1468c627cc44dc09/extensions/games/game-7daystodie/src/util.ts) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Nexus-Mods/Vortex](https://github.com/Nexus-Mods/Vortex)：`{"repo":"Nexus-Mods/Vortex","ref":"efc1370d768a5f5843c4ba9d1468c627cc44dc09","branch":"master","release":"v2.9.0","published_at":"2026-10-19T12:43:14Z","license":"GPL-3.0","release_url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0","prerelease":{"version":"v2.9.0-beta.4","published_at":"2026-10-15T10:52:28Z","url":"https://github.com/Nexus-Mods/Vortex/releases/tag/v2.9.0-beta.4"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-project-zomboid"></a>

## Project Zomboid

`project-zomboid` · Steam 108600

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Build 41 模组<br>`pz-b41` · 外部工具 | Build 41 legacy<br><Mod>/mod.info + media/ | `Linux: ~/Zomboid/mods/<Mod>/；Proton 为当前前缀用户 Zomboid/mods/`<br>MOD ID与Workshop ID不同；从包内 mod.info 读取身份；在游戏内为存档启用。 | [源1](https://pzwiki.net/wiki/Mod_structure)、[源2](https://github.com/devynspencer/zomboid-mod-tools/blob/d9dd3f4dbd94f884472f82817ddebc97e53d4cf1/ZomboidModTools/public/Deploy-ZomboidMod.ps1) |
| Build 42 版本化模组<br>`pz-b42` · 外部工具 | Build 42；42.x 需按实际版本子目录声明<br><Mod>/common/ plus 42[.minor]/mod.info + media/ | `Linux: ~/Zomboid/mods/<Mod>/；不要丢到游戏根目录`<br>保留 common 与所有版本文件夹，让游戏选择匹配分支；不能删除旧分支做扁平化。；存在多个MOD ID与地图项时需要游戏内存档/服务器配置确认。 | [源1](https://pzwiki.net/wiki/Mod_structure) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 搜索缓存中的 LabX1 模板当前 GitHub API 已不可访问，不作为最新开源证据；采用官方 PZwiki 路径说明。
- MIT开放源码的zomboid-mod-tools仅作为用户目录部署行为参考；其PowerShell工具不能称为SteamOS现成安装器，B42规则以官方Wiki为准。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[devynspencer/zomboid-mod-tools](https://github.com/devynspencer/zomboid-mod-tools)：`{"repo":"devynspencer/zomboid-mod-tools","ref":"d9dd3f4dbd94f884472f82817ddebc97e53d4cf1","branch":"main","release":null,"published_at":null,"license":"MIT","release_url":null,"prerelease":null,"checked_at":"2026-10-19","release_kind":"no_stable_release"}`

<a id="game-cities-skylines"></a>

## Cities: Skylines

`cities-skylines` · Steam 255710

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Steam Workshop / Skyve CS1<br>`cs1-workshop` · 外部工具 | Cities: Skylines I 与其对应 DLC/游戏更新<br>Workshop package; local Addons Mods/Assets | `原生 Linux用户路径 .local/share/Colossal Order/Cities_Skylines/Addons/；Proton路径另算`<br>CS1 与 CS2 的管理器、MOD API及路径完全不同。；Workshop由Steam管理；本地用户目录部署与加载顺序需外部Skyve/游戏内容管理器。 | [源1](https://skylines.paradoxwikis.com/User_path)、[源2](https://github.com/JadHajjar/Skyve-CS1) |

- Skyve-CS1 仓库API未声明许可，研究其接口/文档不代表可复制其实现。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[JadHajjar/Skyve-CS1](https://github.com/JadHajjar/Skyve-CS1)：`{"repo":"JadHajjar/Skyve-CS1","ref":"143ea82048d68851c130a8fbba83d101f223420b","branch":"main","release":null,"published_at":null,"license":"not-declared","release_url":null,"prerelease":null,"archived":false,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"no_stable_release"}`

<a id="game-cities-skylines-ii"></a>

## Cities: Skylines II

`cities-skylines-ii` · Steam 949230

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 历史/明确BepInEx MOD<br>`bepinex-plugins` · 手动说明 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L3787)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |
| Paradox Mods / Skyve CS2<br>`cs2-pdx` · 外部工具 | 由 Paradox Mods 与 MOD manifest 标记的 CS2 游戏版本<br>PDX Mods playsets and subscriptions | `Skyve/游戏 Paradox Mods 管理的用户数据目录`<br>使用游戏或Skyve管理playset、依赖与授权；不直接复制PDX缓存到BepInEx。；Skyve为桌面应用；SteamOS适用性需另行验证，不承诺一键运行。 | [源1](https://github.com/JadHajjar/Skyve/blob/09cc376489dd5c1e90b560973a5fdb4057c8d687/README.md) |

- Thunderstore BepInEx属于独立旧生态；当前官方路线优先Paradox Mods，不将两类包混装。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[JadHajjar/Skyve](https://github.com/JadHajjar/Skyve)：`{"repo":"JadHajjar/Skyve","ref":"09cc376489dd5c1e90b560973a5fdb4057c8d687","branch":"main","release":null,"published_at":null,"license":"not-declared","release_url":null,"prerelease":null,"archived":false,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"no_stable_release"}`

<a id="game-satisfactory"></a>

## Satisfactory

`satisfactory` · Steam 526870

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Satisfactory Mod Manager / SML<br>`satisfactory-smm` · 外部工具 | SML、MOD版本与游戏CL#逐项匹配<br>smod/ZIP containing .uplugin; GameFeature true/false alters destination | `GameFeature=true: <game-root>/FactoryGame/Mods/GameFeatures/<Mod>/；否则 FactoryGame/Mods/<Mod>/`<br>官方建议Linux使用SMM，避免过时SML2手工方法。；文件夹名称必须和.uplugin名称相同；依赖与平台二进制由SMM解决。 | [源1](https://github.com/satisfactorymodding/Documentation/blob/master/modules/ROOT/pages/ManualInstallDirections.adoc)、[源2](https://github.com/satisfactorymodding/Documentation/blob/master/modules/ROOT/pages/ForUsers/SatisfactoryModManager.adoc) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[satisfactorymodding/SatisfactoryModManager](https://github.com/satisfactorymodding/SatisfactoryModManager)：`{"repo":"satisfactorymodding/SatisfactoryModManager","ref":"c16350b316b88edb1b8a4ae32cd72571d31b4aa0","branch":"master","release":"v3.1.0","published_at":"2026-06-06T16:22:15Z","license":"GPL-3.0","release_url":"https://github.com/satisfactorymodding/SatisfactoryModManager/releases/tag/v3.1.0","prerelease":{"version":"v3.0.0-beta.4","published_at":"2024-05-29T18:42:05Z","url":"https://github.com/satisfactorymodding/SatisfactoryModManager/releases/tag/v3.0.0-beta.4"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-core-keeper"></a>

## Core Keeper

`core-keeper` · Steam 1621690

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 官方 SDK MOD / mod.io / Workshop<br>`corekeeper-manifest` · 可实现候选 | 按 ModManifest.json 与当前游戏 SDK 兼容声明<br><Mod>/ModManifest.json with assemblies/assets | `<game-root>/CoreKeeper_Data/StreamingAssets/Mods/<Mod>/`<br>mod.io/Workshop订阅与本地副本避免重复；手动包需用户手动更新。；仅识别ModManifest，不执行包内代码；依赖与可能的Elevated Permissions由游戏确认。 | [源1](https://github.com/Pugstorm/CoreKeeperModDocs/blob/0328be0c448a061dd221c022ee24ed52f464878b/modding-documentation/playing-with-mods/installing-mods.md)、[源2](https://github.com/CoreKeeperMods/Core-Keeper-Docs/blob/main/playing-with-mods/installing-mods/on-game-clients.md) |
| 历史 BepInEx 生态<br>`bepinex-plugins` · 手动说明 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L4140)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- 旧 BepInEx MOD 不等于当前官方SDK MOD；必须按包中入口类型选择。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[Pugstorm/CoreKeeperModDocs](https://github.com/Pugstorm/CoreKeeperModDocs)：`{"repo":"Pugstorm/CoreKeeperModDocs","ref":"0328be0c448a061dd221c022ee24ed52f464878b","branch":"main","release":null,"published_at":null,"license":"not-declared","release_url":null,"prerelease":null,"archived":false,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"no_stable_release"}`

<a id="game-hollow-knight"></a>

## Hollow Knight

`hollow-knight` · Steam 367520

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Hollow Knight Modding API / Lumafly<br>`hk-api` · 外部工具 | API 1.5.78.11833-77 对应其上游游戏分支；旧分支需旧API<br>Modding API managed assemblies and mod DLL folders | `<game-root>/hollow_knight_Data/Managed/Mods/；具体OS/游戏分支以Lumafly检测为准`<br>不是Silksong的BepInEx目录；API注入会替换Managed程序集，需专用管理器备份。；当前通过跨平台 Lumafly 完成下载、依赖、启禁与API切换。 | [源1](https://github.com/TheMulhima/Lumafly/blob/9765dd7b70b5e49136e60f817f00a45a08d337a8/README.md)、[源2](https://github.com/hk-modding/api/blob/3ea7ee5e6919bbb60da4d8c32851422141fe759c/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[TheMulhima/Lumafly](https://github.com/TheMulhima/Lumafly)：`{"repo":"TheMulhima/Lumafly","ref":"9765dd7b70b5e49136e60f817f00a45a08d337a8","branch":"master","release":"v3.3.0.0","published_at":"2024-09-29T18:26:58Z","license":"GPL-3.0","release_url":"https://github.com/TheMulhima/Lumafly/releases/tag/v3.3.0.0","prerelease":{"version":"v1.41.0.0","published_at":"2023-04-30T03:05:00Z","url":"https://github.com/TheMulhima/Lumafly/releases/tag/v1.41.0.0"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[hk-modding/api](https://github.com/hk-modding/api)：`{"repo":"hk-modding/api","ref":"3ea7ee5e6919bbb60da4d8c32851422141fe759c","branch":"master","release":"1.5.78.11833-77","published_at":"2025-12-08T06:40:58Z","license":"MIT","release_url":"https://github.com/hk-modding/api/releases/tag/1.5.78.11833-77","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-hades"></a>

## Hades

`hades` · Steam 1145360

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| ModImporter 的 Lua / SJSON / 资源包<br>`hades-modimporter` · 外部工具 | 按MOD作者标记的Hades游戏版本；不是Hades II新框架<br>Content/Mods/<Mod>/modfile.txt and content | `<game-root>/Content/Mods/<Mod>/；安装后在Content运行ModImporter`<br>ModImporter会修改游戏脚本，不是仅复制文件；需其备份、依赖与卸载清理流程。；插件不自动运行任意modfile安装指令或Python；目前外部工具处理。 | [源1](https://github.com/SGG-Modding/ModImporter/blob/8bda3bbefdc165afc4485db1158a87715b2524b0/modimporter.py)、[源2](https://github.com/hongbeans/hades-sett/blob/main/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[SGG-Modding/ModImporter](https://github.com/SGG-Modding/ModImporter)：`{"repo":"SGG-Modding/ModImporter","ref":"8bda3bbefdc165afc4485db1158a87715b2524b0","branch":"main","release":"1.6.1","published_at":"2024-05-08T15:09:07Z","license":"MIT","release_url":"https://github.com/SGG-Modding/ModImporter/releases/tag/1.6.1","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-hades-ii"></a>

## Hades II

`hades-ii` · Steam 1145350

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Hell2Modding / r2modman<br>`hell2modding` · 外部工具 | 按当前Hades II构建与Hell2Modding nightly精确匹配<br>Ship/d3d12.dll; ReturnOfModding/plugins/<Author-Mod> | `<game-root>/Ship/ReturnOfModding/plugins/；loader d3d12.dll紧邻Ship/Hades2.exe`<br>nightly标签虽GitHub prerelease=false，但这是滚动开发构建，不能标为稳定版本。；与旧Nexus ModImporter MOD不兼容；迁移须先按官方清理旧补丁。 | [源1](https://github.com/SGG-Modding/Hell2Modding/blob/b303fcdae987bb9fd00cba9450b6f799685dfa90/README.md)、[源2](https://github.com/SGG-Modding/Hades2ModWiki/blob/ce2886e9b86e5aca9fdf21883b43a4eac4aa27ef/docs/installing-mods/getting-started.md) |
| 旧 Technical Test / Early Access ModImporter<br>`hades2-modimporter-legacy` · 手动说明 | 仅作者明确说明的旧分支<br>Content/Mods/<Mod>/modfile.txt | `<game-root>/Content/Mods/<Mod>/`<br>不得与Hell2Modding混装；先恢复干净游戏文件，不自动迁移。 | [源1](https://github.com/SGG-Modding/Hades2ModWiki/blob/ce2886e9b86e5aca9fdf21883b43a4eac4aa27ef/docs/installing-mods/getting-started.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[SGG-Modding/Hell2Modding](https://github.com/SGG-Modding/Hell2Modding)：`{"repo":"SGG-Modding/Hell2Modding","ref":"b303fcdae987bb9fd00cba9450b6f799685dfa90","branch":"master","release":"nightly","published_at":"2026-10-18T20:35:26Z","license":"MIT","release_url":"https://github.com/SGG-Modding/Hell2Modding/releases/tag/nightly","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"rolling_development_nightly"}`；[SGG-Modding/Hades2ModWiki](https://github.com/SGG-Modding/Hades2ModWiki)：`{"repo":"SGG-Modding/Hades2ModWiki","ref":"ce2886e9b86e5aca9fdf21883b43a4eac4aa27ef","branch":"main","release":null,"published_at":null,"license":"not-declared","release_url":null,"prerelease":null,"archived":false,"checked_at":"2026-10-19","license_note":"No standard reuse permission verified; source-visible does not mean OSI open source.","release_kind":"no_stable_release"}`；[SGG-Modding/ModImporter](https://github.com/SGG-Modding/ModImporter)：`{"repo":"SGG-Modding/ModImporter","ref":"8bda3bbefdc165afc4485db1158a87715b2524b0","branch":"main","release":"1.6.1","published_at":"2024-05-08T15:09:07Z","license":"MIT","release_url":"https://github.com/SGG-Modding/ModImporter/releases/tag/1.6.1","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-vampire-survivors"></a>

## Vampire Survivors

`vampire-survivors` · Steam 1794680

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| 新 Unity IL2CPP 引擎 MOD<br>`vs-unity` · 手动说明 | Unity6新引擎；按包与BepInEx bleeding-edge元数据兼容要求；部分MelonLoader包需其指定版本<br>BepInEx/plugins/*.dll or MelonLoader Mods/*.dll | `<game-root>/BepInEx/plugins/ 或 <game-root>/Mods/，由包类型决定`<br>最新stable BepInEx不等于兼容Unity6 IL2CPP；需要作者当前指定的构建。；先辨别Mono/IL2CPP、引擎分支和加载器，不按DLL后缀猜测。 | [源1](https://github.com/Der-Floh/Vortex-VS-Support/blob/c9e254d5340d999715862251c87da814d3ce5a99/README.md) |
| 旧 JavaScript / Electron 引擎包<br>`vs-old-engine` · 手动说明 | 仅旧引擎分支<br>JavaScript mod loader or resource replacement | `作者指定旧版 resources/app/.webpack 等目录；不在未知布局强装`<br>不能安装到Unity新引擎；必须匹配原始版本资源及备份。 | [源1](https://github.com/Der-Floh/Vortex-VS-Support/blob/c9e254d5340d999715862251c87da814d3ce5a99/README.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[Der-Floh/Vortex-VS-Support](https://github.com/Der-Floh/Vortex-VS-Support)：`{"repo":"Der-Floh/Vortex-VS-Support","ref":"c9e254d5340d999715862251c87da814d3ce5a99","branch":"main","release":"v3.0.0","published_at":"2026-09-21T17:17:21Z","license":"MIT","release_url":"https://github.com/Der-Floh/Vortex-VS-Support/releases/tag/v3.0.0","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[LavaGang/MelonLoader](https://github.com/LavaGang/MelonLoader)：`{"repo":"LavaGang/MelonLoader","ref":"5aff4d9d7c16ae153aad2f1035114dbc2713bf99","branch":"master","release":"v0.7.3","published_at":"2026-05-14T20:20:01Z","license":"Apache-2.0","release_url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.7.3","prerelease":{"version":"v0.6.0","published_at":"2022-12-25T15:18:05Z","url":"https://github.com/LavaGang/MelonLoader/releases/tag/v0.6.0"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-among-us"></a>

## Among Us

`among-us` · Steam 945360

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| BepInEx 插件包<br>`bepinex-plugins` · 可实现候选 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。；Among Us多为IL2CPP包，需由具体MOD发布页确认架构和完整BepInEx pack；不能套Unity Mono stable包。；联网时所有玩家/房间兼容要求由MOD作者说明，插件不自动修改匹配或反作弊配置。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L745)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

<a id="game-dredge"></a>

## Dredge

`dredge` · Steam 1562430

| 方案 | 版本 / 包格式 | 目标与必要条件 | 来源 |
| --- | --- | --- | --- |
| Winch / DREDGE Mod Manager<br>`dredge-winch` · 外部工具 | Winch与MOD发布页对应当前DREDGE构建<br>Winch MOD directory / manager package | `DREDGE Mod Manager所检测并维护的MOD目录`<br>必须先安装Winch；由官方社区开源管理器处理loader、启禁、更新。；没有从README确认可直接根目录复制的统一包规范，因此不猜路径自动部署。 | [源1](https://dredgemods.com/manager/)、[源2](https://github.com/DREDGE-Mods/Winch/blob/eab943ff5c28ab150581ff42278946c22d1f1b7f/README.md)、[源3](https://github.com/DREDGE-Mods/DredgeModManager/blob/8531f9011fe58385269c1423e83d65dac4488f51/README.md) |
| 明确声明 BepInEx 的包<br>`bepinex-plugins` · 手动说明 | 按作者标注的游戏版本与 BepInEx 主版本选择<br>ZIP: BepInEx/plugins/<Mod>/*.dll and companion assets | `<game-root>/BepInEx/plugins/<Mod>/`<br>先按当前 MOD 文档安装该游戏对应 BepInEx 与依赖；Mono、IL2CPP、x86/x64 及 Linux/Proton 不可混装。；只管理经过预览的完整 BepInEx/plugins 包；patchers、monomod、loader/core 需独立确认。 | [源1](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/src/assets/data/ecosystem.json#L5125)、[源2](https://github.com/ebkr/r2modmanPlus/blob/a1897e3d6f7c1946dc51312252db1cc25f1dace0/docs/Adding%20a%20game.md) |

- Thunderstore BepInEx为独立路线；Winch生态MOD不得伪装为BepInEx插件。
- 仅完成来源及文件布局研究；不等于 Steam Deck 游戏内验证。
- 仅完成公开安装协议与版本分支研究；未进行 Steam Deck 实机验证。

上游版本与许可：[ebkr/r2modmanPlus](https://github.com/ebkr/r2modmanPlus)：`{"repo":"ebkr/r2modmanPlus","ref":"a1897e3d6f7c1946dc51312252db1cc25f1dace0","branch":"develop","release":"v3.2.20","published_at":"2026-09-22T12:23:15Z","license":"MIT","release_url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.2.20","prerelease":{"version":"v3.1.58","published_at":"2025-04-17T19:44:59Z","url":"https://github.com/ebkr/r2modmanPlus/releases/tag/v3.1.58"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[BepInEx/BepInEx](https://github.com/BepInEx/BepInEx)：`{"repo":"BepInEx/BepInEx","ref":"6cea286d204eb3754d3b8363a5a1fd6640164a49","branch":"master","release":"v5.4.23.5","published_at":"2026-02-08T01:03:44Z","license":"LGPL-2.1","release_url":"https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5","prerelease":{"version":"v6.0.0-pre.2","published_at":"2024-08-27T19:20:16Z","url":"https://github.com/BepInEx/BepInEx/releases/tag/v6.0.0-pre.2"},"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[DREDGE-Mods/Winch](https://github.com/DREDGE-Mods/Winch)：`{"repo":"DREDGE-Mods/Winch","ref":"eab943ff5c28ab150581ff42278946c22d1f1b7f","branch":"master","release":"v0.6.2","published_at":"2026-05-02T07:33:34Z","license":"MIT","release_url":"https://github.com/DREDGE-Mods/Winch/releases/tag/v0.6.2","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`；[DREDGE-Mods/DredgeModManager](https://github.com/DREDGE-Mods/DredgeModManager)：`{"repo":"DREDGE-Mods/DredgeModManager","ref":"8531f9011fe58385269c1423e83d65dac4488f51","branch":"main","release":"v0.1.8","published_at":"2026-05-01T00:13:41Z","license":"MIT","release_url":"https://github.com/DREDGE-Mods/DredgeModManager/releases/tag/v0.1.8","prerelease":null,"archived":false,"checked_at":"2026-10-19","release_kind":"stable_release_tag"}`

