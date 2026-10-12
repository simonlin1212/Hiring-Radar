"""Hiring Radar 核心包。命令行入口是仓库根目录的 hiring_radar.py。

模块分工：
  http       联网（重试、限流退避、被拦就停）
  schema     统一字段、日期、时间分档
  ats/       按公司查：每个招聘系统(ATS)一个文件
  boards/    跨公司：聚合板、开放数据、freehire、Workable 搜索
  directory  公司名录（openroles，运行时下载）
  process    去重、标中介
  store      本地存档（SQLite，记首次/最近看到）
  sweep      多来源整片拉取（可断点续跑）
  local      中国/自建站本地解析器
  plugins    私有插件（不进仓库的来源）
  mcp        MCP 服务（给 Claude / Codex 等直接调用）
"""
__version__ = "2.0.0"
