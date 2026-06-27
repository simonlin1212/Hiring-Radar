# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Português** · [Русский](README.ru.md) · [العربية](README.ar.md)

<p align="center">
  <b>Um radar com IA para o mercado de trabalho global — varre vagas do mundo todo e da China, para busca de emprego e captação de sinais de indústria.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portais-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-só_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## O que é isto

**Hiring Radar é uma ferramenta de dados de recrutamento nativa de IA — dá à sua IA (Claude Code / ChatGPT / qualquer agente) a capacidade de ler as vagas oficiais de empresas do mundo todo + China.** Ela lê diretamente os endpoints públicos dos sistemas de gestão de candidaturas (ATS) que as empresas usam e agrega as vagas em **dados estruturados** para alimentar sua IA. Não é mais um site de empregos que exige cadastro: roda localmente, e um único comando consulta qualquer empresa do mundo, um setor inteiro, ou varre várias empresas, **sem conta e sem configuração**.

Os ATS usados pelas empresas (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) expõem **os mesmos endpoints JSON públicos que seus próprios frontends chamam**, com descrição completa da vaga, departamento, local, data de publicação e salário. O Hiring Radar lê exatamente esses endpoints públicos: rápido, limpo e pronto para alimentar uma IA.

Dois usos:

- 🔎 **Busca de emprego / "onde se contrata" (principal)**: quais empresas contratam agora em um setor, em quais cidades, com qual salário.
- 📈 **Sinal antecipado de indústria / investimento (secundário)**: a contratação costuma revelar a estratégia meses antes dos resultados financeiros. Veja [Sinal de indústria](#-sinal-de-indústria-secundário).

Cobertura: **9 grandes ATS internacionais + 4 plataformas globais de trabalho remoto + 170 portais oficiais de empresas chinesas**. A cobertura da China (parsers universais de Feishu Hire / Moka / Beisen + portais próprios de Tencent/NetEase/JD/Baidu/ByteDance/Unitree) é a lacuna que a maioria das ferramentas existentes deixa em aberto.

**Grandes marcas internacionais funcionam só com o nome da empresa**, p. ex. NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, e mais.

> ⚠️ Lê **vagas que as empresas publicam por conta própria** — nunca currículos/dados pessoais, nunca conteúdo atrás de login. Uso próprio, baixa frequência, visitante educado. Veja [Uso responsável](#-uso-responsável--conformidade).

## ✨ Recursos

| Recurso | Descrição |
|---|---|
| **Por empresa (internacional)** | Um nome de empresa basta para auto-sondar 8 ATS (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio); em acerto: JD completa + departamento + local + data + salário |
| **Boards remotos globais** | `--board` varre várias empresas: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **170 empresas chinesas** | `--local`: parsers **universais** de Feishu Hire / Moka / Beisen (adicionar empresa = adicionar uma linha) + 6 portais próprios. IA incorporada / LLM / semicondutores / automotivas / energia / quant / multinacionais / games |
| **Filtro por palavra-chave / recência** | `--keyword a,b,c` (vírgula = OU; busca título/departamento/local/JD/salário) · `--recent-days N` |
| **Saída estruturada unificada** | Esquema de 15 campos; `--json` emite tudo (incl. JD completa) para alimentar IA |
| **Resumo no terminal** | Por padrão top de empresas / departamentos / locais + lista de vagas |
| **Orientado a dados** | A lista de empresas chinesas é uma tabela semente `companies.seed` — **adicionar empresa = uma linha, sem código** |
| **Só stdlib** | Script de ponto de entrada único, zero dependências (só Moka precisa de `pycryptodome`), roda em qualquer `python3` |

## 🚀 Início rápido

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # opcional, só para empresas chinesas com Moka

python3 hiring_radar.py --list             # lista todas as empresas / boards consultáveis
```

```bash
# 1) Internacional: basta o nome da empresa (figure/1x/anthropic/openai/scale/nvidia integrados) ou auto-sonde qualquer um
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # ATS explícito
python3 hiring_radar.py --workday host,tenant,site

# 2) China: --local <key> (keys via --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (próprio)

# 3) Boards: "onde se contrata" entre empresas
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) Saída estruturada completa (com JD completa) para análise
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**Opções comuns**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 Campos de saída

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(salário) · jd(completa) · url · apply_url · id` (15 campos)

GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu geralmente incluem JD completa; Workday e alguns tenants Moka são só a nível de lista (título/departamento/local/data). `--json` emite tudo.

## 🌐 Fontes

**ATS internacionais (auto-sondagem por nome — 9 sistemas)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

Grandes marcas funcionam só com o nome da empresa (todas verificadas), p. ex.:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**Boards remotos globais (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**China — 170 empresas (`--local`, portais oficiais, tabela semente)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (grande indústria / automotivas / eletrodomésticos / máquinas pesadas): Dreame, Chery, Leapmotor, BOE, SANY …
- **Próprios**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> Lista completa: `python3 hiring_radar.py --list`

## ➕ Adicionar empresa = adicionar uma linha (sem código)

A lista de empresas chinesas está em `parsers/companies.seed` (separado por `|`), carregada na inicialização. Adicione uma linha:

```
key | feishu | Empresa | domínio-portal (p. ex. nio.jobs.feishu.cn)
key | moka   | Empresa | orgId | siteId   # ambos na URL app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | Empresa | slug             # portal {slug}.zhiye.com, p. ex. dreame
```

Para uma fonte totalmente nova (escrever um parser), veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 Sinal de indústria (secundário)

A contratação é um **indicador antecipado**. Por exemplo:

- Contratar engenheiros de linha = linha ainda em montagem; QA/manutenção = preparando produção contínua; turnos noturnos = ramp-up iminente; QA de entrada/qualidade de fornecedores = onboarding de fornecedores externos.
- Use `--local <empresa> --keyword factory,production,assembly` para o lado fabril; `--recent-days` para o recente; tire **snapshots mensais** dos nomes-chave para acompanhar a tendência.

> ⚠️ **Contratação ≠ produção.** Vagas são "entradas", não "saídas"; rendimento/ramp-up/cadeia de suprimentos estão no meio. Trate como sinal, não como conselho de investimento.

## ⚖️ Uso responsável / Conformidade

Ferramenta **pessoal / de pesquisa, local + open source**. Use com responsabilidade:

- **Só vagas — nunca currículos / dados pessoais.**
- **Só endpoints públicos sem login**: se houver muro de login / captcha / anti-bot ativo, **não burle**.
- **Só local**: sem hosting / upload / servidor. Se republicar os dados, avalie a conformidade por conta própria.
- **Baixa frequência, visitante educado**; sem revenda comercial. "Visível publicamente" ≠ "livre para agregar e republicar".

## ⚠️ Aviso legal

1. **Você controla seus dados.** Roda localmente; não coleta nem envia nada.
2. **Você cumpre os termos de terceiros.** Respeite os ToS de cada plataforma; sem spam ou sobrecarga.
3. **Sinais, não fatos.** Dados de contratação são um sinal; julgamentos de indústria/investimento são de sua responsabilidade.

Sob [licença MIT](LICENSE) "como está", sem garantia de qualquer tipo.

## 🙋 Autor

**Simon Lin** · Douyin: Simon林 · WeChat: 硅基世纪

Uma ferramenta local que agrega vagas oficiais de empresas do mundo todo e da China. PRs bem-vindos para adicionar mais empresas / fontes (veja [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
