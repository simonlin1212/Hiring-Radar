"""Remotive：公开 JSON（远程岗）。"""
from ..http import get_json
from ..schema import rec, strip_html
from . import single_page

NAME = "remotive"
DESC = "Remotive 远程岗"
FILTERS = set()


def fetch():
    d = get_json("https://remotive.com/api/remote-jobs")
    out = []
    for j in (d.get("jobs") or []):
        out.append(rec(
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("candidate_required_location", ""),
            remote="Remote",
            dept=j.get("category", ""),
            type=j.get("job_type", ""),
            date=j.get("publication_date", ""),
            comp=j.get("salary", ""),
            jd=strip_html(j.get("description", "")),
            url=j.get("url", ""), apply_url=j.get("url", ""),
            id=str(j.get("id", "")),
            source="board/remotive",
        ))
    return out, "board/remotive"


pages = single_page(fetch)
