<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <b>Deutsch</b> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>Ein KI-gestütztes Radar für den globalen Stellenmarkt – erfasst offene Stellen weltweit und in China, für Jobsuche, Branchensignale und Marktforschung.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_Quellen-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_Portale-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-unterst%C3%BCtzt-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-nur_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## Was ist das

**Hiring Radar ist ein KI-natives Werkzeug für Stellendaten – es lässt Ihre KI (Claude Code / Codex / ChatGPT / jeden Agenten) offizielle offene Stellen von Unternehmen weltweit und in China lesen.** Es liest die Bewerbermanagementsysteme (ATS) der Unternehmen und öffentliche Stellenquellen über deren öffentliche Schnittstellen und macht daraus **strukturierte Daten mit einheitlichen Feldern**. Es läuft lokal; ein Befehl fragt ein Unternehmen, ein Land oder eine Funktion ab – **ohne Konto, ohne Konfiguration**.

Drei Einsatzarten:

- 🔎 **Jobsuche / „Wo wird eingestellt?“**: Welche Unternehmen in einem Bereich gerade einstellen, in welchen Städten, zu welchem Gehalt.
- 📊 **Marktforschung / Produktchancen**: ganze Ausschnitte nach Land, Funktion und Zeitraum abrufen, um zu sehen, wofür der Markt Leute bezahlt (neu in v2).
- 📈 **Branchen-/Investment-Frühindikator**: Stellenausschreibungen verraten Strategie oft Monate vor den Geschäftszahlen. Siehe „Branchensignal“ unten.

**Große globale Namen funktionieren mit nur einem Firmennamen**, z. B. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab und mehr.

**Neu in v2**: 24 ATS plus ein Verzeichnis von ca. 90.000 Unternehmen (per Name nachschlagen, welches System eine Firma nutzt) · 12 unternehmensübergreifende Quellen (u. a. der Aggregator freehire sowie die staatlichen Jobbörsen Schwedens, Singapurs und Deutschlands) · quellenübergreifende Deduplizierung und Markierung von Personalvermittlern · Altersklassen nach Veröffentlichungsdatum · fortsetzbare Läufe · lokale Schnappschüsse für neue/entfernte Stellen · ein **MCP-Server**, den Ihr KI-Assistent direkt aufrufen kann. Alle Änderungen in [CHANGELOG.md](CHANGELOG.md).

> ⚠️ Es liest nur **Stellenanzeigen, die Unternehmen selbst veröffentlichen** – keine Lebensläufe oder personenbezogenen Daten, keine Inhalte hinter einem Login, und es stoppt bei jeder Bot-Prüfung. Siehe „Verantwortungsvolle Nutzung“ unten.

## Funktionen

| Funktion | Was sie tut |
|---|---|
| **Nach Unternehmen** | Firmenname genügt: zuerst das Verzeichnis (ca. 90.000 Firmen in 24 ATS), sonst werden gängige Systeme geraten; oder exakt mit `--ats system slug` |
| **Unternehmensübergreifend** | `--board` nach Land / Stichwort / letzten N Tagen: freehire, Workable-weite Suche, staatliche Jobbörsen, Remote-Boards; mehrere Quellen auf einmal, dedupliziert |
| **Altersklassen** | Jede Stelle erhält 0–3 Monate / 3–6 Monate / über 6 Monate / ohne Datum; `--board` zeigt standardmäßig die letzten sechs Monate |
| **Vermittler-Markierung** | Markiert Stellen von Headhuntern oder Zeitarbeitsfirmen (Feld `agency`); `--no-agency` entfernt sie |
| **Fortsetzbar** | Wird eine Quelle gedrosselt oder fällt aus, laufen die anderen weiter; derselbe Befehl mit `--resume` holt nur das Fehlende nach |
| **Lokale Schnappschüsse** | `--save` speichert in eine lokale SQLite-Datei mit erstem/letztem Sichtungsdatum; `--history` zeigt neue und entfernte Stellen je Lauf |
| **MCP-Server** | `--mcp` – Claude Code / Codex usw. rufen es direkt auf (Firmenabfrage, Stellensuche, Verzeichnis) |
| **China: 170 Firmen** | `--local`: drei universelle Parser (Feishu Hire / Moka / Beisen) + 6 Eigenportale großer Tech-Firmen |
| **Private Plugins** | Quellen, deren Bedingungen keine öffentliche Verbreitung erlauben, liegen in Ihrem eigenen Plugin-Ordner (`--plugins`), außerhalb des Repos |
| **Nur Standardbibliothek** | Keine Abhängigkeiten (nur der Moka-Parser braucht `pycryptodome`); läuft mit jedem `python3` |

