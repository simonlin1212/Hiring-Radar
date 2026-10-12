"""iCIMS：{slug}.icims.com/sitemap.xml 列出全部在招职位，逐岗读职位页（in_iframe=1）里的 schema.org JobPosting。

注意：iCIMS 页面里的 datePosted 是「当前时间减两年」生成的，不是真实发布日期，这里不用；
日期改用 sitemap 里每个职位的 lastmod（最后修改时间，接近发布或更新日期）。"""
import re

from ..http import get_text
from ..schema import rec
from . import _jsonld


def fetch(slug, meta=None):
    host = f"https://{slug}.icims.com"
    xml = get_text(host + "/sitemap.xml")
    rows = re.findall(r"<loc>(" + re.escape(host) + r"/jobs/(\d+)/[^<]*/job)</loc>(?:<lastmod>([^<]*)</lastmod>)?", xml)
    got = _jsonld.details([u + "?in_iframe=1" for u, _, _ in rows])
    out = []
    for url, jid, lastmod in rows:
        jp = got.get(url + "?in_iframe=1")
        r = _jsonld.to_rec(jp, url, id=jid) if jp else rec(url=url, id=jid,
                                                          title=url.rsplit("/", 2)[-2].replace("-", " ").title())
        r.update(date=lastmod or "", date_updated=lastmod or "", url=url, apply_url=url)
        out.append(r)
    return out, f"icims/{slug}"
