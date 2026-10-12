"""SmartRecruiters：公开 postings 接口，翻页(100/页)。列表级：标题/地点/部门/类型/首发日期；完整 JD 需详情接口（不抓，保持轻量）。"""
from ..http import get_json
from ..schema import rec


def _label(v):
    return v.get("label", "") if isinstance(v, dict) else (v or "")


def fetch(slug, meta=None):
    out = []
    for page in range(50):  # 安全上限 5000 岗
        d = get_json(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={page*100}&status=PUBLIC")
        items = d.get("content") or []
        if not items:
            break
        for j in items:
            loc = j.get("location") or {}
            full = loc.get("fullLocation") or ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x)
            location = ", ".join(x for x in [full, ("Remote" if loc.get("remote") else "")] if x)
            ref = j.get("ref") if isinstance(j.get("ref"), str) else ""
            url = ""
            if ref.startswith("https://api.smartrecruiters.com/v1/companies/"):
                url = "https://jobs.smartrecruiters.com/" + ref.split("/v1/companies/", 1)[1]
            if not url and j.get("id"):
                url = f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}"
            out.append(rec(
                title=j.get("name", ""),
                location=location,
                dept=_label(j.get("department")) or _label(j.get("function")),
                type=_label(j.get("typeOfEmployment")),
                date=j.get("releasedDate", ""),
                req_id=str(j.get("refNumber") or j.get("uuid") or ""),
                url=url, apply_url=url, id=str(j.get("id", "")),
                country=(loc.get("country") or "").upper(),
            ))
        if len(items) < 100:
            break
    return out, f"smartrecruiters/{slug}"
