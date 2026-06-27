#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：Moka 摩卡(国产ATS)通用 → JSON(stdout)。

所有 Moka 租户共用同一接口，只换 orgId+siteId（都在社招页 URL /social-recruitment/{orgId}/{siteId} 里）。
响应 AES-128-CBC 加密：key=响应里的 necromancer，IV=全局常量。列表接口已含 完整JD+地点+部门+日期+薪资，无需逐岗详情。
用法: python3 moka.py <orgId> <siteId> <company> [keyword] [pages]
  例:  python3 moka.py yostar 145292 悠星
"""
import os
import sys, json, re, ssl, base64, html as _html, urllib.request
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError:
    sys.exit("[moka] 需要 pycryptodome 才能解密 Moka 响应：pip install pycryptodome")

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
IV = b"de7c21ed8d6f50fe"
H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "Content-Type": "application/json",
     "Accept": "application/json", "Origin": "https://app.mokahr.com"}
API = "https://app.mokahr.com/api/outer/ats-apply/website/jobs/v2"


def _strip(s):
    if not s:
        return ""
    t = re.sub(r"(?i)<br\s*/?>", "\n", str(s))
    t = re.sub(r"(?i)</(p|li|div|h[1-6])>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()


def _decrypt(d):
    if isinstance(d, dict) and "data" in d and "necromancer" in d:
        key = d["necromancer"].encode()
        if len(key) not in (16, 24, 32):
            raise RuntimeError(f"[moka] 解密失败：necromancer 密钥长度异常({len(key)})，接口可能已改版")
        try:
            pt = unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(base64.b64decode(d["data"])), 16)
            return json.loads(pt.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"[moka] AES 解密/解析失败：{type(e).__name__}: {e}（接口或加密方案可能已变）")
    return d


def _call(org, site, limit, offset):
    body = {"orgId": org, "siteId": int(site), "locale": "zh-CN", "limit": limit, "offset": offset}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=H)
    return _decrypt(json.load(urllib.request.urlopen(req, timeout=25, context=CTX)))


def _jobs(resp):
    data = resp.get("data") if isinstance(resp, dict) else resp
    if isinstance(data, dict):
        return data.get("jobs") or data.get("list") or []
    return data if isinstance(data, list) else []


def fetch(org, site, company, keyword="", pages=10, limit=50):
    out = []
    for pg in range(pages):
        jobs = _jobs(_call(org, site, limit, pg * limit))
        if not jobs:
            break
        for j in jobs:
            jid = str(j.get("id", ""))
            locs = ", ".join(x.get("cityName", "") for x in (j.get("locations") or [])
                             if isinstance(x, dict) and x.get("cityName"))
            dep = j.get("department") or {}
            mn, mx = j.get("minSalary"), j.get("maxSalary")
            comp = f"{mn}-{mx}" if (mn or mx) else ""
            out.append({
                "title": j.get("title", ""),
                "company": company,
                "location": locs,
                "dept": dep.get("name", "") if isinstance(dep, dict) else "",
                "type": j.get("commitment", ""),
                "date": j.get("publishedAt") or j.get("createdAt") or j.get("openedAt", ""),
                "comp": comp,
                "jd": _strip(j.get("jobDescription", "")),
                "url": f"https://app.mokahr.com/social-recruitment/{org}/{site}/job/{jid}",
                "id": jid,
            })
        if len(jobs) < limit:
            break
    return out


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("用法: moka.py <orgId> <siteId> <company> [keyword] [pages]")
    org, site, company = sys.argv[1], sys.argv[2], sys.argv[3]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", org) or not str(site).isdigit():
        sys.exit("[moka] orgId 应为字母数字/连字符、siteId 应为纯数字")
    kw = sys.argv[4] if len(sys.argv) > 4 else ""
    pg = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    print(json.dumps(fetch(org, site, company, kw, pg), ensure_ascii=False))
