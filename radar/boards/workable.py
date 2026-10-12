"""Workable 全站职位搜索（jobs.workable.com 前端用的公开接口）：跨所有用 Workable 的公司，按关键词和国家搜。
每页 20 条；遇到 429 由 http 层退避，仍不行就停下（可 --resume 续跑）。"""
import time

from ..countries import code
from ..http import get_json
from ..schema import rec, strip_html

NAME = "workable"
DESC = "Workable 全站搜索（跨公司，可按国家/关键词）"
FILTERS = {"keyword", "country"}
URL = "https://jobs.workable.com/api/v1/jobs"
PAUSE = 1.5  # 翻页间隔；Workable 对连续翻页较敏感


def to_rec(j, cc=""):
    loc = j.get("location") or {}
    locs = j.get("locations") or []
    jd = "\n\n".join(strip_html(j.get(k, "")) for k in ("description", "requirementsSection", "benefitsSection") if j.get(k))
    return rec(
        title=j.get("title", ""),
        company=(j.get("company") or {}).get("title", ""),
        dept=j.get("department", "") or "",
        type=j.get("employmentType", "") or "",
        location=", ".join(x for x in [loc.get("city"), loc.get("subregion"), loc.get("countryName")] if x),
        remote="Remote" if "TELECOMMUTE" in locs else (j.get("workplace") or ""),
        date=j.get("created", ""),
        date_updated=j.get("updated", ""),
        jd=jd,
        url=j.get("url", ""), apply_url=j.get("url", ""),
        id=str(j.get("id", "")),
        country=code(loc.get("countryName")) or cc,
        source="workable/search",
    )


def pages(q, state=None):
    st = dict(state or {})
    combos = [(k, c) for k in (q.keywords or [""]) for c in (q.countries or [""])]
    for ci in range(st.get("i", 0), len(combos)):
        kw, cc = combos[ci]
        token = st.get("token") if st.get("i") == ci else None
        while True:
            params = {"query": kw, "location": cc, "limit": 20}
            if token:
                params["pageToken"] = token
            d = get_json(URL, params)
            token = d.get("nextPageToken")
            yield [to_rec(j, cc) for j in d.get("jobs") or []], ({"i": ci, "token": token} if token else {"i": ci + 1})
            if not token:
                break
            time.sleep(PAUSE)
        st = {}
