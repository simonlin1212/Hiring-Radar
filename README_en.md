<p align="center"><a href="README.md">简体中文</a> | <b>English</b> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>An AI-powered radar for the global job market — scanning open roles worldwide and in China, for job hunting, industry signals and market research.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_cross--company_sources-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_official_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-supported-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

<p align="center">
  <a href="#what-is-this">What is this</a> ·
  <a href="#features">Features</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#for-ai-assistants-mcp">MCP</a> ·
  <a href="#output-fields">Output fields</a> ·
  <a href="#sources">Sources</a> ·
  <a href="#related-projects-where-to-find-the-big-platforms">Related projects</a> ·
  <a href="#responsible-use--compliance">Responsible use</a>
</p>

---

## What Is This

**Hiring Radar is an AI-native hiring-data tool — it lets your AI (Claude Code / Codex / ChatGPT / any agent) read official open positions from companies worldwide and in China.** It reads companies' own applicant-tracking systems (ATS) and public job sources through their public endpoints, and turns open positions into **structured data with one unified set of fields**. It runs locally; one command queries a company, a country or a job function, with **no account and zero config**.

Three ways to use it:

- 🔎 **Job hunting / "where is the hiring"**: which companies are hiring in a field right now, in which cities, at what pay.
- 📊 **Market research / product opportunities**: pull whole slices by country, function and time to see what the market is paying people to do (new in v2).
- 📈 **Industry / investment "leading signal"**: hiring often reveals strategy months ahead of earnings. See [Industry signal](#industry-signal).

**Big global names work from just a company name**, e.g. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, and more.

**New in v2**: 24 ATS plus a directory of ~90,000 companies (look up which system a company uses by name) · 12 cross-company sources (incl. the freehire aggregator and the Swedish, Singaporean and German government job banks) · cross-source dedupe and agency flags · posting-age buckets · resumable runs · local snapshots to see new/removed jobs · an **MCP server** your AI assistant can call directly. Full list in [CHANGELOG.md](CHANGELOG.md).

> ⚠️ It reads **job postings that companies publish themselves** — never resumes or personal data, never login-gated content, and it stops at any bot check. See [Responsible use](#responsible-use--compliance).

## Features

| Feature | What it does |
|---|---|
| **By company** | Give a company name: it checks the company directory first (~90,000 companies across 24 ATS), then falls back to guessing common systems; or pin it with `--ats system slug` |
| **Cross-company sweeps** | `--board` pulls by country / keyword / last N days: the freehire aggregator, Workable-wide search, government job banks, remote boards; several sources at once, deduplicated |
| **Age buckets** | Every job is tagged 0-3 months / 3-6 months / 6+ months / no date; `--board` defaults to the last six months |
| **Agency flags** | Marks jobs posted by recruiters or staffing agencies (`agency` field); `--no-agency` drops them |
| **Resumable** | If one source is rate-limited or fails, the others keep going; rerun the same command with `--resume` to fill in only what is missing |
| **Local snapshots** | `--save` stores results in a local SQLite file with first/last seen dates; `--history` shows new and removed jobs per run |
| **MCP server** | `--mcp` lets Claude Code / Codex and other assistants call it directly (company lookup, job search, directory) |
| **China: 170 companies** | `--local`: three universal parsers (Feishu Hire / Moka / Beisen) + 6 in-house portals of big tech firms |
| **Private plugins** | Sources whose terms don't suit public distribution go in your own plugin folder (`--plugins`), outside the repo |
| **Stdlib only** | Zero dependencies (only the Moka parser needs `pycryptodome`); runs on any `python3` |

## Quick Start

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # download the company directory (~90k companies, stored locally; optional but recommended)
python3 hiring_radar.py --list               # list every source
```

```bash
# 1) By company: a name is enough
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # found in the directory → uses the right system
python3 hiring_radar.py --find xero                  # only show which ATS it uses
python3 hiring_radar.py --ats teamtailor <slug>      # pin the system and account
python3 hiring_radar.py --workday host,tenant,site

# 2) Cross-company sweeps: country + keyword + time
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json > au.json   # no cap, everything
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # Swedish government job bank
python3 hiring_radar.py --board all --keyword "AI engineer"                              # the 4 remote boards

# 3) Resume after an interruption / snapshot to track changes
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json --resume > au.json   # after an interruption: exactly the same flags as above, plus --resume
python3 hiring_radar.py anthropic --save          # the next run shows new/removed jobs
python3 hiring_radar.py --history

# 4) Chinese companies
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka; needs pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (in-house)
```

**Common flags**: `--keyword a,b` (any match) · `--recent-days N` (0 = no limit) · `--country AU,NZ` · `--max N` (per-source cap, default 1000, 0 = no cap) · `--no-agency` · `--json` · `--limit N` · `--debug`

**Upgrading from v1**: `--board` now defaults to the last 183 days, at most 1,000 jobs per source, and de-duplication across sources; for v1-style results add `--recent-days 0 --max 0 --no-dedupe`.

**Environment variables**: `HIRING_RADAR_HOME` (directory, snapshots and resume state; default `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (minimum seconds between two requests to the same site; default 0.3) · `HIRING_RADAR_PLUGINS` (private plugin folder) · `HIRING_RADAR_INSECURE=1` (disable certificate checks, only behind an intercepting proxy)

Exit codes: `0` OK; `1` error; `3` incomplete — a source stopped on an error (what was fetched is still printed; rerun the same command with `--resume`), an upstream paging limit returned only part of the results (resuming cannot help; narrow the query), or `--directory-update` could not download some systems (their old lists are kept).

## For AI Assistants (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

Five tools: `company_jobs` (one company) · `search_jobs` (across companies) · `find_company` (directory lookup) · `list_sources` · `job_history`. Job descriptions are cut to 800 characters in MCP results; use the command line with `--json` for full text.

## Output Fields

The 15 v1 fields are unchanged: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (salary) · jd (full) · url · apply_url · id`

v2 adds 9: `country` (two-letter code) · `source` · `age` (bucket 0-3m/3-6m/6m+/unknown) · `agency` (the agency term that matched) · `also` (other sources that carried the same job, after dedupe) · `industry` · `size` (company size, when the source gives it) · `first_seen` · `last_seen` (only with snapshots)

`--json` envelope: `source · total · matched · jobs` (as in v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## How It Works

```
Company name / country + keyword
        │
        ▼
┌─────────────────────────┐
│ Pick sources             │  By company: company directory → public endpoints of 24 ATS
│                         │  Cross-company: freehire / Workable / government job banks / remote boards / private plugins
│                         │  China: Feishu / Moka / Beisen / in-house portals
└──────────┬──────────────┘
           │  Network: honest identity, per-site pacing, back off on 429, stop on 403 or bot checks
┌──────────▼──────────────┐
│ 24 unified fields + age  │  Keyword / country / last-N-days filters; cross-source dedupe; agency flags
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (full)   Snapshots / MCP
```

## Sources

**By company: 24 ATS** (company directory from [openroles](https://github.com/datascry/openroles), downloaded to your machine at runtime, not bundled in the repo)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**Cross-company sources `--board` (12)**

| Source | Coverage | Notes |
|---|---|---|
| `freehire` | Global (claims ~3.3M open jobs; ~2.03M searchable via the public API on 2026-10-12) | [freehire](https://github.com/strelov1/freehire) public API, aggregating 225 sources, full job descriptions, filter by country / keyword / last N days |
| `workable` | Global | Workable-wide job search, filter by country / keyword |
| `jobtech` | Sweden | Swedish Public Employment Service open data, full job descriptions |
| `mycareersfuture` | Singapore | Singapore government job portal, salaries, no job descriptions |
| `arbeitsagentur` | Germany | German Federal Employment Agency, no job descriptions |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | Remote jobs | `--board all` = these 4 |
| `reed` · `adzuna` · `usajobs` | UK / 19 countries / US federal government | Need your own free keys (`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`); written from the official docs, not live-tested by the maintainer |

**China: 170 companies (`--local`)**: Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · in-house (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). Full list: `--list`.

**Not supported / known limits**
- **Paycom**: its robots.txt does not allow the job-list endpoint, so this tool doesn't read it.
- **iCIMS**: the `datePosted` in its pages is generated by the system (current time minus two years), so this tool uses the sitemap update time instead. Treat posting dates from iCIMS data collected by other tools with care.
- The directory contains many inactive accounts, so finding a company with zero jobs is normal; different companies with the same name can collide — when several match, all candidates are listed.
- Dedupe is by country + company + job title: the same title posted by one company in several cities of one country becomes one row.

> **About Moka (honest note)**: Moka's endpoints apply a light front-end obfuscation to responses (AES-128-CBC, with key and IV shipped in its public front-end). This tool uses those public front-end values to recover exactly the public job list a browser shows — no login cracking, no auth bypass. Strictly speaking it "replays front-end processing", which is a shade greyer than reading plain JSON; for local research use only, at your own risk. For the cleanest posture, delete every `moka` line in `parsers/companies.seed` and the built-in `yostar`/`tesla-cn` lines in `radar/local.py`.

## Private Plugins

For large platforms whose terms don't suit publishing scraper code, write your own plugin and keep it outside the repo:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

Every `.py` file in the plugin folder that doesn't start with `_` is one source, defining `NAME`, `DESC`, `FILTERS` and `pages(q, state=None)` (same interface as `radar/boards/`); files starting with `_` can hold shared code. Plugins run with your permissions, and you are responsible for the terms of the sites they visit.

## Related Projects: Where to Find the Big Platforms

Hiring Radar ships no scrapers for big platforms such as Indeed, LinkedIn or SEEK. The two third-party open-source repositories below do; the table shows, per platform, roughly where the code lives so you can look for yourself.

- **[speedyapply/JobSpy](https://github.com/speedyapply/JobSpy)**: Python library, MIT licence. Queries several platforms at once and returns title, company, location, salary, link and description.
- **[strelov1/freehire](https://github.com/strelov1/freehire)**: Job search engine written in Go, MIT licence, 225 sources. Its code in the table is part of its back-end crawler, not a standalone library; this repo's `--board freehire` reads its public API.

| Platform | Coverage | Repository | Approximate location |
|---|---|---|---|
| Indeed | ~60 countries, incl. US, UK, CA, AU, NZ, IE | JobSpy | `jobspy/indeed/` |
| LinkedIn | Worldwide | JobSpy | `jobspy/linkedin/` |
| Glassdoor | ~20 countries | JobSpy | `jobspy/glassdoor/` |
| ZipRecruiter | US, Canada | JobSpy | `jobspy/ziprecruiter/` |
| Google Jobs | Put the location in the search term | JobSpy | `jobspy/google/` |
| Naukri | India | JobSpy | `jobspy/naukri/` |
| Bayt | Middle East & Gulf | JobSpy | `jobspy/bayt/` |
| BDJobs | Bangladesh | JobSpy | `jobspy/bdjobs/` |
| HelloWork | France | JobSpy | `jobspy/hellowork/` |
| SEEK | Australia, New Zealand | freehire | `internal/ingest/sources/seek.go` |
| JobStreet / JobsDB | SG, MY, ID, PH / HK, TH | freehire | same `seek.go` (shared protocol) |
| LinkedIn public job listings | Worldwide; used only to find companies that are hiring | freehire | `cmd/harvest-linkedin/` |
| WhatJobs | Many countries; needs a WhatJobs publisher account | freehire | `internal/ingest/sources/whatjobs.go` |

> These are third-party projects, not part of Hiring Radar. We have not reviewed their code, and we provide no code to plug them into this tool. An open-source licence covers how the code may be used, not whether a platform allows scraping: check the target site's terms of use and robots.txt first. Checked on 2026-10-12; the repositories may change.

## Add a Company = Add a Line (China)

The Chinese company list is `parsers/companies.seed` (`|`-separated); adding a company is one line:

```
key | feishu | company name | portal domain (e.g. nio.jobs.feishu.cn)
key | moka   | company name | orgId | siteId
key | beisen | company name | slug
```

To add a new ATS or cross-company source, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Industry Signal

Hiring is a **leading indicator**: where a company is expanding, in what direction and at what stage often shows up months before earnings. Hiring line-development engineers = the line is still being built; hiring QA/maintenance = preparing for sustained production; hiring night shifts = volume ramp is near. Use `--save` for regular snapshots and `--history` to see the rhythm.

> ⚠️ **Hiring ≠ output**: positions are inputs, not outputs; "hiring" can also be pipeline building or even a counter-signal. Treat conclusions as signals, not investment advice.

## Project Structure

```
Hiring-Radar/
├── hiring_radar.py     # command-line entry (v1 command syntax unchanged)
├── radar/              # core package
│   ├── http.py         # network: honest identity, pacing, backoff, stop when blocked
│   ├── schema.py       # unified fields, dates, age buckets
│   ├── ats/            # by company: one file per ATS
│   ├── boards/         # cross-company sources
│   ├── directory.py    # company directory (downloaded at runtime)
│   ├── process.py      # dedupe, agency flags
│   ├── sweep.py        # multi-source sweeps, resume
│   ├── store.py        # local snapshots (SQLite)
│   ├── local.py        # China / in-house parser dispatch
│   ├── plugins.py      # private plugin loader
│   └── mcp.py          # MCP server
├── parsers/            # China / in-house parsers + companies.seed
├── tests/              # smoke_test.py · test_offline.py (offline, no network)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## Tech & Dependencies

- **Python 3.8+**, core is pure stdlib (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: only for the Moka parsers (`pip install pycryptodome`)
- Needs internet (some international sites may need a proxy); SSL certificates are verified by default, set `HIRING_RADAR_INSECURE=1` behind an intercepting proxy

## Responsible Use / Compliance

A **personal / research, local + open-source** tool. Use it responsibly:

- **Read job postings only — never resumes / any personal data** (personal data triggers China's PIPL — don't).
- **Read only public, login-free endpoints**: if a site has a login wall / captcha / active anti-bot, **don't bypass it**; a 403 or bot-check page stops the run; no proxy pools, no browser-fingerprint spoofing.
- **Honest identity, low frequency**: the User-Agent names HiringRadar and the project URL (exceptions: the Feishu Hire and ByteDance APIs reject a program identity, so those two parsers keep v1's browser User-Agent; the official USAJobs API requires the User-Agent to be the email you registered your key with, so that board sends it as required); by default 0.3 seconds between two requests to the same site; on 429 it backs off as asked, and if that still fails it stops and waits for you to resume. robots.txt is checked before a new source is added (which is why Paycom is not supported).
- **Keys only in environment variables**: sources that need a key read it from the environment, and keys are masked in error messages.
- **Local only**: no hosting / upload / server side; data lands only on your machine. If you re-publish the data, evaluate compliance yourself; no commercial resale. The company directory is CC BY-SA 4.0 — redistribution requires attribution and the same license (see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- "Publicly viewable" ≠ "free to aggregate and re-publish" — mass scraping + re-publishing can constitute unfair competition in many jurisdictions (incl. Chinese Anti-Unfair-Competition case law).

## Disclaimer

1. **You control your data.** The tool runs locally; it collects and uploads nothing.
2. **You comply with third-party ToS.** Follow each job platform's terms; do not use this to spam employers or overload their systems.
3. **Signals, not facts.** Hiring data is a signal, not ground truth; industry/investment judgments are your own responsibility.

Provided under the [MIT License](LICENSE) "as is", without warranty of any kind. Third-party code and data: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

PRs welcome to add more companies / sources (see [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
