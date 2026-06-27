# Hiring Radar

[中文](README.md) · [English](README.en.md) · **한국어** · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>글로벌 채용 시장을 위한 AI 레이더 — 전 세계와 중국의 채용 공고를 스캔하여 구직과 산업 신호 포착에 활용.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

## 무엇인가요

**Hiring Radar는 AI 네이티브 채용 데이터 도구입니다 — 당신의 AI(Claude Code / ChatGPT / 모든 에이전트)가 전 세계 + 중국 기업의 공식 채용 공고를 직접 읽을 수 있게 해줍니다.** 기업이 사용하는 공식 채용 시스템(ATS)의 공개 엔드포인트를 직접 읽어 채용 공고를 **구조화 데이터**로 모아 AI에 투입합니다. 가입을 요구하는 또 하나의 채용 사이트가 아니라, 로컬에서 실행되며 한 줄 명령으로 전 세계 어떤 회사든, 한 분야 전체든, 여러 회사를 가로질러 검색합니다. **계정 불필요, 설정 불필요.**

기업이 쓰는 ATS(Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…)는 모두 **프런트엔드가 호출하는 공개 JSON 엔드포인트**를 노출하며, 전체 JD·부서·근무지·게시일·연봉을 담고 있습니다. Hiring Radar는 바로 그 공개 엔드포인트를 읽습니다 — 빠르고 깔끔하며, AI 분석에 바로 넣을 수 있습니다.

두 가지 용도:

