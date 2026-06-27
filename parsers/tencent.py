#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：腾讯官方招聘 API → JSON(stdout)。
用法: python3 tencent.py [keyword] [pages]   端点匿名 GET，字段六项全。"""
import os
import sys, json, ssl, urllib.request, urllib.parse

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch(keyword="", pages=6, size=100):
    out = []
    for p in range(1, pages + 1):
        q = urllib.parse.urlencode({"keyword": keyword, "pageIndex": p, "pageSize": size, "language": "zh-cn"})
        url = f"https://careers.tencent.com/tencentcareer/api/post/Query?{q}"
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=CTX))
        posts = ((d.get("Data") or {}).get("Posts")) or []
        if not posts:
            break
        for j in posts:
            out.append({
                "title": j.get("RecruitPostName", ""),
                "company": "腾讯",
                "location": j.get("LocationName", ""),
                "dept": j.get("CategoryName", "") or j.get("BGName", ""),
                "date": j.get("LastUpdateTime", ""),
                "jd": j.get("Responsibility", ""),
                "url": j.get("PostURL", ""),
                "id": str(j.get("PostId", "")),
            })
        if len(posts) < size or len(out) >= ((d.get("Data") or {}).get("Count") or 0):
            break
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
