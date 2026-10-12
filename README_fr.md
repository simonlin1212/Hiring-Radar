<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <b>Français</b> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>Un radar du marché mondial de l'emploi propulsé par l'IA – il recense les postes ouverts dans le monde et en Chine, pour la recherche d'emploi, les signaux sectoriels et les études de marché.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_sources-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/Chine-170_portails-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-pris_en_charge-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-stdlib_seule-lightgrey.svg" alt="stdlib">
</p>

---

## Qu'est-ce que c'est

**Hiring Radar est un outil de données d'embauche pensé pour l'IA – il permet à votre IA (Claude Code / Codex / ChatGPT / tout agent) de lire les postes ouverts officiels d'entreprises du monde entier et de Chine.** Il lit les logiciels de recrutement (ATS) des entreprises et des sources d'offres publiques via leurs interfaces publiques, et en tire des **données structurées aux champs unifiés**. Il tourne en local ; une commande interroge une entreprise, un pays ou une fonction, **sans compte ni configuration**.

Trois usages :

- 🔎 **Recherche d'emploi / « qui recrute ? »** : quelles entreprises recrutent dans un domaine, dans quelles villes, à quel salaire.
- 📊 **Études de marché / opportunités produit** : extraire des pans entiers par pays, fonction et période pour voir pour quoi le marché paie des gens (nouveau en v2).
- 📈 **Signal avancé sectoriel / d'investissement** : les recrutements trahissent souvent la stratégie des mois avant les résultats. Voir « Signal sectoriel » plus bas.

**Les grands noms mondiaux fonctionnent avec un simple nom d'entreprise**, par ex. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, et d'autres.

**Nouveau en v2** : 24 ATS plus un annuaire d'environ 90 000 entreprises (trouver par le nom quel système une entreprise utilise) · 12 sources multi-entreprises (dont l'agrégateur freehire et les bourses d'emploi publiques de Suède, Singapour et Allemagne) · dédoublonnage entre sources et repérage des cabinets de recrutement · tranches d'ancienneté · reprise après interruption · instantanés locaux pour voir les postes nouveaux/retirés · un **serveur MCP** que votre assistant IA peut appeler directement.

> ⚠️ Il ne lit que **les offres publiées par les entreprises elles-mêmes** – jamais de CV ni de données personnelles, jamais de contenu derrière une connexion, et il s'arrête à toute vérification anti-robot. Voir « Usage responsable » plus bas.

## Fonctionnalités

