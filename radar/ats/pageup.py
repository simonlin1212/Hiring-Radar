"""PageUp：澳洲的招聘系统（澳新零售、大学、政府常用）。公开职位板 {host}/{instance}/{clientkey}/en/listing/，
列表取标题、地点、简介，逐岗读职位页拿完整 JD、工作类型和发布日期（Advertised）。名录里有 host/instance/clientkey。"""
import re
import sys

from ..http import Blocked, RateLimited, get_text
from ..schema import rec, strip_html

HOST = re.compile(r"(careers|careersmanager|careersite)\.pageuppeople\.com")
CAP = 150


def _detail(html):
    """职位页 → (JD, 工作类型, 发布日期)。正文在 id="job-content" 里，到「返回/申请」按钮为止。"""
    m = re.search(r'id="job-content"[^>]*>(.*?)<a[^>]*class="[^"]*(?:back-link|apply-link)', html, re.S)
    body = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>|<!--.*?-->", " ", m.group(1) if m else "")
    body = re.sub(r"(?s)<div class='jobdets'>.*?</p>", " ", body, count=1)   # 去掉开头的编号/类型/地点栏
    wt = re.search(r'<span class="work-type[^"]*">([^<]*)</span>', html)
    adv = re.search(r'class="open-date">\s*<time datetime="([^"]+)"', html)
    return strip_html(body)[:20000], (wt.group(1).strip() if wt else ""), (adv.group(1) if adv else "")


def fetch(slug, meta=None):
    meta = meta or {}
    host, inst, key = meta.get("host", ""), meta.get("instance", ""), meta.get("clientkey", "")
    if not (HOST.fullmatch(host) and inst.isdigit() and re.fullmatch(r"[A-Za-z0-9]{1,20}", key)):
        raise ValueError("PageUp 需要 host/instance/clientkey（名录里有），先 --directory-update 再按公司名查")
    base = f"https://{host}/{inst}/{key}/en"
    rows, seen = [], set()
    for page in range(1, 51):
        html = get_text(base + "/listing/", {"page": page, "page-items": 100} if page > 1 else {"page-items": 100})
        new = 0
        for li in re.split(r'<li class="[^"]*jobbox|<tr', html)[1:]:
            m = re.search(r'class="job-link"[^>]*href="(/' + inst + "/" + key + r'/en/job/(\d+)/[^"]*)"[^>]*>(.*?)</a>', li, re.S) \
                or re.search(r'href="(/' + inst + "/" + key + r'/en/job/(\d+)/[^"]*)"[^>]*class="job-link"[^>]*>(.*?)</a>', li, re.S)
            if not m or m.group(2) in seen:
                continue
            seen.add(m.group(2))
            new += 1
            loc = re.search(r'class="location"[^>]*>(.*?)</span>', li, re.S)
            summ = re.search(r'class="[^"]*pup-summary[^"]*"[^>]*>(.*?)</div>', li, re.S)
            url = f"https://{host}{m.group(1)}"
            rows.append(rec(title=strip_html(m.group(3)), location=strip_html(loc.group(1)) if loc else "",
                            jd=strip_html(summ.group(1)) if summ else "", url=url, apply_url=url, id=m.group(2)))
        if not new:
            break
    for r in rows[:CAP]:
        try:
            jd, wt, adv = _detail(get_text(r["url"]))
        except (Blocked, RateLimited):
            raise
        except Exception:
            continue
        r["jd"] = jd or r["jd"]
        r["type"] = wt
        r["date"] = adv
    if len(rows) > CAP:
        sys.stderr.write(f"[i] PageUp {slug}: 前 {CAP} 个岗位抓了 JD，其余只有简介\n")
    return rows, f"pageup/{slug}"
