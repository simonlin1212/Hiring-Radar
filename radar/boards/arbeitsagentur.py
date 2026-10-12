"""德国联邦就业局（Bundesagentur für Arbeit）职位搜索接口：德国最大的职位库（也含部分奥地利等邻国职位），免注册。
X-API-Key 用的是官方网页客户端的公开固定标识 jobboerse-jobsuche（见 jobsuche.api.bund.dev），不是个人密钥。
列表有职位名、雇主、地点、首次发布日期；没有 JD 正文。单次查询最多翻 100 页（1 万条），更多请用具体关键词。"""
import sys

from ..http import get_json
from ..schema import rec

NAME = "arbeitsagentur"
DESC = "德国联邦就业局 Jobbörse（全国，可按关键词/近 N 天，无 JD）"
FILTERS = {"keyword"}   # 近 N 天：接口最多支持 100 天，这里只用来缩小范围，精确过滤在本地做
COUNTRY = "DE"
API = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
PAGE, MAX_PAGES = 100, 100
LAND = {"DEUTSCHLAND": "DE", "OESTERREICH": "AT", "SCHWEIZ": "CH", "NIEDERLANDE": "NL", "BELGIEN": "BE",
        "LUXEMBURG": "LU", "FRANKREICH": "FR", "POLEN": "PL", "TSCHECHIEN": "CZ", "DAENEMARK": "DK"}


def to_rec(j):
    locs = [(x or {}).get("adresse") or {} for x in j.get("stellenlokationen") or []]
    ccs = []
    for a in locs:
        cc = LAND.get((a.get("land") or "").upper(), "")
        if cc and cc not in ccs:
            ccs.append(cc)
    ref = j.get("referenznummer", "")
    url = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}"
    typ = "Vollzeit" if j.get("arbeitszeitVollzeit") else ("Teilzeit" if any(
        j.get(k) for k in ("arbeitszeitTeilzeitVormittag", "arbeitszeitTeilzeitNachmittag", "arbeitszeitTeilzeitAbend",
                           "arbeitszeitTeilzeitFlexibel")) else "")
    return rec(
        title=j.get("stellenangebotsTitel") or j.get("hauptberuf", ""),
        company=j.get("firma", ""),
        location="; ".join(", ".join(x for x in [a.get("ort"), a.get("region")] if x) for a in locs[:3]),
        remote="Homeoffice möglich" if j.get("homeofficemoeglich") else "",
        type=", ".join(x for x in [typ, {"UNBEFRISTET": "unbefristet", "BEFRISTET": "befristet"}.get(
            j.get("vertragsdauer", ""), "")] if x),
        dept=j.get("hauptberuf", ""),
        date=j.get("datumErsteVeroeffentlichung", ""),
        date_updated=j.get("aenderungsdatum", ""),
        url=url, apply_url=j.get("externeURL") or url,
        id=ref,
        country=",".join(ccs),
        source="gov/arbeitsagentur",
    )


def pages(q, state=None):
    if q.countries and COUNTRY not in q.countries:
        return
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        params = {"was": kws[ki] or None, "size": PAGE,
                  "veroeffentlichtseit": q.recent_days if 0 < q.recent_days <= 100 else None}
        page = st.get("page", 1) if st.get("k") == ki else 1
        while True:
            d = get_json(API, dict(params, page=page), headers=HEADERS)
            rows = d.get("ergebnisliste") or []
            total = int(d.get("maxErgebnisse") or 0)
            last = len(rows) < PAGE or page * PAGE >= total or page >= MAX_PAGES
            if last and page >= MAX_PAGES and total > page * PAGE:
                sys.stderr.write(f"[!] Arbeitsagentur「{kws[ki]}」共 {total} 条，只能翻到前 {page * PAGE} 条，请用更具体的关键词\n")
            page += 1
            yield [to_rec(j) for j in rows], ({"k": ki + 1} if last else {"k": ki, "page": page})
            if last:
                break
        st = {}
