"""Zoho Recruit：{slug}.zohorecruit.com/jobs/Careers/rss 公开 RSS，含完整 JD 和发布时间。公司已撤下职位页时返回空。"""
import xml.etree.ElementTree as ET

from ..http import get_text
from ..schema import iso_day, rec, strip_html


def _t(node, tag):
    e = node.find(tag)
    return (e.text or "").strip() if e is not None and e.text else ""


def fetch(slug, meta=None):
    txt = get_text(f"https://{slug}.zohorecruit.com/jobs/Careers/rss").strip()
    if not txt.startswith("<"):
        return [], f"zohorecruit/{slug}"   # 「joblist has been removed」之类的纯文本
    root = ET.fromstring(txt)
    ch = root.find("channel")
    company = _t(ch, "title").rsplit(" - Careers", 1)[0] if ch is not None else ""
    out = []
    for it in root.iter("item"):
        link = _t(it, "link").replace("?source=RSS", "")
        out.append(rec(
            title=_t(it, "title"), company=company,
            date=iso_day(_t(it, "pubDate")),
            jd=strip_html(_t(it, "description")),
            url=link, apply_url=link, id=_t(it, "guid"),
        ))
    return out, f"zohorecruit/{slug}"
