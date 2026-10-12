"""schema.org JobPosting（JSON-LD）解析：很多招聘系统在职位页里给 Google 招聘放这块结构化数据，
标题、发布日期、地点、完整 JD、薪资都在里面，比解析页面稳。JazzHR、Jobvite、iCIMS 等共用。"""
import json
import re

from ..countries import code
from ..schema import rec, strip_html

_BLOCK = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)


def postings(html):
    """页面里所有 @type=JobPosting 的对象。"""
    out = []
    for m in _BLOCK.finditer(html or ""):
        try:
            d = json.loads(m.group(1).strip())
        except ValueError:
            continue
        stack = d if isinstance(d, list) else [d]
        while stack:
            x = stack.pop(0)
            if not isinstance(x, dict):
                continue
            stack += x.get("@graph") or []
            t = x.get("@type")
            if t == "JobPosting" or (isinstance(t, list) and "JobPosting" in t):
                out.append(x)
    return out


def _name(x):
    if isinstance(x, dict):
        return x.get("name") or ""
    return x if isinstance(x, str) else ""


def details(urls, cap=150):
    """逐个抓职位页取 JobPosting（中小公司一般几十个岗位）。超过 cap 的只留列表信息。
    单个页面出错跳过；被限流/被拦照常抛出，由上层停下。"""
    from ..http import Blocked, RateLimited, get_text
    out = {}
    for u in urls[:cap]:
        try:
            jp = postings(get_text(u))
        except (Blocked, RateLimited):
            raise
        except Exception:
            continue
        if jp:
            out[u] = jp[0]
    if len(urls) > cap:
        import sys
        sys.stderr.write(f"[i] 岗位较多：前 {cap} 个抓了详情，其余 {len(urls) - cap} 个只有标题和链接\n")
    return out


def _places(jp):
    locs = jp.get("jobLocation") or []
    locs = locs if isinstance(locs, list) else [locs]
    texts, ccs = [], []
    for loc in locs:
        a = (loc or {}).get("address") or {} if isinstance(loc, dict) else {}
        if isinstance(a, str):
            texts.append(a)
            continue
        cc = code(_name(a.get("addressCountry")))
        parts = [a.get("addressLocality"), a.get("addressRegion"), cc]
        t = ", ".join(p for p in parts if isinstance(p, str) and p and p.upper() != "UNAVAILABLE")
        if t and t not in texts:
            texts.append(t)
        if cc and cc not in ccs:
            ccs.append(cc)
    return "; ".join(texts), ",".join(ccs)


def _salary(jp):
    s = jp.get("baseSalary")
    if not isinstance(s, dict):
        return ""
    v = s.get("value") or {}
    cur = s.get("currency") or ""
    if not isinstance(v, dict):
        return f"{cur} {v}".strip() if v else ""
    lo, hi, unit = v.get("minValue"), v.get("maxValue"), v.get("unitText") or ""
    if not (lo or hi or v.get("value")):
        return ""
    amt = f"{lo}-{hi}" if lo and hi and lo != hi else str(lo or hi or v.get("value"))
    return f"{cur} {amt}".strip() + (f"/{unit.lower()}" if unit else "")


def to_rec(jp, url="", **extra):
    loc, cc = _places(jp)
    et = jp.get("employmentType") or ""
    et = ", ".join(et) if isinstance(et, list) else str(et)
    remote = "Remote" if str(jp.get("jobLocationType", "")).upper() == "TELECOMMUTE" else ""
    ident = jp.get("identifier")
    ident = ident.get("value") if isinstance(ident, dict) else ident
    r = rec(
        title=strip_html(jp.get("title") or ""),
        company=_name(jp.get("hiringOrganization")),
        location=loc,
        remote=remote,
        type=et,
        date=jp.get("datePosted") or "",
        comp=_salary(jp),
        jd=strip_html(jp.get("description") or ""),
        url=jp.get("url") or url, apply_url=jp.get("url") or url,
        id=str(ident or ""),
        country=cc,
        industry=_name(jp.get("industry")) if not isinstance(jp.get("industry"), list) else ", ".join(jp["industry"]),
        dept=_name(jp.get("occupationalCategory")),
    )
    r.update(extra)
    return r
