#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser：宇树科技(Unitree) 自建招聘 API → JSON(stdout)。

宇树官方招聘页(www.unitree.com/cn/position/)是 Next.js SPA，岗位数据走
api.unitree.com/website/job/list?perPage=N。该接口要求【标准浏览器请求头】(完整
Chrome UA + Origin/Referer + Accept)才返回 JSON，否则只回 SPA 外壳 HTML——本脚本
按浏览器同样的请求头读取，无需 cookie/登录、不破解登录/鉴权/验证码。纯自用研究、低频、只读岗位。

用法:  python3 unitree.py [keyword] [pages]
       keyword 可空(取全部)；接口一次返回全量，pages 仅占位兼容。
输出:  JSON 数组，每条 {title, company, location, dept, type, date, comp, jd, url, id}
"""
import os
import sys
import json
import ssl
import calendar
import time
import unicodedata
import urllib.request

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
API = "https://api.unitree.com/website/job/list"
HEAD = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Origin": "https://www.unitree.com",
    "Referer": "https://www.unitree.com/",
}
# cityId 用电话区号，自建站只列了杭州；其余主要科技城市预映射，未知则回落原编码
CITY = {"0571": "杭州", "010": "北京", "021": "上海", "0755": "深圳", "0769": "东莞",
        "028": "成都", "029": "西安", "027": "武汉", "025": "南京", "0512": "苏州",
        "020": "广州", "0571,010": "杭州, 北京"}
CAT = {"YS-CATEGORY-1": "研发", "YS-CATEGORY-2": "销售服务"}
RTYPE = {"1": "校招", "2": "社招"}


def _to_ms(s):
    """'2026/06/01' → epoch ms（雷达 _fmt_date 按 epoch 渲染 YYYY-MM-DD）。"""
    try:
        return int(calendar.timegm(time.strptime(s, "%Y/%m/%d")) * 1000)
    except Exception:
        return s or ""


def _rtype(code):
    parts = [RTYPE.get(t.strip(), t.strip()) for t in str(code).split(",") if t.strip()]
    # 去重保序（"2,1"/"1,2" 归一）
    seen, uniq = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return "/".join(uniq)


def fetch(keyword="", pages=1, per=200):
    req = urllib.request.Request(f"{API}?perPage={per}", headers=HEAD)
    d = json.load(urllib.request.urlopen(req, timeout=25, context=CTX))
    items = ((d.get("data") or {}).get("items")) or []
    out = []
    for j in items:
        # NFKC 归一化：宇树 JD/标题混用康熙部首等异体字(⾝→身/⼯→工)，否则关键词匹配失效
        title = unicodedata.normalize("NFKC", j.get("title", "") or "")
        jd = unicodedata.normalize(
            "NFKC", "\n\n".join(x for x in [j.get("duty", ""), j.get("ability", "")] if x))
        if keyword and keyword.lower() not in (title + " " + jd).lower():
            continue
        sal = (j.get("salary") or "").strip()
        out.append({
            "title": title,
            "company": "宇树科技",
            "location": CITY.get(str(j.get("cityId", "")), str(j.get("cityId", ""))),
            "dept": CAT.get(j.get("categoryId", ""), j.get("categoryId", "") or ""),
            "type": _rtype(j.get("type", "")),
            "date": _to_ms(j.get("postTime", "")),
            "comp": (sal + "K") if sal and sal[0].isdigit() else sal,
            "jd": jd,
            "url": "https://www.unitree.com/cn/position/" + str(j.get("id", "")),
            "id": str(j.get("id", "")),
        })
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
