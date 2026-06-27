# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>Un radar con IA para el mercado laboral global — escanea vacantes de todo el mundo y de China, para buscar empleo y captar señales de industria.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portales-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-solo_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## Qué es esto

**Hiring Radar es una herramienta de datos de contratación nativa de IA: le da a tu IA (Claude Code / ChatGPT / cualquier agente) la capacidad de leer las vacantes oficiales de empresas de todo el mundo + China.** Lee directamente los endpoints públicos de los sistemas de seguimiento de candidatos (ATS) que usan las empresas y agrega las vacantes en **datos estructurados** para alimentar a tu IA. No es otro portal de empleo que te pide registrarte: corre en local y un solo comando consulta cualquier empresa del mundo, un sector entero, o escanea varias empresas, **sin cuenta y sin configuración**.

Los ATS que usan las empresas (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) exponen **los mismos endpoints JSON públicos que llaman sus propios frontends**, con la descripción completa del puesto, departamento, ubicación, fecha de publicación y salario. Hiring Radar lee exactamente esos endpoints públicos: rápido, limpio y listo para alimentar una IA.

Dos usos:

- 🔎 **Búsqueda de empleo / "dónde se contrata" (principal)**: qué empresas contratan ahora en un sector, en qué ciudades, con qué salario.
- 📈 **Señal anticipada de industria / inversión (secundario)**: la contratación suele revelar la estrategia meses antes que los resultados financieros. Ver [Señal de industria](#-señal-de-industria-secundario).

Cobertura: **9 grandes ATS internacionales + 4 bolsas globales de empleo remoto + 170 portales oficiales de empresas chinas**. La cobertura de China (parsers universales de Feishu Hire / Moka / Beisen + portales propios de Tencent/NetEase/JD/Baidu/ByteDance/Unitree) es el hueco que dejan la mayoría de las herramientas existentes.

**Las grandes marcas internacionales funcionan con solo el nombre de la empresa**, p. ej. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, y más.

> ⚠️ Lee **vacantes que las empresas publican ellas mismas**, nunca currículums/datos personales, nunca contenido tras login. Uso propio, baja frecuencia, visitante educado. Ver [Uso responsable](#-uso-responsable--cumplimiento).

## ✨ Funciones

| Función | Descripción |
|---|---|
| **Empresa internacional** | Un nombre de empresa basta para auto-sondear 8 ATS (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio); en acierto: JD completa + departamento + ubicación + fecha + salario |
| **Bolsas remotas globales** | `--board` escanea varias empresas: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 empresas chinas** | `--local`: parsers **universales** de Feishu Hire / Moka / Beisen (añadir empresa = añadir una línea) + 6 portales propios. IA encarnada / LLM / semiconductores / automotrices / energía / quant / multinacionales / videojuegos |
| **Filtro por palabra clave / recencia** | `--keyword a,b,c` (coma = OR; busca en título/departamento/ubicación/JD/salario) · `--recent-days N` |
| **Salida estructurada unificada** | Esquema de 15 campos; `--json` emite todo (incl. JD completa) para alimentar IA |
| **Resumen en terminal** | Por defecto top de empresas / departamentos / ubicaciones + lista de vacantes |
| **Basado en datos** | La lista de empresas chinas es una tabla semilla `companies.seed` — **añadir empresa = una línea, sin código** |
| **Solo stdlib** | Script de un solo punto de entrada, cero dependencias (solo Moka necesita `pycryptodome`), corre en cualquier `python3` |

## 🚀 Inicio rápido

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # opcional, solo para empresas chinas con Moka

python3 hiring_radar.py --list             # lista todas las empresas / bolsas consultables
```

```bash
# 1) Internacional: basta el nombre de la empresa (figure/1x/anthropic/openai/scale/nvidia integrados) o auto-sondea cualquiera
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # ATS explícito
python3 hiring_radar.py --workday host,tenant,site

# 2) China: --local <key> (keys vía --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (propio)

# 3) Bolsas: "dónde se contrata" entre empresas
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Salida estructurada completa (con JD completa) para análisis
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Opciones comunes**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Campos de salida

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(salario) · jd(completa) · url · apply_url · id` (15 campos)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu suelen incluir JD completa; Workday y algunos tenants de Moka son solo a nivel de lista (título/departamento/ubicación/fecha). `--json` emite todo.

## 🌐 Fuentes

**ATS internacionales (auto-sondeo por nombre — 9 sistemas)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Las grandes marcas funcionan con solo el nombre de la empresa (todas verificadas), p. ej.:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Bolsas remotas globales (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**China — 170 empresas (`--local`, portales oficiales, tabla semilla)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (gran manufactura / automotrices / electrodomésticos / maquinaria pesada): Dreame, Chery, Leapmotor, BOE, SANY …
- **Propios**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Lista completa: `python3 hiring_radar.py --list`

## ➕ Añadir empresa = añadir una línea (sin código)

La lista de empresas chinas está en `parsers/companies.seed` (separado por `|`), cargada al inicio. Añade una línea:

```
key | feishu | Empresa | dominio-portal (p. ej. nio.jobs.feishu.cn)
key | moka   | Empresa | orgId | siteId   # ambos en la URL app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | Empresa | slug             # portal {slug}.zhiye.com, p. ej. dreame
```

Para una fuente nueva (escribir un parser), ver [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Señal de industria (secundario)

La contratación es un **indicador anticipado**. Por ejemplo:

- Contratar ingenieros de línea = la línea aún se monta; QA/mantenimiento = preparándose para producción sostenida; turnos de noche = rampa inminente; QA de entrada/calidad de proveedores = incorporación de proveedores externos.
- Usa `--local <empresa> --keyword factory,production,assembly` para el lado de manufactura; `--recent-days` para lo reciente; toma **instantáneas mensuales** de los nombres clave para seguir la tendencia.

> ⚠️ **Contratación ≠ producción.** Las vacantes son "entradas", no "salidas"; rendimiento/rampa/cadena de suministro están en medio. Trátalo como señal, no como consejo de inversión.

## ⚖️ Uso responsable / Cumplimiento

Herramienta **personal / de investigación, local + de código abierto**. Úsala con responsabilidad:

- **Solo vacantes — nunca currículums / datos personales.**
- **Solo endpoints públicos sin login**: si hay muro de login / captcha / anti-bot activo, **no lo eludas**.
- **Solo local**: sin hosting / subida / servidor. Si republicas los datos, evalúa el cumplimiento por tu cuenta.
- **Baja frecuencia, visitante educado**; sin reventa comercial. "Visible públicamente" ≠ "libre para agregar y republicar".

## ⚠️ Aviso legal

1. **Tú controlas tus datos.** Corre en local; no recopila ni sube nada.
2. **Cumples los términos de terceros.** Respeta los ToS de cada plataforma; no hagas spam ni sobrecargues sus sistemas.
3. **Señales, no hechos.** Los datos de contratación son una señal; los juicios de industria/inversión son tu responsabilidad.

Bajo [licencia MIT](LICENSE) "tal cual", sin garantía de ningún tipo.

## 🙋 Autor

**Simon Lin** · Douyin: Simon林 · WeChat: 硅基世纪

Una herramienta local que agrega vacantes oficiales de empresas de todo el mundo y de China. PRs bienvenidos para añadir más empresas / fuentes (ver [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
