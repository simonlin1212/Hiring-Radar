"""Hireology：api.hireology.com 公开职业页接口（分页），含完整 JD、发布日期、薪资（汽车经销商、诊所等小企业多）。"""
from ..http import get_json
from ..schema import rec, strip_html


def _comp(c):
    if not isinstance(c, dict):
        return ""
    lo, hi = c.get("comp_range_min"), c.get("comp_range_max")
    amt = f"{lo}-{hi}" if c.get("is_comp_range") and lo and hi else (c.get("comp_single_amount") or lo or "")
    if not amt:
        return ""
    return f"{amt}" + (f"/{c['comp_frequency']}" if c.get("comp_frequency") else "")


def fetch(slug, meta=None):
    out = []
    for page in range(1, 41):
        d = get_json(f"https://api.hireology.com/v2/public/careers/{slug}", {"page": page, "page_size": 100})
        rows = d.get("data") or []
        for j in rows:
            locs = j.get("locations") or []
            loc = "; ".join(", ".join(x for x in [l.get("city"), l.get("state")] if x) for l in locs if isinstance(l, dict))
            url = j.get("career_site_url") or ""
            out.append(rec(
                title=j.get("name", ""),
                company=(j.get("organization") or {}).get("name", ""),
                dept=(j.get("job_family") or {}).get("name", ""),
                location=loc,
                remote="Remote" if j.get("remote") else "",
                type=j.get("employment_status") or "",
                date=j.get("created_at", ""),
                comp=_comp(j.get("compensation")),
                jd=strip_html(j.get("job_description", "")),
                url=url, apply_url=url,
                id=str(j.get("id", "")),
            ))
        if len(rows) < 100 or len(out) >= int(d.get("count") or 0):
            break
    return out, f"hireology/{slug}"
