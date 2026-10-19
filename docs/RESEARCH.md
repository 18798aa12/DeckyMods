# 调研记录 — 2026-10-19

## Nexus 普通账户

- [官方 API 客户端说明](https://github.com/Nexus-Mods/node-nexus-api/blob/master/docs/classes/_nexus_.nexus.md)：下载 URL 的普通账户调用需要网站生成的 `key`、`expires`，不能将仅 API Key 的 Premium 路径当作普通账户能力。
- [官方 SSO 示例](https://github.com/Nexus-Mods/sso-integration-demo)：正式应用需要自己的应用身份。本项目不借用 Vortex 或其他插件的 SSO 标识。
- [API acceptable use policy](https://help.nexusmods.com/article/114-api-acceptable-use-policy)：当前是个人 Key 自用测试构建。商店发行前完成 Nexus 应用登记、SSO 和数据使用要求核对。

实现：个人 Key 只在私有设置 0600 文件保存；公开 RPC 仅返回账户名称、ID、会员状态。网站产生的 NXM 授权校验账户及有效期，下载后不持久保存；私有接收队列在消费时删除授权。请求 API 和下载 CDN 分别设置请求头，不把 API Key 发送到 CDN。连接使用 HTTPS，限制域名、公网 DNS 及重定向。

## 游戏与已有工具

参考 GitHub 上现有 Decky Nexus 插件思路；研究快照 `ca1a4ea05e2231e29d632eac70a8064bc868cd77` 展示了 Decky 接收下载和游戏映射的做法，其普通会员 NXM 接收仍有未完成部分，因此未把它当作可直接使用的实现。部署引擎独立实现，包含内容对象、层覆盖、原文件备份、校验和 SQLite 恢复日志。

- [Vortex 官方游戏扩展目录](https://github.com/Nexus-Mods/vortex-games)，研究快照 `18bbee9baf1fefb2bf1f9d28ae0e39fb8266974e`。其中不少目录只是扩展入口；“存在映射”不能推导出“已经可安装”。
- [REFramework 官方源码](https://github.com/praydog/REFramework)：脚本/插件目录及 Proton 的 `dinput8.dll` 加载条件。
- [REFramework LooseFileLoader](https://github.com/praydog/REFramework/blob/master/src/mods/LooseFileLoader.cpp)：RE4 重制版松散资源须明确启用对应设置，不能仅复制 `natives` 后宣称生效。
- [Fluffy Mod Manager 作者说明](https://www.patreon.com/FluffyQuack/posts/fluffy-manager-68199696)：早期 RE Engine 资源替换涉及原 PAK 处理，不能一概按普通目录覆盖。
- [剑星 Vortex 扩展作者页面](https://www.nexusmods.com/site/mods/1324)：核对 `SB/Content/Paks/~mods` 与 PAK/IOStore 格式事实。该扩展的代码再分发受限制，本项目没有复制其代码。

Steam AppID 与游戏名字通过 Steam 官方商店 API 核对。72 个条目及每条适配来源均保存在 `data/games.json` 和 [兼容表](COMPATIBILITY.md)。识别 60 个系列是目录覆盖，具体部署能力单独标注。

## 安全读取与协议接收

- [libarchive-c 官方源码/说明](https://github.com/Changaco/python-libarchive-c)：只使用 `fd_reader` 和逐条数据块读取，路径由插件自行校验。不调用归档的自动解压到目录接口。
- [Desktop Entry Exec 规范](https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html)：NXM 接收使用固定 Python 脚本和正确引用的参数，不将 URI 放进 shell 命令。

## 开发依赖检查

0.2.0 生化危机补充：REFramework 固定提交 `d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee` 的 LooseFileLoader/Mod 配置定义证实共享 `re2_fw_config.txt` 与 `LooseFileLoader_Enabled`；PAK Directory Loading 依赖新 TDB，按 RE9 单独适配。现代非 RT 旧分支不能使用当前通用包。[官方源码](https://github.com/praydog/REFramework/tree/d052e8fd3fd41d0a1a33394fcf6e6c19be39b1ee)、[Fluffy 作者对 LooseFileLoader 的说明](https://www.patreon.com/posts/113299381)。旧引擎各作资源替换的具体作者依据随游戏条目保存，未复制第三方管理器实现。

初版继承配置中发现 [Rollup 文件路径公告](https://github.com/advisories/GHSA-mw96-cpmx-2vgc) 与 [Vitest UI 公告](https://github.com/advisories/GHSA-5xrq-8626-4rwp)。已更新构建/测试工具，移除旧清理依赖，使用 `node:fs` 清理固定输出目录；最终版本由 package.json 和锁文件记录。测试不启动对局域网开放的 Vitest UI。

## Proxy virtual DNS compatibility

Some TUN configurations return addresses in the reserved 198.18.0.0/15 range. These are never connected to as public destinations. For an entirely virtual response and only the official Nexus/GitHub hosts, use the fixed Cloudflare HTTPS resolver at 1.1.1.1, validate a bounded JSON response, reject every non-public result, pin the resulting public IP and retain the original hostname for TLS. Ordinary private/mixed DNS results remain blocked. The DNS query contains a hostname only; no Nexus API credentials are sent to the resolver. See the [Cloudflare JSON DoH specification](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/).
