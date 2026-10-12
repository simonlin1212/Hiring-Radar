"""RemoteOK：公开 JSON（远程岗，约 100 条最新）。"""
from ..http import get_json
from ..schema import rec, strip_html
from . import single_page

NAME = "remoteok"
DESC = "RemoteOK 远程岗"
FILTERS = set()


def fetch():
    d = get_json("https://remoteok.com/api")
    out = []
    for j in (d if isinstance(d, list) else []):
        if not isinstance(j, dict) or not j.get("position"):
            continue  # 跳过首个元数据对象
        smin, smax = j.get("salary_min") or 0, j.get("salary_max") or 0
        out.append(rec(
            title=j.get("position", ""),
            company=j.get("company", ""),
            location=j.get("location", "") or "Remote",
            remote="Remote",
            team=", ".join(j.get("tags") or []),
            date=j.get("date", ""),
            comp=f"${smin}-{smax}" if (smin or smax) else "",
            jd=strip_html(j.get("description", "")),
            url=j.get("url", ""), apply_url=j.get("apply_url") or j.get("url", ""),
            id=str(j.get("id") or j.get("slug", "")),
            source="board/remoteok",
        ))
    return out, "board/remoteok"


pages = single_page(fetch)
