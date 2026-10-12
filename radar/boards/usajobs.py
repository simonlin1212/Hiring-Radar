"""USAJOBS：美国联邦政府职位官方接口。需要免费 API key：developer.usajobs.gov 注册后设置环境变量
USAJOBS_API_KEY 和 USAJOBS_EMAIL（接口要求把注册邮箱放在 User-Agent 里，这是官方规定，不是伪装）。
有职位名、机构、地点、薪资、发布日期、职位摘要。

注意：本模块按官方文档的字段编写，维护者没有 key，未经实网测试。"""
from ..http import get_json
from ..schema import rec
from ._keys import need

NAME = "usajobs"
DESC = "USAJOBS 美国联邦政府（需 USAJOBS_API_KEY/USAJOBS_EMAIL，可按关键词/近 N 天）"
FILTERS = {"keyword"}
COUNTRY = "US"
API = "https://data.usajobs.gov/api/search"
PAGE = 500


def to_rec(it):
    j = it.get("MatchedObjectDescriptor") or {}
    pay = (j.get("PositionRemuneration") or [{}])[0] or {}
    comp = f"USD {pay.get('MinimumRange', '')}-{pay.get('MaximumRange', '')}/{pay.get('RateIntervalCode', '')}" \
        if pay.get("MinimumRange") else ""
    det = ((j.get("UserArea") or {}).get("Details") or {})
    return rec(
        title=j.get("PositionTitle", ""),
        company=j.get("OrganizationName", ""),
        team=j.get("DepartmentName", ""),
        dept=", ".join(c.get("Name", "") for c in j.get("JobCategory") or []),
        location=j.get("PositionLocationDisplay", ""),
        type=", ".join(s.get("Name", "") for s in j.get("PositionSchedule") or []),
        date=j.get("PublicationStartDate", ""),
        comp=comp,
        jd=det.get("JobSummary", "") if isinstance(det, dict) else "",
        url=j.get("PositionURI", ""), apply_url=(j.get("ApplyURI") or [j.get("PositionURI", "")])[0],
        id=str(j.get("PositionID") or it.get("MatchedObjectId", "")),
        req_id=str(it.get("MatchedObjectId", "")),
        country=COUNTRY,
        industry="Government",
        source="gov/usajobs",
    )


def pages(q, state=None):
    if q.countries and COUNTRY not in q.countries:
        return
    key, email = need("USAJOBS", "https://developer.usajobs.gov/apirequest/", "USAJOBS_API_KEY", "USAJOBS_EMAIL")
    hdr = {"Host": "data.usajobs.gov", "User-Agent": email, "Authorization-Key": key}
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        page = st.get("page", 1) if st.get("k") == ki else 1
        while True:
            params = {"Keyword": kws[ki] or None, "ResultsPerPage": PAGE, "Page": page,
                      "DatePosted": q.recent_days if 0 < q.recent_days <= 60 else None}
            d = (get_json(API, params, headers=hdr).get("SearchResult") or {})
            rows = d.get("SearchResultItems") or []
            last = len(rows) < PAGE or page * PAGE >= int(d.get("SearchResultCountAll") or 0)
            page += 1
            yield [to_rec(x) for x in rows], ({"k": ki + 1} if last else {"k": ki, "page": page})
            if last:
                break
        st = {}
