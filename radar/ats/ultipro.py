"""UKG Pro（UltiPro）：recruiting.ultipro.com 公开职位板搜索接口（POST，分页）。需公司代码 + 职位板 ID（名录里有）。
含标题、发布日期、简介、地点和国家，没有完整 JD。"""
import re

from ..countries import code
from ..http import post_json
from ..schema import rec

_BOARD = re.compile(r"[0-9a-fA-F-]{36}")


def fetch(slug, meta=None):
    board = (meta or {}).get("board_id", "")
    if not _BOARD.fullmatch(board or ""):
        raise ValueError("UltiPro 需要职位板 ID（board_id，36 位），名录里有；或用 --directory-update 后按公司名查")
    tenant = slug.upper()
    base = f"https://recruiting.ultipro.com/{tenant}/JobBoard/{board}"
    out = []
    for page in range(50):
        d = post_json(base + "/JobBoardView/LoadSearchResults", {"opportunitySearch": {
            "Top": 100, "Skip": page * 100, "QueryString": "", "OrderBy": [{"Value": "postedDateDesc"}], "Filters": []}})
        rows = d.get("opportunities") or []
        for j in rows:
            locs, ccs = [], []
            for l in j.get("Locations") or []:
                a = l.get("Address") or {}
                cc = code((a.get("Country") or {}).get("Code"))
                t = ", ".join(x for x in [a.get("City"), (a.get("State") or {}).get("Code"), cc] if x) or l.get("LocalizedName")
                if t and t not in locs:
                    locs.append(t)
                if cc and cc not in ccs:
                    ccs.append(cc)
            url = f"{base}/OpportunityDetail?opportunityId={j.get('Id', '')}"
            out.append(rec(
                title=j.get("Title", ""),
                dept=j.get("JobCategoryName") or "",
                location="; ".join(locs),
                type="Full-time" if j.get("FullTime") else "Part-time" if j.get("FullTime") is False else "",
                date=j.get("PostedDate") or "",
                req_id=j.get("RequisitionNumber") or "",
                jd=j.get("BriefDescription") or "",
                url=url, apply_url=url,
                id=j.get("Id", ""),
                country=",".join(ccs),
            ))
        if len(rows) < 100 or len(out) >= (d.get("totalCount") or 0):
            break
    return out, f"ultipro/{slug}"
