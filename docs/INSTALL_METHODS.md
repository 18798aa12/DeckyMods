# 热门游戏 MOD 安装方式研究与插件目录

核查日期：2026-10-19。当前插件目录 **145 款独立 Steam 游戏**，其中本轮 **113 款**有公开安装协议、版本分支及来源研究；原有 72 个游戏身份保留，新增 73 款。GTA V Legacy/Enhanced 与 DOS2 Classic/DE 各算一款；Minecraft 没有 Steam AppID 不凑数，tModLoader 并入 Terraria 加载器方法。

这是安装目录与协议研究，**并非 113 款游戏全部 MOD 都能全自动安装**。未进行 Steam Deck 实机验证。是否有可执行安装方案以插件当前界面和受限格式检查为准；新增目录记录本身仍是 `catalog`，不会擅自提升为自动适配。

研究优先选择生化危机、Bethesda、赛博朋克、巫师、魂类、Stardew、Palworld、BepInEx 与其它常见 MOD 生态；没有把此选取顺序伪称实时下载排行榜。每个来源记录源码 commit、稳定版/开发版差异及许可证，完整可机读数据为 [install_guides.json](../data/install_guides.json)。

- [动作、Unreal、RE 与其它路线](INSTALL_METHODS_ACTION.md)
- [RPG、Bethesda、FromSoftware 与版本分支](INSTALL_METHODS_RPG.md)
- [Unity、独立游戏与加载器路线](INSTALL_METHODS_UNITY.md)

## 必须分开的版本与安装协议

- REFramework stable v1.5.9.1 与 2026-10-11 nightly-01432 分开。新统一包只有 dinput8.dll 和 revision 文本；旧非 RT RE2/3/7 需要匹配旧构建，不能盲升新单体版。
- RE0/RE1/旧 RE4/RE5/RE6/Revelations 不是 RE Engine，不能安装 REFramework。
- Palworld 普通 PAK、LogicMods、PalSchema、新旧 UE4SS 目录与 Win64/WinGDK 不混用。Okaetsu 固定 commit-tag 2281fa31 与 experimental-palworld 滚动资产分开记录。
- Skyrim Classic/SE/AE/VR、Fallout 旧新运行时与 VR 的原生扩展不通用；GOG 和 Steam 的版本号不直接等价。
- Granblue Relink 1.x 与 Endless Ragnarok 2.x、XCOM2 Base/WotC、Project Zomboid B41/B42、DOS2 Classic/DE、Subnautica 当前/旧 QMod 均保留独立路线。
- No Man's Sky 当前 GAMEDATA/MODS 与旧 deprecated PAK 的 GAMEDATA/PCBANKS/MODS 分开；不猜切换 build 阈值。
- KCD 标准清单叫 mod.manifest（XML）。一代排序写目录名，二代使用 modid；未实现安全排序合并时，文件部署不代表已启用。
- BepInEx Mono/IL2CPP、5/6 主版本、Linux 原生/Windows Proton 与 x86/x64 均需匹配。
- 归档中的 FOMOD、多个可选版本、脚本、EXE 安装器和归档内资源合并不会自动执行或盲目展开。

所有安装先预览、冲突确认并保留所有权与备份。已有游戏 ID、手工根目录、MOD 层、任务与启动项不迁移或重命名。未知 Nexus 域名留空，只提供本地导入和公开来源说明。普通 Nexus 账号 API 身份不取代网站确认下载权限。

## 本轮已加入插件的 113 款研究游戏

