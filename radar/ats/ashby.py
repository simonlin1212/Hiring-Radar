"""Ashby：posting-api 公开接口。includeCompensation=true 带回薪资区间（含股权说明）；descriptionPlain = 完整 JD。"""
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
    out = []
    for j in d.get("jobs", []):
        comp = ""
        c = j.get("compensation")
        if isinstance(c, dict):
            comp = c.get("compensationTierSummary") or c.get("scrapeableCompensationSalarySummary") or ""
        out.append(rec(
            title=j.get("title", ""),
            location=j.get("location", ""),
            dept=j.get("department", ""),
            team=j.get("team", ""),
            type=j.get("employmentType", ""),
            remote=("Remote" if j.get("isRemote") else (j.get("workplaceType", "") or "")),
            date=j.get("publishedAt", ""),
            req_id=str(j.get("id", "")),
            comp=comp,
            jd=j.get("descriptionPlain") or strip_html(j.get("descriptionHtml", "")),
            url=j.get("jobUrl", ""),
            apply_url=j.get("applyUrl", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"ashby/{slug}"
