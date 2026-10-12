<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <b>Español</b> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>Un radar del mercado laboral global impulsado por IA: rastrea vacantes abiertas en todo el mundo y en China, para buscar empleo, leer señales sectoriales y hacer estudios de mercado.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_fuentes-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portales-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-compatible-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-solo_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## Qué es

**Hiring Radar es una herramienta de datos de contratación pensada para IA: permite que tu IA (Claude Code / Codex / ChatGPT / cualquier agente) lea las vacantes oficiales de empresas de todo el mundo y de China.** Lee los sistemas de seguimiento de candidatos (ATS) de las empresas y fuentes públicas de empleo a través de sus interfaces públicas, y convierte las vacantes en **datos estructurados con campos unificados**. Se ejecuta en local; un comando consulta una empresa, un país o una función, **sin cuenta ni configuración**.

Tres usos:

- 🔎 **Buscar empleo / «¿quién está contratando?»**: qué empresas contratan ahora en un área, en qué ciudades y con qué salario.
- 📊 **Estudios de mercado / oportunidades de producto**: extraer porciones enteras por país, función y periodo para ver por qué está pagando el mercado (nuevo en v2).
- 📈 **Señal adelantada sectorial / de inversión**: la contratación suele revelar la estrategia meses antes que los resultados. Ver «Señal sectorial» más abajo.

**Las grandes marcas globales funcionan con solo el nombre de la empresa**, p. ej. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, y más.

**Novedades de v2**: 24 ATS y un directorio de unas 90.000 empresas (busca por nombre qué sistema usa una empresa) · 12 fuentes multiempresa (incluido el agregador freehire y las bolsas de empleo públicas de Suecia, Singapur y Alemania) · deduplicación entre fuentes y marcado de agencias · franjas por antigüedad de publicación · ejecuciones reanudables · instantáneas locales para ver vacantes nuevas/retiradas · un **servidor MCP** que tu asistente de IA puede llamar directamente.

> ⚠️ Solo lee **ofertas que las propias empresas publican**: nunca CV ni datos personales, nunca contenido tras inicio de sesión, y se detiene ante cualquier verificación anti-bots. Ver «Uso responsable» más abajo.

## Funciones

| Función | Qué hace |
|---|---|
| **Por empresa** | Basta el nombre: primero consulta el directorio (~90.000 empresas en 24 ATS) y, si no aparece, prueba los sistemas habituales; o se fija con `--ats sistema slug` |
| **Multiempresa** | `--board` por país / palabra clave / últimos N días: freehire, búsqueda global de Workable, bolsas públicas, portales de remoto; varias fuentes a la vez, deduplicadas |
| **Antigüedad** | Cada vacante se etiqueta 0-3 meses / 3-6 meses / más de 6 meses / sin fecha; `--board` muestra por defecto los últimos seis meses |
| **Agencias** | Marca las vacantes publicadas por headhunters o ETT (campo `agency`); `--no-agency` las quita |
| **Reanudable** | Si una fuente se limita o falla, las demás siguen; el mismo comando con `--resume` completa solo lo pendiente |
| **Instantáneas locales** | `--save` guarda en un SQLite local con fechas de primera/última vez visto; `--history` muestra altas y bajas por ejecución |
| **Servidor MCP** | `--mcp`: Claude Code / Codex, etc. lo llaman directamente (empresa, búsqueda, directorio) |
| **China: 170 empresas** | `--local`: tres analizadores universales (Feishu Hire / Moka / Beisen) + 6 portales propios de grandes tecnológicas |
| **Plugins privados** | Las fuentes cuyas condiciones no permiten distribuir el código públicamente van en tu propia carpeta (`--plugins`), fuera del repositorio |
| **Solo stdlib** | Cero dependencias (solo el analizador de Moka necesita `pycryptodome`); funciona con cualquier `python3` |

## Inicio rápido

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # descargar el directorio (~90.000 empresas, guardado en local; opcional pero recomendado)
python3 hiring_radar.py --list               # listar todas las fuentes
```

```bash
# 1) Por empresa: basta el nombre
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # encontrado en el directorio → usa el sistema correcto
python3 hiring_radar.py --find xero                  # solo mostrar qué ATS usa
python3 hiring_radar.py --ats teamtailor <slug>      # fijar sistema y cuenta
python3 hiring_radar.py --workday host,tenant,site

# 2) Multiempresa: país + palabra clave + periodo
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country ES --max 0 --json > es.json   # sin tope
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # bolsa pública de Suecia
python3 hiring_radar.py --board all --keyword "AI engineer"                              # los 4 portales de remoto

# 3) Reanudar tras una interrupción / instantáneas
python3 hiring_radar.py --board freehire --country AU --max 0 --resume
python3 hiring_radar.py anthropic --save          # la siguiente ejecución muestra altas/bajas
python3 hiring_radar.py --history

