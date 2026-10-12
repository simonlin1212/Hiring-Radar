"""Reed（英国最大的招聘网站之一）官方求职者接口。需要免费 API key：reed.co.uk/developers 注册后设置
环境变量 REED_API_KEY。列表有职位名、雇主、地点、薪资、发布日期、JD 摘要（完整 JD 要逐条查详情，这里不查）。

注意：本模块按官方文档的字段编写，维护者没有 key，未经实网测试。"""
import base64
import sys
from datetime import datetime

from ..http import get_json
from ..schema import rec
from ._keys import need

NAME = "reed"
DESC = "Reed 英国（需 REED_API_KEY，可按关键词）"
FILTERS = {"keyword"}
COUNTRY = "GB"
API = "https://www.reed.co.uk/api/1.0/search"
PAGE, CAP = 100, 10000


def _date(s):
    try:
        return datetime.strptime(s or "", "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return s or ""


def to_rec(j):
    lo, hi = j.get("minimumSalary"), j.get("maximumSalary")
    comp = f"{j.get('currency') or 'GBP'} {lo or ''}-{hi or ''}".strip() if (lo or hi) else ""
    return rec(
        title=j.get("jobTitle", ""),
        company=j.get("employerName", ""),
        location=j.get("locationName", ""),
        date=_date(j.get("date")),
        comp=comp,
        jd=j.get("jobDescription", ""),
        url=j.get("jobUrl", ""), apply_url=j.get("jobUrl", ""),
        id=str(j.get("jobId", "")),
        country=COUNTRY,
        source="board/reed",
    )


def pages(q, state=None):
    if q.countries and COUNTRY not in q.countries:
        return
    key, = need("Reed", "https://www.reed.co.uk/developers/jobseeker", "REED_API_KEY")
    auth = {"Authorization": "Basic " + base64.b64encode(f"{key}:".encode()).decode()}
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        skip = st.get("skip", 0) if st.get("k") == ki else 0
        while True:
            d = get_json(API, {"keywords": kws[ki] or None, "resultsToTake": PAGE, "resultsToSkip": skip}, headers=auth)
            rows = d.get("results") or []
            skip += len(rows)
            total = d.get("totalResults") or 0
            last = len(rows) < PAGE or skip >= total or skip >= CAP
            if last and skip >= CAP and total > skip:
                sys.stderr.write(f"[!] Reed「{kws[ki]}」共 {total} 条，只拉前 {skip} 条\n")
            yield [to_rec(j) for j in rows], ({"k": ki + 1} if last else {"k": ki, "skip": skip})
            if last:
                break
        st = {}
