# Changelog

本项目遵循语义化版本。日期为发布日。

## [2.0.0] - 2026-10-12

v1 的命令写法和 JSON 前 15 个字段照常可用，但 `--board` 的默认结果变了：默认只看近 183 天、每个来源最多 1000 条、多个来源自动去重。要和 v1 一样的结果，加 `--recent-days 0 --max 0 --no-dedupe`。

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
- 某个来源出错不影响其他来源；`--resume` 从中断处继续。
- 结果不全时退出码为 3：有来源出错（可 `--resume`），或上游翻页有上限只给了一部分（续跑补不回来，需缩小查询；输出里会提示），或 `--directory-update` 有系统没下载成功。

### 新功能
- **时间分档**：每条标 近3个月 / 3-6个月 / 半年以前 / 无日期（`age` 字段），输出里给各档数量。
- **本地存档**：`--save` 存进 SQLite，记首次/最近看到；`--history` 看历次新增和下架；`--db` 指定位置。
- **MCP 服务**：`--mcp`（stdio），工具 `company_jobs` / `search_jobs` / `find_company` / `list_sources` / `job_history`。
- **私有插件**：`--plugins 目录` 或 `HIRING_RADAR_PLUGINS`，放条款不适合公开分发的来源，不进仓库。
- 新增 9 个字段：`country · source · age · agency · also · industry · size · first_seen · last_seen`（共 24 个）。
- README 新增“相关项目”：列出能抓 Indeed、LinkedIn、SEEK 等大平台的第三方开源仓库和代码大致位置（本仓库不含这些代码）。

### 修复
- Workday：职位链接改成当前可打开的格式（旧链接 404）；翻页不再只到第 2 页；名录缺站点名时读 robots.txt 和常见站点名。
- 中国门户解析脚本（`parsers/`）改用统一联网模块（限速、退避、被拦就停），并改为如实报身份。唯一例外：飞书招聘和字节跳动的接口不接受程序身份（HTTP 405），这两套沿用 v1 的浏览器 UA。
- 日期："30+ days ago" 这类只知道下限的说法不再当成正好 30 天；能识别 `2026年10月12日` 这种中文日期。
- 去重：非拉丁文字（中文、阿拉伯文等）的公司名和职位名不再被清空后误合并；公司或职位名缺失的条目不做模糊合并。
- 续跑：进度按字节位置记，中断时写了一半的行会丢掉重拉；续跑不再重写已有结果，结果文件和进度对不上时从头重拉，不会悄悄漏职位；同一来源重复出现的职位只算一次，先去重再算 `--max`。
- 存档对比：只和"同样查询、上次完整跑完"的结果比（Workday 站点、`--jd` 也算查询条件）；超出时间窗口的旧职位不算下架；不完整的一次不比较；新增/下架在存档时算好存下，之后不会被改写；多个进程同时建库不再报错。
- 被拦（403/人机验证）优先于限流判断；`Retry-After` 支持日期格式，要求等待超过 5 分钟时直接停下，不缩短等待；429/502/503/504 重试用完一律停下这个来源。
- 报错里的密钥（含请求头和环境变量里的密钥值）一律打码；`--debug` 日志和异常堆栈也打码。
- 给公司名查询（查名录、自动探测）时，某个招聘系统被拦就不再继续请求它。
- `--directory-update` 有系统失败时保留旧名单，不再清空。
- iCIMS 站点地图改用 XML 解析；ApplicantPro 数字薪资不再报错；Workday 取 JD 时被拦或限流会停下，个别详情格式不对只跳过那一条，没补完的都标记结果不全。
- 私有插件导入时打印到标准输出的内容改到标准错误，不再弄坏 MCP 通信。
- MCP：参数类型不对时回报错误、服务继续运行。

### 联网与安全
- User-Agent 改为如实标明 HiringRadar 和项目地址（v1 是浏览器 UA）；飞书招聘、字节跳动两套例外，见上。
- 429/502/503/504 按 `Retry-After` 退避，仍不行就停下；403 或人机验证页直接停，不绕过；同一网站两次请求默认间隔 0.3 秒（`HIRING_RADAR_DELAY`）。
- 密钥只从环境变量读；报错信息、日志和续跑进度文件里的密钥参数会打码。
- 代码拆成 `radar/` 包，`hiring_radar.py` 只做入口；离线单元测试 51 个。
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
