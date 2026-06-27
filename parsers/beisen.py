#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：北森(Beisen i-Talent / zhiye.com) 通用社招门户 → JSON(stdout)。

所有用北森招聘的公司共享同一接口 /api/Jobad/GetJobAdPageList，只差一个子域名 slug。
裸 HTTP 直调（无需登录/cookie/JS，门户首页是 SPA 但该接口公开），一个脚本通吃所有 {slug}.zhiye.com 公司。
大型制造业/车企/家电/装备巨头多用北森，是产业信号的重要补充。

用法: python3 beisen.py <slug> <company> [keyword] [pages]
  例:  python3 beisen.py dreame 追觅 产品
"""
import os
import sys, json, re, ssl, urllib.request

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _call(slug, keyword, page, size):
    # Category=["1"] 社会招聘；接口忽略未知 DisplayFields，Duty/LocNames 等始终回传
    body = {"PageIndex": page, "PageSize": size, "LocId": [], "Category": ["1"],
            "KeyWords": keyword or "", "SpecialType": 0, "PortalId": "",
            "DisplayFields": ["Category", "Kind", "LocId", "PostDate", "Salary"]}
    headers = {"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json",
               "Origin": f"https://{slug}.zhiye.com", "Referer": f"https://{slug}.zhiye.com/social/jobs"}
    req = urllib.request.Request(f"https://{slug}.zhiye.com/api/Jobad/GetJobAdPageList",
                                 data=json.dumps(body).encode(), headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=25, context=CTX))


def fetch(slug, company, keyword="", pages=8, limit=50):
    if not re.fullmatch(r"[A-Za-z0-9-]+", slug or ""):
        sys.exit("[beisen] slug 非法（应为 {slug}.zhiye.com 的子域名，如 dreame）")
    out = []
    for pg in range(pages):
        try:
            d = _call(slug, keyword, pg, limit)
        except Exception:
            break                              # 单页失败：保留已抓到的，优雅退出
        posts = d.get("Data") or []
        if not posts:
            break
        for j in posts:
            jid = str(j.get("JobAdId", "") or j.get("Id", ""))
            title = j.get("JobAdName", "")
            m = re.search(r"\(J\d+\)", title)   # 北森职位号 (J12345) → req_id
            out.append({
                "title": title,
                "company": company,
                "location": ", ".join(j.get("LocNames") or []),
                "type": j.get("Category", ""),   # 社会招聘 / 校园招聘
                "date": j.get("PostDate", ""),   # ISO 8601；主脚本 _fmt_date 可解析
                "req_id": m.group(0).strip("()") if m else "",
                "comp": j.get("Salary", "") or "",
                "jd": j.get("Duty", "") or "",
                "url": f"https://{slug}.zhiye.com/social/jobs",   # SPA 门户(深链需 JS 路由)
                "id": jid,
            })
        if len(posts) < limit or len(out) >= int(d.get("Count") or 0):
            break
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("用法: beisen.py <slug> <company> [keyword] [pages]")
    slug, company = sys.argv[1], sys.argv[2]
    kw = sys.argv[3] if len(sys.argv) > 3 else ""
    pg = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    print(json.dumps(fetch(slug, company, kw, pg), ensure_ascii=False))