| Fonction | Ce qu'elle fait |
|---|---|
| **Par entreprise** | Un nom suffit : d'abord l'annuaire (~90 000 entreprises sur 24 ATS), sinon devinette des systèmes courants ; ou précisément avec `--ats système slug` |
| **Multi-entreprises** | `--board` par pays / mot-clé / N derniers jours : freehire, recherche globale Workable, bourses d'emploi publiques, sites de télétravail ; plusieurs sources à la fois, dédoublonnées |
| **Ancienneté** | Chaque offre est classée 0-3 mois / 3-6 mois / plus de 6 mois / sans date ; `--board` montre par défaut les six derniers mois |
| **Cabinets repérés** | Marque les offres publiées par des chasseurs de têtes ou agences d'intérim (champ `agency`) ; `--no-agency` les retire |
| **Reprise** | Si une source est limitée ou échoue, les autres continuent ; la même commande avec `--resume` ne complète que le manquant |
| **Instantanés locaux** | `--save` enregistre dans un fichier SQLite local avec dates de première/dernière vue ; `--history` montre les ajouts et retraits par passage |
| **Serveur MCP** | `--mcp` : Claude Code / Codex, etc. l'appellent directement (entreprise, recherche d'offres, annuaire) |
| **Chine : 170 entreprises** | `--local` : trois analyseurs universels (Feishu Hire / Moka / Beisen) + 6 portails maison de grands groupes tech |
| **Extensions privées** | Les sources dont les conditions ne se prêtent pas à une diffusion publique vont dans votre propre dossier (`--plugins`), hors du dépôt |
| **Bibliothèque standard** | Aucune dépendance (seul l'analyseur Moka requiert `pycryptodome`) ; tourne avec tout `python3` |

## Démarrage rapide

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # télécharger l'annuaire (~90 000 entreprises, stocké en local ; facultatif mais conseillé)
python3 hiring_radar.py --list               # lister toutes les sources
```

```bash
# 1) Par entreprise : un nom suffit
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # trouvé dans l'annuaire → bon système
python3 hiring_radar.py --find xero                  # afficher seulement l'ATS utilisé
python3 hiring_radar.py --ats teamtailor <slug>      # fixer le système et le compte
python3 hiring_radar.py --workday host,tenant,site

# 2) Multi-entreprises : pays + mot-clé + période
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country FR --max 0 --json > fr.json   # sans plafond
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # bourse d'emploi publique suédoise
python3 hiring_radar.py --board all --keyword "AI engineer"                              # les 4 sites de télétravail

# 3) Reprendre après interruption / instantanés
python3 hiring_radar.py --board freehire --country AU --max 0 --resume
python3 hiring_radar.py anthropic --save          # le passage suivant montre les ajouts/retraits
python3 hiring_radar.py --history

# 4) Entreprises chinoises
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka ; pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (portail maison)
```

**Options courantes** : `--keyword a,b` (n'importe lequel) · `--recent-days N` (0 = sans limite) · `--country AU,NZ` · `--max N` (plafond par source, 1000 par défaut, 0 = aucun) · `--no-agency` · `--json` · `--limit N` · `--debug`

**Variables d'environnement** : `HIRING_RADAR_HOME` (annuaire, instantanés, état de reprise ; par défaut `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (secondes minimum entre deux requêtes au même site ; 0,3 par défaut) · `HIRING_RADAR_PLUGINS` (dossier d'extensions privées) · `HIRING_RADAR_INSECURE=1` (désactive la vérification des certificats, uniquement derrière un proxy intercepteur)

Codes de sortie : `0` OK ; `3` certaines sources n'ont pas fini (ce qui a été récupéré est quand même affiché ; utilisez `--resume`).

## Pour les assistants IA (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

Cinq outils : `company_jobs` (une entreprise) · `search_jobs` (multi-entreprises) · `find_company` (annuaire) · `list_sources` · `job_history`. Les descriptions sont coupées à 800 caractères dans les résultats MCP ; le texte complet s'obtient en ligne de commande avec `--json`.

## Champs de sortie

Les 15 champs de la v1 restent : `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (salaire) · jd (complète) · url · apply_url · id`

La v2 en ajoute 9 : `country` (code pays) · `source` · `age` (tranche 0-3m/3-6m/6m+/unknown) · `agency` (terme de cabinet détecté) · `also` (autres sources ayant la même offre, après dédoublonnage) · `industry` · `size` (taille de l'entreprise, si la source la donne) · `first_seen` · `last_seen` (avec instantanés uniquement)

Enveloppe `--json` : `source · total · matched · jobs` (comme en v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## Fonctionnement

```
Nom d'entreprise / pays + mot-clé
        │
        ▼
┌─────────────────────────┐
│ Choix des sources        │  Par entreprise : annuaire → interfaces publiques de 24 ATS
│                         │  Multi-entreprises : freehire / Workable / bourses publiques / télétravail / extensions
│                         │  Chine : Feishu / Moka / Beisen / portails maison
└──────────┬──────────────┘
           │  Réseau : identité honnête, cadence par site, recul sur 429, arrêt sur 403 ou anti-robot
┌──────────▼──────────────┐
│ 24 champs + ancienneté   │  Filtres mot-clé / pays / N derniers jours ; dédoublonnage ; repérage des cabinets
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (complet)  Instantanés / MCP
```

## Sources

**Par entreprise : 24 ATS** (annuaire issu d'[openroles](https://github.com/datascry/openroles), téléchargé localement à l'exécution, non inclus dans le dépôt)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**Sources multi-entreprises `--board` (12)**

| Source | Couverture | Remarques |
|---|---|---|
| `freehire` | Monde (revendique ~3,3 M d'offres ouvertes) | API publique de [freehire](https://github.com/strelov1/freehire), agrège 225 sources, descriptions complètes, filtres pays / mot-clé / N derniers jours |
| `workable` | Monde | Recherche globale Workable, filtres pays / mot-clé |
| `jobtech` | Suède | Données ouvertes du service public de l'emploi suédois, descriptions complètes |
| `mycareersfuture` | Singapour | Portail d'emploi du gouvernement de Singapour, salaires, sans description |
| `arbeitsagentur` | Allemagne | Agence fédérale allemande pour l'emploi, sans description |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | Télétravail | `--board all` = ces 4 |
| `reed` · `adzuna` · `usajobs` | Royaume-Uni / 19 pays / administration fédérale américaine | Clés gratuites personnelles requises (`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`) ; écrites d'après la documentation officielle, non testées en réel par le mainteneur |

**Chine : 170 entreprises (`--local`)** : Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · portails maison (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). Liste complète : `--list`.

**Non pris en charge / limites connues**
- **Paycom** : son robots.txt n'autorise pas l'accès à la liste des offres, l'outil ne le lit donc pas.
- **iCIMS** : le `datePosted` de ses pages est généré par le système (heure actuelle moins deux ans) ; l'outil utilise à la place la date de mise à jour du plan du site. Prudence avec les dates de publication iCIMS collectées par d'autres outils.
- L'annuaire contient beaucoup de comptes inactifs – trouver une entreprise sans offre est normal ; des homonymes peuvent se confondre – en cas de plusieurs résultats, tous les candidats sont listés.
- Le dédoublonnage se fait par pays + entreprise + intitulé : un même intitulé publié par une entreprise dans plusieurs villes d'un pays devient une seule ligne.

> **À propos de Moka (en toute franchise)** : les interfaces Moka appliquent un léger brouillage côté navigateur (AES-128-CBC, clé et IV livrés avec leur front-end public). L'outil utilise ces valeurs publiques pour retrouver exactement la liste publique d'offres qu'affiche un navigateur – sans casser de connexion ni contourner d'authentification. À strictement parler, il « rejoue le traitement du front-end », un peu plus gris que la lecture de JSON brut ; pour la recherche locale uniquement, à vos risques. Pour la posture la plus propre, supprimez toutes les lignes `moka` de `parsers/companies.seed` et les lignes intégrées `yostar`/`tesla-cn` de `radar/local.py`.

## Extensions privées

Pour les grandes plateformes dont les conditions ne se prêtent pas à la publication de code de collecte, écrivez votre propre extension hors du dépôt :

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

Chaque fichier `.py` du dossier qui ne commence pas par `_` est une source, définissant `NAME`, `DESC`, `FILTERS` et `pages(q, state=None)` (même interface que `radar/boards/`) ; les fichiers commençant par `_` peuvent contenir du code partagé. Les extensions s'exécutent avec vos droits ; le respect des conditions des sites visités vous incombe.

## Ajouter une entreprise = une ligne (Chine)

La liste des entreprises chinoises est `parsers/companies.seed` (séparateur `|`) ; une entreprise = une ligne :

```
key | feishu | nom | domaine du portail (ex. nio.jobs.feishu.cn)
key | moka   | nom | orgId | siteId
key | beisen | nom | slug
```

Pour ajouter un ATS ou une source multi-entreprises, voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Signal sectoriel

Le recrutement est un **indicateur avancé** : où une entreprise s'étend, dans quelle direction et à quel stade apparaît souvent des mois avant les résultats. Recruter des ingénieurs de ligne = la ligne se construit ; recruter qualité/maintenance = production durable en préparation ; recruter des équipes de nuit = montée en cadence imminente. Utilisez `--save` pour des instantanés réguliers et `--history` pour voir le rythme.

> ⚠️ **Recrutement ≠ production** : les postes sont des intrants, pas des extrants ; « recrute » peut aussi être du vivier ou un contre-signal. Traitez les conclusions comme des signaux, pas comme des conseils d'investissement.

## Structure du projet

```
Hiring-Radar/
├── hiring_radar.py     # point d'entrée en ligne de commande (usage v1 inchangé)
├── radar/              # paquet principal
│   ├── http.py         # réseau : identité honnête, cadence, recul, arrêt si bloqué
│   ├── schema.py       # champs unifiés, dates, tranches d'ancienneté
│   ├── ats/            # par entreprise : un fichier par ATS
│   ├── boards/         # sources multi-entreprises
│   ├── directory.py    # annuaire (téléchargé à l'exécution)
│   ├── process.py      # dédoublonnage, repérage des cabinets
│   ├── sweep.py        # collecte multi-sources, reprise
│   ├── store.py        # instantanés locaux (SQLite)
│   ├── local.py        # analyseurs Chine / portails maison
│   ├── plugins.py      # chargeur d'extensions privées
│   └── mcp.py          # serveur MCP
├── parsers/            # analyseurs Chine / portails maison + companies.seed
├── tests/              # smoke_test.py · test_offline.py (hors ligne, sans réseau)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## Technique et dépendances

- **Python 3.8+**, cœur en bibliothèque standard pure (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`** : uniquement pour les analyseurs Moka (`pip install pycryptodome`)
- Accès Internet requis (certains sites internationaux peuvent nécessiter un proxy) ; certificats SSL vérifiés par défaut, définir `HIRING_RADAR_INSECURE=1` derrière un proxy intercepteur

## Usage responsable / conformité

Un outil **personnel / de recherche, local + open source**. Utilisez-le de façon responsable :

- **Lire uniquement des offres – jamais de CV / données personnelles** (les données personnelles relèvent de la PIPL chinoise – à proscrire).
- **Uniquement des interfaces publiques sans connexion** : mur de connexion / captcha / anti-robot actif **non contournés** ; un 403 ou une page de vérification arrête la collecte ; pas de pools de proxys, pas d'empreinte de navigateur falsifiée.
- **Identité honnête, faible fréquence** : l'User-Agent indique HiringRadar et l'URL du projet ; par défaut 0,3 seconde entre deux requêtes au même site ; sur 429 l'outil patiente comme demandé, et s'il échoue encore il s'arrête et attend votre `--resume`. Le robots.txt est vérifié avant d'ajouter une source (d'où l'absence de Paycom).
- **Clés uniquement en variables d'environnement** : les sources à clé la lisent dans l'environnement, et les clés sont masquées dans les messages d'erreur.
- **Local uniquement** : ni hébergement, ni envoi, ni serveur ; les données restent sur votre machine. En cas de republication, évaluez vous-même la conformité ; pas de revente commerciale. L'annuaire est sous CC BY-SA 4.0 – toute redistribution exige attribution et même licence (voir [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- « Visible publiquement » ≠ « librement agrégeable et republiable » – la collecte massive suivie de republication peut constituer de la concurrence déloyale dans de nombreux pays (y compris la jurisprudence chinoise).

## Avertissement

1. **Vous maîtrisez vos données.** L'outil tourne en local ; il ne collecte ni n'envoie rien.
2. **Vous respectez les conditions des tiers.** Respectez les conditions de chaque plateforme ; ne l'utilisez pas pour démarcher abusivement les employeurs ni surcharger leurs systèmes.
3. **Des signaux, pas des faits.** Les données d'embauche sont un signal ; vos décisions sectorielles ou d'investissement relèvent de votre responsabilité.

Fourni sous [licence MIT](LICENSE) « en l'état », sans garantie d'aucune sorte. Code et données tiers : voir [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

Les PR pour ajouter des entreprises / sources sont bienvenues (voir [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
