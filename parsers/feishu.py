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
import sys, json, re, urllib.error

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 仓库根目录
from radar.http import BROWSER_UA, Blocked, RateLimited, get_text, post_json  # noqa: E402  统一联网：限速、429 退避、被拦就停
# 飞书招聘网关只认浏览器 UA（如实报身份一律回 405），这里沿用 v1 的浏览器 UA；README 已写明这个例外
PAGE = {"User-Agent": BROWSER_UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.9"}
_PATH_RE = re.compile(r"[A-Za-z0-9_/-]{1,40}")


def _homepage_path(host):
    try:
        html = get_text(f"https://{host}/", headers=PAGE, timeout=20)
        m = re.search(r'id="js-websiteInfo"[^>]*>(.*?)</script>', html, re.S)
        if m:
            p = ((json.loads(m.group(1)).get("website_info")) or {}).get("path", "") or ""
            return p if _PATH_RE.fullmatch(p or "") else ""
    except (Blocked, RateLimited):
        raise                     # 被拦/限流就停，不再试别的路径
    except Exception:
        pass
    return ""


def _call(host, path, keyword, limit, offset):
    body = {"keyword": keyword, "limit": limit, "offset": offset, "portal_type": 2,
            "job_category_id_list": [], "location_code_list": [], "subject_id_list": [],
            "recruitment_id_list": [], "job_function_id_list": []}
    headers = {"User-Agent": BROWSER_UA, "Origin": f"https://{host}", "Referer": f"https://{host}/",
               "Portal-Channel": "office", "Portal-Platform": "pc", "website-path": path}
    try:
        return post_json(f"https://{host}/api/v1/search/job/posts", body, headers=headers)
    except urllib.error.HTTPError as e:
        if e.code == 405:   # 网关拒绝：当作被拦，停下，不换路径重试
            raise Blocked(f"飞书招聘网关拒绝请求（HTTP 405）：{host}，停止")
        raise


def _resolve_path(host, keyword, forced=""):
    # 显式 website-path：门户不在根路径时用（如 galbot owm6...feishu.cn/870797）。根目录探测会 404。
    def ok(path):
        try:
            return _call(host, path, keyword, 1, 0).get("code") == 0
        except (Blocked, RateLimited):
            raise                 # 被拦/限流就停，不再试别的路径
        except Exception:
            return False

    if forced and ok(forced):
        return forced
    p = _homepage_path(host)
    if p and ok(p):
        return p
    for cand in ("index", "experienced", "fte", "social", "recruitment", "campus"):
        if ok(cand):
            return cand
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
