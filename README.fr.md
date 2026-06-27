# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Français** · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>Un radar IA pour le marché de l'emploi mondial — il scanne les offres du monde entier et de Chine, pour la recherche d'emploi et les signaux industriels.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/Chine-170_portails-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-stdlib_uniquement-lightgrey.svg" alt="stdlib">
</p>

---

## C'est quoi

**Hiring Radar est un outil de données de recrutement nativement conçu pour l'IA : il donne à votre IA (Claude Code / ChatGPT / tout agent) la capacité de lire les offres officielles d'entreprises du monde entier + Chine.** Il lit directement les endpoints publics des systèmes de suivi des candidatures (ATS) qu'utilisent les entreprises et agrège les offres en **données structurées** à donner à votre IA. Ce n'est pas un énième site d'emploi qui exige une inscription : il tourne en local, et une seule commande interroge n'importe quelle entreprise du monde, un secteur entier, ou balaie plusieurs entreprises, **sans compte ni configuration**.

Les ATS utilisés par les entreprises (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) exposent **les mêmes endpoints JSON publics que leurs propres frontends appellent**, contenant la description de poste complète, le service, le lieu, la date de publication et le salaire. Hiring Radar lit exactement ces endpoints publics : rapide, propre, et prêt à alimenter une IA.

Deux usages :

- 🔎 **Recherche d'emploi / « où ça recrute » (principal)** : quelles entreprises recrutent dans un secteur, dans quelles villes, à quel salaire.
- 📈 **Signal avancé industrie / investissement (secondaire)** : le recrutement révèle souvent la stratégie des mois avant les résultats financiers. Voir [Signal industrie](#-signal-industrie-secondaire).

Couverture : **9 grands ATS internationaux + 4 plateformes mondiales d'emploi à distance + 170 portails officiels d'entreprises chinoises**. La couverture Chine (parsers universels Feishu Hire / Moka / Beisen + portails maison de Tencent/NetEase/JD/Baidu/ByteDance/Unitree) est le manque que laissent la plupart des outils existants.

**Les grandes marques internationales fonctionnent avec un simple nom d'entreprise**, p. ex. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, etc.

> ⚠️ Il lit **les offres que les entreprises publient elles-mêmes**, jamais de CV/données personnelles, jamais de contenu derrière un login. Usage personnel, basse fréquence, visiteur poli. Voir [Usage responsable](#-usage-responsable--conformité).

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| **Par entreprise (international)** | Un nom d'entreprise suffit pour auto-détecter 8 ATS (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio) ; si trouvé : description complète + service + lieu + date + salaire |
| **Plateformes remote mondiales** | `--board` balaie plusieurs entreprises : RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 entreprises chinoises** | `--local` : parsers **universels** Feishu Hire / Moka / Beisen (ajouter une entreprise = ajouter une ligne) + 6 portails maison. IA incarnée / LLM / semi-conducteurs / automobile / énergie / quant / multinationales / jeux vidéo |
| **Filtre mot-clé / récence** | `--keyword a,b,c` (virgule = OU ; cherche titre/service/lieu/JD/salaire) · `--recent-days N` |
| **Sortie structurée unifiée** | Schéma à 15 champs ; `--json` émet tout (JD complète incl.) pour alimenter l'IA |
| **Résumé terminal** | Par défaut top entreprises / services / lieux + liste des offres |
| **Piloté par les données** | La liste des entreprises chinoises est une table de seed `companies.seed` — **ajouter une entreprise = une ligne, sans code** |
| **stdlib pur** | Script à point d'entrée unique, zéro dépendance (seul Moka requiert `pycryptodome`), tourne sur tout `python3` |

## 🚀 Démarrage rapide

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # optionnel, seulement pour les entreprises chinoises sous Moka

python3 hiring_radar.py --list             # liste toutes les entreprises / plateformes interrogeables
```

```bash
# 1) International : un nom d'entreprise suffit (figure/1x/anthropic/openai/scale/nvidia intégrés) ou auto-détectez n'importe lequel
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # ATS explicite
python3 hiring_radar.py --workday host,tenant,site

# 2) Chine : --local <key> (clés via --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (maison)

# 3) Plateformes : « où ça recrute » entre entreprises
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Sortie structurée complète (avec JD complète) pour analyse
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Options communes** : `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Champs de sortie

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(salaire) · jd(complète) · url · apply_url · id` (15 champs)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu incluent en général la JD complète ; Workday et certains tenants Moka sont au niveau liste uniquement (titre/service/lieu/date). `--json` émet tout.

## 🌐 Sources

**ATS internationaux (auto-détection par nom — 9 systèmes)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Les grandes marques fonctionnent avec un simple nom d'entreprise (toutes vérifiées), p. ex. :
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Plateformes remote mondiales (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**Chine — 170 entreprises (`--local`, portails officiels, table de seed)**
- **Feishu Hire** : Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka** : Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (grande industrie / automobile / électroménager / engins lourds) : Dreame, Chery, Leapmotor, BOE, SANY …
- **Maison** : Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Liste complète : `python3 hiring_radar.py --list`

## ➕ Ajouter une entreprise = ajouter une ligne (sans code)

La liste des entreprises chinoises est dans `parsers/companies.seed` (séparé par `|`), chargée au démarrage. Ajoutez une ligne :

```
key | feishu | Entreprise | domaine-portail (p. ex. nio.jobs.feishu.cn)
key | moka   | Entreprise | orgId | siteId   # les deux dans l'URL app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | Entreprise | slug             # portail {slug}.zhiye.com, p. ex. dreame
```

Pour une source entièrement nouvelle (écrire un parser), voir [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Signal industrie (secondaire)

Le recrutement est un **indicateur avancé**. Par exemple :

- Recruter des ingénieurs de ligne = la ligne se monte encore ; QA/maintenance = préparation à la production continue ; équipes de nuit = montée en cadence imminente ; QA réception/qualité fournisseurs = intégration de fournisseurs externes.
- Utilisez `--local <entreprise> --keyword factory,production,assembly` pour le côté industriel ; `--recent-days` pour le récent ; prenez des **instantanés mensuels** des valeurs clés pour suivre la tendance.

> ⚠️ **Recrutement ≠ production.** Les offres sont des « entrées », pas des « sorties » ; rendement/montée en cadence/chaîne d'appro sont entre les deux. À traiter comme un signal, pas un conseil d'investissement.

## ⚖️ Usage responsable / Conformité

Outil **personnel / de recherche, local + open source**. À utiliser de manière responsable :

- **Offres uniquement — jamais de CV / données personnelles.**
- **Endpoints publics sans login uniquement** : en cas de mur de connexion / captcha / anti-bot actif, **ne le contournez pas**.
- **Local uniquement** : pas d'hébergement / d'upload / de serveur. Si vous republiez les données, évaluez la conformité vous-même.
- **Basse fréquence, visiteur poli** ; pas de revente commerciale. « Visible publiquement » ≠ « libre d'agréger et de republier ».

## ⚠️ Avertissement

1. **Vous contrôlez vos données.** Tourne en local ; ne collecte ni n'envoie rien.
2. **Vous respectez les CGU des tiers.** Respectez les ToS de chaque plateforme ; pas de spam ni de surcharge.
3. **Des signaux, pas des faits.** Les données de recrutement sont un signal ; les jugements industrie/investissement relèvent de votre responsabilité.

Sous [licence MIT](LICENSE) « en l'état », sans garantie d'aucune sorte.

## 🙋 Auteur

Créé par **Simon** — un outil local qui agrège les offres officielles d'entreprises du monde entier et de Chine. PRs bienvenues pour ajouter des entreprises / sources (voir [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
