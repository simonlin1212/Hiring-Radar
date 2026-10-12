<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <b>한국어</b> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>AI 기반 글로벌 채용 시장 레이더 — 전 세계와 중국의 채용 중인 포지션을 수집해 구직, 산업 시그널, 시장 조사에 활용합니다.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_sources-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-supported-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

## 이게 뭔가요

**Hiring Radar는 AI를 위한 채용 데이터 도구입니다. 여러분의 AI(Claude Code / Codex / ChatGPT / 모든 에이전트)가 전 세계와 중국 기업의 공식 채용 공고를 직접 읽을 수 있게 해 줍니다.** 기업이 쓰는 채용 관리 시스템(ATS)과 공개 채용 소스를 공개 인터페이스로 읽고, 채용 공고를 **통일된 필드의 구조화 데이터**로 정리합니다. 로컬에서 실행되며, 명령 하나로 한 회사, 한 국가, 한 직무를 조회합니다. **계정도 설정도 필요 없습니다.**

세 가지 용도:

- 🔎 **구직 / "어디서 뽑고 있나"**: 특정 분야에서 지금 어떤 회사가, 어느 도시에서, 얼마를 주고 채용하는지.
- 📊 **시장 조사 / 제품 기회**: 국가·직무·기간별로 통째로 가져와 시장이 어떤 일에 돈을 쓰고 있는지 확인 (v2 신규).
- 📈 **산업 / 투자 "선행 신호"**: 채용은 실적보다 몇 달 앞서 전략을 드러내곤 합니다. 아래 "산업 시그널" 참고.

**글로벌 대기업은 회사 이름만으로 조회됩니다.** 예: NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab 등.

**v2 신규**: 24개 ATS와 약 9만 개 회사 디렉터리(회사 이름으로 어떤 시스템을 쓰는지 조회) · 12개 기업 횡단 소스(freehire 애그리게이터, 스웨덴·싱가포르·독일 정부 채용 DB 포함) · 소스 간 중복 제거와 헤드헌터 표시 · 게시 시기 구간 · 중단 후 이어받기 · 로컬 스냅숏으로 신규/마감 공고 확인 · AI 어시스턴트가 바로 호출하는 **MCP 서버**.

> ⚠️ **기업이 직접 공개한 채용 공고만** 읽습니다. 이력서나 개인정보, 로그인이 필요한 콘텐츠는 다루지 않으며, 봇 확인이 나오면 멈춥니다. 아래 "책임 있는 사용" 참고.

## 기능

| 기능 | 설명 |
|---|---|
| **회사별 조회** | 회사 이름만 주면 먼저 디렉터리(24개 ATS, 약 9만 개 회사)를 찾고, 없으면 흔한 시스템을 추측합니다. `--ats 시스템 slug`로 정확히 지정할 수도 있습니다 |
| **기업 횡단 수집** | `--board`로 국가 / 키워드 / 최근 N일 기준 수집: freehire, Workable 전체 검색, 정부 채용 DB, 원격 근무 보드. 여러 소스를 한 번에, 중복 제거 포함 |
| **시기 구간** | 공고마다 0-3개월 / 3-6개월 / 6개월 이상 / 날짜 없음 표시. `--board`는 기본으로 최근 6개월만 |
| **헤드헌터 표시** | 헤드헌터·인력 파견 회사가 올린 공고를 표시(`agency` 필드), `--no-agency`로 제외 |
| **이어받기** | 한 소스가 제한·오류로 멈춰도 다른 소스는 계속. 같은 명령에 `--resume`을 붙이면 못 끝낸 부분만 보충 |
| **로컬 스냅숏** | `--save`로 로컬 SQLite에 저장(처음/마지막으로 본 날짜), `--history`로 실행별 신규·마감 확인 |
| **MCP 서버** | `--mcp`로 Claude Code / Codex 등이 직접 호출(회사 조회, 공고 검색, 디렉터리) |
| **중국 170개사** | `--local`: Feishu Hire / Moka / Beisen 범용 파서 3종 + 대형 테크 기업 자체 포털 6곳 |
| **비공개 플러그인** | 약관상 공개 배포가 맞지 않는 소스는 저장소 밖 본인 폴더(`--plugins`)에 둡니다 |
| **표준 라이브러리만** | 의존성 없음(Moka 파서만 `pycryptodome` 필요). 어떤 `python3`에서도 실행 |

