"""BambooHR：{slug}.bamboohr.com/careers/list 公开列表（轻量：无 JD/日期）。url=/careers/{id}"""
from ..http import get_json
from ..schema import rec


def fetch(slug, meta=None):
    d = get_json(f"https://{slug}.bamboohr.com/careers/list")
    origin = f"https://{slug}.bamboohr.com"
    out = []
    for j in (d.get("result") or []):
        if not j or not j.get("jobOpeningName") or not str(j.get("id") or "").strip():
            continue
        loc = j.get("location") or {}
        remote = "Remote" if j.get("isRemote") else ""
        location = ", ".join(x for x in [loc.get("city"), loc.get("state"), remote] if x)
        jid = str(j.get("id")).strip()
        url = f"{origin}/careers/{jid}"
        out.append(rec(
            title=j.get("jobOpeningName", ""),
            location=location,
            dept=j.get("departmentLabel", ""),
            type=j.get("employmentStatusLabel", ""),
            req_id=jid, url=url, apply_url=url, id=jid,
        ))
    return out, f"bamboohr/{slug}"
