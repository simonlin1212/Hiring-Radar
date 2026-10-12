#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘雷达 (Hiring Radar) — 读公司自己的招聘系统(ATS)和公开职位来源，输出统一字段的在招岗位。

v2 起代码在 radar/ 包里，本文件只是入口：v1 的全部用法和输出不变，直接 python3 hiring_radar.py … 即可。

用法（详见 README）:
  hiring_radar.py figure                              # 按公司名：内置 → 公司名录 → 猜 slug
  hiring_radar.py nvidia --keyword HBM,packaging      # 关键词过滤
  hiring_radar.py --greenhouse <slug> / --ats teamtailor <slug> / --workday host,tenant,site [--jd]
  hiring_radar.py --board all --keyword robotics      # 4 个远程板
  hiring_radar.py --board freehire,workable --country AU,NZ --keyword receptionist --json   # 整片拉取+去重
  hiring_radar.py --directory-update ; hiring_radar.py --find atlassian                    # 公司名录
  hiring_radar.py --local tencent                     # 中国/自建招聘页
  hiring_radar.py --mcp                               # MCP 服务（给 Claude / Codex 调用）

只读公开、免登录的接口；遇到登录墙、验证码、主动反爬不绕过；被限流就退避，仍不行就停下并说明。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from radar import __version__, ats, boards, local  # noqa: E402
from radar.cli import COMPANIES, main  # noqa: E402
from radar.schema import FIELDS  # noqa: E402

# ---- v1 兼容名（老脚本 import hiring_radar 时仍可用）----
LOCAL_PARSERS = local.LOCAL_PARSERS
PARSER_ROOT = local.PARSER_ROOT
BOARDS = boards.BOARDS
_load_company_seeds = local.load_company_seeds
fetch_local = local.fetch_local


def _ats(kind):
    return lambda slug: ats.fetch(kind, slug)


fetch_greenhouse, fetch_ashby, fetch_lever = _ats("greenhouse"), _ats("ashby"), _ats("lever")
fetch_smartrecruiters, fetch_recruitee, fetch_breezy = _ats("smartrecruiters"), _ats("recruitee"), _ats("breezy")
fetch_bamboohr, fetch_personio = _ats("bamboohr"), _ats("personio")
fetch_workday = ats.workday.fetch_board

if __name__ == "__main__":
    main()
