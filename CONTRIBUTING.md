# 贡献指南 / Contributing

欢迎补充更多公司、修接口。两类常见贡献：

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

## 2. 写一个新 parser（接一个新数据源）

在 `parsers/` 下放一个脚本，它负责抓取、把岗位以 **JSON 数组**打到 **stdout**，本工具负责过滤/聚合/输出（取数与分析解耦）。

- **输出格式**：`[{...}, {...}]` 或 `{"jobs": [...]}`。每条岗位 key 名灵活（会自动归一化），尽量含：
  `title`(必需) · `company` · `location` · `dept` · `date` · `jd` · `url` · `id` · `comp`(薪资)
- **入参**：脚本可接收命令行参数；注册时 `{keyword}` 会被替换成用户的首个关键词传入。
- **注册**：
  - 通用型（一个脚本覆盖多家，如 feishu/moka）→ 走 `companies.seed`。
  - 单站型（一家一个，如腾讯/网易）→ 在 `hiring_radar.py` 的 `LOCAL_PARSERS` 加一行 `"key": {"command":"python3","args":["parsers/xxx.py","{keyword}"]}`。
- **参考实现**：`parsers/tencent.py`（最简单的单站 JSON）、`parsers/feishu.py`（通用型 + 自动探测）、`parsers/moka.py`（带解密的通用型）。

## 代码与合规

- 纯标准库优先（Moka 解密用 `pycryptodome`）。SSL 默认验证证书；拦截式代理可设 `HIRING_RADAR_INSECURE=1`。
- **只接「门开着」的公开接口**：不接需登录/验证码/主动反爬的来源。只读岗位信息，**不抓个人简历**。
- 详见 README 的"使用边界"。

## 自测

```bash
python3 tests/smoke_test.py      # 离线烟测：编译 + 注册表加载
```
