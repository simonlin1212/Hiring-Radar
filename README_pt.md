<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <b>Português</b> | <a href="README_ru.md">Русский</a> | <a href="README_ar.md">العربية</a></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>Um radar do mercado de trabalho global movido a IA – mapeia vagas abertas no mundo e na China, para procurar emprego, ler sinais setoriais e fazer pesquisa de mercado.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_fontes-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portais-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-suportado-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-s%C3%B3_stdlib-lightgrey.svg" alt="stdlib">
</p>

---

## O que é

**Hiring Radar é uma ferramenta de dados de contratação feita para IA – permite que sua IA (Claude Code / Codex / ChatGPT / qualquer agente) leia as vagas oficiais de empresas do mundo todo e da China.** Ela lê os sistemas de recrutamento (ATS) das empresas e fontes públicas de vagas pelas interfaces públicas delas, e transforma as vagas em **dados estruturados com campos unificados**. Roda localmente; um comando consulta uma empresa, um país ou uma função, **sem conta e sem configuração**.

Três usos:

- 🔎 **Procurar emprego / "quem está contratando?"**: quais empresas contratam agora numa área, em quais cidades, com que salário.
- 📊 **Pesquisa de mercado / oportunidades de produto**: puxar fatias inteiras por país, função e período para ver pelo que o mercado está pagando (novo na v2).
- 📈 **Sinal antecedente setorial / de investimento**: contratações costumam revelar a estratégia meses antes dos resultados. Veja "Sinal setorial" abaixo.

**Grandes marcas globais funcionam só com o nome da empresa**, ex.: NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab, e outras.

**Novo na v2**: 24 ATS e um diretório de cerca de 90 mil empresas (descubra pelo nome qual sistema uma empresa usa) · 12 fontes multiempresa (incluindo o agregador freehire e os bancos de vagas públicos da Suécia, de Singapura e da Alemanha) · deduplicação entre fontes e marcação de agências · faixas por idade da publicação · execuções retomáveis · instantâneos locais para ver vagas novas/removidas · um **servidor MCP** que seu assistente de IA chama diretamente.

> ⚠️ Lê apenas **vagas que as próprias empresas publicam** – nunca currículos ou dados pessoais, nunca conteúdo atrás de login, e para em qualquer verificação anti-robô. Veja "Uso responsável" abaixo.

## Recursos

| Recurso | O que faz |
|---|---|
| **Por empresa** | Basta o nome: consulta primeiro o diretório (~90 mil empresas em 24 ATS) e, se não achar, tenta os sistemas comuns; ou fixe com `--ats sistema slug` |
| **Multiempresa** | `--board` por país / palavra-chave / últimos N dias: freehire, busca geral do Workable, bancos públicos, sites de vagas remotas; várias fontes de uma vez, deduplicadas |
| **Idade** | Cada vaga recebe 0-3 meses / 3-6 meses / mais de 6 meses / sem data; `--board` mostra por padrão os últimos seis meses |
| **Agências** | Marca vagas publicadas por headhunters ou agências de trabalho temporário (campo `agency`); `--no-agency` remove |
| **Retomável** | Se uma fonte for limitada ou falhar, as outras seguem; o mesmo comando com `--resume` completa só o que falta |
| **Instantâneos locais** | `--save` grava num SQLite local com datas de primeira/última vez vista; `--history` mostra entradas e saídas por execução |
| **Servidor MCP** | `--mcp`: Claude Code / Codex etc. chamam diretamente (empresa, busca de vagas, diretório) |
| **China: 170 empresas** | `--local`: três analisadores universais (Feishu Hire / Moka / Beisen) + 6 portais próprios de grandes empresas de tecnologia |
| **Plugins privados** | Fontes cujos termos não combinam com distribuição pública ficam na sua própria pasta (`--plugins`), fora do repositório |
| **Só stdlib** | Zero dependências (só o analisador Moka precisa de `pycryptodome`); roda em qualquer `python3` |

## Início rápido

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # baixar o diretório (~90 mil empresas, guardado localmente; opcional, recomendado)
python3 hiring_radar.py --list               # listar todas as fontes
```

```bash
# 1) Por empresa: basta o nome
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # achado no diretório → usa o sistema certo
python3 hiring_radar.py --find xero                  # só mostrar qual ATS ela usa
python3 hiring_radar.py --ats teamtailor <slug>      # fixar sistema e conta
python3 hiring_radar.py --workday host,tenant,site

# 2) Multiempresa: país + palavra-chave + período
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country BR --max 0 --json > br.json   # sem limite
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # banco público da Suécia
python3 hiring_radar.py --board all --keyword "AI engineer"                              # os 4 sites de vagas remotas

# 3) Retomar após interrupção / instantâneos
python3 hiring_radar.py --board freehire --country AU --max 0 --resume
python3 hiring_radar.py anthropic --save          # a próxima execução mostra vagas novas/removidas
python3 hiring_radar.py --history