# 4) Empresas chinas
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka; pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (portal propio)
```

**Opciones habituales**: `--keyword a,b` (cualquiera) · `--recent-days N` (0 = sin límite) · `--country AU,NZ` · `--max N` (tope por fuente, 1000 por defecto, 0 = sin tope) · `--no-agency` · `--json` · `--limit N` · `--debug`

**Variables de entorno**: `HIRING_RADAR_HOME` (directorio, instantáneas y estado de reanudación; por defecto `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (segundos mínimos entre dos peticiones al mismo sitio; 0,3 por defecto) · `HIRING_RADAR_PLUGINS` (carpeta de plugins privados) · `HIRING_RADAR_INSECURE=1` (desactiva la verificación de certificados, solo tras un proxy interceptor)

Códigos de salida: `0` correcto; `3` alguna fuente no terminó (lo obtenido se muestra igualmente; usa `--resume`).

## Para asistentes de IA (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

Cinco herramientas: `company_jobs` (una empresa) · `search_jobs` (multiempresa) · `find_company` (directorio) · `list_sources` · `job_history`. Las descripciones se recortan a 800 caracteres en los resultados MCP; el texto completo se obtiene por línea de comandos con `--json`.

## Campos de salida

Los 15 campos de v1 se mantienen: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (salario) · jd (completa) · url · apply_url · id`

v2 añade 9: `country` (código de país) · `source` (fuente) · `age` (franja 0-3m/3-6m/6m+/unknown) · `agency` (término de agencia detectado) · `also` (otras fuentes con la misma vacante, tras deduplicar) · `industry` · `size` (tamaño de la empresa, si la fuente lo da) · `first_seen` · `last_seen` (solo con instantáneas)

Envoltorio `--json`: `source · total · matched · jobs` (como en v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## Cómo funciona

```
Nombre de empresa / país + palabra clave
        │
        ▼
┌─────────────────────────┐
│ Elegir fuentes           │  Por empresa: directorio → interfaces públicas de 24 ATS
│                         │  Multiempresa: freehire / Workable / bolsas públicas / remoto / plugins
│                         │  China: Feishu / Moka / Beisen / portales propios
└──────────┬──────────────┘
           │  Red: identidad honesta, ritmo por sitio, espera ante 429, parada ante 403 o anti-bots
┌──────────▼──────────────┐
│ 24 campos + antigüedad   │  Filtros palabra clave / país / últimos N días; deduplicación; marcado de agencias
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (completo)  Instantáneas / MCP
```

## Fuentes

**Por empresa: 24 ATS** (directorio de [openroles](https://github.com/datascry/openroles), descargado en local al ejecutar, no incluido en el repositorio)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**Fuentes multiempresa `--board` (12)**

| Fuente | Cobertura | Notas |
|---|---|---|
| `freehire` | Mundial (dice tener ~3,3 M de vacantes abiertas) | API pública de [freehire](https://github.com/strelov1/freehire), agrega 225 fuentes, descripciones completas, filtros por país / palabra clave / últimos N días |
| `workable` | Mundial | Búsqueda global de Workable, filtros por país / palabra clave |
| `jobtech` | Suecia | Datos abiertos del servicio público de empleo sueco, descripciones completas |
| `mycareersfuture` | Singapur | Portal de empleo del gobierno de Singapur, con salario, sin descripción |
| `arbeitsagentur` | Alemania | Agencia Federal de Empleo alemana, sin descripción |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | Remoto | `--board all` = estos 4 |
| `reed` · `adzuna` · `usajobs` | Reino Unido / 19 países / gobierno federal de EE. UU. | Requieren tus propias claves gratuitas (`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`); escritas según la documentación oficial, sin prueba real por parte del mantenedor |

**China: 170 empresas (`--local`)**: Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · portales propios (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). Lista completa: `--list`.

**No compatible / límites conocidos**
- **Paycom**: su robots.txt no permite la lista de vacantes, así que no se lee.
- **iCIMS**: el `datePosted` de sus páginas lo genera el sistema (hora actual menos dos años); esta herramienta usa en su lugar la fecha de actualización del mapa del sitio. Cuidado con las fechas de publicación de iCIMS recogidas con otras herramientas.
- El directorio tiene muchas cuentas inactivas: encontrar una empresa sin vacantes es normal; empresas homónimas pueden confundirse: si hay varias coincidencias, se listan todas.
- La deduplicación es por país + empresa + título: el mismo título de una empresa en varias ciudades de un país queda en una sola fila.

> **Sobre Moka (nota honesta)**: las interfaces de Moka aplican un ligero ofuscado en el front-end (AES-128-CBC, con clave e IV incluidos en su front-end público). La herramienta usa esos valores públicos para obtener exactamente la lista pública de vacantes que muestra un navegador, sin romper inicios de sesión ni saltarse autenticación. En sentido estricto «reproduce el procesamiento del front-end», algo más gris que leer JSON plano; solo para investigación local, bajo tu propio riesgo. Para la postura más limpia, borra todas las líneas `moka` de `parsers/companies.seed` y las líneas integradas `yostar`/`tesla-cn` de `radar/local.py`.

## Plugins privados

Para grandes plataformas cuyas condiciones no permiten publicar código de extracción, escribe tu propio plugin fuera del repositorio:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

Cada archivo `.py` de la carpeta que no empiece por `_` es una fuente que define `NAME`, `DESC`, `FILTERS` y `pages(q, state=None)` (misma interfaz que `radar/boards/`); los archivos que empiezan por `_` pueden contener código compartido. Los plugins se ejecutan con tus permisos y tú respondes de las condiciones de los sitios que visitan.

## Añadir una empresa = añadir una línea (China)

La lista de empresas chinas es `parsers/companies.seed` (separada por `|`); una empresa = una línea:

```
key | feishu | nombre | dominio del portal (p. ej. nio.jobs.feishu.cn)
key | moka   | nombre | orgId | siteId
key | beisen | nombre | slug
```

Para añadir un ATS o una fuente multiempresa, ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Señal sectorial

La contratación es un **indicador adelantado**: dónde se expande una empresa, en qué dirección y en qué fase suele verse meses antes que en los resultados. Contratar ingenieros de línea = la línea se está montando; contratar calidad/mantenimiento = se prepara producción sostenida; contratar turno de noche = se acerca el aumento de volumen. Usa `--save` para instantáneas periódicas y `--history` para ver el ritmo.

> ⚠️ **Contratación ≠ producción**: las vacantes son insumos, no resultados; «contratando» también puede ser reserva o una contraseñal. Trata las conclusiones como señales, no como consejo de inversión.

## Estructura del proyecto

```
Hiring-Radar/
├── hiring_radar.py     # entrada por línea de comandos (uso de v1 sin cambios)
├── radar/              # paquete principal
│   ├── http.py         # red: identidad honesta, ritmo, espera, parada si bloquean
│   ├── schema.py       # campos unificados, fechas, franjas de antigüedad
│   ├── ats/            # por empresa: un archivo por ATS
│   ├── boards/         # fuentes multiempresa
│   ├── directory.py    # directorio de empresas (descargado al ejecutar)
│   ├── process.py      # deduplicación, marcado de agencias
│   ├── sweep.py        # extracción multifuente, reanudación
│   ├── store.py        # instantáneas locales (SQLite)
│   ├── local.py        # analizadores de China / portales propios
│   ├── plugins.py      # cargador de plugins privados
│   └── mcp.py          # servidor MCP
├── parsers/            # analizadores de China / portales propios + companies.seed
├── tests/              # smoke_test.py · test_offline.py (sin conexión)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## Tecnología y dependencias

