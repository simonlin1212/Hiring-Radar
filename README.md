# Hiring Radar · 招聘雷达

**中文** · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>AI 驱动的全球招聘信息雷达 —— 扫描全球与中国的在招岗位，用来找工作、读产业风向。</b><br>
  An AI-powered radar for the global job market — scanning open roles worldwide and in China, for job hunting and industry signals.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/全球-9_ATS_+_4_聚合板-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/中国-170_家官方门户-red.svg" alt="China">
  <img src="https://img.shields.io/badge/依赖-纯标准库-lightgrey.svg" alt="stdlib">
</p>

---

## 这是什么

**Hiring Radar 是一个面向 AI 的招聘数据工具——它让 AI（Claude Code / ChatGPT / 任意 agent）能直接读取全球 + 中国公司的官方在招岗位。** 它直接读公司自己的官方招聘系统（ATS）公开接口，把在招岗位聚合成**结构化数据**喂给 AI 分析。不是又一个要你注册登录的招聘网站——它在你本地跑，一条命令查全球任意一家公司、一个赛道、或跨公司广撒网，**零账号、零配置**。

公司用的招聘系统（Greenhouse / Ashby / Lever / 飞书招聘 / Moka / 北森…）都有**前端自己调用的公开接口**，带完整 JD、部门、地点、发布日期、薪资。Hiring Radar 读的就是这些公开接口，几秒拉回岗位，干净、快、可直接喂给 AI 做分析。

两类用法：

