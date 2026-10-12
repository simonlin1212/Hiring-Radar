"""freehire（github.com/strelov1/freehire，MIT）公开接口：225 个来源、自称约 330 万在招职位，免注册，含完整 JD。

条款允许通过公开接口自动读取，禁止绕过接口另行抓取、禁止绕过限流；作者实测限速约每分钟 300 次。
本模块每页 100 条，同一主机请求间隔不低于 HIRING_RADAR_DELAY（默认 0.3 秒），远低于限速。
单次查询最多翻到第 10,000 条（freehire 的翻页深度上限）；超过时按 freehire 文档建议用筛选条件
（按来源 source）拆成多次查询，请求总数不变，不是绕限流。
"""

from ..http import get_json
from ..schema import rec

NAME = "freehire"
DESC = "freehire 聚合（225 个来源，可按国家/关键词/近 N 天，含完整 JD）"
# 关键词也发给服务端缩小范围，但 freehire 对多个词按 OR 搜、还做词干匹配，和其他来源的「整串包含」不同；
# 所以不算服务端过滤，返回后由 sweep 按统一规则再筛一遍。
FILTERS = {"country", "recent_days"}
API = "https://freehire.me/api/v1"
PAGE, CAP = 100, 10000


def _params(q, kw):
    p = {}
    if q.countries:
        p["countries"] = ",".join(c.lower() for c in q.countries)
    if kw:
        p["q"] = kw
    if q.recent_days:
        p["posted_within_days"] = q.recent_days
    return p


def _parts(base):
    """总数超过翻页上限时，按来源拆分；否则一次查完。"""
    d = (get_json(API + "/jobs/facets", base) or {}).get("data") or {}
    if (d.get("total") or 0) <= CAP:
        return [{}]
    src = (d.get("facets") or {}).get("source") or {}
    src = dict(src) if isinstance(src, list) else src
    return [{"source": s} for s in sorted(src, key=lambda s: -src[s])] or [{}]


def to_rec(j):
    e = j.get("enrichment") or {}
    comp = ""
    if e.get("salary_min") or e.get("salary_max"):
        comp = f"{e.get('salary_currency', '')} {e.get('salary_min', '')}-{e.get('salary_max', '')}"
        comp = comp.strip() + (f"/{e['salary_period']}" if e.get("salary_period") else "")
    return rec(
        title=j.get("title", ""),
        company=j.get("company", "") or j.get("company_slug", ""),
        location=j.get("location", "") or ", ".join(j.get("cities") or []),
        remote=j.get("work_mode", ""),
        type=e.get("employment_type", ""),
        dept=e.get("category", ""),
        date=j.get("posted_at", ""),
        date_updated=j.get("updated_at", ""),
        comp=comp,
        jd=j.get("description", ""),
        url=j.get("url", ""), apply_url=j.get("url", ""),
        id=j.get("public_slug", ""),
        country=",".join(c.upper() for c in (j.get("countries") or [])),
        source=f"freehire/{j.get('source', '')}",
        size=e.get("company_size", ""),
        industry=",".join(e.get("domains") or []),
    )


def pages(q, state=None):
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        base = _params(q, kws[ki])
        resumed = st.get("k") == ki and "parts" in st
        parts = st["parts"] if resumed else _parts(base)
        for pi in range(st.get("p", 0) if resumed else 0, len(parts)):
            off = st.get("off", 0) if (resumed and st.get("p") == pi) else 0
            while off < CAP:
                params = dict(base, **parts[pi])
                params.update(limit=min(PAGE, CAP - off), offset=off, description_format="text")
                d = get_json(API + "/agent/jobs/search", params)
                rows = d.get("data") or []
                off += len(rows)
                total = (d.get("meta") or {}).get("total") or 0
                last = len(rows) < params["limit"] or off >= min(total, CAP)
                if last and total > CAP:
                    q.truncate(f"freehire {parts[pi] or base} 共 {total} 条，超过翻页上限，只拉到前 {CAP} 条")
                nxt = {"k": ki, "parts": parts, "p": pi + 1, "off": 0} if last else {"k": ki, "parts": parts, "p": pi, "off": off}
                yield [to_rec(j) for j in rows], nxt
                if last:
                    break
        st = {}
