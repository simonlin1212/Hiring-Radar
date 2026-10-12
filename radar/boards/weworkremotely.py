"""WeWorkRemotely：RSS。item 标题是「公司: 职位」，拆开取雇主。"""
import re
import xml.etree.ElementTree as ET

from ..http import get_text
from ..schema import rec, strip_html
from . import single_page

NAME = "weworkremotely"
DESC = "WeWorkRemotely 远程岗"
FILTERS = set()


def _t(node, tag):
    e = node.find(tag)
    return (e.text or "").strip() if (e is not None and e.text) else ""


def fetch():
    txt = get_text("https://weworkremotely.com/remote-jobs.rss")
    txt = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", txt)  # 去命名空间声明
    txt = re.sub(r'(</?)\w+:', r'\1', txt)            # 去标签前缀(media:/dc: 等)，否则 ET 报 unbound prefix
    out = []
    try:
        root = ET.fromstring(txt)
    except ET.ParseError:
        return out, "board/weworkremotely"
    for it in root.iter("item"):
        raw_title = _t(it, "title")
        company, sep, role = raw_title.partition(": ")
        if not sep:
            company, role = "", raw_title
        link = _t(it, "link")
        out.append(rec(
            title=role,
            company=company,
            location=", ".join(x for x in [_t(it, "region"), _t(it, "country"), _t(it, "state")] if x),
            remote="Remote",
            dept=_t(it, "category"),
            type=_t(it, "type"),
            date=_t(it, "pubDate"),
            jd=strip_html(_t(it, "description")),
            url=link, apply_url=link,
            id=_t(it, "guid") or link,
            source="board/weworkremotely",
        ))
    return out, "board/weworkremotely"


pages = single_page(fetch)
