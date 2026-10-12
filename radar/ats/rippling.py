"""Rippling：api.rippling.com 公开招聘板接口。列表只有标题/部门/地点，逐岗再取详情拿 JD、发布日期、薪资。"""
import sys

from ..http import Blocked, RateLimited, get_json
from ..schema import rec, strip_html

API = "https://api.rippling.com/platform/api/ats/v1/board"
CAP = 150


def fetch(slug, meta=None):
    rows = get_json(f"{API}/{slug}/jobs")
    rows = rows if isinstance(rows, list) else []
    out = []
    for i, j in enumerate(rows):
        uid = j.get("uuid", "")
        url = f"https://ats.rippling.com/{slug}/jobs/{uid}"
        r = rec(title=j.get("name", ""), dept=(j.get("department") or {}).get("label", ""),
                location=(j.get("workLocation") or {}).get("label", ""), url=url, apply_url=url, id=uid)
        if i < CAP and uid:
            try:
                d = get_json(f"{API}/{slug}/jobs/{uid}")
            except (Blocked, RateLimited):
                raise
            except Exception:
                d = {}
            desc = d.get("description") or {}
            r["jd"] = "\n\n".join(strip_html(desc.get(k) or "") for k in ("role", "company") if desc.get(k)) \
                if isinstance(desc, dict) else strip_html(str(desc))
            r["date"] = d.get("createdOn") or ""
            r["company"] = d.get("companyName") or ""
            r["type"] = (d.get("employmentType") or {}).get("id", "")
            r["location"] = "; ".join(d.get("workLocations") or []) or r["location"]
            pay = d.get("payRangeDetails") or []
            if pay and isinstance(pay[0], dict):
                p = pay[0]
                r["comp"] = f"{p.get('currency', '')} {p.get('rangeStart', '')}-{p.get('rangeEnd', '')}".strip()
                if p.get("frequency"):
                    r["comp"] += f"/{p['frequency']}"
        out.append(r)
    if len(rows) > CAP:
        sys.stderr.write(f"[i] Rippling {slug}: 前 {CAP} 个岗位抓了详情，其余只有标题\n")
    return out, f"rippling/{slug}"
