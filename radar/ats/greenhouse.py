"""Greenhouse：boards-api 公开接口。content=true 一次带回完整 JD（CA 等地的薪资区间也在 JD 正文里）。"""
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    out = []
    for j in d.get("jobs", []):
        out.append(rec(
            title=j.get("title", ""),
            location=(j.get("location") or {}).get("name", ""),
            dept=", ".join(x.get("name", "") for x in (j.get("departments") or []) if isinstance(x, dict)),
            date=j.get("first_published") or j.get("updated_at", ""),
            date_updated=j.get("updated_at", ""),
            req_id=str(j.get("requisition_id") or j.get("internal_job_id") or ""),
            jd=strip_html(j.get("content", "")),
            url=j.get("absolute_url", ""),
            apply_url=j.get("absolute_url", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"greenhouse/{slug}"
