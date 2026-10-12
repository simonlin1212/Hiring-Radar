# 贡献指南 / Contributing

欢迎补充更多公司、修接口、接新来源。四类常见贡献：

## 1. 加一家中国公司（零代码，改数据即可）

编辑 `parsers/companies.seed`，加一行（管道 `|` 分隔，`#` 开头为注释）：

```
key | feishu | 公司名 | 门户域名
key | moka   | 公司名 | orgId | siteId
key | beisen | 公司名 | slug
```

- **飞书招聘**：门户域名形如 `{slug}.jobs.feishu.cn`。怎么找：搜公司「飞书招聘」或在其官网"招聘"链接里看跳转域名（slug 可能是随机串，必须实际找到，不能猜）。`website-path` 程序会自动探测；门户不在根路径时写成 `域名/path`（如 `xxx.jobs.feishu.cn/870797`）。
- **Moka 摩卡**：`orgId` + `siteId` 都在社招页 URL `https://app.mokahr.com/social-recruitment/{orgId}/{siteId}` 里。
- **北森 i-Talent**：门户 `{slug}.zhiye.com`，slug 多为公司英文名（dreame/chery/leapmotor…）。验真：`curl -s -o /dev/null -w '%{http_code}' https://{slug}.zhiye.com/` 非 404 即在网。**大型制造业/车企/家电/装备巨头多在北森**。

加完用 `python3 hiring_radar.py --local <key> --limit 5` 自测能返回岗位即可。

## 2. 写一个新 parser（中国 / 自建招聘站）

在 `parsers/` 下放一个脚本，它负责抓取、把岗位以 **JSON 数组**打到 **stdout**，本工具负责过滤/聚合/输出（取数与分析解耦）。

- **输出格式**：`[{...}, {...}]` 或 `{"jobs": [...]}`。每条岗位 key 名灵活（会自动归一化），尽量含：
  `title`(必需) · `company` · `location` · `dept` · `date` · `jd` · `url` · `id` · `comp`(薪资)
- **入参**：脚本可接收命令行参数；注册时 `{keyword}` 会被替换成用户的首个关键词传入。
- **注册**：
  - 通用型（一个脚本覆盖多家，如 feishu/moka）→ 走 `companies.seed`。
  - 单站型（一家一个，如腾讯/网易）→ 在 `radar/local.py` 的 `LOCAL_PARSERS` 加一行 `"key": {"command":"python3","args":["parsers/xxx.py","{keyword}"]}`。
- **联网**：用 `radar.http` 的 `get_json` / `get_text` / `post_json` / `post_form`（参考现有脚本开头的 import），不要自己用 `urllib`，也不要设浏览器 User-Agent（飞书招聘、字节跳动是仅有的例外，接口不接受程序身份；USAJobs 按官方要求用申请密钥的邮箱作 User-Agent）。目标网站拒绝访问时，抛 `Blocked` 停下。
- **参考实现**：`parsers/tencent.py`（最简单的单站 JSON）、`parsers/feishu.py`（通用型 + 自动探测）、`parsers/moka.py`（带解密的通用型）。

## 3. 接一个新的招聘系统（ATS，按公司查）

在 `radar/ats/` 加 `xxx.py`，实现 `fetch(slug, meta=None) -> (items, source)`：

- `items` 每条用 `radar.schema.rec(...)` 生成（统一 24 字段，没有的留空）；日期用 `iso_day()` 转成 `YYYY-MM-DD`，HTML 用 `strip_html()` 转纯文本。
- `source` 写成 `xxx/{slug}`。
- 联网一律用 `radar.http` 的 `get_json` / `get_text` / `post_json` / `post_form`：它们负责如实报身份、限速、429 退避、403/人机验证就停。不要自己用 `urllib`。
- `slug` 已由 `check_slug` 校验过（单段字母数字）；`meta` 来自公司名录（如 Workday 的 host/site）。meta 里的域名、编号**必须先用正则校验**再拼进 URL，防止把请求改写到别的网站（SSRF）。
- 页面有 schema.org `JobPosting` 的，可直接用 `radar/ats/_jsonld.py`。

然后在 `radar/ats/__init__.py` 的 import 和 `REGISTRY` 各加一行；如果 openroles 名录收录了这个系统，再把名字加进 `radar/directory.py` 的 `PREFER`，`--directory-update` 就会下载它的公司名单。

## 4. 接一个跨公司来源（`--board`）

在 `radar/boards/` 加 `xxx.py`，定义：

```python
NAME = "xxx"                      # --board 用的名字
DESC = "一句话说明"
FILTERS = {"keyword", "country", "recent_days"}   # 服务端能过滤的子集；不支持的由 sweep 在本地补过滤

def pages(q, state=None):         # q 是 boards.Query：keywords / countries / recent_days / max_items
    ...
    yield items, next_state       # 每拉一页 yield 一次；next_state 可 JSON 序列化，传回能从断点继续（--resume）
```

- 一次返回全部的简单来源，可写 `fetch()` 再用 `pages = single_page(fetch)` 包一下（参考 `remotive.py`）。
- 只覆盖一个国家的来源，`q.countries` 不含该国时直接返回（参考 `jobtech.py`）。
- 上游翻页有上限、拿不全时，调用 `q.truncate("说明")`：结果会标成不全（退出码 3），提示用户缩小查询（参考 `freehire.py`）。
- 需要密钥的来源，用 `radar/boards/_keys.py` 的 `need()` 从环境变量读，并在 `boards/__init__.py` 的 `NEEDS_KEY` 登记。密钥不要写进日志或报错信息；`radar.http.safe()` 会给 URL 里常见的密钥参数打码。
- 在 `boards/__init__.py` 的 import 和 `BOARDS` 各加一行。

**条款不适合公开分发的来源**（大型招聘平台等）不要提交到本仓库，写成私有插件：放在你自己的目录，接口同上，用 `--plugins 目录` 或 `HIRING_RADAR_PLUGINS` 加载；目录里以 `_` 开头的文件可放共用代码。

## 代码与合规

- 纯标准库优先（Moka 解密用 `pycryptodome`）。SSL 默认验证证书；拦截式代理可设 `HIRING_RADAR_INSECURE=1`。
- **只接「门开着」的公开接口**：不接需登录/验证码/主动反爬的来源；不用代理池、不伪装浏览器指纹。只读岗位信息，**不抓个人简历**。
- 加新来源前先看它的 robots.txt 和使用条款；不放行的就不接（例：Paycom）。
- 详见 README 的"使用边界"。

## 自测

```bash
python3 tests/smoke_test.py      # 离线烟测：编译 + 注册表加载
python3 tests/test_offline.py    # 离线单元测试：字段映射、去重、时间分档、密钥打码、MCP 协议等
```

新来源请在 `tests/test_offline.py` 里加一个用本地样例数据的映射测试（不联网），并在 PR 里写明用哪家真实公司或哪个查询实测过。
