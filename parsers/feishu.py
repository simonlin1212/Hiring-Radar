#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：飞书招聘(Feishu Hire / 字节系国产ATS) 通用门户 → JSON(stdout)。

所有用飞书招聘的公司共享同一接口 /api/v1/search/job/posts，只差一个 per站点 website-path 头。
本脚本自动从门户首页(js-websiteInfo)探测 path；失败则试候选值。一个脚本通吃所有飞书招聘公司。
支持 "host/website-path" 形式（门户不在根路径时，如 galbot）。

用法: python3 feishu.py <portal_host[/path]> <company> [keyword] [pages]
  例:  python3 feishu.py nio.jobs.feishu.cn 蔚来 算法
"""
import os
import sys, json, re, ssl, urllib.request

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BROWSER = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.9"}
_PATH_RE = re.compile(r"[A-Za-z0-9_/-]{1,40}")


def _homepage_path(host):
    try:
        html = urllib.request.urlopen(urllib.request.Request(f"https://{host}/", headers=BROWSER),
                                      timeout=20, context=CTX).read().decode("utf-8", "replace")
        m = re.search(r'id="js-websiteInfo"[^>]*>(.*?)</script>', html, re.S)
        if m:
            p = ((json.loads(m.group(1)).get("website_info")) or {}).get("path", "") or ""
            return p if _PATH_RE.fullmatch(p or "") else ""
    except Exception:
        pass
    return ""


def _call(host, path, keyword, limit, offset):
    body = {"keyword": keyword, "limit": limit, "offset": offset, "portal_type": 2,
            "job_category_id_list": [], "location_code_list": [], "subject_id_list": [],
            "recruitment_id_list": [], "job_function_id_list": []}
    headers = {"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json",
               "Origin": f"https://{host}", "Referer": f"https://{host}/",
               "Portal-Channel": "office", "Portal-Platform": "pc", "website-path": path}
    req = urllib.request.Request(f"https://{host}/api/v1/search/job/posts", data=json.dumps(body).encode(), headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=25, context=CTX))


def _resolve_path(host, keyword, forced=""):
    # 显式 website-path：门户不在根路径时用（如 galbot owm6...feishu.cn/870797）。根目录探测会 404。
    if forced:
        try:
            if _call(host, forced, keyword, 1, 0).get("code") == 0:
                return forced
        except Exception:
            pass
    p = _homepage_path(host)
    if p:
        try:
            if _call(host, p, keyword, 1, 0).get("code") == 0:
                return p
        except Exception:
            pass
    for cand in ("index", "experienced", "fte", "social", "recruitment", "campus"):
        try:
            if _call(host, cand, keyword, 1, 0).get("code") == 0:
                return cand
        except Exception:
            continue
    return p or "index"


def fetch(host, company, keyword="", pages=8, limit=50):
    forced = ""
    if "/" in host:                       # 支持 "host/website-path"（门户非根路径）
        host, forced = host.split("/", 1)
        forced = forced.strip("/")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host or ""):
        sys.exit("[feishu] host 非法（应为纯域名，如 nio.jobs.feishu.cn）")
    if forced and not _PATH_RE.fullmatch(forced):
        sys.exit("[feishu] website-path 非法")
    path = _resolve_path(host, keyword, forced)
    out = []
    for pg in range(pages):
        d = _call(host, path, keyword, limit, pg * limit)
        data = d.get("data") or {}
        posts = data.get("job_post_list") or []
        if not posts:
            break
        for j in posts:
            jid = str(j.get("id", ""))
            jd = "\n\n".join(x for x in [j.get("description", ""), j.get("requirement", "")] if x)
            cities = ", ".join(c.get("name", "") for c in (j.get("city_list") or []) if isinstance(c, dict))
            jf = j.get("job_function") or {}
            rt = j.get("recruit_type") or {}
            out.append({
                "title": j.get("title", ""),
                "company": company,
                "location": cities,
                "dept": jf.get("name", "") if isinstance(jf, dict) else "",
                "type": rt.get("name", "") if isinstance(rt, dict) else "",
                "date": j.get("publish_time", ""),   # epoch ms
                "jd": jd,
                "url": f"https://{host}/{path}/position/{jid}/detail",
                "id": jid,
            })
        if len(posts) < limit or len(out) >= int(data.get("count") or 0):
            break
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("用法: feishu.py <portal_host[/path]> <company> [keyword] [pages]")
    host, company = sys.argv[1], sys.argv[2]
    kw = sys.argv[3] if len(sys.argv) > 3 else ""
    pg = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    print(json.dumps(fetch(host, company, kw, pg), ensure_ascii=False))
