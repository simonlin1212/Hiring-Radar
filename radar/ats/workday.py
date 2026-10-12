"""Workday：{host}/wday/cxs/{tenant}/{site}/jobs 公开 JSON 接口（POST，20 条/页）。
列表无 JD；--jd 时逐岗补抓（慢：每岗一次请求）。
公司名录（openroles）里有约 4,400 家 Workday 公司的 host 和 site，给公司名即可直查。"""
import re
import sys
import urllib.error

from ..http import get_json, get_text, post_json
from ..schema import rec, strip_html

HOST = re.compile(r"[a-z0-9-]{1,64}\.wd\d{1,3}(?:-[a-z0-9]+)?\.myworkdayjobs\.com")
SITE = re.compile(r"[A-Za-z0-9_-]{1,64}")


def check(host, tenant, site):
    """防 SSRF：host 只能是 *.myworkdayjobs.com，tenant/site 只能是单段字母数字。"""
    host = (host or "").strip().lower()
    if not HOST.fullmatch(host):
        raise ValueError(f"Workday host 应为 xxx.wdN.myworkdayjobs.com：{host!r}")
    for v in (tenant, site):
        if not SITE.fullmatch(v or ""):
            raise ValueError(f"Workday tenant/site 只允许字母数字下划线连字符：{v!r}")
    return host, tenant, site


def fetch_board(host, tenant, site, search="", pages=40):
    host, tenant, site = check(host, tenant, site)
    out, total = [], 0
    base = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    for p in range(pages):
        d = post_json(base, {"appliedFacets": {}, "limit": 20, "offset": p * 20, "searchText": search})
        total = total or d.get("total") or 0  # Workday 只在第一页给 total，后面的页是 0
        posts = d.get("jobPostings", [])
        if not posts:
            break
        for j in posts:
            path = j.get("externalPath", "")
            r = rec(
                title=j.get("title", ""),
                location=j.get("locationsText", ""),
                date=j.get("postedOn", ""),
                req_id=", ".join(j.get("bulletFields") or []),
                url=f"https://{host}/{site}{path}" if path.startswith("/job/") else f"https://{host}{path}",
                id=(j.get("bulletFields") or [""])[0],
            )
            r["apply_url"] = r["url"]
            r["_wd"] = (host, tenant, site, path)  # 供 --jd 逐岗抓
            out.append(r)
        if len(posts) < 20 or (p + 1) * 20 >= total:
            break
    return out, f"workday/{tenant}"


# 站点名发现（移植自 openroles 的 workday-site.ts，MIT）：Workday 首页对程序返回 406，但 /robots.txt 公开，
# 里面 Allow: /<站点名>/ 和 Sitemap 就是站点名。一个公司有多个站点时，挑面向大众的（External/Careers），
# 避开实习、校招、内部等窄站点。
_BROAD = {"external", "externals", "general", "generals", "career", "careers", "main", "public", "global",
          "globals", "professional", "professionals", "experienced"}
_NARROW = {"college", "colleges", "intern", "interns", "internship", "internships", "internal", "internals",
           "special", "specials", "invite", "invites", "admin", "admins", "alum", "alumni", "early", "student",
           "students", "apprentice", "apprentices", "apprenticeship", "apprenticeships", "graduate", "graduates",
           "temporary", "temp", "temps"}
_sites = {}


def _score(seg):
    t = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", seg))
    return sum(5 * (w in _BROAD) - 10 * (w in _NARROW) for w in re.split(r"[_-]+", t.lower()) if w)


def discover_site(host):
    """读 https://{host}/robots.txt 找站点名；找不到返回 ""。"""
    host = check(host, "x", "x")[0]
    if host in _sites:
        return _sites[host]
    try:
        txt = get_text(f"https://{host}/robots.txt", tries=2)
    except Exception:
        txt = ""
    allow, sitemap = [], []
    for line in txt.splitlines():
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "allow":
            seg = v.lstrip("/").split("/")[0]
        elif k == "sitemap":
            m = re.match(r"https?://[^/]+/([^/]+)/", v)
            seg = m.group(1) if m else ""
        else:
            continue
        if SITE.fullmatch(seg) and seg != "refreshFacet":
            (allow if k == "allow" else sitemap).append(seg)
    cands = allow or sitemap
    _sites[host] = max(cands, key=_score) if cands else ""   # 同分时取 robots.txt 里靠前的
    return _sites[host]


# robots.txt 也找不到时依次试的常见站点名（同 openroles）
FALLBACK_SITES = ["External", "Careers", "External_Career_Site", "External_Site"]


def fetch(slug, meta=None):
    """slug = tenant；meta 需含 host。site 没给时：robots.txt 找 → 常见站点名逐个试（只在第一页 404 时换下一个）。"""
    meta = meta or {}
    host = meta.get("host", "")
    if meta.get("site"):
        return fetch_board(host, slug, meta["site"], meta.get("search", ""))
    found = discover_site(host)
    for site in dict.fromkeys(([found] if found else []) + FALLBACK_SITES):
        try:
            return fetch_board(host, slug, site, meta.get("search", ""))
        except urllib.error.HTTPError as e:
            if e.code not in (400, 404, 422):
                raise
    raise ValueError(f"Workday {host} 找不到站点名，可用 --workday host,tenant,site 手动指定")


def enrich_jds(items):
    """对 Workday 岗位逐个抓 JD（/job/{path}）。慢：每岗一次 HTTP。"""
    done = 0
    for it in items:
        meta = it.get("_wd")
        if not meta:
            continue
        host, tenant, site, path = meta
        try:
            d = get_json(f"https://{host}/wday/cxs/{tenant}/{site}{path}")
            info = (d.get("jobPostingInfo") or {})
            it["jd"] = strip_html(info.get("jobDescription", ""))
            it["location"] = info.get("location", "") or it["location"]
            it["date"] = info.get("startDate", "") or it["date"]
            done += 1
        except Exception:
            continue
    sys.stderr.write(f"[i] --jd: Workday 逐岗 JD 抓到 {done}/{len(items)}\n")
    return items
