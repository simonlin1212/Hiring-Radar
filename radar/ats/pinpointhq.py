"""Pinpoint：{slug}.pinpointhq.com/postings.json 公开接口，含完整 JD、部门、地点、薪资（有填时）。没有发布日期。"""
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://{slug}.pinpointhq.com/postings.json")
    out = []
    for j in d.get("data") or []:
        job = j.get("job") or {}
        loc = j.get("location") or {}
        jd = "\n\n".join(strip_html(j.get(k) or "") for k in
                         ("description", "key_responsibilities", "skills_knowledge_expertise", "benefits") if j.get(k))
        lo, hi = j.get("compensation_minimum"), j.get("compensation_maximum")
        comp = f"{j.get('compensation_currency') or ''} {lo or ''}-{hi or ''}".strip() if (lo or hi) else ""
        if comp and j.get("compensation_frequency"):
            comp += f"/{j['compensation_frequency']}"
        out.append(rec(
            title=j.get("title", ""),
            dept=((job.get("department") or {}).get("name") or ""),
            location=", ".join(x for x in [loc.get("city") or loc.get("name"), loc.get("province")] if x),
            remote="" if j.get("workplace_type") == "onsite" else (j.get("workplace_type_text") or ""),
            type=j.get("employment_type_text") or "",
            req_id=job.get("requisition_id") or "",
            comp=comp, jd=jd,
            url=j.get("url", ""), apply_url=j.get("url", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"pinpointhq/{slug}"
