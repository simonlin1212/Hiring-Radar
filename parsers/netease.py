#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：网易官方招聘 API → JSON(stdout)。
用法: python3 netease.py [keyword] [pages]   匿名 POST JSON，字段六项全。"""
import os
import sys, json, ssl, urllib.request

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
HEAD = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "Content-Type": "application/json"}
API = "https://hr.163.com/api/hr163/position/queryPage"


def fetch(keyword="", pages=6, size=50):
    out = []
    for p in range(1, pages + 1):
        body = {"currentPage": p, "pageSize": size, "keyword": keyword}
        req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=HEAD)
        d = json.load(urllib.request.urlopen(req, timeout=25, context=CTX))
        data = d.get("data") or {}
        rows = data.get("list") or []
        if not rows:
            break
        for j in rows:
            jid = str(j.get("id", ""))
            jd = "\n\n".join(x for x in [j.get("description", ""), j.get("requirement", "")] if x)
            out.append({
                "title": j.get("name", ""),
                "company": "网易",
                "location": ", ".join(j.get("workPlaceNameList") or []),
                "dept": j.get("firstDepName", "") or j.get("firstPostTypeName", ""),
                "date": j.get("updateTime", ""),   # epoch ms
                "jd": jd,
                "url": f"https://hr.163.com/position/detail?id={jid}",
                "id": jid,
            })
        if len(out) >= (data.get("total") or 0):
            break
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
