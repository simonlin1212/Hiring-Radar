"""Lever：postings 公开接口（mode=json），含完整 JD 和薪资区间（有填时）。"""
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    out = []
    for j in (d if isinstance(d, list) else []):
        c = j.get("categories", {}) or {}
        jd = j.get("descriptionPlain") or strip_html(j.get("description", ""))
        for lst in (j.get("lists") or []):
            jd += "\n\n" + strip_html(lst.get("text", "")) + ":\n" + strip_html(lst.get("content", ""))
        jd += "\n\n" + (j.get("additionalPlain") or strip_html(j.get("additional", "")))
        sr = j.get("salaryRange") or {}
        comp = f"{sr.get('currency', '')} {sr.get('min', '')}-{sr.get('max', '')}".strip() if sr.get("min") else ""
        out.append(rec(
            title=j.get("text", ""),
            location=c.get("location", ""),
            dept=c.get("department", "") or c.get("team", ""),
            team=c.get("team", ""),
            type=c.get("commitment", ""),
            remote=c.get("workplaceType", ""),
            date=j.get("createdAt", ""),
            req_id=str(j.get("id", "")),
            comp=comp,
            jd=jd.strip(),
            url=j.get("hostedUrl", ""),
            apply_url=j.get("applyUrl") or j.get("hostedUrl", ""),
            id=str(j.get("id", "")),
            country=(j.get("country") or "").upper(),
        ))
    return out, f"lever/{slug}"
