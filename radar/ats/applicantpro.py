"""ApplicantPro / iSolvedHire（同一平台）：先从 {slug}.{域名}/jobs/ 页面取 domain_id，再调 core/jobs/{domain_id} 公开接口。
列表含标题、地点、部门、雇佣类型、薪资和开始日期（startDateRef），不含 JD。"""
import re
from datetime import datetime

from ..countries import code
from ..http import get_json, get_text
from ..schema import rec

_DOMAIN_ID = re.compile(r"[\"']domain_id[\"']\s*:\s*[\"'](\d{1,12})[\"']")


def _date(s):
    try:
        return datetime.strptime((s or "").strip(), "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def fetch_platform(slug, domain, params, kind):
    m = _DOMAIN_ID.search(get_text(f"https://{slug}.{domain}/jobs/"))
    if not m:
        return [], f"{kind}/{slug}"
    d = get_json(f"https://{slug}.{domain}/core/jobs/{m.group(1)}", {"getParams": params})
    out = []
    for j in ((d.get("data") or {}).get("jobs") or []):
        lo, hi = j.get("minSalary"), j.get("maxSalary")
        comp = (f"{lo}-{hi}" if lo and hi and lo != hi else (lo or hi or j.get("payRate") or "")) or ""
        if comp and j.get("payTypeFrame"):
            comp += f" {j['payTypeFrame']}"
        url = j.get("jobUrl") or f"https://{slug}.{domain}/jobs/{j.get('id', '')}"
        out.append(rec(
            title=j.get("title", ""),
            dept=j.get("classification") or j.get("orgTitle") or "",
            team=j.get("orgTitle") or "",
            location=j.get("jobLocation") or ", ".join(x for x in [j.get("city"), j.get("abbreviation")] if x),
            remote=j.get("workplaceType") if j.get("workplaceType") not in (None, "Onsite") else "",
            type=j.get("employmentType") or "",
            date=_date(j.get("startDateRef")),
            comp=str(comp),
            url=url, apply_url=url,
            id=str(j.get("id", "")),
            country=code(j.get("iso3")),
        ))
    return out, f"{kind}/{slug}"


def fetch(slug, meta=None):
    return fetch_platform(slug, "applicantpro.com", "{}", "applicantpro")