## Schnellstart

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # Firmenverzeichnis laden (ca. 90.000 Firmen, lokal gespeichert; optional, empfohlen)
python3 hiring_radar.py --list               # alle Quellen auflisten
```

```bash
# 1) Nach Unternehmen: ein Name genügt
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # im Verzeichnis gefunden → richtiges System
python3 hiring_radar.py --find xero                  # nur anzeigen, welches ATS es nutzt
python3 hiring_radar.py --ats teamtailor <slug>      # System und Konto festlegen
python3 hiring_radar.py --workday host,tenant,site

# 2) Unternehmensübergreifend: Land + Stichwort + Zeitraum
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json > au.json   # ohne Obergrenze
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # schwedische öffentliche Stellenbörse
python3 hiring_radar.py --board all --keyword "AI engineer"                              # die 4 Remote-Boards

# 3) Nach Abbruch fortsetzen / Schnappschüsse
python3 hiring_radar.py --board freehire,workable --country AU --max 0 --json --resume > au.json   # nach Abbruch: exakt dieselben Optionen wie oben, plus --resume
python3 hiring_radar.py anthropic --save          # der nächste Lauf zeigt neue/entfernte Stellen
python3 hiring_radar.py --history

# 4) Chinesische Unternehmen
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka; pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (Eigenportal)
```

**Häufige Optionen**: `--keyword a,b` (beliebiger Treffer) · `--recent-days N` (0 = unbegrenzt) · `--country AU,NZ` · `--max N` (Obergrenze je Quelle, Standard 1000, 0 = keine) · `--no-agency` · `--json` · `--limit N` · `--debug`

**Umstieg von v1**: `--board` zeigt jetzt standardmäßig nur die letzten 183 Tage, höchstens 1.000 Stellen je Quelle, und entfernt Dubletten über Quellen hinweg; für Ergebnisse wie in v1 `--recent-days 0 --max 0 --no-dedupe` anhängen.

**Umgebungsvariablen**: `HIRING_RADAR_HOME` (Verzeichnis, Schnappschüsse, Fortsetzungsstand; Standard `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (Mindestabstand in Sekunden zwischen zwei Anfragen an dieselbe Website; Standard 0,3) · `HIRING_RADAR_PLUGINS` (privater Plugin-Ordner) · `HIRING_RADAR_INSECURE=1` (Zertifikatsprüfung aus, nur hinter einem abfangenden Proxy)

Exit-Codes: `0` OK; `1` Fehler; `3` unvollständig – eine Quelle wurde wegen eines Fehlers gestoppt (Abgerufenes wird trotzdem ausgegeben; denselben Befehl mit `--resume` wiederholen), eine Blätter-Obergrenze der Quelle lieferte nur einen Teil (Fortsetzen hilft nicht; Abfrage eingrenzen) oder `--directory-update` konnte einige Systeme nicht laden (die alten Listen bleiben erhalten).

## Für KI-Assistenten (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

Fünf Werkzeuge: `company_jobs` (ein Unternehmen) · `search_jobs` (unternehmensübergreifend) · `find_company` (Verzeichnis) · `list_sources` · `job_history`. Stellenbeschreibungen werden in MCP-Ergebnissen auf 800 Zeichen gekürzt; den Volltext liefert die Kommandozeile mit `--json`.

## Ausgabefelder

Die 15 Felder aus v1 bleiben: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (Gehalt) · jd (vollständig) · url · apply_url · id`

v2 ergänzt 9: `country` (Ländercode) · `source` (Quelle) · `age` (Klasse 0-3m/3-6m/6m+/unknown) · `agency` (gefundener Vermittler-Begriff) · `also` (weitere Quellen derselben Stelle nach Deduplizierung) · `industry` · `size` (Firmengröße, falls die Quelle sie liefert) · `first_seen` · `last_seen` (nur mit Schnappschüssen)

`--json`-Hülle: `source · total · matched · jobs` (wie v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## Funktionsweise

```
Firmenname / Land + Stichwort
        │
        ▼
