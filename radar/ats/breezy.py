"""Breezy：{slug}.breezy.hr/json 公开 board feed（顶层数组），含 published_date；feed 带 JD 则一并收。"""
from ..http import get_json
from ..schema import rec, strip_html


def _name(v):
    return v.get("name", "") if isinstance(v, dict) else (v or "")


def fetch(slug, meta=None):
    d = get_json(f"https://{slug}.breezy.hr/json")
    out = []
    for j in (d if isinstance(d, list) else []):
        if not j or not j.get("name"):
            continue
        loc = j.get("location") or {}
        country = loc.get("country")
        country_name = country.get("name", "") if isinstance(country, dict) else (country or "")
        base = (loc.get("name") or "").strip() or ", ".join(x for x in [loc.get("city"), loc.get("state"), country_name] if x)
        remote = "Remote" if loc.get("is_remote") else ""
        location = base if (not remote or "remote" in base.lower()) else ", ".join(x for x in [base, remote] if x)
        raw = j.get("url")
        url = raw if isinstance(raw, str) and raw.startswith("https://") else ""
        out.append(rec(
            title=j.get("name", ""),
            location=location,
            dept=_name(j.get("department")),
            type=_name(j.get("type")),
            date=j.get("published_date", ""),
            req_id=str(j.get("id", "")),
            jd=strip_html(j.get("description", "")),
            url=url, apply_url=url, id=str(j.get("id", "")),
            country=(country.get("id", "") if isinstance(country, dict) else "").upper(),
        ))
    return out, f"breezy/{slug}"