## 빠른 시작

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # 회사 디렉터리 다운로드(약 9만 개, 로컬 저장, 선택이지만 권장)
python3 hiring_radar.py --list               # 전체 소스 목록
```

```bash
# 1) 회사별 조회: 이름이면 충분
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # 디렉터리에서 찾음 → 맞는 시스템 사용
python3 hiring_radar.py --find xero                  # 어떤 ATS를 쓰는지만 확인
python3 hiring_radar.py --ats teamtailor <slug>      # 시스템과 계정 지정
python3 hiring_radar.py --workday host,tenant,site

# 2) 기업 횡단 수집: 국가 + 키워드 + 기간
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country KR --max 0 --json > kr.json   # 상한 없이 전부
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # 스웨덴 정부 채용 DB
python3 hiring_radar.py --board all --keyword "AI engineer"                              # 원격 근무 보드 4곳

# 3) 중단 후 이어받기 / 스냅숏
python3 hiring_radar.py --board freehire --country AU --max 0 --resume
python3 hiring_radar.py anthropic --save          # 다음 실행 때 신규/마감 표시
python3 hiring_radar.py --history

# 4) 중국 기업
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka, pip install pycryptodome 필요)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (자체 포털)
```

**자주 쓰는 옵션**: `--keyword a,b`(하나라도 일치) · `--recent-days N`(0 = 제한 없음) · `--country AU,NZ` · `--max N`(소스별 상한, 기본 1000, 0 = 제한 없음) · `--no-agency` · `--json` · `--limit N` · `--debug`

**환경 변수**: `HIRING_RADAR_HOME`(디렉터리·스냅숏·이어받기 상태, 기본 `~/.hiring-radar`) · `HIRING_RADAR_DELAY`(같은 사이트에 대한 두 요청 사이 최소 초, 기본 0.3) · `HIRING_RADAR_PLUGINS`(비공개 플러그인 폴더) · `HIRING_RADAR_INSECURE=1`(인증서 검증 끄기, 가로채는 프록시 환경에서만)

종료 코드: `0` 정상, `3` 일부 소스가 끝나지 않음(받은 데이터는 그대로 출력, `--resume` 사용).

## AI 어시스턴트용 (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

도구 5개: `company_jobs`(회사 하나) · `search_jobs`(기업 횡단) · `find_company`(디렉터리) · `list_sources` · `job_history`. MCP 결과의 직무 설명은 800자로 잘립니다. 전문은 명령줄 `--json`으로 받으세요.

## 출력 필드

v1의 15개 필드는 그대로: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(급여) · jd(전체) · url · apply_url · id`

v2에서 9개 추가: `country`(국가 코드) · `source`(소스) · `age`(구간 0-3m/3-6m/6m+/unknown) · `agency`(감지된 헤드헌터 표현) · `also`(중복 제거 시 같은 공고가 있던 다른 소스) · `industry` · `size`(회사 규모, 소스가 줄 때만) · `first_seen` · `last_seen`(스냅숏 사용 시만)

`--json` 바깥 구조: `source · total · matched · jobs`(v1과 동일) + `version · query · ages · sources · incomplete · candidates · saved`.

## 동작 방식

```
회사 이름 / 국가 + 키워드
        │
        ▼
┌─────────────────────────┐
│ 소스 선택                │  회사별: 디렉터리 → 24개 ATS 공개 인터페이스
│                         │  기업 횡단: freehire / Workable / 정부 채용 DB / 원격 보드 / 플러그인
│                         │  중국: Feishu / Moka / Beisen / 자체 포털
└──────────┬──────────────┘
           │  네트워크: 정직한 신원 표시, 사이트별 간격, 429면 대기, 403·봇 확인이면 중지
┌──────────▼──────────────┐
│ 24개 필드 + 시기 구간     │  키워드 / 국가 / 최근 N일 필터, 중복 제거, 헤드헌터 표시
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
   터미널    --json(전체)    스냅숏 / MCP
```

## 지원 소스