┌─────────────────────────┐
│ Quellen wählen           │  Nach Firma: Verzeichnis → öffentliche Schnittstellen von 24 ATS
│                         │  Übergreifend: freehire / Workable / staatliche Jobbörsen / Remote-Boards / Plugins
│                         │  China: Feishu / Moka / Beisen / Eigenportale
└──────────┬──────────────┘
           │  Netz: ehrliche Kennung, Takt je Website, Rückzug bei 429, Stopp bei 403 oder Bot-Prüfung
┌──────────▼──────────────┐
│ 24 Felder + Altersklasse │  Filter Stichwort / Land / letzte N Tage; Deduplizierung; Vermittler-Markierung
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (voll)   Schnappschüsse / MCP
```

## Quellen

**Nach Unternehmen: 24 ATS** (Firmenverzeichnis von [openroles](https://github.com/datascry/openroles), zur Laufzeit lokal heruntergeladen, nicht im Repo enthalten)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**Unternehmensübergreifende Quellen `--board` (12)**

| Quelle | Abdeckung | Hinweise |
|---|---|---|
| `freehire` | Weltweit (nach eigenen Angaben ca. 3,3 Mio. offene Stellen) | Öffentliche API von [freehire](https://github.com/strelov1/freehire), bündelt 225 Quellen, volle Beschreibungen, Filter nach Land / Stichwort / letzten N Tagen |
| `workable` | Weltweit | Workable-weite Stellensuche, Filter nach Land / Stichwort |
| `jobtech` | Schweden | Offene Daten der schwedischen Arbeitsverwaltung, volle Beschreibungen |
| `mycareersfuture` | Singapur | Staatliches Jobportal Singapurs, mit Gehalt, ohne Beschreibung |
| `arbeitsagentur` | Deutschland | Bundesagentur für Arbeit, ohne Beschreibung |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | Remote | `--board all` = diese 4 |
| `reed` · `adzuna` · `usajobs` | UK / 19 Länder / US-Bundesbehörden | Eigene kostenlose Schlüssel nötig (`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`); nach offizieller Doku geschrieben, vom Maintainer nicht live getestet |

**China: 170 Unternehmen (`--local`)**: Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · Eigenportale (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). Vollständige Liste: `--list`.

**Nicht unterstützt / bekannte Grenzen**
- **Paycom**: seine robots.txt erlaubt den Stellenlisten-Endpunkt nicht, daher wird er nicht gelesen.
- **iCIMS**: das `datePosted` in den Seiten wird vom System erzeugt (aktuelle Zeit minus zwei Jahre); dieses Werkzeug nutzt stattdessen das Aktualisierungsdatum aus der Sitemap. Veröffentlichungsdaten aus iCIMS-Daten anderer Werkzeuge mit Vorsicht behandeln.
- Das Verzeichnis enthält viele inaktive Konten – eine Firma ohne Stellen ist normal; gleichnamige Firmen können kollidieren – bei mehreren Treffern werden alle Kandidaten gelistet.
- Dedupliziert wird nach Land + Firma + Stellentitel: derselbe Titel einer Firma in mehreren Städten eines Landes wird zu einer Zeile.

> **Zu Moka (ehrlicher Hinweis)**: Moka-Schnittstellen verschleiern Antworten leicht im Frontend (AES-128-CBC, Schlüssel und IV werden mit dem öffentlichen Frontend ausgeliefert). Das Werkzeug nutzt diese öffentlichen Werte, um genau die öffentliche Stellenliste zu erhalten, die ein Browser zeigt – kein Knacken von Logins, keine Umgehung der Authentifizierung. Streng genommen „spielt es die Frontend-Verarbeitung nach“, etwas grauer als reines JSON-Lesen; nur für lokale Forschung, auf eigenes Risiko. Für die sauberste Haltung alle `moka`-Zeilen in `parsers/companies.seed` sowie die eingebauten Zeilen `yostar`/`tesla-cn` in `radar/local.py` löschen.

## Private Plugins

Für große Plattformen, deren Bedingungen keine Veröffentlichung von Scraper-Code erlauben, schreiben Sie ein eigenes Plugin außerhalb des Repos:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

Jede `.py`-Datei im Plugin-Ordner, die nicht mit `_` beginnt, ist eine Quelle mit `NAME`, `DESC`, `FILTERS` und `pages(q, state=None)` (gleiche Schnittstelle wie `radar/boards/`); Dateien mit `_` am Anfang können gemeinsamen Code enthalten. Plugins laufen mit Ihren Rechten; für die Bedingungen der besuchten Websites sind Sie selbst verantwortlich.

## Verwandte Projekte: wo es die großen Plattformen gibt

Hiring Radar enthält keine Scraper für große Plattformen wie Indeed, LinkedIn oder SEEK. Die zwei folgenden Open-Source-Repositories von Dritten schon; die Tabelle zeigt je Plattform, wo der Code ungefähr liegt, damit Sie selbst nachsehen können.

- **[speedyapply/JobSpy](https://github.com/speedyapply/JobSpy)**: Python-Bibliothek, MIT-Lizenz. Fragt mehrere Plattformen auf einmal ab und liefert Titel, Firma, Ort, Gehalt, Link und Beschreibung.
- **[strelov1/freehire](https://github.com/strelov1/freehire)**: In Go geschriebene Stellensuchmaschine, MIT-Lizenz, 225 Quellen. Ihr Code in der Tabelle ist Teil ihres Backend-Crawlers, keine eigenständige Bibliothek; `--board freehire` in diesem Repo liest ihre öffentliche API.

| Plattform | Abdeckung | Repository | Ungefähre Stelle |
|---|---|---|---|
| Indeed | ca. 60 Länder, u. a. USA, UK, CA, AU, NZ, IE | JobSpy | `jobspy/indeed/` |
| LinkedIn | weltweit | JobSpy | `jobspy/linkedin/` |
| Glassdoor | ca. 20 Länder | JobSpy | `jobspy/glassdoor/` |
| ZipRecruiter | USA, Kanada | JobSpy | `jobspy/ziprecruiter/` |
| Google Jobs | Ort im Suchbegriff angeben | JobSpy | `jobspy/google/` |
| Naukri | Indien | JobSpy | `jobspy/naukri/` |
| Bayt | Naher Osten & Golf | JobSpy | `jobspy/bayt/` |
| BDJobs | Bangladesch | JobSpy | `jobspy/bdjobs/` |
| HelloWork | Frankreich | JobSpy | `jobspy/hellowork/` |
| SEEK | Australien, Neuseeland | freehire | `internal/ingest/sources/seek.go` |
| JobStreet / JobsDB | SG, MY, ID, PH / HK, TH | freehire | ebenfalls `seek.go` (gleiches Protokoll) |
| Öffentliche LinkedIn-Stellenliste | weltweit; nur zum Finden von Firmen, die einstellen | freehire | `cmd/harvest-linkedin/` |
| WhatJobs | viele Länder; braucht ein WhatJobs-Publisher-Konto | freehire | `internal/ingest/sources/whatjobs.go` |

> Das sind Projekte Dritter, nicht Teil von Hiring Radar. Wir haben ihren Code nicht geprüft und liefern keinen Code, um sie an dieses Tool anzubinden. Eine Open-Source-Lizenz regelt die Nutzung des Codes, nicht ob eine Plattform Scraping erlaubt: Prüfen Sie vorher Nutzungsbedingungen und robots.txt der Zielseite. Stand 2026-10-12; die Repositories können sich ändern.

## Unternehmen hinzufügen = eine Zeile (China)

Die chinesische Firmenliste ist `parsers/companies.seed` (`|`-getrennt); eine Firma = eine Zeile:

```
key | feishu | Firmenname | Portal-Domain (z. B. nio.jobs.feishu.cn)
key | moka   | Firmenname | orgId | siteId
key | beisen | Firmenname | slug
```

Neue ATS oder übergreifende Quellen: siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Branchensignal

Stellenanzeigen sind ein **Frühindikator**: wo eine Firma expandiert, in welche Richtung und in welcher Phase, zeigt sich oft Monate vor den Geschäftszahlen. Linien-Entwickler gesucht = Linie im Aufbau; QS/Wartung gesucht = Dauerproduktion in Vorbereitung; Nachtschicht gesucht = Hochlauf steht bevor. Mit `--save` regelmäßig Schnappschüsse anlegen, mit `--history` den Rhythmus sehen.

> ⚠️ **Einstellungen ≠ Produktion**: Stellen sind Input, nicht Output; „sucht“ kann auch Vorratsbildung oder ein Gegensignal sein. Ergebnisse als Signal behandeln, nicht als Anlageberatung.

## Projektstruktur

```
Hiring-Radar/
├── hiring_radar.py     # Kommandozeilen-Einstieg (v1-Befehlssyntax unverändert)
├── radar/              # Kernpaket
│   ├── http.py         # Netz: ehrliche Kennung, Takt, Rückzug, Stopp bei Sperre
│   ├── schema.py       # einheitliche Felder, Datum, Altersklassen
│   ├── ats/            # nach Unternehmen: eine Datei je ATS
│   ├── boards/         # übergreifende Quellen
│   ├── directory.py    # Firmenverzeichnis (zur Laufzeit geladen)
│   ├── process.py      # Deduplizierung, Vermittler-Markierung
│   ├── sweep.py        # Mehrquellen-Abruf, Fortsetzen
│   ├── store.py        # lokale Schnappschüsse (SQLite)
│   ├── local.py        # China / Eigenportal-Parser
│   ├── plugins.py      # Lader für private Plugins
│   └── mcp.py          # MCP-Server
├── parsers/            # China / Eigenportal-Parser + companies.seed
├── tests/              # smoke_test.py · test_offline.py (offline, ohne Netz)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## Technik & Abhängigkeiten