# 4) Empresas chinesas
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka; pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (portal próprio)
```

**Opções comuns**: `--keyword a,b` (qualquer uma) · `--recent-days N` (0 = sem limite) · `--country AU,NZ` · `--max N` (limite por fonte, padrão 1000, 0 = sem limite) · `--no-agency` · `--json` · `--limit N` · `--debug`

**Variáveis de ambiente**: `HIRING_RADAR_HOME` (diretório, instantâneos e estado de retomada; padrão `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (segundos mínimos entre duas requisições ao mesmo site; padrão 0,3) · `HIRING_RADAR_PLUGINS` (pasta de plugins privados) · `HIRING_RADAR_INSECURE=1` (desliga a verificação de certificados, só atrás de proxy interceptador)

Códigos de saída: `0` ok; `3` alguma fonte não terminou (o que foi obtido é exibido mesmo assim; use `--resume`).

## Para assistentes de IA (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

Cinco ferramentas: `company_jobs` (uma empresa) · `search_jobs` (multiempresa) · `find_company` (diretório) · `list_sources` · `job_history`. As descrições são cortadas em 800 caracteres nos resultados MCP; o texto completo sai pela linha de comando com `--json`.

## Campos de saída

Os 15 campos da v1 continuam: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (salário) · jd (completa) · url · apply_url · id`

A v2 acrescenta 9: `country` (código do país) · `source` (fonte) · `age` (faixa 0-3m/3-6m/6m+/unknown) · `agency` (termo de agência encontrado) · `also` (outras fontes com a mesma vaga, após deduplicar) · `industry` · `size` (porte da empresa, se a fonte informar) · `first_seen` · `last_seen` (só com instantâneos)

Envelope `--json`: `source · total · matched · jobs` (como na v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## Como funciona

```
Nome da empresa / país + palavra-chave
        │
        ▼
┌─────────────────────────┐
│ Escolher fontes          │  Por empresa: diretório → interfaces públicas de 24 ATS
│                         │  Multiempresa: freehire / Workable / bancos públicos / remoto / plugins
│                         │  China: Feishu / Moka / Beisen / portais próprios
└──────────┬──────────────┘
           │  Rede: identidade honesta, ritmo por site, espera no 429, parada no 403 ou anti-robô
┌──────────▼──────────────┐
│ 24 campos + idade        │  Filtros palavra-chave / país / últimos N dias; deduplicação; marcação de agências
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (completo)  Instantâneos / MCP
```

## Fontes

**Por empresa: 24 ATS** (diretório do [openroles](https://github.com/datascry/openroles), baixado localmente na execução, não incluído no repositório)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**Fontes multiempresa `--board` (12)**

| Fonte | Cobertura | Observações |
|---|---|---|
| `freehire` | Mundial (diz ter ~3,3 milhões de vagas abertas) | API pública do [freehire](https://github.com/strelov1/freehire), agrega 225 fontes, descrições completas, filtros por país / palavra-chave / últimos N dias |
| `workable` | Mundial | Busca geral do Workable, filtros por país / palavra-chave |
| `jobtech` | Suécia | Dados abertos do serviço público de emprego sueco, descrições completas |
| `mycareersfuture` | Singapura | Portal de empregos do governo de Singapura, com salário, sem descrição |
| `arbeitsagentur` | Alemanha | Agência Federal de Emprego alemã, sem descrição |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | Remoto | `--board all` = esses 4 |
| `reed` · `adzuna` · `usajobs` | Reino Unido / 19 países / governo federal dos EUA | Exigem suas próprias chaves gratuitas (`REED_API_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`+`USAJOBS_EMAIL`); escritas a partir da documentação oficial, sem teste real pelo mantenedor |

**China: 170 empresas (`--local`)**: Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · portais próprios (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). Lista completa: `--list`.

**Não suportado / limites conhecidos**
- **Paycom**: o robots.txt dela não libera a lista de vagas, então não é lida.
- **iCIMS**: o `datePosted` das páginas é gerado pelo sistema (hora atual menos dois anos); esta ferramenta usa a data de atualização do sitemap. Cuidado com datas de publicação do iCIMS coletadas por outras ferramentas.
- O diretório tem muitas contas inativas – achar uma empresa sem vagas é normal; empresas homônimas podem colidir – com várias correspondências, todos os candidatos são listados.
- A deduplicação é por país + empresa + título: o mesmo título de uma empresa em várias cidades de um país vira uma linha só.

> **Sobre a Moka (nota honesta)**: as interfaces da Moka aplicam uma leve ofuscação no front-end (AES-128-CBC, com chave e IV distribuídos no front-end público). A ferramenta usa esses valores públicos para obter exatamente a lista pública de vagas que um navegador mostra – sem quebrar login nem contornar autenticação. A rigor, "reproduz o processamento do front-end", um pouco mais cinzento que ler JSON puro; só para pesquisa local, por sua conta e risco. Para a postura mais limpa, apague todas as linhas `moka` de `parsers/companies.seed` e as linhas embutidas `yostar`/`tesla-cn` em `radar/local.py`.

## Plugins privados

Para grandes plataformas cujos termos não combinam com publicar código de coleta, escreva seu próprio plugin fora do repositório:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

Cada arquivo `.py` da pasta que não começa com `_` é uma fonte e define `NAME`, `DESC`, `FILTERS` e `pages(q, state=None)` (mesma interface de `radar/boards/`); arquivos que começam com `_` podem guardar código compartilhado. Os plugins rodam com as suas permissões e a responsabilidade pelos termos dos sites visitados é sua.

## Adicionar uma empresa = adicionar uma linha (China)

A lista de empresas chinesas é `parsers/companies.seed` (separada por `|`); uma empresa = uma linha:

```
key | feishu | nome | domínio do portal (ex.: nio.jobs.feishu.cn)
key | moka   | nome | orgId | siteId
key | beisen | nome | slug
```

Para adicionar um ATS ou uma fonte multiempresa, veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Sinal setorial

Contratação é um **indicador antecedente**: onde uma empresa se expande, em que direção e em que fase costuma aparecer meses antes dos resultados. Contratar engenheiros de linha = a linha está sendo montada; contratar qualidade/manutenção = produção contínua em preparação; contratar turno da noite = aumento de volume próximo. Use `--save` para instantâneos regulares e `--history` para ver o ritmo.

> ⚠️ **Contratação ≠ produção**: vagas são insumos, não resultados; "contratando" também pode ser banco de talentos ou um contrassinal. Trate as conclusões como sinais, não como recomendação de investimento.

## Estrutura do projeto

```
Hiring-Radar/
├── hiring_radar.py     # entrada de linha de comando (uso da v1 inalterado)
├── radar/              # pacote principal
│   ├── http.py         # rede: identidade honesta, ritmo, espera, parada se bloqueado
│   ├── schema.py       # campos unificados, datas, faixas de idade
│   ├── ats/            # por empresa: um arquivo por ATS
│   ├── boards/         # fontes multiempresa
│   ├── directory.py    # diretório de empresas (baixado na execução)
│   ├── process.py      # deduplicação, marcação de agências
│   ├── sweep.py        # coleta multifonte, retomada
│   ├── store.py        # instantâneos locais (SQLite)
│   ├── local.py        # analisadores da China / portais próprios
│   ├── plugins.py      # carregador de plugins privados
│   └── mcp.py          # servidor MCP
├── parsers/            # analisadores da China / portais próprios + companies.seed
├── tests/              # smoke_test.py · test_offline.py (offline, sem rede)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## Tecnologia e dependências

