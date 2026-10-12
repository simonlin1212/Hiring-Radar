<p align="center"><b>简体中文</b> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar · 招聘雷达</h1>

<p align="center">
  <b>AI 驱动的全球招聘信息雷达 —— 扫描全球与中国的在招岗位，用来找工作、读产业风向、看市场在花钱招什么人。</b><br>
  An AI-powered radar for the global job market — scanning open roles worldwide and in China, for job hunting, industry signals and market research.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/全球-24_ATS_+_12_跨公司来源-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/中国-170_家官方门户-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-支持-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/依赖-纯标准库-lightgrey.svg" alt="stdlib">
</p>

---

<p align="center">
  <a href="#这是什么">这是什么</a> ·
  <a href="#能力-features">能力</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#给-ai-用mcp">MCP</a> ·
  <a href="#输出字段">输出字段</a> ·
  <a href="#覆盖来源">覆盖来源</a> ·
  <a href="#相关项目大平台去哪找">相关项目</a> ·
  <a href="#使用边界--合规">使用边界</a>
</p>

---

## 这是什么

**Hiring Radar 是一个面向 AI 的招聘数据工具——它让 AI（Claude Code / Codex / ChatGPT / 任意 agent）能直接读取全球 + 中国公司的官方在招岗位。** 它读公司自己的招聘系统（ATS）和公开职位来源的公开接口，把在招岗位整理成**统一字段的结构化数据**。在你本地跑，一条命令查一家公司、一个国家、一个职能，**零账号、零配置**。

三类用法：

