#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：京东官方招聘 API → JSON(stdout)。
用法: python3 jd.py [keyword] [pages]   匿名 POST(需 Referer/X-Requested-With)，返回顶层数组。"""
import os
import sys, json, ssl, urllib.request, urllib.parse

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
HEAD = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://zhaopin.jd.com/web/job/job_info_list/3",
    "X-Requested-With": "XMLHttpRequest",
}
API = "https://zhaopin.jd.com/web/job/job_list"


def fetch(keyword="", pages=6, size=50):
    out = []
    for p in range(1, pages + 1):
        form = {"pageIndex": p, "pageSize": size, "jobType": 3}
        if keyword:
            form["keyword"] = keyword
        req = urllib.request.Request(API, data=urllib.parse.urlencode(form).encode(), headers=HEAD)
        d = json.load(urllib.request.urlopen(req, timeout=25, context=CTX))
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
