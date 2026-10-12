"""Recruitee：{slug}.recruitee.com/api/offers/；免费带 description/requirements(完整 JD) + created_at + department。"""
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://{slug}.recruitee.com/api/offers/")
    out = []
    for j in (d.get("offers") or []):
        remote = "Remote" if j.get("remote") else ""
        location = j.get("location") or ", ".join(x for x in [j.get("city"), j.get("country"), remote] if x)
        jd = strip_html(j.get("description", ""))
        if j.get("requirements"):
            jd = (jd + "\n\n" + strip_html(j.get("requirements", ""))).strip()
        raw = j.get("careers_url") or j.get("url") or ""
        url = raw if isinstance(raw, str) and raw.startswith("https://") else ""
        out.append(rec(
            title=j.get("title", ""),
            location=location,
            dept=j.get("department", "") or "",
            date=j.get("published_at") or j.get("created_at", ""),
            req_id=str(j.get("id", "")),
            jd=jd, url=url, apply_url=url, id=str(j.get("id", "")),
            country=(j.get("country_code") or "").upper(),
        ))
    return out, f"recruitee/{slug}"
