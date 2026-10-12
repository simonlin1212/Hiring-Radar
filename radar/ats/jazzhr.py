"""JazzHR：{slug}.applytojob.com/apply/ 公开职位板（美国小企业多）。列表页只有链接，逐岗读职位页里的
schema.org JobPosting，拿 JD、发布日期、地点、雇佣类型。"""
import re

from ..http import get_text
from ..schema import rec, strip_html
from . import _jsonld


def fetch(slug, meta=None):
    host = f"https://{slug}.applytojob.com"
    html = get_text(host + "/apply/")
    links = {}
    for m in re.finditer(r'href="(' + re.escape(host) + r'/apply/([A-Za-z0-9]{6,20})/[^"#?]*)"[^>]*>(.*?)</a>', html, re.S):
        links.setdefault(m.group(2), (m.group(1), strip_html(m.group(3))))
    got = _jsonld.details([u for u, _ in links.values()])
    out = []
    for code_, (url, title) in links.items():
        jp = got.get(url)
        out.append(_jsonld.to_rec(jp, url, id=code_, apply_url=url) if jp else
                   rec(title=title, url=url, apply_url=url, id=code_))
    return [r for r in out if r["title"]], f"jazzhr/{slug}"
