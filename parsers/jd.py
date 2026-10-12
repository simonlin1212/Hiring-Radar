#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：京东官方招聘 API → JSON(stdout)。
用法: python3 jd.py [keyword] [pages]   匿名 POST(需 Referer/X-Requested-With)，返回顶层数组。"""
import os
import sys, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 仓库根目录
from radar.http import post_form  # noqa: E402  统一联网：如实报身份、限速、429 退避、被拦就停
HEAD = {"Referer": "https://zhaopin.jd.com/web/job/job_info_list/3", "X-Requested-With": "XMLHttpRequest"}
API = "https://zhaopin.jd.com/web/job/job_list"


def fetch(keyword="", pages=6, size=50):
    out = []
    for p in range(1, pages + 1):
        form = {"pageIndex": p, "pageSize": size, "jobType": 3}
        if keyword:
            form["keyword"] = keyword
        d = post_form(API, form, headers=HEAD)
        rows = d if isinstance(d, list) else (d.get("data") or d.get("list") or [])
        if not rows:
            break
        for j in rows:
            pid = str(j.get("positionId", ""))
            out.append({
                "title": j.get("positionName", ""),
                "company": "京东",
                "location": j.get("workCity", ""),
                "dept": j.get("positionDeptName", ""),
                "date": j.get("formatPublishTime", "") or j.get("publishTime", ""),
                "jd": j.get("qualification", "") or j.get("workContent", ""),
                "url": f"https://zhaopin.jd.com/web/job/job_detail/{pid}",
                "id": pid,
            })
        if len(rows) < size:
            break
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
