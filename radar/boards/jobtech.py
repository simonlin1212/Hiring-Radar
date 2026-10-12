"""瑞典公共就业服务（Arbetsförmedlingen）的开放接口 JobTech JobSearch：全国在招职位，免注册，含完整 JD。
数据是开放数据（jobtechdev.se）。单次查询最多翻到第 2,100 条（offset ≤ 2000）；总数更多时按发布时间
每 12 小时拆一段分别查（瑞典每天新增 2,000 多条），请求数随数据量增加，不是绕限流。"""
import sys
from datetime import datetime, timedelta, timezone

from ..countries import code
from ..http import get_json
from ..schema import rec

NAME = "jobtech"
DESC = "瑞典公共就业服务 JobTech（全国，可按关键词/近 N 天，含完整 JD）"
FILTERS = {"keyword", "recent_days"}
COUNTRY = "SE"
API = "https://jobsearch.api.jobtechdev.se/search"
PAGE, CAP = 100, 2000
_FMT = "%Y-%m-%dT%H:%M:%S"


def _label(x):
    return (x or {}).get("label") or "" if isinstance(x, dict) else ""


def to_rec(h):
    a = h.get("workplace_address") or {}
    desc = h.get("description") or {}
    cn = a.get("country") or ""
    return rec(
        title=h.get("headline", ""),
        company=(h.get("employer") or {}).get("name", ""),
        location=", ".join(x for x in [a.get("municipality") or a.get("city"), a.get("region")] if x),
        remote=_label(h.get("workplace_model")),
        type=_label(h.get("employment_type")),
        dept=_label(h.get("occupation")),
        industry=_label(h.get("occupation_field")),
        date=h.get("publication_date", ""),
        comp=h.get("salary_description") or "",
        jd=desc.get("text", "") if isinstance(desc, dict) else "",
        url=h.get("webpage_url", ""),
        apply_url=(h.get("application_details") or {}).get("url") or h.get("webpage_url", ""),
        id=str(h.get("id", "")),
        country=COUNTRY if cn in ("", "Sverige") else code(cn),
        source="gov/jobtech",
    )


def _parts(kw, q):
    """查询的时间段：总数不超过翻页上限就一段，否则从今天往回每 12 小时一段。"""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    start = now - timedelta(days=q.recent_days or 400)
    base = {"q": kw or None, "published-after": start.strftime(_FMT) if q.recent_days else None}
    total = (get_json(API, dict(base, limit=0)).get("total") or {}).get("value") or 0
    if total <= CAP + PAGE:
        return [base]
    out, t = [], now
    while t > start:
        out.append({"q": kw or None, "published-after": max(t - timedelta(hours=12), start).strftime(_FMT),
                    "published-before": t.strftime(_FMT)})
        t -= timedelta(hours=12)
    if not q.recent_days:   # 400 天之前发布、仍在招的
        out.append({"q": kw or None, "published-before": start.strftime(_FMT)})
    return out


def pages(q, state=None):
    if q.countries and COUNTRY not in q.countries:
        return
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        resumed = st.get("k") == ki and "parts" in st
        parts = st["parts"] if resumed else _parts(kws[ki], q)
        for pi in range(st.get("p", 0) if resumed else 0, len(parts)):
            off = st.get("off", 0) if (resumed and st.get("p") == pi) else 0
            while off <= CAP:
                d = get_json(API, dict(parts[pi], limit=PAGE, offset=off))
                rows = d.get("hits") or []
                total = (d.get("total") or {}).get("value") or 0
                off += len(rows)
                last = len(rows) < PAGE or off >= total or off > CAP
                if last and total > CAP + PAGE:
                    sys.stderr.write(f"[!] JobTech {parts[pi]} 共 {total} 条，超过翻页上限，只拉到前 {off} 条\n")
                nxt = {"k": ki, "parts": parts, "p": pi + 1, "off": 0} if last else {"k": ki, "parts": parts, "p": pi, "off": off}
                yield [to_rec(h) for h in rows], nxt
                if last:
                    break
        st = {}
