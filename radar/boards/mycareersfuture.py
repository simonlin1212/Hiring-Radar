"""新加坡政府求职网 MyCareersFuture（劳动力发展局 WSG）：全国在招职位，公开搜索接口，免注册。
列表里有职位名、公司、薪资（新加坡要求标薪资）、类别、发布日期；没有 JD 正文。
单次查询最多翻 100 页（1 万条，再往后接口直接拒绝），更多请用具体关键词。"""
import sys

from ..http import post_json
from ..schema import rec

NAME = "mycareersfuture"
DESC = "新加坡政府求职网 MyCareersFuture（全国，可按关键词，有薪资，无 JD）"
FILTERS = {"keyword"}
COUNTRY = "SG"
API = "https://api.mycareersfuture.gov.sg/v2/search"
PAGE, MAX_PAGES = 100, 100


def to_rec(j):
    m = j.get("metadata") or {}
    a = j.get("address") or {}
    s = j.get("salary") or {}
    comp = ""
    if (s.get("minimum") or s.get("maximum")) and not m.get("isHideSalary"):
        comp = f"SGD {s.get('minimum', '')}-{s.get('maximum', '')}/{((s.get('type') or {}).get('salaryType') or '').lower()}"
    dist = a.get("districts") or [{}]
    url = m.get("jobDetailsUrl") or f"https://www.mycareersfuture.gov.sg/job/{j.get('uuid', '')}"
    return rec(
        title=j.get("title", ""),
        company=((j.get("hiringCompany") or {}).get("name") or (j.get("postedCompany") or {}).get("name") or ""),
        location=", ".join(x for x in [a.get("building"), (dist[0] or {}).get("region")] if x) or "Singapore",
        type=", ".join(t.get("employmentType", "") for t in j.get("employmentTypes") or []),
        dept=", ".join(c.get("category", "") for c in j.get("categories") or []),
        team=", ".join(p.get("position", "") for p in j.get("positionLevels") or []),
        date=m.get("newPostingDate", ""),
        date_updated=m.get("updatedAt", ""),
        comp=comp,
        url=url, apply_url=url,
        id=m.get("jobPostId") or j.get("uuid", ""),
        country=COUNTRY,
        agency="posted on behalf" if m.get("isPostedOnBehalf") else "",
        source="gov/mycareersfuture",
    )


def pages(q, state=None):
    if q.countries and COUNTRY not in q.countries:
        return
    st = dict(state or {})
    kws = q.keywords or [""]
    for ki in range(st.get("k", 0), len(kws)):
        body = {"sortBy": ["new_posting_date"]}
        if kws[ki]:
            body["search"] = kws[ki]
        page = st.get("page", 0) if st.get("k") == ki else 0
        while True:
            d = post_json(f"{API}?limit={PAGE}&page={page}", body)
            rows = d.get("results") or []
            page += 1
            total = d.get("total") or 0
            last = len(rows) < PAGE or page * PAGE >= total or page >= MAX_PAGES
            if last and page >= MAX_PAGES and total > page * PAGE:
                sys.stderr.write(f"[!] MyCareersFuture「{kws[ki]}」共 {total} 条，只能翻到前 {page * PAGE} 条，请用更具体的关键词\n")
            yield [to_rec(j) for j in rows], ({"k": ki + 1} if last else {"k": ki, "page": page})
            if last:
                break
        st = {}