- **Python 3.8+**, núcleo só com a biblioteca padrão (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: só para os analisadores Moka (`pip install pycryptodome`)
- Precisa de internet (alguns sites internacionais podem exigir proxy); certificados SSL verificados por padrão; atrás de proxy interceptador, defina `HIRING_RADAR_INSECURE=1`

## Uso responsável / conformidade

Uma ferramenta **pessoal / de pesquisa, local e de código aberto**. Use com responsabilidade:

- **Só vagas de emprego – nunca currículos / dados pessoais** (dados pessoais acionam a PIPL chinesa – não faça).
- **Só interfaces públicas sem login**: barreira de login / captcha / anti-robô ativo **não são contornados**; um 403 ou página de verificação encerra a execução; sem pools de proxy, sem impressão digital de navegador falsificada.
- **Identidade honesta, baixa frequência**: o User-Agent informa HiringRadar e a URL do projeto; por padrão 0,3 segundo entre duas requisições ao mesmo site; no 429 espera o que for pedido e, se continuar falhando, para e aguarda seu `--resume`. O robots.txt é verificado antes de adicionar uma fonte (por isso não há Paycom).
- **Chaves só em variáveis de ambiente**: fontes com chave a leem do ambiente, e as chaves são mascaradas nas mensagens de erro.
- **Só local**: sem hospedagem / upload / servidor; os dados ficam na sua máquina. Se republicar os dados, avalie você mesmo a conformidade; sem revenda comercial. O diretório de empresas é CC BY-SA 4.0 – redistribuir exige atribuição e a mesma licença (veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- "Visível publicamente" ≠ "livre para agregar e republicar" – raspagem em massa com republicação pode configurar concorrência desleal em muitas jurisdições (incluindo a jurisprudência chinesa).

## Aviso legal

1. **Você controla seus dados.** A ferramenta roda localmente; não coleta nem envia nada.
2. **Você cumpre os termos de terceiros.** Siga os termos de cada plataforma; não use para assediar empregadores nem sobrecarregar seus sistemas.
3. **Sinais, não fatos.** Dados de contratação são sinal; decisões setoriais ou de investimento são sua responsabilidade.

Fornecido sob a [licença MIT](LICENSE) "no estado em que se encontra", sem garantia de qualquer tipo. Código e dados de terceiros: veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

PRs para adicionar empresas / fontes são bem-vindos (veja [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