- 🔎 **구직 / "어디서 채용 중인가"(주)**: 특정 분야에서 지금 어느 회사가, 어느 도시에서, 얼마에 뽑는지.
- 📈 **산업 / 투자 "선행 신호"(부)**: 채용은 종종 실적 발표보다 몇 달 앞서 전략을 드러냅니다 — 어디를 확장하는지, 어떤 방향으로, 어느 단계까지. [산업 신호](#-산업-신호-부) 참고.

커버리지: **글로벌 9대 ATS + 4개 글로벌 리모트 잡보드 + 중국 170개 기업 공식 포털**. 특히 중국 커버리지(Feishu Hire / Moka / Beisen 범용 파서 + 텐센트/넷이즈/JD/바이두/바이트댄스/유니트리 자체 포털)는 대부분의 기존 도구가 비워둔 공백입니다.

**글로벌 유명 기업은 회사명 하나면 조회됩니다**, 예: NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab 등.

> ⚠️ 기업이 **스스로 공개한 채용 공고**만 읽습니다 — 이력서/개인정보는 절대, 로그인 필요 콘텐츠도 안 됩니다. 자가 사용·저빈도·예의 있는 방문자로. [책임 있는 사용](#-책임-있는-사용--컴플라이언스) 참고.

## ✨ 기능

| 기능 | 설명 |
|---|---|
| **글⁠로⁠벌⁠ ⁠회⁠사⁠별⁠ ⁠조⁠회** | 회사명 하나로 8개 ATS 자동 탐지(Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio). 적중 시 전체 JD + 부서 + 근무지 + 날짜 + 연봉 |
| **글⁠로⁠벌⁠ ⁠리⁠모⁠트⁠ ⁠보⁠드** | `--board`로 회사 가로질러 검색: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **중⁠국⁠ ⁠1⁠7⁠0⁠개⁠ ⁠기⁠업** | `--local` 직접 조회: Feishu Hire / Moka / Beisen **범용** 파서(회사 추가 = 한 줄 추가) + 자체 포털 6곳. 임바디드 AI / LLM / 반도체 / 완성차 / 에너지 / 퀀트 / 외국계 / 게임 |
| **키⁠워⁠드⁠ ⁠/⁠ ⁠최⁠근⁠성⁠ ⁠필⁠터** | `--keyword a,b,c`(콤마 = OR, 제목/부서/근무지/JD/연봉 검색) · `--recent-days N` |
| **통⁠합⁠ ⁠구⁠조⁠화⁠ ⁠출⁠력** | 15개 필드 통합 스키마; `--json`은 전체(전체 JD 포함) 출력 → 다운스트림 AI에 투입 |
| **터⁠미⁠널⁠ ⁠요⁠약** | 기본적으로 회사 / 부서 / 근무지 Top + 공고 목록으로 집계 |
| **데⁠이⁠터⁠ ⁠주⁠도** | 중국 회사 목록은 시드 테이블 `companies.seed` — **회사 추가 = 한 줄, 코드 불필요** |
| **순⁠수⁠ ⁠표⁠준⁠ ⁠라⁠이⁠브⁠러⁠리** | 단일 진입 스크립트, 의존성 0(Moka 파싱만 `pycryptodome` 필요), 모든 `python3`에서 실행 |

## 🚀 빠른 시작

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # 선택, Moka 계열 중국 회사 조회 시에만

python3 hiring_radar.py --list             # 조회 가능한 모든 회사 / 보드 목록
```

```bash
# 1) 글로벌: 회사명 하나면 OK(내장 figure/1x/anthropic/openai/scale/nvidia) 또는 임의 회사 auto-probe
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # ATS 명시 지정
python3 hiring_radar.py --workday host,tenant,site

# 2) 중국: --local <key> (key는 --list 참고)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (자체)

# 3) 보드: 회사 가로질러 "어디서 채용 중인가"
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) 전체 구조화 출력(전체 JD 포함) → 분석용
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**공통 옵션**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 출력 필드

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(연봉) · jd(전체) · url · apply_url · id` (15개 필드)

GH / Ashby / Lever / Feishu / Moka / Beisen / 텐센트 / 넷이즈 / JD / 바이두는 보통 전체 JD 포함; Workday와 일부 Moka 테넌트는 목록 수준만(제목/부서/근무지/날짜). `--json`은 전체 출력.

## 🌐 소스

**글로벌 ATS(회사명 auto-probe — 9개 시스템)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

유명 기업은 회사명 하나면 조회됩니다(모두 검증됨), 예:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**글로벌 리모트 보드(`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**중국 — 170개 기업(`--local`, 공식 포털, 데이터 주도 시드 테이블)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen**(대형 제조/완성차/가전/중장비): Dreame, Chery, Leapmotor, BOE, SANY …
- **자체 포털**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> 전체 목록: `python3 hiring_radar.py --list`

## ➕ 회사 추가 = 한 줄 추가(코드 불필요)

중국 회사 목록은 `parsers/companies.seed`(파이프 `|` 구분)에 있고 시작 시 자동 로드됩니다. 한 줄만 추가:

```
key | feishu | 회사 | portal-domain (예: nio.jobs.feishu.cn)
key | moka   | 회사 | orgId | siteId   # app.mokahr.com/social-recruitment/{orgId}/{siteId} URL에 둘 다 있음
key | beisen | 회사 | slug             # 포털 {slug}.zhiye.com, 예: dreame
```

완전히 새로운 소스(파서 작성)는 [CONTRIBUTING.md](CONTRIBUTING.md) 참고.

## 📈 산업 신호(부)

채용은 **선행 지표**입니다. 예:

- 라인 구축 엔지니어 채용 = 라인 구성 중; QA/유지보수 = 지속 생산 준비; 야간 교대 = 양산 임박; 입고 QA/공급사 품질 = 외부 공급사 온보딩.
- `--local <회사> --keyword factory,production,assembly`로 제조 측면, `--recent-days`로 최근 공고, 핵심 종목은 **월간 스냅샷**으로 추세 추적.

> ⚠️ **채용 ≠ 생산량.** 공고는 "투입"이지 "산출"이 아니며 수율/램프업/공급망이 그 사이에 있습니다. 투자 조언이 아닌 신호로 취급하세요.

## ⚖️ 책임 있는 사용 / 컴플라이언스

**개인 / 연구용 · 로컬 · 오픈소스** 도구입니다. 책임 있게 사용하세요:

- **채용 공고만 — 이력서/개인정보는 절대.**
- **공개·로그인 불필요 엔드포인트만**: 로그인 월/캡차/능동 안티봇이 있으면 **우회하지 않습니다**.
- **로컬 전용**: 호스팅/업로드/서버 없음. 데이터 재배포는 본인 책임 하에 컴플라이언스 평가.
- **저빈도·예의 있는 방문자**; 상업적 재판매 금지. "공개되어 있음" ≠ "자유롭게 수집·재배포 가능".

## ⚠️ 면책

1. **데이터는 당신이 통제.** 로컬 실행, 수집·업로드 없음.
2. **제3자 약관 준수.** 각 채용 플랫폼 ToS 준수, 스팸/과부하 금지.
3. **사실이 아닌 신호.** 채용 데이터는 신호이며 산업/투자 판단은 본인 책임.

[MIT 라이선스](LICENSE) 하에 "있는 그대로" 제공, 어떠한 보증도 없음.

## 🙋 저자

**Simon** 제작 — 전 세계와 중국 기업의 공식 채용 공고를 한곳에 모으는 로컬 도구. 회사/소스 추가 PR 환영([CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