**회사별 조회: 24개 ATS** (회사 디렉터리는 [openroles](https://github.com/datascry/openroles)에서 실행 시 로컬로 다운로드, 저장소에 포함하지 않음)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**기업 횡단 소스 `--board` (12개)**

| 소스 | 범위 | 비고 |
|---|---|---|
| `freehire` | 전 세계(자체 발표 약 330만 건 채용 중) | [freehire](https://github.com/strelov1/freehire) 공개 API, 225개 소스 집계, 전체 직무 설명, 국가 / 키워드 / 최근 N일 필터 |
| `workable` | 전 세계 | Workable 전체 검색, 국가 / 키워드 필터 |
| `jobtech` | 스웨덴 | 스웨덴 공공 고용 서비스 공개 데이터, 전체 직무 설명 |
| `mycareersfuture` | 싱가포르 | 싱가포르 정부 구직 포털, 급여 있음, 직무 설명 없음 |
| `arbeitsagentur` | 독일 | 독일 연방고용청, 직무 설명 없음 |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | 원격 근무 | `--board all` = 이 4곳 |
| `reed` · `adzuna` · `usajobs` | 영국 / 19개국 / 미국 연방정부 | 본인의 무료 키 필요(`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`). 공식 문서 기준으로 작성, 관리자가 실제 네트워크에서 테스트하지 않음 |

**중국 170개사 (`--local`)**: Feishu Hire(Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka(Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen(Dreame / Chery / Leapmotor / BOE / SANY…) · 자체 포털(Tencent / NetEase / JD / Baidu / ByteDance / Unitree). 전체 목록: `--list`.

**미지원 / 알려진 한계**
- **Paycom**: robots.txt가 공고 목록 접근을 허용하지 않아 읽지 않습니다.
- **iCIMS**: 페이지의 `datePosted`는 시스템이 만든 가짜 날짜(현재 시각에서 2년을 뺀 값)라서, 이 도구는 사이트맵의 갱신 시각을 씁니다. 다른 도구로 수집한 iCIMS 데이터의 게시일은 주의하세요.
- 디렉터리에는 비활성 계정이 많아, 회사를 찾았는데 공고가 0건인 것은 정상입니다. 이름이 같은 다른 회사가 겹칠 수 있어, 여러 개가 맞으면 후보를 모두 보여 줍니다.
- 중복 제거 기준은 국가 + 회사 + 직무명입니다. 한 회사가 같은 나라 여러 도시에 같은 직무명으로 올리면 한 줄로 합쳐집니다.

> **Moka에 관한 솔직한 설명**: Moka 계열 인터페이스는 응답에 가벼운 프런트엔드 난독화를 적용합니다(AES-128-CBC, 키와 IV는 공개 프런트엔드에 포함되어 배포). 이 도구는 그 공개 값을 사용해 브라우저가 보여 주는 것과 똑같은 공개 공고 목록을 복원할 뿐, 로그인을 뚫거나 인증을 우회하지 않습니다. 엄밀히는 "프런트엔드 처리를 재현"하는 것이라 순수 JSON 읽기보다 약간 회색 지대이며, 로컬 연구용으로만 본인 책임하에 쓰세요. 가장 깔끔하게 하려면 `parsers/companies.seed`의 `moka` 줄 전부와 `radar/local.py`에 내장된 `yostar`/`tesla-cn` 두 줄을 지우면 됩니다.

## 비공개 플러그인

약관상 수집 코드를 공개 배포하기 어려운 대형 플랫폼은 직접 플러그인으로 만들어 저장소 밖에 두세요:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

플러그인 폴더에서 `_`로 시작하지 않는 `.py` 파일 하나가 소스 하나이며, `NAME`, `DESC`, `FILTERS`, `pages(q, state=None)`를 정의합니다(`radar/boards/`와 같은 인터페이스). `_`로 시작하는 파일에는 공용 코드를 둘 수 있습니다. 플러그인은 본인 권한으로 실행되며, 방문하는 사이트의 약관 준수는 본인 책임입니다.

## 회사 추가 = 한 줄 추가 (중국)

중국 회사 목록은 `parsers/companies.seed`(`|` 구분)이며, 한 회사 = 한 줄입니다:

```
key | feishu | 회사명 | 포털 도메인(예: nio.jobs.feishu.cn)
key | moka   | 회사명 | orgId | siteId
key | beisen | 회사명 | slug
```

새 ATS나 기업 횡단 소스를 추가하려면 [CONTRIBUTING.md](CONTRIBUTING.md)를 보세요.

## 산업 시그널

채용은 **선행 지표**입니다. 회사가 어디로 확장하는지, 어떤 방향으로, 어느 단계에 있는지가 실적보다 몇 달 앞서 드러나곤 합니다. 라인 개발 인력 채용 = 라인 구축 중, 품질/설비 보전 채용 = 지속 생산 준비, 야간조 채용 = 양산 증대 임박. `--save`로 정기 스냅숏을 남기고 `--history`로 흐름을 보세요.

> ⚠️ **채용 ≠ 생산**: 공고는 "투입"이지 "산출"이 아니며, "채용 중"은 인력 풀 확보나 반대 신호일 수도 있습니다. 결론은 신호로만 참고하고 투자 조언으로 받아들이지 마세요.

## 프로젝트 구조

```
Hiring-Radar/
├── hiring_radar.py     # 명령줄 진입점(v1 사용법 그대로)
├── radar/              # 핵심 패키지
│   ├── http.py         # 네트워크: 정직한 신원, 간격, 대기, 차단 시 중지
│   ├── schema.py       # 통일 필드, 날짜, 시기 구간
│   ├── ats/            # 회사별: ATS마다 파일 하나
│   ├── boards/         # 기업 횡단 소스
│   ├── directory.py    # 회사 디렉터리(실행 시 다운로드)
│   ├── process.py      # 중복 제거, 헤드헌터 표시
│   ├── sweep.py        # 다중 소스 수집, 이어받기
│   ├── store.py        # 로컬 스냅숏(SQLite)
│   ├── local.py        # 중국 / 자체 포털 파서
│   ├── plugins.py      # 비공개 플러그인 로더
│   └── mcp.py          # MCP 서버
├── parsers/            # 중국 / 자체 포털 파서 + companies.seed
├── tests/              # smoke_test.py · test_offline.py (오프라인, 네트워크 없음)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## 기술 및 의존성

- **Python 3.8+**, 핵심은 순수 표준 라이브러리(urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: Moka 파서에서만 필요(`pip install pycryptodome`)
- 인터넷 필요(일부 해외 사이트는 프록시가 필요할 수 있음). SSL 인증서는 기본으로 검증하며, 가로채는 프록시 환경에서는 `HIRING_RADAR_INSECURE=1` 설정

## 책임 있는 사용 / 컴플라이언스

**개인 / 연구용, 로컬 + 오픈 소스** 도구입니다. 책임감 있게 사용하세요:

- **채용 공고만 읽고, 이력서 / 개인정보는 절대 수집하지 않습니다**(개인정보는 중국 PIPL에 해당 — 금지).
- **로그인이 필요 없는 공개 인터페이스만**: 로그인 벽 / 캡차 / 적극적 봇 차단은 **우회하지 않습니다**. 403이나 봇 확인 페이지가 나오면 멈추며, 프록시 풀이나 브라우저 지문 위장도 쓰지 않습니다.
- **정직한 신원, 낮은 빈도**: User-Agent에 HiringRadar와 프로젝트 주소를 밝히고, 같은 사이트에는 기본 0.3초 간격으로 요청합니다. 429가 오면 요구대로 기다리고, 그래도 안 되면 멈춰서 `--resume`을 기다립니다. 새 소스를 추가하기 전에 robots.txt를 확인합니다(그래서 Paycom은 미지원).
- **키는 환경 변수에만**: 키가 필요한 소스는 환경 변수에서 읽고, 오류 메시지 속 키는 가립니다.
- **로컬 전용**: 호스팅 / 업로드 / 서버 없음. 데이터는 본인 컴퓨터에만 남습니다. 재배포 시 컴플라이언스는 직접 판단하고, 상업적 재판매는 하지 마세요. 회사 디렉터리는 CC BY-SA 4.0이므로 재배포 시 출처 표시와 동일 라이선스가 필요합니다([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 참고).
- "공개적으로 보임" ≠ "마음대로 모아 재게시해도 됨" — 대량 수집 후 재게시는 많은 법역(중국 판례 포함)에서 부정경쟁이 될 수 있습니다.

## 면책 조항

1. **데이터는 본인이 관리합니다.** 도구는 로컬에서 실행되며 아무것도 수집·업로드하지 않습니다.
2. **제3자 약관은 본인이 지킵니다.** 각 채용 플랫폼의 약관을 따르고, 고용주를 괴롭히거나 시스템에 부담을 주는 데 쓰지 마세요.
3. **신호일 뿐 사실이 아닙니다.** 채용 데이터는 신호이며, 산업·투자 판단은 본인 책임입니다.

[MIT 라이선스](LICENSE)에 따라 "있는 그대로" 제공되며 어떠한 보증도 없습니다. 제3자 코드와 데이터: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 참고.

## License

[MIT](LICENSE)

회사 / 소스 추가 PR을 환영합니다([CONTRIBUTING.md](CONTRIBUTING.md) 참고).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