- 🔎 **求职 / 看「哪里在招人」**：某个方向现在哪些公司在招、在哪个城市、给多少薪。
- 📊 **市场研究 / 找产品机会**：按国家、职能、时间整片拉取，看整个市场在花钱招什么人（v2 新增）。
- 📈 **产业 / 投资「领先信号」**：招聘往往比财报早几个月暴露公司战略。详见 [产业信号应用](#产业信号应用)。

**全球大牌只需一个公司名即可查到**，例如 NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab 等等。

**v2 新增**：24 个招聘系统 + 约 9 万家公司的名录（按公司名直接查到用哪个系统）· 12 个跨公司来源（含 freehire 聚合、瑞典/新加坡/德国政府职位库）· 多来源去重和疑似中介标记 · 按发布时间分档 · 中断可续跑 · 本地存档看新增/下架 · **MCP 服务**，AI 助手可直接调用。 完整变更见 [CHANGELOG.md](CHANGELOG.md)。

> ⚠️ 只读**企业主动公开的岗位信息**，不抓个人简历、不碰需要登录的内容，遇到人机验证就停。详见 [使用边界 / 合规](#使用边界--合规)。

## 能力 Features

| 能力 | 说明 |
|---|---|
| **按⁠公⁠司⁠查** | 给公司名即可：先查公司名录（约 9 万家，覆盖 24 个招聘系统），查不到再猜常见系统；也可 `--ats 系统 slug` 精确指定 |
| **跨⁠公⁠司⁠整⁠片⁠拉** | `--board` 按国家 / 关键词 / 近 N 天拉：freehire 聚合、Workable 全站、政府职位库、远程板；多个来源一次拉、自动去重 |
| **时⁠间⁠分⁠档** | 每条标 近3个月 / 3-6个月 / 半年以前 / 无日期；`--board` 默认只看近半年 |
| **疑⁠似⁠中⁠介** | 标出猎头/劳务派遣发的岗位（`agency` 字段），`--no-agency` 可去掉 |
| **断⁠点⁠续⁠跑** | 某个来源被限流或出错，其他来源照跑；同样的命令加 `--resume` 只补没完成的 |
| **本⁠地⁠存⁠档** | `--save` 存进本机 SQLite，记首次/最近看到；`--history` 看历次新增和下架 |
| **M⁠C⁠P⁠ ⁠服⁠务** | `--mcp` 让 Claude Code / Codex 等直接调用（查公司、搜职位、查名录） |
| **中⁠国⁠ ⁠1⁠7⁠0⁠ ⁠家** | `--local` 直查：飞书招聘 / Moka / 北森 三套通用解析 + 6 家大厂自建 |
| **私⁠有⁠插⁠件** | 条款不适合公开分发的来源，放你自己的插件目录（`--plugins`），不进仓库 |
| **纯⁠标⁠准⁠库** | 零依赖（仅 Moka 解析需 `pycryptodome`），任意 `python3` 可跑 |

## 快速开始

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # 下载公司名录（约 9 万家，存在本机，可选但推荐）
python3 hiring_radar.py --list               # 列出所有来源
```

```bash
# 1) 按公司查：给名字即可
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # 名录查到 → 自动用对的系统
python3 hiring_radar.py --find xero                  # 只查它用哪个招聘系统
python3 hiring_radar.py --ats teamtailor <slug>      # 精确指定系统和账号
python3 hiring_radar.py --workday host,tenant,site

# 2) 跨公司整片拉：国家 + 关键词 + 时间
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json > au.json   # 不设上限，全量
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # 瑞典政府职位库
python3 hiring_radar.py --board all --keyword "AI engineer"                              # 4 个远程板

# 3) 中断后续跑 / 存档看变化
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json --resume > au.json   # 中断后：参数和上面那条完全一样，只加 --resume
python3 hiring_radar.py anthropic --save          # 下次再跑会显示新增/下架
python3 hiring_radar.py --history

# 4) 中国公司
python3 hiring_radar.py --local agibot --keyword 机器人      # 智元机器人(飞书系)
python3 hiring_radar.py --local cambricon --keyword 大模型   # 寒武纪(Moka系，需 pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # 腾讯(自建)
```

**常用参数**：`--keyword a,b`（任一命中）· `--recent-days N`（0=不限）· `--country AU,NZ` · `--max N`（每个来源上限，默认 1000，0=不限）· `--no-agency` · `--json` · `--limit N` · `--debug`

**从 v1 升级**：`--board` 现在默认只看近 183 天、每个来源最多 1000 条，多个来源自动去重；要和 v1 一样的结果，加 `--recent-days 0 --max 0 --no-dedupe`。

**环境变量**：`HIRING_RADAR_HOME`（名录/存档/续跑进度目录，默认 `~/.hiring-radar`）· `HIRING_RADAR_DELAY`（同一网站两次请求最小间隔秒数，默认 0.3）· `HIRING_RADAR_PLUGINS`（私有插件目录）· `HIRING_RADAR_INSECURE=1`（仅拦截式代理下关闭证书校验）

退出码：`0` 正常；`1` 出错；`3` 结果不全——有来源出错停下（已拉到的照常输出，同样的命令加 `--resume` 补完），或上游翻页有上限只给了一部分（续跑补不回来，请缩小查询），或 `--directory-update` 有系统没下载成功（保留旧名单）。

## 给 AI 用（MCP）

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

提供 5 个工具：`company_jobs`（查一家公司）· `search_jobs`（跨公司搜）· `find_company`（查名录）· `list_sources` · `job_history`。JD 在 MCP 结果里截到 800 字，要全文用命令行 `--json`。

## 输出字段

v1 的 15 个字段不变：`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(薪资) · jd(完整) · url · apply_url · id`

v2 追加 9 个：`country`（两位国家码）· `source`（来源）· `age`（时间分档 0-3m/3-6m/6m+/unknown）· `agency`（疑似中介命中的词）· `also`（去重时同一职位出现过的其他来源）· `industry` · `size`（公司规模，来源给了才有）· `first_seen` · `last_seen`（存档时才有）

`--json` 外层：`source · total · matched · jobs`（同 v1）+ `version · query · ages · sources · incomplete · candidates · saved`。

## 工作原理

```
公司名 / 国家 + 关键词
        │
        ▼
┌───────────────────────┐
│ 选来源                 │  按公司：公司名录 → 24 个招聘系统公开接口
│                       │  跨公司：freehire / Workable / 政府职位库 / 远程板 / 私有插件
│                       │  中国：飞书 / Moka / 北森 / 大厂自建
└──────────┬────────────┘
           │  联网：如实报身份、同站限速、429 退避、403/验证页就停
┌──────────▼────────────┐
│ 统一 24 字段 + 时间分档 │  关键词 / 国家 / 近 N 天过滤；多来源去重；标疑似中介
└──────────┬────────────┘
      ┌────┴─────┬──────────┐
      ▼          ▼          ▼
  终端摘要    --json 全量   本地存档 / MCP
```

## 覆盖来源

**按公司查：24 个招聘系统**（公司名录来自 [openroles](https://github.com/datascry/openroles)，运行时下载到本机，不打包进仓库）

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**跨公司来源 `--board`（12 个）**

| 来源 | 范围 | 说明 |
|---|---|---|
| `freehire` | 全球（自称约 330 万在招；2026-10-12 公开接口可搜到约 203 万） | [freehire](https://github.com/strelov1/freehire) 公开接口，聚合 225 个来源，含完整 JD，可按国家/关键词/近 N 天 |
| `workable` | 全球 | Workable 全站搜索，可按国家/关键词 |
| `jobtech` | 瑞典全国 | 瑞典公共就业服务开放数据，含完整 JD |
| `mycareersfuture` | 新加坡全国 | 新加坡政府求职网，有薪资，无 JD |
| `arbeitsagentur` | 德国全国 | 德国联邦就业局，无 JD |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | 远程岗 | `--board all` = 这 4 个 |
| `reed` · `adzuna` · `usajobs` | 英国 / 19 国 / 美国联邦政府 | 需要你自己的免费密钥（`REED_API_KEY`、`ADZUNA_APP_ID`+`ADZUNA_APP_KEY`、`USAJOBS_API_KEY`+`USAJOBS_EMAIL`），按官方文档编写，维护者未实网测试 |

**中国 170 家（`--local`）**：飞书招聘系（理想/小鹏/蔚来/智元/月之暗面/MiniMax/智谱…）· Moka 系（鹰角/寒武纪/幻方/SHEIN…）· 北森系（追觅/奇瑞/零跑/京东方/三一…）· 大厂自建（腾讯/网易/京东/百度/字节/宇树）。完整名单 `--list`。

**不支持 / 已知限制**
- **Paycom**：它的 robots.txt 不放行职位列表接口，按规矩不读。
- **iCIMS**：页面里的 `datePosted` 是系统生成的假日期（当前时间减两年），本工具改用站点地图里的更新时间。用其他工具抓的 iCIMS 数据，发布日期要当心。
- 名录里有不少已停用的账号，查到但没有岗位属正常；同名不同公司可能撞上，命中多个时会列出全部候选。
- 去重按 国家 + 公司 + 职位名：同一公司同名职位在同一国家多个城市发布，会合成一条。

> **关于 Moka（诚实说明）**：Moka 系公司的接口对响应做了一层轻量前端混淆（AES-128-CBC，密钥与 IV 都随其公开前端下发）。本工具用这些前端自带的公开值还原出与浏览器所见完全相同的公开岗位列表——不破解登录、不绕鉴权。严格说属「还原前端处理」，比纯读 JSON 略灰，仅供本地研究自用、自担风险。想要最干净的合规姿态，删 `parsers/companies.seed` 里所有 `moka` 行 + `radar/local.py` 里内置的 `yostar`/`tesla-cn` 两行即可。

## 私有插件

条款不适合把抓取代码公开分发的大平台，可以写成你自己的插件，放在仓库之外：

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

插件目录里每个不以 `_` 开头的 `.py` 是一个来源，定义 `NAME`、`DESC`、`FILTERS` 和 `pages(q, state=None)`（接口同 `radar/boards/`）；以 `_` 开头的文件可放共用代码。插件以你的权限运行，访问网站的条款由你自行遵守。

## 相关项目：大平台去哪找

Hiring Radar 不带 Indeed、LinkedIn、SEEK 这类大平台的抓取代码。下面两个第三方开源仓库有，表里按平台列出代码大致在哪，方便你自己去看。

- **[speedyapply/JobSpy](https://github.com/speedyapply/JobSpy)**：Python 库，MIT 许可证。一次查多个平台，返回职位名、公司、地点、薪资、链接和 JD。
- **[strelov1/freehire](https://github.com/strelov1/freehire)**：Go 写的职位搜索引擎，MIT 许可证，225 个来源。下表里它的代码是后台采集的一部分，不是单独的库；本仓库 `--board freehire` 读的就是它的公开接口。

| 平台 | 覆盖 | 仓库 | 代码大致位置 |
|---|---|---|---|
| Indeed | 约 60 个国家，含美英加澳新爱 | JobSpy | `jobspy/indeed/` |
| LinkedIn | 全球 | JobSpy | `jobspy/linkedin/` |
| Glassdoor | 约 20 个国家 | JobSpy | `jobspy/glassdoor/` |
| ZipRecruiter | 美国、加拿大 | JobSpy | `jobspy/ziprecruiter/` |
| Google 职位搜索 | 地点写在搜索词里 | JobSpy | `jobspy/google/` |
| Naukri | 印度 | JobSpy | `jobspy/naukri/` |
| Bayt | 中东、海湾 | JobSpy | `jobspy/bayt/` |
| BDJobs | 孟加拉 | JobSpy | `jobspy/bdjobs/` |
| HelloWork | 法国 | JobSpy | `jobspy/hellowork/` |
| SEEK | 澳洲、新西兰 | freehire | `internal/ingest/sources/seek.go` |
| JobStreet / JobsDB | 新加坡、马来西亚、印尼、菲律宾 / 香港、泰国 | freehire | 同上 `seek.go`（同一套接口） |
| LinkedIn 公开职位列表 | 全球；它只用来找在招的公司 | freehire | `cmd/harvest-linkedin/` |
| WhatJobs | 多国；需要 WhatJobs 发布方账号 | freehire | `internal/ingest/sources/whatjobs.go` |

> 这些是第三方项目，不属于 Hiring Radar。我们没有审查过它们的代码，也不提供把它们接进本工具的代码。开源许可证只说明代码怎么用，不代表平台允许抓取：用之前请先看目标网站的使用条款和 robots.txt。以上 2026-10-12 核对，仓库结构以后可能变。

## 加公司 = 加一行（中国）

中国公司清单在 `parsers/companies.seed`（`|` 分隔），新增一家只加一行：

```
key | feishu | 公司名 | 门户域名(如 nio.jobs.feishu.cn)
key | moka   | 公司名 | orgId | siteId
key | beisen | 公司名 | slug
```

接新的招聘系统或跨公司来源见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 产业信号应用

招聘是**领先指标**：公司在哪扩产、招什么方向、招到哪个阶段，往往比财报早几个月暴露战略。招产线开发 = 线还在搭；招质检/维护 = 准备持续生产；招夜班 = 上量临近。用 `--save` 定期存档、`--history` 看环比节奏。

> ⚠️ **招聘 ≠ 产量**：岗位是「投入」非「产出」；「在招」也可能是储备或反信号。结论当信号参考，非投资建议。

## 项目结构

```
Hiring-Radar/
├── hiring_radar.py     # 命令行入口（v1 命令写法不变）
├── radar/              # 核心包
│   ├── http.py         # 联网：如实报身份、限速、退避、被拦就停
│   ├── schema.py       # 统一字段、日期、时间分档
│   ├── ats/            # 按公司查：每个招聘系统一个文件
│   ├── boards/         # 跨公司来源
│   ├── directory.py    # 公司名录（运行时下载）
│   ├── process.py      # 去重、标中介
│   ├── sweep.py        # 多来源整片拉取、续跑
│   ├── store.py        # 本地存档（SQLite）
│   ├── local.py        # 中国/自建站解析器调度
│   ├── plugins.py      # 私有插件加载
│   └── mcp.py          # MCP 服务
├── parsers/            # 中国 / 自建站解析器 + companies.seed
├── tests/              # smoke_test.py · test_offline.py（离线，不连外网）
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## 技术栈与依赖

- **Python 3.8+**，核心纯标准库（urllib / json / re / ssl / argparse / sqlite3 / xml.etree）
- **`pycryptodome`**：仅 Moka 系解析需要（`pip install pycryptodome`）
- 联网即可（部分国际站点可能需代理）；SSL 默认验证证书，拦截式代理可设 `HIRING_RADAR_INSECURE=1`

## 使用边界 / 合规

这是一个 **个人 / 研究自用 + 开源** 的本地工具。请负责任地使用：

- **只读「岗位信息」，不抓简历 / 任何个人信息**（碰个人信息踩 PIPL，禁止）。
- **只读公开、无需登录的接口**：遇到登录墙 / 验证码 / 主动反爬的站点**不绕过**；403 或人机验证页直接停下；不用代理池、不伪装浏览器指纹。
- **如实报身份、低频**：User-Agent 写明 HiringRadar 和项目地址（例外：飞书招聘和字节跳动的接口不接受程序身份，这两套沿用 v1 的浏览器 UA；USAJobs 官方接口要求 User-Agent 填你申请密钥时的邮箱，照它的要求来）；同一网站两次请求默认间隔 0.3 秒；429 按对方要求退避，仍不行就停下等你续跑。加新来源前检查 robots.txt（Paycom 因此不支持）。
- **密钥只放环境变量**：需要密钥的来源从环境变量读，报错信息里的密钥会打码。
- **仅本地运行**：不含托管 / 上传 / 服务端；数据只落你本地。二次发布需你自行评估合规，不商用转卖数据。公司名录数据是 CC BY-SA 4.0，再分发须署名并同样许可（见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)）。
- 「公开可见」≠「可随意聚合再发布」——大规模抓取并公开转载他人数据在多地（含中国《反不正当竞争法》判例）可能构成不正当竞争。

## 免责声明

1. **你掌控你的数据。** 工具在你本地运行，不收集、不上传任何数据。
2. **你遵守第三方条款。** 须遵守你访问的各招聘平台条款；不得用本工具骚扰雇主或冲击其系统。
3. **结论仅供参考。** 招聘数据是信号，非事实；产业/投资判断自负其责。

本软件以 [MIT 许可](LICENSE) 「按现状」提供，不作任何担保。第三方代码与数据见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## License

[MIT](LICENSE)

欢迎 PR 补充更多公司 / 数据源（见 [CONTRIBUTING.md](CONTRIBUTING.md)）。

**作者：** Simon 林 · X [@linsizhen](https://x.com/linsizhen) · 邮箱：[simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