- **Python 3.8+**, Kern nur Standardbibliothek (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: nur für Moka-Parser (`pip install pycryptodome`)
- Internetzugang nötig (manche internationale Websites ggf. per Proxy); SSL-Zertifikate werden standardmäßig geprüft, hinter einem abfangenden Proxy `HIRING_RADAR_INSECURE=1` setzen

## Verantwortungsvolle Nutzung / Compliance

Ein **persönliches / Forschungs-, lokales + Open-Source**-Werkzeug. Bitte verantwortungsvoll nutzen:

- **Nur Stellenanzeigen lesen – nie Lebensläufe / personenbezogene Daten** (personenbezogene Daten fallen unter Chinas PIPL – nicht tun).
- **Nur öffentliche Schnittstellen ohne Login**: Login-Sperre / Captcha / aktiver Bot-Schutz wird **nicht umgangen**; 403 oder eine Bot-Prüfseite beendet den Lauf; keine Proxy-Pools, keine gefälschten Browser-Fingerabdrücke.
- **Ehrliche Kennung, niedrige Frequenz**: Der User-Agent nennt HiringRadar und die Projekt-URL (einzige Ausnahme: Die APIs von Feishu Hire und ByteDance lehnen eine Programmkennung ab, daher behalten diese beiden Parser den Browser-User-Agent aus v1); standardmäßig 0,3 Sekunden zwischen zwei Anfragen an dieselbe Website; bei 429 wird wie verlangt gewartet, und wenn es weiter scheitert, stoppt der Lauf und wartet auf Ihr `--resume`. robots.txt wird vor dem Aufnehmen einer neuen Quelle geprüft (deshalb kein Paycom).
- **Schlüssel nur in Umgebungsvariablen**: Quellen mit Schlüssel lesen ihn aus der Umgebung; in Fehlermeldungen werden Schlüssel maskiert.
- **Nur lokal**: kein Hosting / Upload / Server; Daten landen nur auf Ihrem Rechner. Bei Weiterveröffentlichung Compliance selbst prüfen; kein kommerzieller Weiterverkauf. Das Firmenverzeichnis steht unter CC BY-SA 4.0 – Weitergabe nur mit Namensnennung und gleicher Lizenz (siehe [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- „Öffentlich sichtbar“ ≠ „frei aggregier- und weiterveröffentlichbar“ – massenhaftes Scrapen + Weiterveröffentlichen kann in vielen Rechtsordnungen unlauterer Wettbewerb sein (inkl. chinesischer Rechtsprechung).

## Haftungsausschluss

1. **Sie kontrollieren Ihre Daten.** Das Werkzeug läuft lokal; es sammelt und lädt nichts hoch.
2. **Sie halten Drittbedingungen ein.** Beachten Sie die Bedingungen jeder Plattform; nutzen Sie es nicht, um Arbeitgeber zu belästigen oder ihre Systeme zu überlasten.
3. **Signale, keine Fakten.** Stellendaten sind ein Signal, keine Gewissheit; Branchen-/Anlageentscheidungen liegen in Ihrer Verantwortung.

Bereitgestellt unter der [MIT-Lizenz](LICENSE) „wie besehen“, ohne jede Gewährleistung. Code und Daten Dritter: siehe [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

PRs für weitere Unternehmen / Quellen willkommen (siehe [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
