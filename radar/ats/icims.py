"""iCIMS：{slug}.icims.com/sitemap.xml 列出全部在招职位，逐岗读职位页（in_iframe=1）里的 schema.org JobPosting。

注意：iCIMS 页面里的 datePosted 是「当前时间减两年」生成的，不是真实发布日期，这里不用；
日期改用 sitemap 里每个职位的 lastmod（最后修改时间，接近发布或更新日期）。"""
import re
import xml.etree.ElementTree as ET

from ..http import get_text
from ..schema import rec
from . import _jsonld


def _local(tag):
    return tag.rsplit("}", 1)[-1]   # 去掉命名空间前缀


def _sitemap(xml, host):
    """sitemap → [(职位链接, 职位号, lastmod)]。按 XML 解析，标签之间有换行、带命名空间都能认。"""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        raise ValueError(f"iCIMS sitemap 不是合法 XML：{e}")
    pat = re.compile(re.escape(host) + r"/jobs/(\d+)/[^\s<]*/job")
    rows = []
    for url in root.iter():
        if _local(url.tag) != "url":
            continue
        loc = lastmod = ""
        for child in url:
            name = _local(child.tag)
            if name == "loc":
                loc = (child.text or "").strip()
            elif name == "lastmod":
                lastmod = (child.text or "").strip()
        m = pat.fullmatch(loc)
        if m:
            rows.append((loc, m.group(1), lastmod))
    return rows


def fetch(slug, meta=None):
    host = f"https://{slug}.icims.com"
    rows = _sitemap(get_text(host + "/sitemap.xml"), host)
    got = _jsonld.details([u + "?in_iframe=1" for u, _, _ in rows])
    out = []
    for url, jid, lastmod in rows:
        jp = got.get(url + "?in_iframe=1")
        r = _jsonld.to_rec(jp, url, id=jid) if jp else rec(url=url, id=jid,
                                                          title=url.rsplit("/", 2)[-2].replace("-", " ").title())
        r.update(date=lastmod or "", date_updated=lastmod or "", url=url, apply_url=url)
        out.append(r)
    return out, f"icims/{slug}"
