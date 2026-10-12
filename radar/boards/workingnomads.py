"""WorkingNomads：公开 JSON（远程岗）。"""
from ..http import get_json
from ..schema import rec, strip_html
from . import single_page

NAME = "workingnomads"
DESC = "WorkingNomads 远程岗"
FILTERS = set()


def fetch():
    d = get_json("https://www.workingnomads.com/api/exposed_jobs/")
    rows = d if isinstance(d, list) else (d.get("jobs") or [])
    out = []
    for j in rows:
        url = j.get("url", "")
        tags = j.get("tags")
        out.append(rec(
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("location", ""),
            remote="Remote",
            dept=j.get("category_name", ""),
            team=tags if isinstance(tags, str) else ", ".join(tags or []),
            date=j.get("pub_date", ""),
            jd=strip_html(j.get("description", "")),
            url=url, apply_url=url,
            id=str(j.get("id") or url),
            source="board/workingnomads",
        ))
    return out, "board/workingnomads"


pages = single_page(fetch)
