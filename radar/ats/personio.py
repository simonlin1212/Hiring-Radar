"""Personio：{slug}.jobs.personio.(de|com)/xml 公开免鉴权 XML feed；含 createdAt + 完整 jobDescriptions。
没传 host 时自动试 .de → .com（用哪个有岗用哪个）。"""
import re
import xml.etree.ElementTree as ET

from ..http import get_text
from ..schema import rec, strip_html


def _t(node, tag):
    e = node.find(tag)
    return (e.text or "").strip() if (e is not None and e.text) else ""


def _parse(h):
    try:
        txt = get_text(f"https://{h}/xml")
    except Exception:
        return []
    txt = re.sub(r'\sxmlns="[^"]*"', "", txt, count=1)  # 去默认命名空间，便于按 tag 直接查
    try:
        root = ET.fromstring(txt)
    except ET.ParseError:
        return []
    rows = []
    for pos in root.iter("position"):
        title = _t(pos, "name")
        jid = _t(pos, "id")
        if not title or not jid.isdigit():
            continue
        offices = []
        for off in pos.iter("office"):
            v = (off.text or "").strip()
            if v and v not in offices:
                offices.append(v)
        jd_parts = []
        for jd in pos.iter("jobDescription"):
            nm = jd.find("name")
            val = jd.find("value")
            seg = ((nm.text or "").strip() + ":\n") if (nm is not None and nm.text) else ""
            seg += strip_html(val.text) if (val is not None and val.text) else ""
            if seg.strip():
                jd_parts.append(seg.strip())
        url = f"https://{h}/job/{jid}"
        rows.append(rec(
            title=title,
            location=", ".join(offices),
            dept=_t(pos, "department") or _t(pos, "recruitingCategory"),
            type=_t(pos, "employmentType"),
            date=_t(pos, "createdAt"),
            req_id=jid, jd="\n\n".join(jd_parts),
            url=url, apply_url=url, id=jid,
        ))
    return rows


def fetch(slug, meta=None):
    host = (meta or {}).get("host", "")
    if host and not re.fullmatch(r"[a-z0-9-]+\.jobs\.personio\.(de|com)", host):
        host = ""  # 只接受 Personio 自己的域名（防 SSRF）
    for h in ([host] if host else [f"{slug}.jobs.personio.de", f"{slug}.jobs.personio.com"]):
        rows = _parse(h)
        if rows:
            return rows, f"personio/{slug}"
    return [], f"personio/{slug}"
