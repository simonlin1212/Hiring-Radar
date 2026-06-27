# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · **Deutsch** · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>Ein KI-Radar für den globalen Arbeitsmarkt — scannt offene Stellen weltweit und in China, für die Jobsuche und Branchensignale.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_Portale-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-nur_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## Was ist das

**Hiring Radar ist ein KI-natives Recruiting-Datentool — es gibt deiner KI (Claude Code / ChatGPT / jedem Agenten) die Fähigkeit, offizielle offene Stellen von Unternehmen weltweit + China zu lesen.** Es liest direkt die öffentlichen Endpunkte der Bewerbermanagementsysteme (ATS), die Unternehmen verwenden, und aggregiert die offenen Stellen zu **strukturierten Daten** für deine KI. Es ist keine weitere Jobbörse mit Registrierungszwang: Es läuft lokal, und ein einziger Befehl fragt jedes Unternehmen weltweit, ein ganzes Feld oder mehrere Unternehmen ab — **ohne Konto, ohne Konfiguration**.

Die von Unternehmen genutzten ATS (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) stellen **dieselben öffentlichen JSON-Endpunkte bereit, die ihre eigenen Frontends aufrufen** — mit vollständiger Stellenbeschreibung, Abteilung, Standort, Veröffentlichungsdatum und Gehalt. Hiring Radar liest genau diese öffentlichen Endpunkte: schnell, sauber und bereit für die KI-Analyse.

Zwei Anwendungen:

