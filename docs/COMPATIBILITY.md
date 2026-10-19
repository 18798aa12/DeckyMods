# 游戏兼容矩阵

本版目录扩展至 **145 款游戏、100 个系列**；下表保留首批 72 款的基础适配器资料。本轮 113 款、244 条分版本路线见 [安装方式研究](INSTALL_METHODS.md)，其余新增项为目录识别，不代表全自动适配。Steam AppID 经 Steam 官方商店 API 核对；MOD 安装路径参考下列作者说明和公开源码。登记数量不是游戏内验证数量。

能力分为：**自动映射 12 款**（5 款 UE PAK，7 款旧引擎生化危机资源替换）、**需准备 7 款**（REFramework 结构化脚本/插件）、**仅下载映射 53 款**（自动安装仍需专用适配）。所有能力均有合成文件测试；已完成 Steam Deck 后端回归和 RE7 Item Unlocker 脚本加载验证，其他游戏内效果仍待验证。

## 安装边界

- 普通 UE PAK 仅安装到各游戏登记的 `Content/Paks/~mods`。若出现 `.ucas` 或 `.utoc`，必须同时保留同名 `.pak/.ucas/.utoc`。普通 PAK、蓝图 LogicMods、UE4SS、存档与配置是不同类型，后几种本版阻止自动安装。
- 多个独立资源包在预览中全部列出；多个可选目录、缺失配套文件、错误游戏目录、可执行安装器和链接会阻止部署。
- REFramework 需要用户先安装官方匹配版本。插件检测到前置后会自动检查并补齐 Proton 的 `dinput8.dll=n,b` 参数，保留其他原有启动项，冲突或复杂命令会提示人工检查。本版识别 `reframework/autorun` 和 `reframework/plugins`；存在 DLL 只代表前置文件存在，仍需确认游戏实际加载成功。
- RE2/3/4 重制、RE7、Village、Requiem 的 `natives` 资源使用共享 `re2_fw_config.txt` 的 LooseFileLoader。配置有效但开关未启用时，在安装确认后备份并配置；缺失或损坏配置会阻止安装。RE9 pak_mods 另要求 PAK Directory Loading，不将此规则套用其他作品。
- RE4 重制版单一 PAK 仅接受 `re_chunk_000.pak.patch_NNN.pak`，并要求原版 `re_chunk_000.pak` 存在。部署引擎负责已启用包的连续编号；多个候选 PAK 需要用户先选出所需版本。游戏版本兼容性仍取决于 MOD 作者说明。
- RE0、HD、RE4 原版、RE5、RE6、启示录 1/2 按各作 nativePC/nativePC_MT/BIO4 目录适配，仅替换已存在的普通资源文件。DLL、安装器、归档内部编辑和不确定的新路径会被拒绝。RE5 Steam Gold 的 Nexus 域名为 residentevil5goldedition。
- Steam 游戏库包括默认目录、合法 Steam 根链接、`steamapps/libraryfolders.vdf` 与旧式 `config/libraryfolders.vdf` 声明的 SD 卡目录。安装目录必须位于对应库的 `steamapps/common` 内。插件不接受 UI 提供任意安装目标。
- 运行中的游戏禁止改动；仅对与已验证游戏路径相关的无法读取进程保守阻止，无关受保护的浏览器或密钥进程不会阻止所有游戏。

## 主要依据

