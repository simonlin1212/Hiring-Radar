# Changelog

本项目遵循语义化版本。日期为发布日。

## [2.0.0] - 待发布

v1 的命令和 JSON 前 15 个字段不变，旧用法照常可用。

### 按公司查
- **24 个招聘系统**（原 9 个 + Workable）：新增 Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp。多数用真实公司实测。
- **公司名录**：`--directory-update` 下载 openroles 每晚更新的名单（约 9.3 万家公司，CC BY-SA 4.0，运行时下载、不打包）；给公司名先查名录，查不到再按 v1 方式猜。`--find 公司名` 只看它用哪个系统，`--ats 系统 slug` 精确指定，`--no-directory` 回到 v1 行为。
- 共用 schema.org JobPosting 解析；iCIMS 页面里的 `datePosted` 是系统生成的假日期，改用站点地图里的更新时间。
- 不支持 Paycom：它的 robots.txt 不放行职位列表接口。

### 跨公司来源 `--board`
- 新增 **freehire**（225 个来源的聚合，可按国家/关键词/近 N 天，含完整 JD）、**Workable 全站搜索**。
- 新增政府职位库：**瑞典 JobTech**、**新加坡 MyCareersFuture**、**德国联邦就业局**（免注册，已实测）。
- 新增 **Reed**、**Adzuna**、**USAJOBS**：需用户自己的免费密钥，放环境变量；按官方文档编写，维护者未实网测试。
- `--country`、`--max`（每个来源上限，默认 1000，0=不限）；`--board` 默认只看近 183 天。`--board all` 仍是 v1 的 4 个远程板。
- 多来源自动去重（`also` 记其他来源，`--no-dedupe` 关闭）；疑似中介/猎头标记（`agency`），`--no-agency` 去掉。
- 某个来源出错不影响其他来源；`--resume` 从中断处继续；有来源没拉完时退出码为 3。

### 新功能
- **时间分档**：每条标 近3个月 / 3-6个月 / 半年以前 / 无日期（`age` 字段），输出里给各档数量。
- **本地存档**：`--save` 存进 SQLite，记首次/最近看到；`--history` 看历次新增和下架；`--db` 指定位置。
- **MCP 服务**：`--mcp`（stdio），工具 `company_jobs` / `search_jobs` / `find_company` / `list_sources` / `job_history`。
- **私有插件**：`--plugins 目录` 或 `HIRING_RADAR_PLUGINS`，放条款不适合公开分发的来源，不进仓库。
- 新增 9 个字段：`country · source · age · agency · also · industry · size · first_seen · last_seen`（共 24 个）。

### 修复
- Workday：职位链接改成当前可打开的格式（旧链接 404）；翻页不再只到第 2 页；名录缺站点名时读 robots.txt 和常见站点名。

### 联网与安全
- User-Agent 改为如实标明 HiringRadar 和项目地址（v1 是浏览器 UA）。
- 429/502/503/504 按 `Retry-After` 退避，仍不行就停下；403 或人机验证页直接停，不绕过；同一网站两次请求默认间隔 0.3 秒（`HIRING_RADAR_DELAY`）。
- 密钥只从环境变量读；报错信息、日志和续跑进度文件里的密钥参数会打码。
- 代码拆成 `radar/` 包，`hiring_radar.py` 只做入口；离线单元测试 29 个。
- 新增 THIRD_PARTY_NOTICES.md：openroles（MIT 代码 / CC BY-SA 数据）、freehire（MIT）。

## [1.1.0] - 2026-06-27

首个开源版本。

### 数据源
- **全球 9 大 ATS**：Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio（给公司名 auto-probe 8 个 ATS）。
- **4 个全球远程聚合板**：RemoteOK · Remotive · WeWorkRemotely · WorkingNomads（`--board`，跨公司）。
- **中国 170 家企业官方门户**：飞书招聘 / Moka / 北森 三套通用解析 + 腾讯/网易/京东/百度/字节/宇树 自建（`--local`，数据驱动种子表 `companies.seed`）。北森系覆盖大型制造/车企/家电/装备巨头（追觅/奇瑞/零跑/京东方/三一…），是产业信号的重要补充。

### 功能
- 统一 15 字段 schema；`--json` 出全量（含完整 JD）；终端摘要按 公司/部门/地点 Top 聚合。
- `--keyword`（逗号 OR，搜标题/部门/地点/JD/薪资）· `--recent-days` · `--limit` · `--list` · `--debug` · `--version`。
- 加公司 = 往 `companies.seed` 加一行，零代码。

### 安全 / 合规
- SSL 默认验证证书（`HIRING_RADAR_INSECURE=1` 可在拦截式代理下关闭）。
- local-parser 机制带安全护栏：解释器白名单 + 路径逃逸防护 + 参数注入防护 + 不用 shell。
- 定位：个人 / 研究自用；只读公开岗位、不抓个人简历、不做公开聚合再分发（见 README「使用边界」）。
