# Hiring Radar

[中文](README.md) · **English** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>An AI-powered radar for the global job market — scanning open roles worldwide and in China, for job hunting and industry signals.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_official_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

## What Is This

**Hiring Radar is an AI-native hiring-data tool — it gives your AI (Claude Code / ChatGPT / any agent) the ability to read official open positions from companies worldwide + China.** It reads companies' own official applicant-tracking systems (ATS) via their public endpoints and aggregates the open positions into **structured data** to feed your AI. It's not yet another job site that wants you to sign up — it runs locally, and one command queries any company worldwide, a whole field, or scans across companies, with **no account and zero config**.

The ATS platforms companies use (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) all expose **the same public JSON endpoints their own front-ends call**, carrying full job descriptions, departments, locations, post dates, and salary. Hiring Radar reads exactly those public endpoints — fast, clean, and ready to feed straight into an AI for analysis.

Two ways to use it:

- 🔎 **Job hunting / "where is the hiring" (primary)**: which companies are hiring in a field right now, in which cities, at what pay.
- 📈 **Industry / investment "leading signal" (secondary)**: hiring often reveals strategy months ahead of earnings — where a company is expanding, in what direction, and at what stage. See [Industry signal](#-industry-signal-secondary).

Coverage: **9 major global ATS + 4 global remote job boards + 170 Chinese company official portals** — the China coverage (Feishu Hire / Moka / Beisen universal parsers + Tencent/NetEase/JD/Baidu/ByteDance/Unitree in-house portals) is the gap most existing job tools leave open.

**Big global names work from just a company name**, e.g. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, and more.

> ⚠️ It reads **job postings that companies publish themselves** — never resumes/personal data, never login-gated content. Self-use, low-frequency, be a polite visitor. See [Responsible Use](#-responsible-use--compliance).

## ✨ Features

| Feature | Description |
|---|---|
| **Global per-company** | A company name auto-probes 8 ATS (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio) — full JD + dept + location + date + salary on hit |
| **Global remote boards** | `--board` scans across companies: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 Chinese employers** | `--local` direct query: Feishu Hire / Moka / Beisen **universal** parsers (add a company = add a line) + 6 in-house portals. Covers embodied AI / LLMs / semiconductors / automakers / energy / quant / MNCs / gaming |
| **Keyword / recency filter** | `--keyword a,b,c` (comma = OR, searches title/dept/location/JD/salary) · `--recent-days N` |
| **Unified structured output** | 15-field schema; `--json` emits everything (incl. full JD) to feed downstream AI |
| **Aggregated terminal summary** | Defaults to top companies / departments / locations + job list, so you see who's expanding where at a glance |
| **Data-driven** | The Chinese company list is a seed table `companies.seed` — **add a company = add one line, no code** |
| **Pure stdlib** | Single entry script, zero deps (only Moka parsing needs `pycryptodome`), runs on any `python3` |

## 🚀 Quick Start

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # optional, only for Moka-based Chinese companies

python3 hiring_radar.py --list             # list every queryable company / board
```

```bash
# 1) Global: just a company name (built-in figure/1x/anthropic/openai/scale/nvidia), or auto-probe any
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # explicit ATS
python3 hiring_radar.py --workday host,tenant,site

# 2) China: --local <key> (keys via --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (in-house)

# 3) Boards: cross-company "where is the hiring"
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Full structured output (with complete JD) for analysis
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Common flags**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Output Fields

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(salary) · jd(full) · url · apply_url · id` (15 fields)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu generally include full JD; Workday and a few Moka tenants are list-level only (title/dept/location/date). `--json` emits everything.

## ⚙️ How It Works

```
A company name / field keyword
        │
        ▼
┌──────────────────┐
│  Pick source     │  Global: 9 ATS public APIs / 4 remote boards
│  (auto-detect)   │  China: Feishu / Moka / Beisen / in-house
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Normalize+filter │  unified 15 fields; keyword / location / recency
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Terminal   --json full
 summary    (full JD,
(top cos/    feed to AI)
 dept/loc)
```

Every ATS exposes a **public JSON endpoint its own front-end calls** (e.g. Greenhouse `boards-api.greenhouse.io/v1/boards/<slug>/jobs`, Feishu Hire `<slug>.jobs.feishu.cn/api/v1/search/job/posts`). This tool reads those public endpoints and normalizes them — **no login-gated content, no breaking of authentication/captcha**.

> **About Moka (honest note)**: Moka-based portals lightly obfuscate the response (AES-128-CBC, with the key and IV both shipped by their public front-end). This tool uses those **front-end-provided public values** to recover the exact same public job list a browser sees — no login break, no auth bypass. The obfuscation isn't access control, but strictly speaking this is "replaying front-end processing," a shade greyer than plain JSON — **for local research use, at your own risk**. For the cleanest posture, delete the `moka` lines in `companies.seed` and the built-in `yostar`/`tesla-cn` lines in `LOCAL_PARSERS`; other sources are unaffected.

## 🌐 Sources

**Global ATS (auto-probe by company name — 9 systems)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Big names work from just a company name (all verified fetchable), e.g.:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Global remote boards (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**China — 170 employers (`--local`, official portals, data-driven seed table)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai, Anker, Insta360 …
- **Moka**: Hypergryph, Perfect World, Lilith, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch, Schneider …
- **Beisen** (large manufacturing / automakers / appliances / heavy equipment): Dreame, Chery, Leapmotor, BOE, SANY …
- **In-house**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Full list: `python3 hiring_radar.py --list`

## ➕ Add a Company = Add a Line (no code)

The Chinese company list lives in `parsers/companies.seed` (pipe-`|`-separated), auto-loaded at startup. Add one line:

```
key | feishu | Company | portal-domain (e.g. nio.jobs.feishu.cn)
key | moka   | Company | orgId | siteId   # both in the app.mokahr.com/social-recruitment/{orgId}/{siteId} URL
key | beisen | Company | slug             # portal {slug}.zhiye.com, e.g. dreame
```

To add a brand-new source (write a parser), see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Industry Signal (secondary)

Hiring is a **leading indicator**: where a company expands, in what direction, at what stage — often months ahead of earnings. For example:

- Hiring line-build engineers = line still being set up; hiring QA/maintenance = preparing for sustained production; hiring night shifts = two-shift ramp imminent; hiring incoming-QA/supplier-quality = external supplier onboarding.
- Use `--local <company> --keyword factory,production,assembly` for the manufacturing side; `--recent-days` for recent posts; take **monthly snapshots** of key names to track the trend.

> ⚠️ **Hiring ≠ output.** Postings are "inputs," not "outputs"; yield/ramp/supply chain sit in between, and an opening can be a buffer or even a counter-signal. Treat as a signal, not investment advice.

## 🗂️ Project Structure

```
Hiring-Radar/
├── hiring_radar.py        # main entry: global ATS / boards + dispatch + normalize
├── parsers/               # China / in-house source parsers
│   ├── feishu.py          # Feishu Hire (universal)
│   ├── moka.py            # Moka (universal, needs pycryptodome)
│   ├── beisen.py          # Beisen (universal)
│   ├── tencent / netease / jd / baidu / bytedance / unitree .py   # in-house
│   └── companies.seed     # China company seed table (add a company = add a line)
├── tests/smoke_test.py    # offline smoke test (CI-able)
├── requirements.txt · CONTRIBUTING.md · CHANGELOG.md · LICENSE
```

## 🧰 Tech & Dependencies

- **Python 3.8+**, core is pure stdlib (urllib / json / re / ssl / argparse / xml.etree)
- **`pycryptodome`**: only for Moka parsing (`pip install pycryptodome`)
- Network access (some endpoints may need a proxy); TLS verified by default — set `HIRING_RADAR_INSECURE=1` only behind an intercepting proxy

## ⚖️ Responsible Use / Compliance

A **personal / research, local + open-source** tool. Use it responsibly:

- **Read job postings only — never resumes / any personal data** (personal data triggers China's PIPL — don't).
- **Read only public, login-free endpoints**: if a site has a login wall / captcha / active anti-bot, **don't bypass it** — this tool deliberately doesn't cover such sources.
- **Local only**: no hosting / upload / server side; `--json` lands on your machine. If you re-publish the data, evaluate compliance yourself.
- **Low-frequency, polite visitor**; no commercial resale. "Publicly viewable" ≠ "free to aggregate and re-publish" — mass scraping + re-publishing can constitute unfair competition in many jurisdictions (incl. Chinese Anti-Unfair-Competition case law).

## ⚠️ Disclaimer

1. **You control your data.** The tool runs locally; it collects and uploads nothing.
2. **You comply with third-party ToS.** Follow each job platform's terms; do not use this to spam employers or overload their systems.
3. **Signals, not facts.** Hiring data is a signal, not ground truth; industry/investment judgments are your own responsibility.

Provided under the [MIT License](LICENSE) "as is", without warranty of any kind.

## 🙋 Author

Built by **Simon** — a local tool that aggregates official open positions from companies worldwide and in China. PRs welcome to add more companies / sources (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
