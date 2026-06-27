# Changelog

本项目遵循语义化版本。日期为发布日。

## [1.1.0] - 2026-06-27

首个开源版本。

### 数据源
- **全球 9 大 ATS**：Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio（给公司名 auto-probe 8 个 ATS）。
- **4 个全球远程聚合板**：RemoteOK · Remotive · WeWorkRemotely · WorkingNomads（`--board`，跨公司）。
- **中国 170 家企业官方门户**：飞书招聘 / Moka / 北森 三套通用解析 + 腾讯/网易/京东/百度/字节/宇树 自建（`--local`，数据驱动种子表 `companies.seed`）。北森系覆盖大型制造/车企/家电/装备巨头（追觅/奇瑞/零跑/京东方/三一…），是产业信号的重要补充。

### 功能
- 统一 15 字段 schema；`--json` 出全量（含完整 JD）；终端摘要按 公司/部门/地点 Top 聚合。
- `--keyword`（逗号 OR，搜标题/部门/地点/JD/薪资）· `--recent-days` · `--limit` · `--list` · `--debug` · `--version`。
- 加公司 = 往 `companies.seed` 加一行，零代码。

### 安全 / 合规
- SSL 默认验证证书（`HIRING_RADAR_INSECURE=1` 可在拦截式代理下关闭）。
- local-parser 机制带安全护栏：解释器白名单 + 路径逃逸防护 + 参数注入防护 + 不用 shell。
- 定位：个人 / 研究自用；只读公开岗位、不抓个人简历、不做公开聚合再分发（见 README「使用边界」）。
