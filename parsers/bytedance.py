#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hiring_radar local-parser 示例：字节跳动官方招聘 API → JSON(stdout)。

演示「中国官方/自建招聘页」如何接入 hiring_radar v2 的 local-parser 机制：
脚本自己负责抓取，把岗位以 JSON 数组打到 stdout，hiring_radar 负责过滤/聚合/输出。

用法:  python3 bytedance.py [keyword] [pages]
       keyword 可空(取全部，分页前 pages 页)；pages 默认 4(每页 30 ≈ 120 岗)
输出:  JSON 数组，每条 {title, company, location, dept, date, jd, url, id}

⚠️ 纯自用研究。字节用自建招聘系统，此接口为其前端公开调用的搜索 API。
"""
import os
import sys
import json
import urllib.error

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 仓库根目录
from radar.http import BROWSER_UA, Blocked, post_json  # noqa: E402  统一联网：限速、429 退避、被拦就停
API = "https://jobs.bytedance.com/api/v1/search/job/posts"
# 字节招聘网关只认浏览器 UA（如实报身份一律回 405），这里沿用 v1 的浏览器 UA；README 已写明这个例外
HEAD = {"User-Agent": BROWSER_UA, "portal-channel": "office", "portal-platform": "pc"}


def fetch(keyword="", pages=4, limit=30):
    out = []
    for p in range(pages):
        body = {
            "keyword": keyword, "limit": limit, "offset": p * limit,
            "job_category_id_list": [], "location_code_list": [],
            "subject_id_list": [], "recruitment_id_list": [],
        }
        try:
            d = post_json(API, body, headers=HEAD)
        except urllib.error.HTTPError as e:
            if e.code == 405:   # 网关拒绝：当作被拦，停下
                raise Blocked("字节跳动招聘网关拒绝请求（HTTP 405），停止")
            raise
        posts = ((d.get("data") or {}).get("job_post_list")) or []
        if not posts:
            break
        for j in posts:
            jid = str(j.get("id", ""))
            city = (j.get("city_info") or {}).get("name", "")
            cat = j.get("job_category") or {}
            dept = cat.get("name", "") if isinstance(cat, dict) else ""
            jd = "\n\n".join(x for x in [j.get("description", ""), j.get("requirement", "")] if x)
            out.append({
                "title": j.get("title", ""),
                "company": "字节跳动",
                "location": city,
                "dept": dept,
                "date": j.get("publish_time", ""),   # epoch ms 或空
                "jd": jd,
                "url": f"https://jobs.bytedance.com/experienced/position/{jid}/detail",
                "id": jid,
            })
        if len(posts) < limit:
            break
    return out


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    pg = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    print(json.dumps(fetch(kw, pg), ensure_ascii=False))
