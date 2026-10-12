"""Jobvite：jobs.jobvite.com/{slug} 公开职位页。列表取链接和部门，逐岗读 schema.org JobPosting 拿 JD、发布日期、薪资。"""
import re

from ..http import get_text
from ..schema import rec, strip_html
from . import _jsonld


def fetch(slug, meta=None):
    base = "https://jobs.jobvite.com"
    html = get_text(f"{base}/{slug}")
    if "jv-job-list" not in html and "/job/" not in html:
        return [], f"jobvite/{slug}"   # 账号不存在时会跳到 Jobvite 帮助页
    links, dept = {}, ""
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>|href="(/' + re.escape(slug) + r'/job/([A-Za-z0-9]{5,20}))"[^>]*>(.*?)</a>',
                         html, re.S):
        if m.group(1) is not None:
            dept = strip_html(m.group(1))
        elif m.group(3) not in links:
            links[m.group(3)] = (base + m.group(2), strip_html(m.group(4)), dept)
    got = _jsonld.details([u for u, _, _ in links.values()])
    out = []
    for code_, (url, title, d) in links.items():
        jp = got.get(url)
        r = _jsonld.to_rec(jp, url, id=code_, apply_url=url + "/apply") if jp else \
            rec(title=title, url=url, apply_url=url + "/apply", id=code_)
        r["dept"] = d or r["dept"]
        out.append(r)
    return out, f"jobvite/{slug}"
