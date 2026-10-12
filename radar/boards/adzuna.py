"""Adzuna 官方接口（聚合多国职位，含英、美、澳、加、新西兰等 19 国）。需要免费 app_id/app_key：
developer.adzuna.com 注册后设置环境变量 ADZUNA_APP_ID、ADZUNA_APP_KEY。列表有职位名、公司、地点、
薪资（可能是 Adzuna 估算的）、类别、发布日期、JD 摘要。

注意：本模块按官方文档的字段编写，维护者没有 key，未经实网测试。"""

from ..http import get_json
from ..schema import rec
from ._keys import need

NAME = "adzuna"
DESC = "Adzuna 多国聚合（需 ADZUNA_APP_ID/ADZUNA_APP_KEY，可按国家/关键词/近 N 天）"
FILTERS = {"keyword", "country", "recent_days"}
API = "https://api.adzuna.com/v1/api/jobs/{cc}/search/{page}"
SUPPORTED = ["GB", "US", "AU", "CA", "NZ", "AT", "BE", "BR", "CH", "DE", "ES", "FR", "IN", "IT", "MX", "NL", "PL",
             "SG", "ZA"]
PAGE, MAX_PAGES = 50, 200


def to_rec(j, cc):
    lo, hi = j.get("salary_min"), j.get("salary_max")
    comp = f"{lo or ''}-{hi or ''}" if (lo or hi) else ""
    if comp and str(j.get("salary_is_predicted")) == "1":
        comp += "（估算）"
    return rec(
        title=j.get("title", ""),
        company=(j.get("company") or {}).get("display_name", ""),
        location=(j.get("location") or {}).get("display_name", ""),
        type=", ".join(x for x in [j.get("contract_time"), j.get("contract_type")] if x),
        dept=(j.get("category") or {}).get("label", ""),
        date=j.get("created", ""),
        comp=comp,
        jd=j.get("description", ""),
        url=j.get("redirect_url", ""), apply_url=j.get("redirect_url", ""),
        id=str(j.get("id", "")),
        country=cc,
        source="board/adzuna",
    )


def pages(q, state=None):
    ccs = [c for c in (q.countries or SUPPORTED) if c in SUPPORTED]
    if not ccs:
        return
    app_id, app_key = need("Adzuna", "https://developer.adzuna.com/", "ADZUNA_APP_ID", "ADZUNA_APP_KEY")
    combos = [(k, c) for k in (q.keywords or [""]) for c in ccs]
    st = dict(state or {})
    for ci in range(st.get("i", 0), len(combos)):
        kw, cc = combos[ci]
        page = st.get("page", 1) if st.get("i") == ci else 1
        while True:
            d = get_json(API.format(cc=cc.lower(), page=page),
                         {"app_id": app_id, "app_key": app_key, "results_per_page": PAGE, "what": kw or None,
                          "max_days_old": q.recent_days or None, "content-type": "application/json"})
            rows = d.get("results") or []
            total = d.get("count") or 0
            last = len(rows) < PAGE or page * PAGE >= total or page >= MAX_PAGES
            if last and page >= MAX_PAGES and total > page * PAGE:
                q.truncate(f"Adzuna {cc}「{kw}」共 {total} 条，只拉前 {page * PAGE} 条")
            page += 1
            yield [to_rec(j, cc) for j in rows], ({"i": ci + 1} if last else {"i": ci, "page": page})
            if last:
                break
        st = {}
