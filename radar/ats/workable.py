"""Workable：apply.workable.com 公开 widget 接口（details=true 带完整 JD、行业、发布日期）。"""
from ..countries import code
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true")
    company = d.get("name", "")
    out = []
    for j in d.get("jobs") or []:
        locs = j.get("locations") or []
        cc = (locs[0].get("countryCode") if locs and isinstance(locs[0], dict) else "") or code(j.get("country"))
        tele = str(j.get("telecommuting")).lower() == "true"
        url = j.get("url") or j.get("shortlink") or ""
        out.append(rec(
            title=j.get("title", ""),
            company=company,
            dept=j.get("department", ""),
            type=j.get("employment_type", ""),
            location=", ".join(x for x in [j.get("city"), j.get("state"), j.get("country")] if x),
            remote="Remote" if tele else "",
            date=j.get("published_on") or j.get("created_at", ""),
            req_id=j.get("code", ""),
            jd=strip_html(j.get("description", "")),
            url=url, apply_url=j.get("application_url") or url,
            id=j.get("shortcode", ""),
            country=(cc or "").upper(),
            industry=j.get("industry", ""),
        ))
    return out, f"workable/{slug}"