| 游戏 / 保持的插件 ID | Steam AppID | 安装路线与分版本 | 证据与完整说明 |
| --- | --- | --- | --- |
| Resident Evil 2 (2019)<br>`residentevil22019` | 883710 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支；旧非 RT 分支；RE2 TDB6…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil22019) |
| Resident Evil 3 (2020)<br>`residentevil32020` | 952060 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支；旧非 RT 分支；RE2 TDB6…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil32020) |
| Resident Evil 4 (2023)<br>`residentevil42023` | 2050650 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil42023) |
| Resident Evil 7<br>`residentevil7` | 418370 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支；旧非 RT 分支；RE2 TDB6…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil7) |
| Resident Evil Village<br>`residentevilvillage` | 1196590 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevilvillage) |
| Resident Evil Requiem<br>`residentevilrequiem` | 3764200 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevilrequiem) |
| Devil May Cry 5<br>`devilmaycry5` | 601150 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-devilmaycry5) |
| Street Fighter 6<br>`streetfighter6` | 1364780 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；Steam 当前分支；nightly 01432 单体包；仅作者声明支持的当前分支；按 MOD 作者声明的游戏分支 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-streetfighter6) |
| Resident Evil 0 HD<br>`residentevil0biohazard0hdremaster` | 339340 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil0biohazard0hdremaster) |
| Resident Evil HD<br>`residentevilbiohazardhdremaster` | 304240 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevilbiohazardhdremaster) |
| Resident Evil 4 (2005)<br>`residentevil4` | 254700 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil4) |
| Resident Evil 5<br>`residentevil5` | 21690 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil5) |
| Resident Evil 6<br>`residentevil6` | 221040 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevil6) |
| Resident Evil Revelations<br>`residentevilrevelations` | 222480 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本；该修复声明支持的 Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevilrevelations) |
| Resident Evil Revelations 2<br>`residentevilrevelations2` | 287290 | PC Steam 对应作品；匹配该作品发布标签；仅明确标注兼容的 PC Steam 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-residentevilrevelations2) |
| Stellar Blade<br>`stellarblade` | 3489700 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-stellarblade) |
| TEKKEN 8<br>`tekken8` | 1778820 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-tekken8) |
| Final Fantasy VII Rebirth<br>`finalfantasy7rebirth` | 2909400 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-finalfantasy7rebirth) |
| Code Vein<br>`codevein` | 678960 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-codevein) |
| Bloodstained Ritual of the Night<br>`bloodstainedritualofthenight` | 692850 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-bloodstainedritualofthenight) |
| Spyro Reignited Trilogy<br>`spyroreignitedtrilogy` | 996580 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-spyroreignitedtrilogy) |
| Final Fantasy VII Remake Intergrade<br>`finalfantasy7remake` | 1462040 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-finalfantasy7remake) |
| Guilty Gear -Strive-<br>`guiltygearstrive` | 1384160 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-guiltygearstrive) |
| Tales of Arise<br>`talesofarise` | 740130 | Steam PC；仅作者声明匹配当前更新的 cooked 资源；依作者要求的 UE、游戏及加载器版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-talesofarise) |
| Palworld<br>`palworld` | 1623730 | Steam/Win64；与当前 Palworld 更新兼容的资源；需要 BPModLoader/作者指定加载器的版本；Okaetsu 2281fa31 / experimental-palworld；按游戏更新核验；旧 UE4SS 2.5.2 / 3.0.0 发行结构；已安装兼容 PalSch…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-palworld) |
| Dragon's Dogma: Dark Arisen<br>`dragonsdogma` | 367500 | Steam Dark Arisen；非 Dragon's Dogma 2；作者指定的游戏版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-dragonsdogma) |
| Granblue Fantasy: Relink<br>`granbluefantasyrelink` | 881020 | 原版 1.x；Endless Ragnarok 2.x 须兼容的新 manager；按游戏 1.x / 2.x 架构匹配工具 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-granbluefantasyrelink) |
| Final Fantasy XV Windows Edition<br>`finalfantasy15` | 637650 | FFXV Windows Edition；不同 Flagrum/游戏版本按作者校验；Steam Workshop 支持的项目 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-finalfantasy15) |
| Final Fantasy XVI<br>`finalfantasy16` | 2515020 | Steam 完整版；loader 1.2.1 按游戏当前更新核验；FFXVI 当前机制；不泛化到 FFT 等其它游戏 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-finalfantasy16) |
| NieR:Automata<br>`nierautomata` | 524220 | Steam 版本；不能自动视为 Game Pass 兼容；对应当前 Steam build 的插件 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-nierautomata) |
| NieR Replicant ver.1.22474487139<br>`nierreplicant` | 1113560 | 作者匹配的 Steam build；示例为 v1.224 输入修复；按 MOD 的配置说明 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-nierreplicant) |
| Grand Theft Auto V (Legacy / Enhanced)<br>`gta5` | 271590, 3240220 | Legacy 与 Enhanced 必须分别核对插件兼容；RageOpenV 自述支持 Legacy + Enhanced，具体资源仍须版本匹配 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-gta5) |
| Red Dead Redemption 2<br>`reddeadredemption2` | 1174180 | 作者明确支持的当前 RDR2 build；指定 LML 版本与游戏 build | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-reddeadredemption2) |
| Bully: Scholarship Edition<br>`bullyscholarshipedition` | 12200 | PC Scholarship Edition；按当前游戏 build 匹配；作者指定的 Scholarship Edition 版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-bullyscholarshipedition) |
| Kingdom Come Deliverance<br>`kingdomcomedeliverance` | 379430 | Steam PC；一代/二代包不能互换；对应本作 mod_order.txt 机制 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-kingdomcomedeliverance) |
| Kingdom Come: Deliverance II<br>`kingdomcomedeliverance2` | 1771300 | Steam PC；一代/二代包不能互换；对应本作 mod_order.txt 机制 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-kingdomcomedeliverance2) |
| Mount & Blade II: Bannerlord<br>`mountandblade2bannerlord` | 261550 | Steam/GOG/Epic PC 版本；按 SubModule 依赖版本约束；不同游戏 build 与 .NET 运行时；Xbox 与其它商店不同 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-mountandblade2bannerlord) |
| Kenshi<br>`kenshi` | 233860 | Steam PC Kenshi；按作者当前版本要求；Kenshi 启动器 / mods.cfg 机制 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-kenshi) |
| XCOM 2<br>`xcom2` | 268500 | XCOM 2 Base；排除 WotC 专用包；XCOM 2 War of the Chosen；与原版独立兼容；Steam Windows/Proton 与 Linux 原生配置位置不同 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-xcom2) |
| No Man's Sky<br>`nomanssky` | 275850 | 当前 Vortex/MO2 2026 源码路线；以具体 MOD 作者的资源版本为准；历史 .pak 包；上游已标 deprecated；按当前 MBINCompiler / AMUMSS 支持版本 | [方法/路径/来源](INSTALL_METHODS_ACTION.md#game-nomanssky) |
| Skyrim Special Edition<br>`skyrimspecialedition` | 489830 | SE 1.5.97；AE 1.6.x；Steam AE 1.7.104；GOG AE 单独匹配；SE1.5.97→SKSE2.0.20；历史Steam1.6.1170→2.2.6；当前Steam1.7.104→2.3.1；GOG: 官网1.6.1179与README1.6.1170冲突需人工确认 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-skyrimspecialedition) |
| The Elder Scrolls V: Skyrim (Classic / Legendary)<br>`skyrim` | 72850 | Classic / Legendary 1.9.32；运行时1.9.32→SKSE1.7.3 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-skyrim) |
| The Elder Scrolls V: Skyrim VR<br>`skyrimvr` | 611670 | VR 1.4.15；与SE/AE区分；VR1.4.15→SKSEVR2.0.12 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-skyrimvr) |
| Enderal: Forgotten Stories (Classic)<br>`enderal` | 933480 | Classic standalone / Skyrim LE-based | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-enderal) |
| Fallout 4<br>`fallout4` | 377160 | 旧版1.10.163；次世代1.10.984；当前1.11.240；1.10.163→0.6.23；1.10.984→0.7.2；1.11.240→0.7.9；VR1.2.72→VR0.6.21 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-fallout4) |
| Fallout 4 VR<br>`fallout4vr` | 611660 | VR1.2.72；不与标准FO4混装；1.10.163→0.6.23；1.10.984→0.7.2；1.11.240→0.7.9；VR1.2.72→VR0.6.21 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-fallout4vr) |
| Fallout 3 / Game of the Year<br>`fallout3` | 22300, 22370 | Standard / GOTY；FOSE按运行时匹配 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-fallout3) |
| Fallout: New Vegas<br>`falloutnv` | 22380 | Standard / Ultimate；NVSE按运行时匹配 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-falloutnv) |
| The Elder Scrolls IV: Oblivion (2006)<br>`oblivion` | 22330 | 原版 / GOTY；不兼容Remastered | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-oblivion) |
| Enderal: Forgotten Stories (Special Edition)<br>`enderalspecialedition` | 976620 | Enderal SE Steam / GOG 独立分支；EnderalSE Steam / GOG | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-enderalspecialedition) |
| The Elder Scrolls IV: Oblivion Remastered<br>`oblivionremastered` | 2623190 | Remastered；原版2006包不自动兼容；Remastered按游戏更新匹配；MO2 basic_games 当前适配模型0.1.0-b.1；UE4SS按游戏构建 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-oblivionremastered) |
| The Elder Scrolls III: Morrowind GOTY<br>`morrowind` | 22320 | 原版Morrowind/GOTY；OpenMW0.51.0稳定；0.50及更旧需按MOD说明 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-morrowind) |
| Starfield<br>`starfield` | 1716740 | 当前Steam/GOG安装，按具体游戏构建匹配；SFSE按运行时分支；商店发行版不同 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-starfield) |
| Cyberpunk 2077<br>`cyberpunk2077` | 1091500 | 1.6.x旧版与2.x当前分支分开；依作者游戏版本；CET/redscript/RED4ext各版本需匹配游戏运行时；支持REDmod的游戏版本；区别于普通archive模组 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-cyberpunk2077) |
| The Witcher 3<br>`witcher3` | 292030 | Classic1.x(含1.32)；Next-Gen4.x；Remastered5.0；1.x/4.x legacy分支；5.0 remastered分支 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-witcher3) |
| The Witcher 2: Assassins of Kings Enhanced Edition<br>`witcher2` | 20920 | Enhanced Edition；包需匹配游戏版本 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-witcher2) |
| The Witcher: Enhanced Edition<br>`witcher` | 20900 | Enhanced Edition | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-witcher) |
| Baldur's Gate 3<br>`baldursgate3` | 1086940 | Patch6及更旧格式；Patch7格式；Patch8格式；按游戏Patch和构建；原生Linux/macOS版本另行验证 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-baldursgate3) |
| Divinity Original Sin 2<br>`divinityoriginalsin2` | 435150 | Definitive Edition；Classic/original分支；与DE分别下载 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-divinityoriginalsin2) |
| Divinity: Original Sin Enhanced Edition<br>`divinityoriginalsinenhancededition` | 373420 | Enhanced Edition；不与原版Classic混用；Enhanced Edition | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-divinityoriginalsinenhancededition) |
| ELDEN RING<br>`eldenring` | 1245620 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对；ModEngine2 release-2.1.0；维护已停止 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-eldenring) |
| ELDEN RING NIGHTREIGN<br>`eldenringnightreign` | 2622380 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-eldenringnightreign) |
| DARK SOULS III<br>`darksouls3` | 374320 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对；ModEngine2 release-2.1.0；维护已停止 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-darksouls3) |
| Sekiro Shadows Die Twice<br>`sekiro` | 814380 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对；旧版0.1.x加载器；me3迁移需作者确认 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-sekiro) |
| ARMORED CORE VI FIRES OF RUBICON<br>`armoredcore6` | 1888160 | me3稳定v0.13.0；profileVersion=v1；游戏运行时与DLL版本另行核对 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-armoredcore6) |
| DARK SOULS REMASTERED<br>`darksoulsremastered` | 570940 | DSR；工具历史稳定1.5，仓库已归档；具体整合包的当前版本 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-darksoulsremastered) |
| Dark Souls II<br>`darksouls2` | 236430 | 32位原版/DX9 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-darksouls2) |
| DARK SOULS II Scholar of the First Sin<br>`darksouls2sotfs` | 335300 | 64位Scholar/DX11 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-darksouls2sotfs) |
| Dragon Age Origins<br>`dragonage` | 17450, 47810 | 对应原版/Ultimate；按游戏和DLC版本 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-dragonage) |
| Dragon Age II / Ultimate<br>`dragonage2` | 1238040 | 对应原版/Ultimate；按游戏和DLC版本 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-dragonage2) |
| Dragon Age: Inquisition<br>`dragonageinquisition` | 1222690 | 旧Frosty1.0.6.3；按游戏profile；未正式发布的master重写；不默认安装；只适用于.daimod作者指定的DAI构建/补丁 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-dragonageinquisition) |
| Mass Effect: Andromeda<br>`masseffectandromeda` | 1238000 | 旧Frosty1.0.6.3；按游戏profile；未正式发布的master重写；不默认安装 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-masseffectandromeda) |
| Mass Effect Legendary Edition (LE1 / LE2 / LE3)<br>`masseffectlegendaryedition` | 1328670 | M3稳定9.2.1.137；LE1/LE2/LE3分别选择；MEM稳定534；LE1/LE2/LE3分开 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-masseffectlegendaryedition) |
| Dragon's Dogma 2<br>`dragonsdogma2` | 2054970 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；对应游戏的REFramework构建；稳定/开发nightly分开；按游戏更新/REF版本/插件ABI匹配；Rise基础/Sunbreak、Wilds…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-dragonsdogma2) |
| MONSTER HUNTER RISE / Sunbreak<br>`monsterhunterrise` | 1446780 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；对应游戏的REFramework构建；稳定/开发nightly分开；按游戏更新/REF版本/插件ABI匹配；Rise基础/Sunbreak、Wilds…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-monsterhunterrise) |
| Monster Hunter Wilds<br>`monsterhunterwilds` | 2246340 | 当前兼容游戏分支：nightly-01432 统一 REFramework.zip；RE2/RE3/RE7 旧非 RT 分支必须另选匹配旧构建；对应游戏的REFramework构建；稳定/开发nightly分开；按游戏更新/REF版本/插件ABI匹配；Rise基础/Sunbreak、Wilds…（完整见详情） | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-monsterhunterwilds) |
| Monster Hunter World<br>`monsterhunterworld` | 582010 | World基础 / Iceborne及对应更新；对应当前World/Iceborne构建 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-monsterhunterworld) |
| Hogwarts Legacy<br>`hogwartslegacy` | 990080 | 非官方传统MOD；按游戏更新与MOD版本选择；按游戏提供的影片文件匹配；旧扩展Mods/Mods.txt布局；UE4SS3.x/new ue4ss/Mods布局需按构建核对 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-hogwartslegacy) |
| Black Myth: Wukong<br>`blackmythwukong` | 2358720 | 游戏版本按MOD说明；WukongMM1.0.0记录布局；UE4SS及CSharpLoader版本独立匹配当前游戏 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-blackmythwukong) |
| Ghost of Tsushima DIRECTOR'S CUT<br>`ghostoftsushima` | 2215430 | PC Director's Cut；按MOD对应版本；与当前PC游戏更新匹配 | [方法/路径/来源](INSTALL_METHODS_RPG.md#game-ghostoftsushima) |
| Valheim<br>`valheim` | 892970 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-valheim) |
| Lethal Company<br>`lethal-company` | 1966720 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-lethal-company) |
| Risk of Rain 2<br>`riskofrain2` | 632360 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-riskofrain2) |
| Content Warning<br>`content-warning` | 2881650 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-content-warning) |
| R.E.P.O.<br>`repo` | 3241660 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-repo) |
| Dyson Sphere Program<br>`dyson-sphere-program` | 1366540 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-dyson-sphere-program) |
| ULTRAKILL<br>`ultrakill` | 1229490 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-ultrakill) |
| Inscryption<br>`inscryption` | 1092790 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-inscryption) |
| Hollow Knight: Silksong<br>`hollow-knight-silksong` | 1030300 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-hollow-knight-silksong) |
| Stardew Valley<br>`stardewvalley` | 413150 | 1.6.x: SMAPI 4.x；1.5.6 legacy: SMAPI 3.18.6；SMAPI 4.5.2 stable; archived installers for older game branches；仅作者明确匹配的旧版/当前游戏资源 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-stardewvalley) |
| Terraria<br>`terraria` | 105600 | 1.4.4 stable；1.4.3 legacy；1.3 legacy；1.4.5 development 按官方分支标记；游戏内资源包系统支持的版本；1.4.3: tModLoader-1.4.3；1.3: ModLoader；1.4.5 development 单独确认 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-terraria) |
| RimWorld<br>`rimworld` | 294100 | 支持版本由 About/About.xml supportedVersions 与 LoadFolders.xml 声明，例如 1.5/1.6；当前 RimSort 及游戏版本 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-rimworld) |
| Factorio<br>`factorio` | 427520 | info.json factorio_version 分别匹配 1.1、2.0、后续版本 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-factorio) |
| Risk of Rain Returns<br>`risk-of-rain-returns` | 1337520 | 由 MOD 声明的 RoRR game build 与 Return Of Modding 版本 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-risk-of-rain-returns) |
| Schedule I<br>`schedule-i` | 3164500 | 游戏默认 IL2CPP 与 alternate/Mono 分支需分别匹配；当前 MelonLoader stable 0.7.3 不代表所有旧 MOD 可直接升级 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-schedule-i) |
| Sons Of The Forest<br>`sons-of-the-forest` | 1326470 | 按作者标注的游戏版本与 BepInEx 主版本选择；按 MOD 的 RedLoader / 游戏版本要求 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-sons-of-the-forest) |
| The Forest<br>`the-forest` | 242760 | ModAPI v2.0.9623；v1 为旧版且不能覆盖安装 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-the-forest) |
| Subnautica<br>`subnautica` | 264710 | Subnautica Living Large/2.0+ 对应 Nautilus；Below Zero 使用明确支持 BZ 的包；Subnautica legacy/pre-Living-Large；Below Zero 仅 MOD 作者明确要求的旧 QMod 分支 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-subnautica) |
| Subnautica: Below Zero<br>`subnautica-below-zero` | 848450 | Subnautica Living Large/2.0+ 对应 Nautilus；Below Zero 使用明确支持 BZ 的包；Subnautica legacy/pre-Living-Large；Below Zero 仅 MOD 作者明确要求的旧 QMod 分支 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-subnautica-below-zero) |
| Slime Rancher<br>`slime-rancher` | 433340 | 仅原版 Slime Rancher；按作者要求的 SRML/game 版本 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-slime-rancher) |
| Slime Rancher 2<br>`slime-rancher-2` | 1657630 | 按Starlight发布页的游戏与 MelonLoader 版本组合；旧 SR2E 与新 Starlight 不自动等同；当前作者Linux教程要求 MelonLoader >=0.7.3；Starlight stable v4.0.4 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-slime-rancher-2) |
| 7 Days to Die<br>`7daystodie` | 251570 | 匹配 A20/A21/1.x/2.x 等明确发布分支；不跨版本假定兼容；由当前版本设置及作者文档指定 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-7daystodie) |
| Project Zomboid<br>`project-zomboid` | 108600 | Build 41 legacy；Build 42；42.x 需按实际版本子目录声明 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-project-zomboid) |
| Cities: Skylines<br>`cities-skylines` | 255710 | Cities: Skylines I 与其对应 DLC/游戏更新 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-cities-skylines) |
| Cities: Skylines II<br>`cities-skylines-ii` | 949230 | 按作者标注的游戏版本与 BepInEx 主版本选择；由 Paradox Mods 与 MOD manifest 标记的 CS2 游戏版本 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-cities-skylines-ii) |
| Satisfactory<br>`satisfactory` | 526870 | SML、MOD版本与游戏CL#逐项匹配 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-satisfactory) |
| Core Keeper<br>`core-keeper` | 1621690 | 按 ModManifest.json 与当前游戏 SDK 兼容声明；按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-core-keeper) |
| Hollow Knight<br>`hollow-knight` | 367520 | API 1.5.78.11833-77 对应其上游游戏分支；旧分支需旧API | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-hollow-knight) |
| Hades<br>`hades` | 1145360 | 按MOD作者标记的Hades游戏版本；不是Hades II新框架 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-hades) |
| Hades II<br>`hades-ii` | 1145350 | 按当前Hades II构建与Hell2Modding nightly精确匹配；仅作者明确说明的旧分支 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-hades-ii) |
| Vampire Survivors<br>`vampire-survivors` | 1794680 | Unity6新引擎；按包与BepInEx bleeding-edge元数据兼容要求；部分MelonLoader包需其指定版本；仅旧引擎分支 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-vampire-survivors) |
| Among Us<br>`among-us` | 945360 | 按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-among-us) |
| Dredge<br>`dredge` | 1562430 | Winch与MOD发布页对应当前DREDGE构建；按作者标注的游戏版本与 BepInEx 主版本选择 | [方法/路径/来源](INSTALL_METHODS_UNITY.md#game-dredge) |
