"""Teamtailor：{slug}.teamtailor.com/jobs.rss 公开 RSS（北欧和欧洲中小企业多），含完整 JD、发布时间、部门、地点和国家。"""
import xml.etree.ElementTree as ET

from ..countries import code
from ..http import get_text
from ..schema import iso_day, rec, strip_html

TT = "{https://teamtailor.com/locations}"


def _t(node, tag):
    e = node.find(tag)
    return (e.text or "").strip() if e is not None and e.text else ""


def fetch(slug, meta=None):
    root = ET.fromstring(get_text(f"https://{slug}.teamtailor.com/jobs.rss"))
    out = []
    for it in root.iter("item"):
        locs, ccs = [], []
        for l in it.iter(TT + "location"):
            city, country = _t(l, TT + "city") or _t(l, TT + "name"), _t(l, TT + "country")
            t = ", ".join(x for x in [city, country] if x)
            if t and t not in locs:
                locs.append(t)
            cc = code(country)
            if cc and cc not in ccs:
                ccs.append(cc)
        rs = _t(it, "remoteStatus")
        link = _t(it, "link")
        out.append(rec(
            title=_t(it, "title"),
            dept=_t(it, TT + "department"),
            location="; ".join(locs),
            remote=rs.capitalize() if rs and rs != "none" else "",
            date=iso_day(_t(it, "pubDate")),
            jd=strip_html(_t(it, "description")),
            url=link, apply_url=link,
            id=_t(it, "guid"),
            country=",".join(ccs),
        ))
    return out, f"teamtailor/{slug}"