- **Python 3.8+**, núcleo solo con la biblioteca estándar (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: solo para los analizadores de Moka (`pip install pycryptodome`)
- Requiere Internet (algunos sitios internacionales pueden necesitar proxy); los certificados SSL se verifican por defecto; tras un proxy interceptor, define `HIRING_RADAR_INSECURE=1`

## Uso responsable / cumplimiento

Una herramienta **personal / de investigación, local y de código abierto**. Úsala con responsabilidad:

- **Solo ofertas de empleo, nunca CV / datos personales** (los datos personales activan la PIPL china: no lo hagas).
- **Solo interfaces públicas sin inicio de sesión**: muros de acceso / captcha / anti-bots activos **no se eluden**; un 403 o una página de verificación detiene la ejecución; sin pools de proxies ni huellas de navegador falsas.
- **Identidad honesta, baja frecuencia**: el User-Agent indica HiringRadar y la URL del proyecto; por defecto 0,3 segundos entre dos peticiones al mismo sitio; ante 429 espera lo que se le pide y, si sigue fallando, se detiene y espera tu `--resume`. Se revisa robots.txt antes de añadir una fuente (por eso no hay Paycom).
- **Claves solo en variables de entorno**: las fuentes con clave la leen del entorno y las claves se enmascaran en los mensajes de error.
- **Solo local**: sin alojamiento / subida / servidor; los datos quedan en tu máquina. Si republicas los datos, evalúa tú el cumplimiento; sin reventa comercial. El directorio de empresas es CC BY-SA 4.0: redistribuirlo exige atribución y la misma licencia (ver [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- «Visible públicamente» ≠ «libre para agregar y republicar»: el raspado masivo con republicación puede constituir competencia desleal en muchas jurisdicciones (incluida la jurisprudencia china).

## Descargo de responsabilidad

1. **Tú controlas tus datos.** La herramienta se ejecuta en local; no recoge ni sube nada.
2. **Tú cumples las condiciones de terceros.** Respeta las condiciones de cada plataforma; no la uses para acosar a empleadores ni sobrecargar sus sistemas.
3. **Señales, no hechos.** Los datos de contratación son una señal; las decisiones sectoriales o de inversión son responsabilidad tuya.

Se ofrece bajo la [licencia MIT](LICENSE) «tal cual», sin garantía de ningún tipo. Código y datos de terceros: ver [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

Se aceptan PR para añadir empresas / fuentes (ver [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
