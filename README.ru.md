# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · **Русский** · [العربية](README.ar.md)

<p align="center">
  <b>ИИ-радар мирового рынка труда — сканирует вакансии по всему миру и в Китае, для поиска работы и отраслевых сигналов.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_порталов-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-только_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## Что это

**Hiring Radar — это инструмент данных о найме, созданный для ИИ: он даёт вашему ИИ (Claude Code / ChatGPT / любому агенту) возможность читать официальные открытые вакансии компаний по всему миру + Китай.** Он напрямую читает публичные эндпоинты систем учёта кандидатов (ATS), которые используют компании, и собирает вакансии в **структурированные данные** для вашего ИИ. Это не очередной сайт вакансий с обязательной регистрацией: он работает локально, и одна команда запрашивает любую компанию мира, целую сферу или сканирует множество компаний — **без аккаунта и без настройки**.

ATS, которые используют компании (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…), отдают **те же публичные JSON-эндпоинты, которые вызывают их собственные фронтенды** — с полным описанием вакансии, отделом, локацией, датой публикации и зарплатой. Hiring Radar читает именно эти публичные эндпоинты: быстро, чисто и готово к подаче в ИИ.

Два применения:

- 🔎 **Поиск работы / «где нанимают» (основное)**: какие компании сейчас нанимают в сфере, в каких городах, за какую зарплату.
- 📈 **Опережающий сигнал для отрасли / инвестиций (второстепенное)**: найм часто раскрывает стратегию за месяцы до финансовой отчётности. См. [Отраслевой сигнал](#-отраслевой-сигнал-второстепенное).

Покрытие: **9 крупных международных ATS + 4 глобальные площадки удалённой работы + 170 официальных порталов китайских компаний**. Покрытие Китая (универсальные парсеры Feishu Hire / Moka / Beisen + собственные порталы Tencent/NetEase/JD/Baidu/ByteDance/Unitree) — это пробел, который оставляет большинство существующих инструментов.

**Крупные мировые бренды работают по одному названию компании**, напр. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab и другие.

> ⚠️ Читает **вакансии, которые компании публикуют сами** — никогда резюме/персональные данные, никогда контент за логином. Личное использование, низкая частота, вежливый посетитель. См. [Ответственное использование](#-ответственное-использование--соответствие).

## ✨ Возможности

| Возможность | Описание |
|---|---|
| **По компании (глобально)** | Одного названия компании достаточно для авто-проверки 8 ATS (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio); при совпадении: полное описание + отдел + локация + дата + зарплата |
| **Глобальные remote-доски** | `--board` сканирует несколько компаний: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 китайских компаний** | `--local`: **универсальные** парсеры Feishu Hire / Moka / Beisen (добавить компанию = добавить строку) + 6 собственных порталов. Воплощённый ИИ / LLM / полупроводники / автопром / энергетика / квант / транснационалы / игры |
| **Фильтр по ключевым словам / свежести** | `--keyword a,b,c` (запятая = ИЛИ; ищет в названии/отделе/локации/описании/зарплате) · `--recent-days N` |
| **Единый структурированный вывод** | Схема из 15 полей; `--json` выдаёт всё (вкл. полное описание) для подачи в ИИ |
| **Сводка в терминале** | По умолчанию топ компаний / отделов / локаций + список вакансий |
| **Управляется данными** | Список китайских компаний — это seed-таблица `companies.seed`: **добавить компанию = одна строка, без кода** |
| **Только stdlib** | Один входной скрипт, ноль зависимостей (только Moka требует `pycryptodome`), работает на любом `python3` |

## 🚀 Быстрый старт

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # опционально, только для китайских компаний на Moka

python3 hiring_radar.py --list             # список всех доступных компаний / досок
```

```bash
# 1) Глобально: достаточно названия компании (figure/1x/anthropic/openai/scale/nvidia встроены) или авто-проверьте любое
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # явный ATS
python3 hiring_radar.py --workday host,tenant,site

# 2) Китай: --local <key> (ключи через --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (собств.)

# 3) Доски: «где нанимают» по многим компаниям
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Полный структурированный вывод (с полным описанием) для анализа
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Общие опции**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Поля вывода

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(зарплата) · jd(полное) · url · apply_url · id` (15 полей)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu обычно содержат полное описание; Workday и отдельные тенанты Moka — только на уровне списка (название/отдел/локация/дата). `--json` выдаёт всё.

## 🌐 Источники

**Международные ATS (авто-проверка по имени — 9 систем)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Крупные бренды работают по одному названию компании (все проверены), напр.:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Глобальные remote-доски (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**Китай — 170 компаний (`--local`, официальные порталы, seed-таблица)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (крупная промышленность / автопром / бытовая техника / тяжёлое машиностроение): Dreame, Chery, Leapmotor, BOE, SANY …
- **Собственные**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Полный список: `python3 hiring_radar.py --list`

## ➕ Добавить компанию = добавить строку (без кода)

Список китайских компаний — в `parsers/companies.seed` (разделитель `|`), загружается при старте. Добавьте строку:

```
key | feishu | Компания | домен-портала (напр. nio.jobs.feishu.cn)
key | moka   | Компания | orgId | siteId   # оба в URL app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | Компания | slug             # портал {slug}.zhiye.com, напр. dreame
```

Для совершенно нового источника (написать парсер) см. [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Отраслевой сигнал (второстепенное)

Найм — это **опережающий индикатор**. Например:

- Найм инженеров сборочной линии = линия ещё строится; QA/обслуживание = подготовка к серийному выпуску; ночные смены = скоро выход на объём; входной QA/качество поставщиков = онбординг внешних поставщиков.
- Используйте `--local <компания> --keyword factory,production,assembly` для производственной стороны; `--recent-days` для свежего; делайте **ежемесячные снимки** ключевых имён для отслеживания тренда.

> ⚠️ **Найм ≠ выпуск.** Вакансии — это «входы», а не «выходы»; между ними выход годных/выход на объём/цепочка поставок. Воспринимайте как сигнал, а не инвестиционный совет.

## ⚖️ Ответственное использование / Соответствие

**Личный / исследовательский, локальный + open-source** инструмент. Используйте ответственно:

- **Только вакансии — никогда резюме / персональные данные.**
- **Только публичные эндпоинты без логина**: при стене логина / капче / активном анти-боте **не обходите**.
- **Только локально**: без хостинга / загрузки / сервера. При перепубликации данных оцените соответствие самостоятельно.
- **Низкая частота, вежливый посетитель**; без коммерческой перепродажи. «Публично видимо» ≠ «свободно агрегировать и перепубликовывать».

## ⚠️ Отказ от ответственности

1. **Вы контролируете свои данные.** Работает локально; ничего не собирает и не отправляет.
2. **Вы соблюдаете условия третьих сторон.** Соблюдайте ToS каждой платформы; без спама и перегрузки.
3. **Сигналы, а не факты.** Данные о найме — это сигнал; отраслевые/инвестиционные суждения под вашу ответственность.

Под [лицензией MIT](LICENSE) «как есть», без каких-либо гарантий.

## 🙋 Автор

Создано **Simon** — локальный инструмент, агрегирующий официальные открытые вакансии компаний по всему миру и в Китае. PR для добавления компаний / источников приветствуются (см. [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