- [官方 Vortex 游戏扩展库](https://github.com/Nexus-Mods/vortex-games)：基础发现映射与专用安装器是不同功能，不能将所有扩展视为同一种安装方式。这里只整理事实映射，未复制 GPL 代码。
- [剑星扩展作者说明](https://www.nexusmods.com/site/mods/1324)：普通 PAK、LogicMods、UE4SS、配置和存档分别处理；符号链接不支持。本项目未复制该扩展受限制的代码或资产。
- [REFramework 官方安装与 Proton 说明](https://github.com/praydog/REFramework)、[现代 LooseFileLoader 源码](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.cpp)。
- [Fluffy 作者排障文档](https://www.patreon.com/FluffyQuack/posts/fluffy-manager-68199696)：版本分支、PAK 文件失效处理、更新后的重读档案及 Steam Deck 差异。
- [Fluffy 新式 PAK 说明](https://www.patreon.com/FluffyQuack/posts/fluffy-mod-v3-151635881)：新 RE Engine 游戏可能使用 `pak_mods`，不能套用旧作的补丁编号。

## 每款游戏

下列来源为具体事实映射依据。Steam 商店来源支持 AppID，扩展/作者来源支持安装方式；“仅下载映射”不代表已实现其专用加载器或可在 SteamOS 正常运行。

| 系列 | 游戏 | Steam AppID | Nexus 域名 | 本版能力 | 来源 |
|---|---|---|---|---|---|
| Stellar Blade | Stellar Blade | 3489700 | stellarblade | 普通 PAK 自动安装 | [依据](https://www.nexusmods.com/games/stellarblade) |
| The Elder Scrolls | Skyrim Special Edition | 489830 | skyrimspecialedition | 仅下载映射 | [依据](https://www.nexusmods.com/games/skyrimspecialedition) |
| Fallout | Fallout 4 | 377160 | fallout4 | 仅下载映射 | [依据](https://www.nexusmods.com/games/fallout4) |
| The Witcher | The Witcher 3 | 292030 | witcher3 | 仅下载映射 | [依据](https://www.nexusmods.com/games/witcher3) |
| Dark Souls | Dark Souls II | 236430 | darksouls2 | 仅下载映射 | [依据](https://www.nexusmods.com/games/darksouls2) |
| Monster Hunter | Monster Hunter World | 582010 | monsterhunterworld | 仅下载映射 | [依据](https://www.nexusmods.com/games/monsterhunterworld) |
| Devil May Cry | Devil May Cry 5 | 601150 | devilmaycry5 | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://www.nexusmods.com/games/devilmaycry5) |
| Dragon's Dogma | Dragon's Dogma: Dark Arisen | 367500 | dragonsdogma | 仅下载映射 | [依据](https://www.nexusmods.com/games/dragonsdogma) |
| 7 Days to Die | 7 Days to Die | 251570 | 7daystodie | 仅下载映射 | [依据](https://www.nexusmods.com/games/7daystodie) |
| A Hat in Time | A Hat in Time | 253230 | ahatintime | 仅下载映射 | [依据](https://www.nexusmods.com/games/ahatintime) |
| Baldur's Gate | Baldur's Gate 3 | 1086940 | baldursgate3 | 仅下载映射 | [依据](https://www.nexusmods.com/games/baldursgate3) |
| BattleTech | BattleTech | 637090 | battletech | 仅下载映射 | [依据](https://www.nexusmods.com/games/battletech) |
| Blade & Sorcery | Blade & Sorcery | 629730 | bladeandsorcery | 仅下载映射 | [依据](https://www.nexusmods.com/games/bladeandsorcery) |
| Bloodstained | Bloodstained Ritual of the Night | 692850 | bloodstainedritualofthenight | 普通 PAK 自动安装 | [依据](https://www.nexusmods.com/games/bloodstainedritualofthenight) |
| Code Vein | Code Vein | 678960 | codevein | 普通 PAK 自动安装 | [依据](https://www.nexusmods.com/games/codevein) |
| Conan | Conan Exiles | 440900 | conanexiles | 仅下载映射 | [依据](https://www.nexusmods.com/games/conanexiles) |
| Cyberpunk | Cyberpunk 2077 | 1091500 | cyberpunk2077 | 仅下载映射 | [依据](https://www.nexusmods.com/games/cyberpunk2077) |
| Darkest Dungeon | Darkest Dungeon | 262060 | darkestdungeon | 仅下载映射 | [依据](https://www.nexusmods.com/games/darkestdungeon) |
| Dawn of Man | Dawn of Man | 858810 | dawnofman | 仅下载映射 | [依据](https://www.nexusmods.com/games/dawnofman) |
| Divinity | Divinity Original Sin 2 | 435150 | divinityoriginalsin2 | 仅下载映射 | [依据](https://www.nexusmods.com/games/divinityoriginalsin2) |
| Dragon Age | Dragon Age Origins | 17450 | dragonage | 仅下载映射 | [依据](https://www.nexusmods.com/games/dragonage) |
| Elex | Elex | 411300 | elex | 仅下载映射 | [依据](https://www.nexusmods.com/games/elex) |
| Factorio | Factorio | 427520 | factorio | 仅下载映射 | [依据](https://www.nexusmods.com/games/factorio) |
| Garden Paws | Garden Paws | 840010 | gardenpaws | 仅下载映射 | [依据](https://www.nexusmods.com/games/gardenpaws) |
| GreedFall | GreedFall | 606880 | greedfall | 仅下载映射 | [依据](https://www.nexusmods.com/games/greedfall) |
| Grim Dawn | Grim Dawn | 219990 | grimdawn | 仅下载映射 | [依据](https://www.nexusmods.com/games/grimdawn) |
| Legend of Grimrock | Legend of Grimrock | 207170 | grimrock | 仅下载映射 | [依据](https://www.nexusmods.com/games/grimrock) |
| Kenshi | Kenshi | 233860 | kenshi | 仅下载映射 | [依据](https://www.nexusmods.com/games/kenshi) |
| Kerbal Space Program | Kerbal Space Program | 220200 | kerbalspaceprogram | 仅下载映射 | [依据](https://www.nexusmods.com/games/kerbalspaceprogram) |
| Kingdom Come | Kingdom Come Deliverance | 379430 | kingdomcomedeliverance | 仅下载映射 | [依据](https://www.nexusmods.com/games/kingdomcomedeliverance) |
| Halo | Halo The Master Chief Collection | 976730 | halothemasterchiefcollection | 仅下载映射 | [依据](https://www.nexusmods.com/games/halothemasterchiefcollection) |
| Microsoft Flight Simulator | Microsoft Flight Simulator | 1250410 | microsoftflightsimulator | 仅下载映射 | [依据](https://www.nexusmods.com/games/microsoftflightsimulator) |
| Mount & Blade | Mount & Blade Warband | 48700 | mbwarband | 仅下载映射 | [依据](https://www.nexusmods.com/games/mbwarband) |
| Neverwinter Nights | Neverwinter Nights Enhanced Edition | 704450 | neverwinter | 仅下载映射 | [依据](https://www.nexusmods.com/games/neverwinter) |
| No Man's Sky | No Man's Sky | 275850 | nomanssky | 仅下载映射 | [依据](https://www.nexusmods.com/games/nomanssky) |
| Oxygen Not Included | Oxygen Not Included | 457140 | oxygennotincluded | 仅下载映射 | [依据](https://www.nexusmods.com/games/oxygennotincluded) |
| Palworld | Palworld | 1623730 | palworld | 普通 PAK 自动安装 | [依据](https://www.nexusmods.com/games/palworld) |
| Pathfinder | Pathfinder Kingmaker | 640820 | pathfinderkingmaker | 仅下载映射 | [依据](https://www.nexusmods.com/games/pathfinderkingmaker) |
| Prison Architect | Prison Architect | 233450 | prisonarchitect | 仅下载映射 | [依据](https://www.nexusmods.com/games/prisonarchitect) |
| RimWorld | RimWorld | 294100 | rimworld | 仅下载映射 | [依据](https://www.nexusmods.com/games/rimworld) |
| Sekiro | Sekiro Shadows Die Twice | 814380 | sekiro | 仅下载映射 | [依据](https://www.nexusmods.com/games/sekiro) |
| Shadowrun | Shadowrun Returns | 234650 | shadowrunreturns | 仅下载映射 | [依据](https://www.nexusmods.com/games/shadowrunreturns) |
| The Sims | The Sims 3 | 47890 | thesims3 | 仅下载映射 | [依据](https://www.nexusmods.com/games/thesims3) |
| Spyro | Spyro Reignited Trilogy | 996580 | spyroreignitedtrilogy | 普通 PAK 自动安装 | [依据](https://www.nexusmods.com/games/spyroreignitedtrilogy) |
| Starbound | Starbound | 211820 | starbound | 仅下载映射 | [依据](https://www.nexusmods.com/games/starbound) |
| Stardew Valley | Stardew Valley | 413150 | stardewvalley | 仅下载映射 | [依据](https://www.nexusmods.com/games/stardewvalley) |
| Starfield | Starfield | 1716740 | starfield | 仅下载映射 | [依据](https://www.nexusmods.com/games/starfield) |
| State of Decay | State of Decay | 241540 | stateofdecay | 仅下载映射 | [依据](https://www.nexusmods.com/games/stateofdecay) |
| Subnautica | Subnautica | 264710 | subnautica | 仅下载映射 | [依据](https://www.nexusmods.com/games/subnautica) |
| Surviving Mars | Surviving Mars | 464920 | survivingmars | 仅下载映射 | [依据](https://www.nexusmods.com/games/survivingmars) |
| Star Wars | Knights of the Old Republic | 32370 | kotor | 仅下载映射 | [依据](https://www.nexusmods.com/games/kotor) |
| Team Fortress | Team Fortress 2 | 440 | teamfortress2 | 仅下载映射 | [依据](https://www.nexusmods.com/games/teamfortress2) |
| Torchlight | Torchlight II | 200710 | torchlight2 | 仅下载映射 | [依据](https://www.nexusmods.com/games/torchlight2) |
| Total War | Total War Three Kingdoms | 779340 | totalwarthreekingdoms | 仅下载映射 | [依据](https://www.nexusmods.com/games/totalwarthreekingdoms) |
| Untitled Goose Game | Untitled Goose Game | 837470 | untitledgoosegame | 仅下载映射 | [依据](https://www.nexusmods.com/games/untitledgoosegame) |
| Vampire The Masquerade | Vampire The Masquerade Bloodlines | 2600 | vampirebloodlines | 仅下载映射 | [依据](https://www.nexusmods.com/games/vampirebloodlines) |
| Wolcen | Wolcen Lords of Mayhem | 424370 | wolcenlordsofmayhem | 仅下载映射 | [依据](https://www.nexusmods.com/games/wolcenlordsofmayhem) |
| X | X4 Foundations | 392160 | x4foundations | 仅下载映射 | [依据](https://www.nexusmods.com/games/x4foundations) |
| XCOM | XCOM 2 | 268500 | xcom2 | 仅下载映射 | [依据](https://www.nexusmods.com/games/xcom2) |
| Resident Evil | Resident Evil 0 HD | 339340 | residentevil0biohazard0hdremaster | 现有资源替换；不执行安装器 | [依据](https://github.com/descawed/re0box) |
| Resident Evil | Resident Evil HD | 304240 | residentevilbiohazardhdremaster | 现有资源替换；不执行安装器 | [依据](https://www.nexusmods.com/residentevilbiohazardhdremaster/mods/241?tab=description) |
| Resident Evil | Resident Evil 2 (2019) | 883710 | residentevil22019 | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
| Resident Evil | Resident Evil 3 (2020) | 952060 | residentevil32020 | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
| Resident Evil | Resident Evil 4 (2005) | 254700 | residentevil4 | 现有资源替换；不执行安装器 | [依据](https://github.com/nipkownix/re4_tweaks) |
| Resident Evil | Resident Evil 4 (2023) | 2050650 | residentevil42023 | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
| Resident Evil | Resident Evil 5 | 21690 | residentevil5goldedition | 现有资源替换；不执行安装器 | [依据](https://www.nexusmods.com/residentevil5goldedition/mods/92?tab=docs) |
| Resident Evil | Resident Evil 6 | 221040 | residentevil6 | 现有资源替换；不执行安装器 | [依据](https://www.nexusmods.com/residentevil6/mods/217) |
| Resident Evil | Resident Evil 7 | 418370 | residentevil7 | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
| Resident Evil | Resident Evil Village | 1196590 | residentevilvillage | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
| Resident Evil | Resident Evil Revelations | 222480 | residentevilrevelations | 现有资源替换；不执行安装器 | [依据](https://www.nexusmods.com/residentevilrevelations/mods/39) |
| Resident Evil | Resident Evil Revelations 2 | 287290 | residentevilrevelations2 | 现有资源替换；不执行安装器 | [依据](https://www.nexusmods.com/residentevilrevelations2/mods/38?tab=posts) |
| Resident Evil | Resident Evil Requiem | 3764200 | residentevilrequiem | 需匹配 REFramework；脚本/资源规则已实现 | [依据](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.hpp) |
