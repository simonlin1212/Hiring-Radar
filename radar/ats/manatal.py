"""Manatal：open.api.manatal.com 职业页公开接口（分页），含完整 JD、国家、是否远程。没有发布日期。"""
from ..countries import code
from ..http import get_json
from ..schema import rec, strip_html


def fetch(slug, meta=None):
    out, url = [], f"https://open.api.manatal.com/open/v3/career-page/{slug}/jobs/"
    for _ in range(50):
        d = get_json(url)
        for j in d.get("results") or []:
            link = f"https://www.careers-page.com/{slug}/job/{j.get('hash', '')}"
            out.append(rec(
                title=j.get("position_name", ""),
                location=j.get("location_display") or ", ".join(x for x in [j.get("city"), j.get("country")] if x),
                remote="Remote" if j.get("is_remote") else "",
                type=(j.get("contract_details") or "").replace("_", " "),
                jd=strip_html(j.get("description", "")),
                url=link, apply_url=link,
                id=str(j.get("id", "")),
                country=code(j.get("country")),
            ))
        url = d.get("next")
        if not url or not url.startswith("https://open.api.manatal.com/"):
            break
    return out, f"manatal/{slug}"