- 🔎 **Jobsuche / „wo wird eingestellt" (primär)**: welche Unternehmen jetzt in einem Bereich einstellen, in welchen Städten, zu welchem Gehalt.
- 📈 **Branchen-/Investment-Frühsignal (sekundär)**: Einstellungen verraten die Strategie oft Monate vor den Geschäftszahlen. Siehe [Branchensignal](#-branchensignal-sekundär).

Abdeckung: **9 große internationale ATS + 4 globale Remote-Jobbörsen + 170 offizielle Portale chinesischer Unternehmen**. Die China-Abdeckung (universelle Parser für Feishu Hire / Moka / Beisen + eigene Portale von Tencent/NetEase/JD/Baidu/ByteDance/Unitree) ist die Lücke, die die meisten bestehenden Tools offen lassen.

**Große internationale Marken funktionieren mit einem bloßen Firmennamen**, z. B. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab usw.

> ⚠️ Es liest **Stellenanzeigen, die Unternehmen selbst veröffentlichen** — niemals Lebensläufe/persönliche Daten, niemals Login-geschützte Inhalte. Eigennutzung, niedrige Frequenz, höflicher Besucher. Siehe [Verantwortungsvolle Nutzung](#-verantwortungsvolle-nutzung--compliance).

## ✨ Funktionen

| Funktion | Beschreibung |
|---|---|
| **Pro Unternehmen (international)** | Ein Firmenname genügt, um 8 ATS automatisch zu prüfen (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio); bei Treffer: volle JD + Abteilung + Standort + Datum + Gehalt |
| **Globale Remote-Boards** | `--board` durchsucht mehrere Unternehmen: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 chinesische Unternehmen** | `--local`: **universelle** Parser für Feishu Hire / Moka / Beisen (Unternehmen hinzufügen = eine Zeile) + 6 eigene Portale. Verkörperte KI / LLM / Halbleiter / Automobil / Energie / Quant / Konzerne / Gaming |
| **Stichwort-/Aktualitätsfilter** | `--keyword a,b,c` (Komma = ODER; sucht Titel/Abteilung/Standort/JD/Gehalt) · `--recent-days N` |
| **Einheitliche strukturierte Ausgabe** | 15-Feld-Schema; `--json` gibt alles aus (inkl. voller JD) für die KI |
| **Terminal-Zusammenfassung** | Standardmäßig Top-Unternehmen / -Abteilungen / -Standorte + Stellenliste |
| **Datengetrieben** | Die chinesische Unternehmensliste ist eine Seed-Tabelle `companies.seed` — **Unternehmen hinzufügen = eine Zeile, kein Code** |
| **Nur stdlib** | Einzelnes Einstiegsskript, null Abhängigkeiten (nur Moka braucht `pycryptodome`), läuft auf jedem `python3` |

## 🚀 Schnellstart

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # optional, nur für chinesische Unternehmen mit Moka

python3 hiring_radar.py --list             # alle abfragbaren Unternehmen / Boards auflisten
```

```bash
# 1) International: ein Firmenname genügt (figure/1x/anthropic/openai/scale/nvidia integriert) oder beliebig auto-prüfen
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # ATS explizit
python3 hiring_radar.py --workday host,tenant,site

# 2) China: --local <key> (Keys via --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (eigen)

# 3) Boards: „wo wird eingestellt" unternehmensübergreifend
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Volle strukturierte Ausgabe (mit voller JD) zur Analyse
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Gemeinsame Optionen**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Ausgabefelder

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(Gehalt) · jd(voll) · url · apply_url · id` (15 Felder)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu enthalten meist die volle JD; Workday und einzelne Moka-Mandanten nur auf Listenebene (Titel/Abteilung/Standort/Datum). `--json` gibt alles aus.

## 🌐 Quellen

**Internationale ATS (Auto-Prüfung per Name — 9 Systeme)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Große Marken funktionieren mit einem bloßen Firmennamen (alle verifiziert), z. B.:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Globale Remote-Boards (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**China — 170 Unternehmen (`--local`, offizielle Portale, Seed-Tabelle)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (Großindustrie / Automobil / Haushaltsgeräte / schwere Maschinen): Dreame, Chery, Leapmotor, BOE, SANY …
- **Eigene**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Vollständige Liste: `python3 hiring_radar.py --list`

## ➕ Unternehmen hinzufügen = eine Zeile (kein Code)

Die chinesische Unternehmensliste liegt in `parsers/companies.seed` (durch `|` getrennt), beim Start automatisch geladen. Eine Zeile hinzufügen:

```
key | feishu | Unternehmen | Portal-Domain (z. B. nio.jobs.feishu.cn)
key | moka   | Unternehmen | orgId | siteId   # beide in der URL app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | Unternehmen | slug             # Portal {slug}.zhiye.com, z. B. dreame
```

Für eine ganz neue Quelle (Parser schreiben) siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Branchensignal (sekundär)

Einstellungen sind ein **Frühindikator**. Beispiel:

- Einstellung von Linien-Ingenieuren = Linie wird noch aufgebaut; QA/Wartung = Vorbereitung auf Dauerproduktion; Nachtschichten = Hochlauf steht bevor; Wareneingangs-QA/Lieferantenqualität = Onboarding externer Lieferanten.
- `--local <Unternehmen> --keyword factory,production,assembly` für die Fertigungsseite; `--recent-days` für Aktuelles; **monatliche Snapshots** der Schlüsselwerte für den Trend.

> ⚠️ **Einstellung ≠ Produktion.** Stellen sind „Inputs", keine „Outputs"; Ausbeute/Hochlauf/Lieferkette liegen dazwischen. Als Signal behandeln, nicht als Anlageberatung.

## ⚖️ Verantwortungsvolle Nutzung / Compliance

Ein **persönliches / Forschungs-, lokales + Open-Source-**Tool. Verantwortungsvoll nutzen:

- **Nur Stellenanzeigen — niemals Lebensläufe / persönliche Daten.**
- **Nur öffentliche, login-freie Endpunkte**: bei Login-Wall / Captcha / aktivem Anti-Bot **nicht umgehen**.
- **Nur lokal**: kein Hosting / Upload / Server. Bei Weiterveröffentlichung der Daten Compliance selbst prüfen.
- **Niedrige Frequenz, höflicher Besucher**; kein kommerzieller Weiterverkauf. „Öffentlich sichtbar" ≠ „frei aggregierbar und weiterveröffentlichbar".

## ⚠️ Haftungsausschluss

1. **Du kontrollierst deine Daten.** Läuft lokal; sammelt und sendet nichts.
2. **Du befolgst die AGB Dritter.** Halte die ToS jeder Plattform ein; kein Spam, keine Überlastung.
3. **Signale, keine Fakten.** Recruiting-Daten sind ein Signal; Branchen-/Investmenturteile liegen in deiner Verantwortung.

Unter [MIT-Lizenz](LICENSE) „wie besehen", ohne jegliche Gewährleistung.

## 🙋 Autor

**Simon Lin** · Douyin: Simon林 · WeChat: 硅基世纪

Ein lokales Tool, das offizielle offene Stellen von Unternehmen weltweit und in China aggregiert. PRs zum Hinzufügen weiterer Unternehmen / Quellen willkommen (siehe [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
