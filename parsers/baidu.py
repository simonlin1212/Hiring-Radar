#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：百度官方招聘 API → JSON(stdout)。
用法: python3 baidu.py [keyword] [pages]   匿名 POST(必须带 Referer)，recruitType=SOCIAL。"""
import os
import sys, json, ssl, urllib.request, urllib.parse

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
HEAD = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://talent.baidu.com/jobs/social",
}
API = "https://talent.baidu.com/httservice/getPostListNew"


def fetch(keyword="", pages=10, size=10):  # 百度 pageSize 只接受小值(>20 报 Illegal argument)
    size = min(size, 20)  # 上限保护：百度 pageSize > 20 直接报错
    out = []
    for p in range(1, pages + 1):
        form = {"recruitType": "SOCIAL", "pageSize": size, "keyWord": keyword, "curPage": p}
        req = urllib.request.Request(API, data=urllib.parse.urlencode(form).encode(), headers=HEAD)
        d = json.load(urllib.request.urlopen(req, timeout=25, context=CTX))
        data = d.get("data") or {}
        rows = data.get("list") or []
        if not rows:
            break
        for j in rows:
            pid = str(j.get("postId", ""))
            jd = "\n\n".join(x for x in [j.get("workContent", ""), j.get("serviceCondition", "")] if x)
            out.append({
                "title": j.get("name", ""),
                "company": "百度",
                "location": j.get("workPlace", ""),
                "dept": j.get("orgName", "") or j.get("bgShortName", ""),
                "date": j.get("publishDate", "") or j.get("updateDate", ""),
                "jd": jd,
                "url": f"https://talent.baidu.com/jobs/social-detail/{pid}",
                "id": pid,
            })
        if len(out) >= int(data.get("total") or 0):
            break
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