- 🔎 **求职 / 看「哪里在招人」（主）**：某个方向现在哪些公司在招、在哪个城市、给多少薪。
- 📈 **产业 / 投资「领先信号」（小应用）**：招聘往往比财报早几个月暴露公司战略——在哪扩产、招什么方向、招到哪个阶段（≈ 离量产多近）。详见 [产业信号应用](#-产业信号应用小)。

覆盖 **9 大主流 ATS + 4 个全球远程聚合板 + 中国 170 家企业官方门户**——尤其补齐了**中国**（飞书招聘 / Moka / 北森 三套通用解析 + 腾讯/网易/京东/百度/字节/宇树 自建），这是大多数同类工具的空白。

**全球大牌只需一个公司名即可查到**，例如 NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab 等等。

> ⚠️ 它读的是**企业主动公开的岗位信息**，不抓个人简历、不碰需要登录的内容。自用、低频、做个有礼貌的访客。详见 [使用边界 / 合规](#-使用边界--合规)。

## ✨ 能力 Features

| 能力 | 说明 |
|---|---|
| **全⁠球⁠ ⁠p⁠e⁠r⁠-⁠c⁠o⁠m⁠p⁠a⁠n⁠y** | 凭公司名自动探测 8 个 ATS（Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio），命中即出完整 JD + 部门 + 地点 + 日期 + 薪资 |
| **全⁠球⁠远⁠程⁠聚⁠合⁠板** | `--board` 跨公司广撒网：RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **中⁠国⁠ ⁠1⁠7⁠0⁠ ⁠家** | `--local` 直查：飞书招聘 / Moka / 北森 三套**通用**解析（加公司=加一行）+ 6 家大厂自建。覆盖具身智能 / 大模型 / 半导体 / 车厂 / 储能光伏 / 量化 / 外企 / 游戏 等赛道 |
| **关⁠键⁠词⁠ ⁠/⁠ ⁠时⁠间⁠过⁠滤** | `--keyword a,b,c`（逗号 OR，搜标题/部门/地点/JD/薪资）· `--recent-days N` 只看近期新发 |
| **统⁠一⁠结⁠构⁠化⁠输⁠出** | 15 字段统一 schema；`--json` 出全量（含完整 JD），喂给后续 AI 分析 |
| **终⁠端⁠聚⁠合⁠摘⁠要** | 默认按「公司 / 部门 / 地点 Top」聚合 + 岗位列表，一眼看清谁在哪扩 |
| **数⁠据⁠驱⁠动⁠扩⁠展** | 中国公司清单是一张种子表 `companies.seed`，**加公司=加一行，零代码** |
| **纯⁠标⁠准⁠库** | 单入口脚本，零依赖（仅 Moka 解析需 `pycryptodome`），任意 `python3` 可跑 |

## 🚀 快速开始

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # 可选，仅查 Moka 系中国公司时需要

python3 hiring_radar.py --list             # 列出所有可查的公司 / 聚合板
```

```bash
# 1) 全球公司：公司名直接查（内置 figure/1x/anthropic/openai/scale/nvidia），或任意公司名 auto-probe
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # 显式指定 ATS
python3 hiring_radar.py --workday host,tenant,site

# 2) 中国公司：--local <key>（key 见 --list）
python3 hiring_radar.py --local agibot --keyword 机器人      # 智元机器人(飞书系)
python3 hiring_radar.py --local cambricon --keyword 大模型   # 寒武纪(Moka系)
python3 hiring_radar.py --local dreame --keyword 产品        # 追觅(北森系)
python3 hiring_radar.py --local tencent --keyword 算法       # 腾讯(自建)

# 3) 聚合板：跨公司「哪里招人」
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) 全量结构化输出（含完整 JD），喂分析
python3 hiring_radar.py --local zhipu --keyword 大模型 --json > out.json
```

**通用参数**：`--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug`（排错）· `--script <path>`（临时跑某个 parser）

## 📋 输出字段

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(薪资) · jd(完整) · url · apply_url · id`（共 15 字段）

GH / Ashby / Lever / 飞书 / Moka / 北森 / 腾讯 / 网易 / 京东 / 百度 一般含完整 JD；Workday 与个别 Moka 租户列表无 JD（仅标题/部门/地点/日期）。`--json` 出全量。

## ⚙️ 工作原理

```
一个公司名 / 赛道关键词
        │
        ▼
┌──────────────────┐
│  选数据源(自动)  │  全球: 9 ATS 公开 API / 4 远程聚合板
│                  │  中国: 飞书 / Moka / 北森 / 大厂自建
└────────┬─────────┘
         │
┌────────▼─────────┐
│  归一化 + 过滤    │  统一 15 字段；关键词 / 地点 / 时间筛
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 终端摘要    --json 全量
(公司/部门/  (含完整 JD,
 地点 Top)    喂 AI 分析)
```

各家 ATS 都有**前端自己调用的公开 JSON 接口**（如 Greenhouse `boards-api.greenhouse.io/v1/boards/<slug>/jobs`、飞书招聘 `<slug>.jobs.feishu.cn/api/v1/search/job/posts`）。本工具直接读这些公开接口并归一化，**不抓需登录的内容、不破解登录/鉴权/验证码**。

> **关于 Moka（诚实说明）**：Moka 系公司的接口对响应做了一层轻量前端混淆（AES-128-CBC，密钥与 IV 都随其公开前端下发）。本工具用这些**前端自带的公开值**还原出与浏览器所见**完全相同的公开岗位列表**——不破解登录、不绕鉴权。这层混淆并非访问控制，但严格说属「还原前端处理」，比纯读 JSON 略灰，**仅供本地研究自用、自担风险**。想要最干净的合规姿态，删 `companies.seed` 里所有 `moka` 行 + 主程序 `LOCAL_PARSERS` 内置的 `yostar`/`tesla-cn` 两行即可，其余来源不受影响。

## 🌐 覆盖来源

**全球 ATS（按公司名 auto-probe，支持 9 大系统）**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

头部大牌只需公司名即可（均实测可抓），例如：
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**全球远程聚合板（`--board`）**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`（合并）

**中国 170 家（`--local`，企业官方门户，数据驱动种子表）**
- **飞书招聘系**：理想 / 小鹏 / 蔚来 / 智元机器人 / 银河通用 / 星动纪元 / 月之暗面 / MiniMax / 智谱 / 小马智行 / 禾赛 / 安克 / 影石 …
- **Moka 系**：鹰角 / 完美世界 / 莉莉丝 / 壁仞 / 寒武纪 / 幻方量化 / 九坤 / SHEIN / 博世 / 施耐德 …
- **北森系**（大型制造/车企/家电/装备巨头多在此）：追觅 / 奇瑞 / 零跑 / 京东方 / 三一 …
- **大厂自建**：腾讯 / 网易 / 京东 / 百度 / 字节跳动 / 宇树科技

> 完整名单：`python3 hiring_radar.py --list`

## ➕ 加公司 = 加一行（零代码）

中国公司清单在 `parsers/companies.seed`（管道 `|` 分隔），程序启动自动加载。新增一家只加一行：

```
key | feishu | 公司名 | 门户域名(如 nio.jobs.feishu.cn)
key | moka   | 公司名 | orgId | siteId        # 两者在 app.mokahr.com/social-recruitment/{orgId}/{siteId} URL 里
key | beisen | 公司名 | slug                  # 门户 {slug}.zhiye.com，如 dreame → dreame.zhiye.com
```

接一个**全新数据源**（写个新 parser）见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📈 产业信号应用（小）

招聘是**领先指标**：公司在哪扩产、招什么方向、招到哪个阶段，往往比财报早几个月暴露战略。例如——

- 招产线开发 = 线还在搭；招质检/维护 = 准备持续生产；招夜班 = 两班倒上量临近；招来料质检/供应商质量 = 外部供应商进厂认证。
- 用 `--local <公司> --keyword 工厂,产线,量产` 看制造侧扩张；用 `--recent-days` 看近期新发；建议对核心标的做**月度对比**看环比节奏。

> ⚠️ **招聘 ≠ 产量**：岗位是「投入」非「产出」，中间隔着良率/爬坡/供应链；「在招」也可能是储备或反信号。结论当**信号参考**，非投资建议。

## 🗂️ 项目结构

```
Hiring-Radar/
├── hiring_radar.py        # 主程序（单入口）：全球 ATS / 聚合板 + 调度 + 归一化
├── parsers/               # 中国 / 自建源解析器
│   ├── feishu.py          # 飞书招聘（通用）
│   ├── moka.py            # Moka 摩卡（通用，需 pycryptodome）
│   ├── beisen.py          # 北森（通用）
│   ├── tencent / netease / jd / baidu / bytedance / unitree .py   # 大厂自建
│   └── companies.seed     # 中国公司种子表（加公司=加一行）
├── tests/smoke_test.py    # 离线烟测（CI 可跑）
├── requirements.txt · CONTRIBUTING.md · CHANGELOG.md · LICENSE
```

## 🧰 技术栈与依赖

- **Python 3.8+**，核心纯标准库（urllib / json / re / ssl / argparse / xml.etree）
- **`pycryptodome`**：仅 Moka 系解析需要（`pip install pycryptodome`）
- 联网即可（部分国际站点可能需代理）；SSL 默认验证证书，拦截式代理可设 `HIRING_RADAR_INSECURE=1`

## ⚖️ 使用边界 / 合规

这是一个 **个人 / 研究自用 + 开源** 的本地工具。请负责任地使用：

- **只读「岗位信息」，不抓简历 / 任何个人信息**（碰个人信息踩 PIPL，禁止）。
- **只读公开、无需登录的接口**：遇到登录墙 / 验证码 / 主动反爬的站点，**不绕过**——本工具刻意不覆盖这类来源。
- **仅本地运行**：不含任何托管 / 上传 / 服务端；`--json` 只落到你本地。若把数据二次发布，需你自行评估合规。
- **低频、当个有礼貌的访客**；不商用转卖数据。「公开可见」≠「可随意聚合再发布」——大规模抓取并公开转载他人数据在多地（含中国《反不正当竞争法》判例）可能构成不正当竞争。

## ⚠️ 免责声明

1. **你掌控你的数据。** 工具在你本地运行，不收集、不上传任何数据。
2. **你遵守第三方条款。** 须遵守你访问的各招聘平台 ToS；不得用本工具骚扰雇主或冲击其系统。
3. **结论仅供参考。** 招聘数据是信号，非事实；产业/投资判断自负其责，本工具不对任何后果负责。

本软件以 [MIT 许可](LICENSE) 「按现状」提供，不作任何担保。

## 🙋 作者

**Simon 林** · 抖音「Simon林」· 公众号「硅基世纪」

一个把全球与中国公司官方在招岗位聚合到一处的本地工具。欢迎 PR 补充更多公司 / 数据源（见 [CONTRIBUTING.md](CONTRIBUTING.md)）。

## 📄 License

[MIT](LICENSE)
