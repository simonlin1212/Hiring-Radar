"""CareerPlug：{slug}.careerplug.com/jobs 公开职位板（加盟连锁店多，一家门店一个账号）。
从列表卡片取标题、地点、发布日期（每页约 30 条），没有 JD。"""
import re
from datetime import datetime

from ..http import get_text
from ..schema import rec, strip_html

_CARD = re.compile(r'<a[^>]*href="/jobs/(\d+)"[^>]*>(.*?)</a>', re.S)


def _field(block, cls):
    """卡片里某一栏的文字（去掉手机版才显示的「Location:」之类小标题）。"""
    if cls == "job-title":
        m = re.search(r'<span class="name">(.*?)</span>', block, re.S)
        return strip_html(m.group(1)) if m else ""
    m = re.search(r'class="' + cls + r'[^"]*">\s*<div>(.*?)</div>', block, re.S)
    if not m:
        return ""
    return strip_html(re.sub(r"<span class='job-row-title[^>]*>.*?</span>", "", m.group(1), flags=re.S))


def _loc(s):
    m = re.fullmatch(r"([A-Z]{2})-(.+?)-(\d{5})", s.strip())   # VT-South Burlington-05403 → South Burlington, VT
    return f"{m.group(2).title()}, {m.group(1)}" if m else s


def _date(s):
    try:
        return datetime.strptime(s.strip(), "%m-%d-%y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def fetch(slug, meta=None):
    base = f"https://{slug}.careerplug.com"
    out, seen, last = [], set(), 1
    for page in range(1, 201):
        html = get_text(base + "/jobs", {"page": page} if page > 1 else None)
        if page == 1:
            last = max([1] + [int(x) for x in re.findall(r"[?&]page=(\d+)", html)])
        for m in _CARD.finditer(html):
            jid, block = m.group(1), m.group(2)
            if jid in seen or "job-title" not in block:
                continue
            seen.add(jid)
            url = f"{base}/jobs/{jid}"
            out.append(rec(title=_field(block, "job-title"), location=_loc(_field(block, "job-location")),
                           date=_date(_field(block, "job-post-date")), url=url, apply_url=url, id=jid))
        if page >= last:
            break
    return out, f"careerplug/{slug}"
