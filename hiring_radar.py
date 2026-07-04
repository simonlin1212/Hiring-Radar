#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘信号雷达 (hiring_radar) — 读公司自己的招聘系统(ATS)直出在招岗位，做投资 / 产业领先信号。

原理：公司用的 ATS(Greenhouse/Ashby/Lever/Workday)都有【免费公开】API，可直接读整张在招板，
带 标题/部门/团队/地点/首发+更新日期/薪资区间/完整JD/链接。招聘往往比财报早几个月暴露战略方向。

⭐ 2026-06-26 起【全字段拉满，不做摘要】：以前只抽 5 个字段(标题/地点/部门/日期/链接)，现在把
   ATS 一次返回的【全部】信息都拉下来——尤其【完整 JD + 薪资区间 + 首发日期】(Greenhouse/Ashby/Lever
   免费带回)。数据量很小但信息密度翻几倍，够做深度分析。--json 出全量；终端只打可读摘要。

覆盖：
- 前沿创业/scaleup（用 GH/Ashby/Lever）→ 按公司名自动命中（Figure/1X/Anthropic/OpenAI/Scale…）→ 全 JD+薪资 免费
- 大盘巨头（用 Workday）→ 需内置端点（已含 Nvidia）；列表级全字段，JD 需 --jd 逐岗抓
- ⚠️ A股公司用智联/BOSS直聘，不在覆盖内 —— 这是盯【全球龙头动向→A股传导】的工具

用法:
  hiring_radar.py figure                         # GH/Ashby/Lever：默认就含完整 JD + 薪资
  hiring_radar.py 1x --json > 1x.json            # 全量结构化(含 JD/薪资/日期)，喂给后续分析
  hiring_radar.py nvidia --keyword HBM,packaging  # 关键词过滤(同时搜 标题/部门/地点/JD/薪资)
  hiring_radar.py --greenhouse <slug> / --ashby <slug> / --lever <slug>
  hiring_radar.py --smartrecruiters <slug> / --recruitee <slug> / --breezy <slug> / --bamboohr <slug> / --personio <slug>   # v2 新增
  hiring_radar.py --workday host,tenant,site [--jd]

  hiring_radar.py --board remoteok --keyword AI         # 聚合板模式(跨公司广撒网，给"哪里招人")
  hiring_radar.py --board all --keyword robotics --json  # 4 个远程板合并抓 → 喂分析

v2 变更：
  Tier1 在 GH/Ashby/Lever/Workday 之外补了 5 个公开匿名 ATS（SmartRecruiters/Recruitee/Breezy/BambooHR/Personio），
        auto-probe 链同步扩展（探测公司名时多试这 5 个）。
  Tier2 新增聚合板模式 --board（remoteok/remotive/weworkremotely/workingnomads/all）：跨公司一次拉回，
        用 company 字段承载雇主，终端摘要按"公司 Top"聚合。schema 增 company 字段(共 15)，其余设计哲学不变。
        仍单文件、纯标准库零依赖。

需联网（西方端点，本机走代理即可）。
"""
import os
import sys
import json
import re
import ssl
import html as _html
import argparse
import subprocess
import urllib.request
from collections import Counter
from datetime import datetime, timezone

__version__ = "1.1.0"

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
_DEBUG = False  # --debug 时打印 auto-probe 被吞的异常

# 内置：投资相关公司 → ATS 配置（已实测命中）。新公司加一行即可。
# greenhouse/ashby/lever: ("kind", slug)；workday: ("workday", host, tenant, site)
COMPANIES = {
    "figure":    ("greenhouse", "figureai"),   # 人形 Figure AI（注意 greenhouse/figure 是金融科技公司，别用）
    "figureai":  ("greenhouse", "figureai"),
    "1x":        ("ashby", "1x"),
    "anthropic": ("greenhouse", "anthropic"),
    "openai":    ("ashby", "openai"),
    "scale":     ("greenhouse", "scaleai"),
    "scaleai":   ("greenhouse", "scaleai"),
    "nvidia":    ("workday", "nvidia.wd5.myworkdayjobs.com", "nvidia", "NVIDIAExternalCareerSite"),
}

# 本地解析器（v2 Tier3）：解析【自建 / 中国官方企业招聘页】等无标准 ATS 的来源。
# 机制：spawn 一个本地脚本(放 parsers/ 下)，脚本自己抓页面 + 把岗位 JSON 打到 stdout，本工具解析+过滤+汇总。
# 安全：command 只能是已知解释器或 PARSER_ROOT 内文件；解释器情形第一个参数须为 root 内脚本(禁内联代码)；不用 shell。
PARSER_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_INTERP = {"python3", "python", "node", "deno", "bun", "sh", "bash"}
_EXT_INTERP = {".py": "python3", ".mjs": "node", ".js": "node", ".sh": "bash", ".ts": "deno"}
LOCAL_PARSERS = {
    # name → {command, args:[...]}；args 里 {keyword}/{company} 会被替换。脚本输出 JSON 数组或 {jobs:[...]}。
    # --- 大厂自建站（一家一个 parser）---
    "bytedance": {"command": "python3", "args": ["parsers/bytedance.py", "{keyword}"]},
    "tencent":   {"command": "python3", "args": ["parsers/tencent.py", "{keyword}"]},
    "netease":   {"command": "python3", "args": ["parsers/netease.py", "{keyword}"]},
    "jd":        {"command": "python3", "args": ["parsers/jd.py", "{keyword}"]},
    "baidu":     {"command": "python3", "args": ["parsers/baidu.py", "{keyword}"]},
    "unitree":   {"command": "python3", "args": ["parsers/unitree.py", "{keyword}"]},
    # --- 飞书招聘（通用 parser，每家=门户域名+公司名；新增公司只加一行）---
    "nio":       {"command": "python3", "args": ["parsers/feishu.py", "nio.jobs.feishu.cn", "蔚来", "{keyword}"]},
    "xpeng":     {"command": "python3", "args": ["parsers/feishu.py", "xiaopeng.jobs.feishu.cn", "小鹏", "{keyword}"]},
    "bambulab":  {"command": "python3", "args": ["parsers/feishu.py", "bambulab.jobs.feishu.cn", "拓竹", "{keyword}"]},
    "momenta":   {"command": "python3", "args": ["parsers/feishu.py", "momenta.jobs.feishu.cn", "Momenta", "{keyword}"]},
    "boke":      {"command": "python3", "args": ["parsers/feishu.py", "boke.jobs.feishu.cn", "波克城市", "{keyword}"]},
    # --- Moka 摩卡（通用 parser，每家=orgId+siteId+公司名）---
    "yostar":    {"command": "python3", "args": ["parsers/moka.py", "yostar", "145292", "悠星", "{keyword}"]},
    "tesla-cn":  {"command": "python3", "args": ["parsers/moka.py", "tesla", "46129", "特斯拉中国", "{keyword}"]},
}

# 统一输出 schema（字段缺失则为空字符串）。保留 title/location/dept/date/url 向后兼容。
# v2 加 company（雇主名）——聚合板跨公司必需；per-company 查询时为空。注意 company=雇主、comp=薪资，两个不同键。
FIELDS = ["title", "company", "dept", "team", "location", "remote", "type",
          "date", "date_updated", "req_id", "comp", "jd", "url", "apply_url", "id"]


def _rec(**kw):
    r = {k: "" for k in FIELDS}
    r.update({k: (v if v is not None else "") for k, v in kw.items()})
    return r


def _get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=CTX))


def _post(url, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={**UA, "Content-Type": "application/json", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=25, context=CTX))


def _get_text(url):
    """GET 取原始文本（给 XML/RSS 类 feed，如 Personio）。"""
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=25, context=CTX).read().decode("utf-8", "replace")


def _strip(s):
    """HTML → 纯文本（保留全长，不截断）。"""
    if not s:
        return ""
    t = re.sub(r"(?i)<br\s*/?>", "\n", str(s))
    t = re.sub(r"(?i)</(p|li|div|h[1-6])>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return t.strip()


def _fmt_date(d):
    if not d:
        return ""
    s = str(d)
    if s.isdigit():  # epoch（ms 或 s）→ YYYY-MM-DD
        try:
            ts = int(s)
            if ts > 1e12:  # 毫秒
                ts /= 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            return s[:16]
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    return m.group(0) if m else s[:16]


def _short(s, n=48):
    """终端显示截断（仅摘要用；--json 始终全量）。"""
    s = str(s or "")
    return s if len(s) <= n else s[:n - 1] + "…"


def _days_ago(d):
    """各种日期字符串 → 距今天数(int) 或 None。"""
    if not d:
        return None
    s = str(d)
    if s.isdigit():  # epoch（ms 或 s，与 _fmt_date 判定一致）
        try:
            ts = int(s)
            if ts > 1e12:  # 毫秒
                ts /= 1000
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return (datetime.now(timezone.utc) - dt).days
        except Exception:
            return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)  # ISO
    if m:
        try:
            dt = datetime.strptime(m.group(0), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - dt).days
        except Exception:
            return None
    sl = s.lower()  # Workday 相对日期
    if "today" in sl:
        return 0
    if "yesterday" in sl:
        return 1
    m = re.search(r"(\d+)\+?\s*day", sl)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\+?\s*month", sl)
    if m:
        return int(m.group(1)) * 30
    return None


# ---------- 各 ATS 全字段抓取 ----------

def fetch_greenhouse(slug):
    # content=true → 一次带回完整 JD（CA 等地的薪资区间也在 JD 正文里）
    d = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    out = []
    for j in d.get("jobs", []):
        out.append(_rec(
            title=j.get("title", ""),
            location=(j.get("location") or {}).get("name", ""),
            dept=", ".join(x.get("name", "") for x in (j.get("departments") or []) if isinstance(x, dict)),
            date=j.get("first_published") or j.get("updated_at", ""),
            date_updated=j.get("updated_at", ""),
            req_id=str(j.get("requisition_id") or j.get("internal_job_id") or ""),
            jd=_strip(j.get("content", "")),
            url=j.get("absolute_url", ""),
            apply_url=j.get("absolute_url", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"greenhouse/{slug}"


def fetch_ashby(slug):
    # includeCompensation=true → 带回薪资区间（含股权说明）；descriptionPlain = 完整 JD
    d = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
    out = []
    for j in d.get("jobs", []):
        comp = ""
        c = j.get("compensation")
        if isinstance(c, dict):
            comp = c.get("compensationTierSummary") or c.get("scrapeableCompensationSalarySummary") or ""
        out.append(_rec(
            title=j.get("title", ""),
            location=j.get("location", ""),
            dept=j.get("department", ""),
            team=j.get("team", ""),
            type=j.get("employmentType", ""),
            remote=("Remote" if j.get("isRemote") else (j.get("workplaceType", "") or "")),
            date=j.get("publishedAt", ""),
            req_id=str(j.get("id", "")),
            comp=comp,
            jd=j.get("descriptionPlain") or _strip(j.get("descriptionHtml", "")),
            url=j.get("jobUrl", ""),
            apply_url=j.get("applyUrl", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"ashby/{slug}"


def fetch_lever(slug):
    d = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    out = []
    for j in (d if isinstance(d, list) else []):
        c = j.get("categories", {}) or {}
        jd = j.get("descriptionPlain") or _strip(j.get("description", ""))
        for lst in (j.get("lists") or []):
            jd += "\n\n" + _strip(lst.get("text", "")) + ":\n" + _strip(lst.get("content", ""))
        jd += "\n\n" + (j.get("additionalPlain") or _strip(j.get("additional", "")))
        sr = j.get("salaryRange") or {}
        comp = f"{sr.get('currency', '')} {sr.get('min', '')}-{sr.get('max', '')}".strip() if sr.get("min") else ""
        out.append(_rec(
            title=j.get("text", ""),
            location=c.get("location", ""),
            dept=c.get("department", "") or c.get("team", ""),
            team=c.get("team", ""),
            type=c.get("commitment", ""),
            remote=c.get("workplaceType", ""),
            date=j.get("createdAt", ""),
            req_id=str(j.get("id", "")),
            comp=comp,
            jd=jd.strip(),
            url=j.get("hostedUrl", ""),
            apply_url=j.get("applyUrl") or j.get("hostedUrl", ""),
            id=str(j.get("id", "")),
        ))
    return out, f"lever/{slug}"


# ---------- v2 新增：从 career-ops 移植的 5 个公开匿名 ATS ----------
# 均照搬 career-ops 思路：https 强制 + 主机名锁定（slug 经清洗，不接受任意 URL）。

def fetch_smartrecruiters(slug):
    # 公开 postings API，翻页(100/页)。列表级：标题/地点/部门/类型/首发日期；完整 JD 需详情接口(不抓,保持轻量)
    out = []
    for page in range(50):  # 安全上限 5000 岗
        d = _get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={page*100}&status=PUBLIC")
        items = d.get("content") or []
        if not items:
            break
        for j in items:
            loc = j.get("location") or {}
            full = loc.get("fullLocation") or ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x)
            location = ", ".join(x for x in [full, ("Remote" if loc.get("remote") else "")] if x)
            ref = j.get("ref") if isinstance(j.get("ref"), str) else ""
            url = ""
            if ref.startswith("https://api.smartrecruiters.com/v1/companies/"):
                url = "https://jobs.smartrecruiters.com/" + ref.split("/v1/companies/", 1)[1]
            if not url and j.get("id"):
                url = f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}"

            def _label(v):
                return v.get("label", "") if isinstance(v, dict) else (v or "")
            out.append(_rec(
                title=j.get("name", ""),
                location=location,
                dept=_label(j.get("department")) or _label(j.get("function")),
                type=_label(j.get("typeOfEmployment")),
                date=j.get("releasedDate", ""),
                req_id=str(j.get("refNumber") or j.get("uuid") or ""),
                url=url, apply_url=url, id=str(j.get("id", "")),
            ))
        if len(items) < 100:
            break
    return out, f"smartrecruiters/{slug}"


def fetch_recruitee(slug):
    # {slug}.recruitee.com/api/offers/ ; offers 免费带 description/requirements(完整 JD) + created_at + department
    d = _get(f"https://{slug}.recruitee.com/api/offers/")
    out = []
    for j in (d.get("offers") or []):
        remote = "Remote" if j.get("remote") else ""
        location = j.get("location") or ", ".join(x for x in [j.get("city"), j.get("country"), remote] if x)
        jd = _strip(j.get("description", ""))
        if j.get("requirements"):
            jd = (jd + "\n\n" + _strip(j.get("requirements", ""))).strip()
        raw = j.get("careers_url") or j.get("url") or ""
        url = raw if isinstance(raw, str) and raw.startswith("https://") else ""
        out.append(_rec(
            title=j.get("title", ""),
            location=location,
            dept=j.get("department", "") or "",
            date=j.get("published_at") or j.get("created_at", ""),
            req_id=str(j.get("id", "")),
            jd=jd, url=url, apply_url=url, id=str(j.get("id", "")),
        ))
    return out, f"recruitee/{slug}"


def fetch_breezy(slug):
    # {slug}.breezy.hr/json 公开 board feed（顶层数组），含 published_date；feed 带 JD 则一并收
    d = _get(f"https://{slug}.breezy.hr/json")
    out = []
    for j in (d if isinstance(d, list) else []):
        if not j or not j.get("name"):
            continue
        loc = j.get("location") or {}
        country = loc.get("country")
        country_name = country.get("name", "") if isinstance(country, dict) else (country or "")
        base = (loc.get("name") or "").strip() or ", ".join(x for x in [loc.get("city"), loc.get("state"), country_name] if x)
        remote = "Remote" if loc.get("is_remote") else ""
        location = base if (not remote or "remote" in base.lower()) else ", ".join(x for x in [base, remote] if x)

        def _name(v):
            return v.get("name", "") if isinstance(v, dict) else (v or "")
        raw = j.get("url")
        url = raw if isinstance(raw, str) and raw.startswith("https://") else ""
        out.append(_rec(
            title=j.get("name", ""),
            location=location,
            dept=_name(j.get("department")),
            type=_name(j.get("type")),
            date=j.get("published_date", ""),
            req_id=str(j.get("id", "")),
            jd=_strip(j.get("description", "")),
            url=url, apply_url=url, id=str(j.get("id", "")),
        ))
    return out, f"breezy/{slug}"


def fetch_bamboohr(slug):
    # {slug}.bamboohr.com/careers/list 公开列表（轻量：无 JD/日期）。url=/careers/{id}
    d = _get(f"https://{slug}.bamboohr.com/careers/list")
    origin = f"https://{slug}.bamboohr.com"
    out = []
    for j in (d.get("result") or []):
        if not j or not j.get("jobOpeningName") or not str(j.get("id") or "").strip():
            continue
        loc = j.get("location") or {}
        remote = "Remote" if j.get("isRemote") else ""
        location = ", ".join(x for x in [loc.get("city"), loc.get("state"), remote] if x)
        jid = str(j.get("id")).strip()
        url = f"{origin}/careers/{jid}"
        out.append(_rec(
            title=j.get("jobOpeningName", ""),
            location=location,
            dept=j.get("departmentLabel", ""),
            type=j.get("employmentStatusLabel", ""),
            req_id=jid, url=url, apply_url=url, id=jid,
        ))
    return out, f"bamboohr/{slug}"


def fetch_personio(slug, host=None):
    # {slug}.jobs.personio.(de|com)/xml 公开免鉴权 XML feed；含 createdAt + 完整 jobDescriptions。标准库 etree 解析(比正则稳)
    # 没传 host 时自动试 .de → .com（用哪个有岗用哪个）。
    import xml.etree.ElementTree as ET
    hosts = [host] if host else [f"{slug}.jobs.personio.de", f"{slug}.jobs.personio.com"]

    def _t(node, tag):
        e = node.find(tag)
        return (e.text or "").strip() if (e is not None and e.text) else ""

    def _parse(h):
        try:
            txt = _get_text(f"https://{h}/xml")
        except Exception:
            return []
        txt = re.sub(r'\sxmlns="[^"]*"', "", txt, count=1)  # 去默认命名空间，便于按 tag 直接查
        try:
            root = ET.fromstring(txt)
        except Exception:
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
                seg += _strip(val.text) if (val is not None and val.text) else ""
                if seg.strip():
                    jd_parts.append(seg.strip())
            url = f"https://{h}/job/{jid}"
            rows.append(_rec(
                title=title,
                location=", ".join(offices),
                dept=_t(pos, "department") or _t(pos, "recruitingCategory"),
                type=_t(pos, "employmentType"),
                date=_t(pos, "createdAt"),
                req_id=jid, jd="\n\n".join(jd_parts),
                url=url, apply_url=url, id=jid,
            ))
        return rows

    for h in hosts:
        rows = _parse(h)
        if rows:
            return rows, f"personio/{slug}"
    return [], f"personio/{slug}"


def fetch_workday(host, tenant, site, search="", pages=40):
    out = []
    base = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    for p in range(pages):
        d = _post(base, {"appliedFacets": {}, "limit": 20, "offset": p * 20, "searchText": search})
        posts = d.get("jobPostings", [])
        if not posts:
            break
        for j in posts:
            r = _rec(
                title=j.get("title", ""),
                location=j.get("locationsText", ""),
                date=j.get("postedOn", ""),
                req_id=", ".join(j.get("bulletFields") or []),
                jd="",  # 列表无 JD，--jd 时逐岗补
                url=f"https://{host}{j.get('externalPath', '')}",
                apply_url=f"https://{host}{j.get('externalPath', '')}",
                id=(j.get("bulletFields") or [""])[0],
            )
            r["_wd"] = (host, tenant, site, j.get("externalPath", ""))  # 供 --jd 逐岗抓
            out.append(r)
        if (p + 1) * 20 >= d.get("total", 0):
            break
    return out, f"workday/{tenant}"



# ---------- v2 新增：聚合板（跨公司，给"哪里招人"广撒网）----------
# 聚合板一次返回多家公司的岗位，用 company 字段承载雇主名；均公开匿名。

def fetch_board_remoteok():
    d = _get("https://remoteok.com/api")
    out = []
    for j in (d if isinstance(d, list) else []):
        if not isinstance(j, dict) or not j.get("position"):
            continue  # 跳过首个元数据对象
        smin, smax = j.get("salary_min") or 0, j.get("salary_max") or 0
        comp = f"${smin}-{smax}" if (smin or smax) else ""
        out.append(_rec(
            title=j.get("position", ""),
            company=j.get("company", ""),
            location=j.get("location", "") or "Remote",
            team=", ".join(j.get("tags") or []),
            date=j.get("date", ""),
            comp=comp,
            jd=_strip(j.get("description", "")),
            url=j.get("url", ""), apply_url=j.get("apply_url") or j.get("url", ""),
            id=str(j.get("id") or j.get("slug", "")),
        ))
    return out, "board/remoteok"


def fetch_board_remotive():
    d = _get("https://remotive.com/api/remote-jobs")
    out = []
    for j in (d.get("jobs") or []):
        out.append(_rec(
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("candidate_required_location", ""),
            dept=j.get("category", ""),
            type=j.get("job_type", ""),
            date=j.get("publication_date", ""),
            comp=j.get("salary", ""),
            jd=_strip(j.get("description", "")),
            url=j.get("url", ""), apply_url=j.get("url", ""),
            id=str(j.get("id", "")),
        ))
    return out, "board/remotive"


def fetch_board_workingnomads():
    d = _get("https://www.workingnomads.com/api/exposed_jobs/")
    rows = d if isinstance(d, list) else (d.get("jobs") or [])
    out = []
    for j in rows:
        url = j.get("url", "")
        tags = j.get("tags")
        team = tags if isinstance(tags, str) else ", ".join(tags or [])
        out.append(_rec(
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("location", ""),
            dept=j.get("category_name", ""),
            team=team,
            date=j.get("pub_date", ""),
            jd=_strip(j.get("description", "")),
            url=url, apply_url=url,
            id=str(j.get("id") or url),
        ))
    return out, "board/workingnomads"


def fetch_board_weworkremotely():
    # RSS XML：item 标题是 "公司: 职位"，拆开取雇主。用标准库 etree 解析。
    import xml.etree.ElementTree as ET
    txt = _get_text("https://weworkremotely.com/remote-jobs.rss")
    txt = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", txt)  # 去命名空间声明
    txt = re.sub(r'(</?)\w+:', r'\1', txt)            # 去标签前缀(media:/dc: 等)，否则 ET 报 unbound prefix
    out = []
    try:
        root = ET.fromstring(txt)
    except Exception:
        return out, "board/weworkremotely"

    def _t(node, tag):
        e = node.find(tag)
        return (e.text or "").strip() if (e is not None and e.text) else ""

    for it in root.iter("item"):
        raw_title = _t(it, "title")
        company, sep, role = raw_title.partition(": ")
        if not sep:
            company, role = "", raw_title
        loc = ", ".join(x for x in [_t(it, "region"), _t(it, "country"), _t(it, "state")] if x)
        link = _t(it, "link")
        out.append(_rec(
            title=role,
            company=company,
            location=loc,
            dept=_t(it, "category"),
            type=_t(it, "type"),
            date=_t(it, "pubDate"),
            jd=_strip(_t(it, "description")),
            url=link, apply_url=link,
            id=_t(it, "guid") or link,
        ))
    return out, "board/weworkremotely"


_BOARD_ALL = [("remoteok", fetch_board_remoteok), ("remotive", fetch_board_remotive),
              ("weworkremotely", fetch_board_weworkremotely), ("workingnomads", fetch_board_workingnomads)]
BOARDS = {
    "remoteok": fetch_board_remoteok,
    "remotive": fetch_board_remotive,
    "weworkremotely": fetch_board_weworkremotely, "wwr": fetch_board_weworkremotely,
    "workingnomads": fetch_board_workingnomads, "nomads": fetch_board_workingnomads,
}


def fetch_boards(name):
    """聚合板取数。name 可为单个板名或 all（全部抓、单板失败不影响其它）。"""
    key = (name or "").lower().strip()
    if key in ("all", "*", ""):
        out, srcs = [], []
        for k, fn in _BOARD_ALL:
            try:
                items, _ = fn()
                out += items
                srcs.append(f"{k}:{len(items)}")
            except Exception:
                srcs.append(f"{k}:ERR")
        return out, "board/all(" + ", ".join(srcs) + ")"
    if key in BOARDS:
        return BOARDS[key]()
    raise RuntimeError(f"未知聚合板 '{name}'。可选: remoteok / remotive / weworkremotely / workingnomads / all")


# ---------- v2 新增：local-parser（自建/中国官方招聘页的通用接入）----------

def _resolve_inside_root(path):
    """把 path 解析为绝对路径并确认在 PARSER_ROOT 内且存在；否则 None（防路径逃逸）。"""
    try:
        cand = path if os.path.isabs(path) else os.path.join(PARSER_ROOT, path)
        rp = os.path.realpath(cand)
    except Exception:
        return None
    root = os.path.realpath(PARSER_ROOT)
    if (rp == root or rp.startswith(root + os.sep)) and os.path.exists(rp):
        return rp
    return None


def _normalize_local(j):
    """把解析器输出的一条岗位（任意 key 命名）归一化进 schema。"""
    def pick(*keys):
        for k in keys:
            v = j.get(k)
            if v:
                return v
        return ""
    loc = pick("location", "city")
    if not loc and isinstance(j.get("locations"), list):
        loc = ", ".join(str(x) for x in j["locations"] if x)
    return _rec(
        title=pick("title", "name", "position"),
        company=pick("company", "company_name", "employer"),
        location=loc,
        dept=pick("dept", "department", "category", "team"),
        type=pick("type", "job_type", "employment_type"),
        date=pick("date", "postedAt", "posted_at", "published_at", "created_at", "pub_date", "publish_time"),
        comp=pick("comp", "salary", "compensation"),
        req_id=str(pick("req_id", "requisition_id") or ""),
        jd=_strip(pick("jd", "description", "content", "requirement")),
        url=pick("url", "jobUrl", "job_url", "applyUrl", "apply_url", "link", "hostedUrl", "absolute_url"),
        apply_url=pick("apply_url", "applyUrl", "url", "link"),
        id=str(pick("id", "slug", "req_id") or ""),
    )


def fetch_local(spec, name="local", keyword="", company=""):
    """spawn 本地解析器脚本（绝不用 shell），读 stdout JSON → 归一化。"""
    cmd = (spec.get("command") or "").strip()
    args = [str(a) for a in (spec.get("args") or [])]
    if spec.get("script"):
        args = [str(spec["script"])] + args
    if not cmd or not args:
        raise RuntimeError("local parser 需要 command + args/script")

    # 占位符替换（{keyword}/{company}）
    args = [a.replace("{keyword}", keyword or "").replace("{company}", company or "") for a in args]
    # 注入防御：替换后的参数（除脚本本身）不得以 - 开头被当 flag
    for a in args[1:]:
        if a.startswith("-"):
            raise RuntimeError(f"local parser 参数不安全(疑似注入 flag): {a!r}")

    # 命令白名单
    if cmd in ALLOWED_INTERP:
        first = args[0]
        if first.startswith("-"):
            raise RuntimeError("禁止内联代码 flag（如 -c/-e），第一个参数须为 parsers 内脚本路径")
        rp = _resolve_inside_root(first)
        if not rp:
            raise RuntimeError(f"脚本须在 {PARSER_ROOT} 内且存在: {first}")
        args[0] = rp
    else:
        rp = _resolve_inside_root(cmd)
        if not rp:
            raise RuntimeError(f"command 不允许: {cmd}（须为 {sorted(ALLOWED_INTERP)} 或 PARSER_ROOT 内文件）")
        cmd = rp

    timeout = (spec.get("timeout_ms") or 30000) / 1000
    maxb = int(spec.get("max_buffer") or 4_000_000)
    try:
        p = subprocess.run([cmd] + args, cwd=PARSER_ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"local parser 超时({timeout}s): {name}")
    if p.returncode != 0:
        raise RuntimeError(f"local parser 退出码 {p.returncode}: {(p.stderr or '')[:300]}")
    out = (p.stdout or "")[:maxb]
    try:
        data = json.loads(out)
    except Exception as e:
        raise RuntimeError(f"local parser 输出非 JSON: {e}；头部: {out[:200]!r}")
    rows = data if isinstance(data, list) else (data.get("jobs") or data.get("results") or data.get("data") or [])
    items = [_normalize_local(j) for j in rows if isinstance(j, dict)]
    items = [it for it in items if it["title"]]
    return items, f"local/{name}"


# ---------- --jd 逐岗增强（Workday）----------


def enrich_workday_jds(items):
    """对 Workday 岗位逐个抓 JD（/job/{path}）。慢：每岗一次 HTTP。"""
    done = 0
    for it in items:
        meta = it.get("_wd")
        if not meta:
            continue
        host, tenant, site, path = meta
        try:
            d = _get(f"https://{host}/wday/cxs/{tenant}/{site}{path}")
            info = (d.get("jobPostingInfo") or {})
            it["jd"] = _strip(info.get("jobDescription", ""))
            it["location"] = info.get("location", "") or it["location"]
            it["date"] = info.get("startDate", "") or it["date"]
            done += 1
        except Exception:
            continue
    sys.stderr.write(f"[i] --jd: Workday 逐岗 JD 抓到 {done}/{len(items)}\n")
    return items


def resolve_and_fetch(company, explicit, search):
    if explicit:
        kind = explicit[0]
        if kind == "greenhouse":
            return fetch_greenhouse(explicit[1])
        if kind == "ashby":
            return fetch_ashby(explicit[1])
        if kind == "lever":
            return fetch_lever(explicit[1])
        if kind == "workday":
            return fetch_workday(explicit[1], explicit[2], explicit[3], search)
        if kind == "smartrecruiters":
            return fetch_smartrecruiters(explicit[1])
        if kind == "recruitee":
            return fetch_recruitee(explicit[1])
        if kind == "breezy":
            return fetch_breezy(explicit[1])
        if kind == "bamboohr":
            return fetch_bamboohr(explicit[1])
        if kind == "personio":
            return fetch_personio(explicit[1])
    key = (company or "").lower().strip()
    if key in COMPANIES:
        cfg = COMPANIES[key]
        if cfg[0] == "workday":
            return fetch_workday(cfg[1], cfg[2], cfg[3], search)
        return {"greenhouse": fetch_greenhouse, "ashby": fetch_ashby, "lever": fetch_lever}[cfg[0]](cfg[1])
    # auto-probe（最佳猜测）：先试常见 GH/Ashby/Lever，再试 v2 新增 5 个 ATS，命中第一个非空即返回。
    # ⚠️ 跨 ATS 探测有“同名不同公司”撞库风险（如 figure），精确查询用显式 --xxx 旗标。
    slug = re.sub(r"[^a-z0-9-]", "", key.replace(" ", "-"))
    for fn in (fetch_greenhouse, fetch_ashby, fetch_lever,
               fetch_smartrecruiters, fetch_recruitee, fetch_breezy, fetch_bamboohr, fetch_personio):
        try:
            items, src = fn(slug)
            if items:
                return items, src
        except Exception as e:
            if _DEBUG:
                sys.stderr.write(f"[debug] auto-probe {fn.__name__}({slug}) 失败: {type(e).__name__}: {e}\n")
    return [], None


def _load_company_seeds():
    """从 parsers/companies.seed 读中国公司种子表，合并进 LOCAL_PARSERS（内置脚本优先，不覆盖）。
    格式： key | type | 公司名 | arg1 | arg2 | 赛道   （# 开头与空行忽略）
    feishu: arg1=门户域名；moka: arg1=orgId, arg2=siteId；beisen: arg1=slug({slug}.zhiye.com)。扩公司=往该文件加一行，零代码。"""
    path = os.path.join(PARSER_ROOT, "parsers", "companies.seed")
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [x.strip() for x in ln.split("|")]
        if len(parts) < 4:
            continue
        key, typ, company, a1 = parts[0].lower(), parts[1].lower(), parts[2], parts[3]
        a2 = parts[4] if len(parts) > 4 else ""
        if not key or key in LOCAL_PARSERS:  # 内置脚本优先
            continue
        if typ == "feishu" and a1:
            LOCAL_PARSERS[key] = {"command": "python3", "args": ["parsers/feishu.py", a1, company, "{keyword}"]}
        elif typ == "moka" and a1 and a2:
            LOCAL_PARSERS[key] = {"command": "python3", "args": ["parsers/moka.py", a1, a2, company, "{keyword}"]}
        elif typ == "beisen" and a1:
            LOCAL_PARSERS[key] = {"command": "python3", "args": ["parsers/beisen.py", a1, company, "{keyword}"]}


def _safe_slug(kind, slug):
    """显式 ATS 旗标的 slug 只允许单段 [A-Za-z0-9_-]:防在 slug 里塞 / . @ : 把请求主机
    改写到任意域名(SSRF)。与 auto-probe 路径(第 751 行 re.sub)一致,且照 --workday 的
    reject 风格:非法直接退出而非静默改写,避免误伤合法 slug(如 SmartRecruiters 大小写)。"""
    slug = (slug or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
        sys.exit(f"[x] --{kind} slug 非法:只允许字母/数字/连字符/下划线(防 SSRF),收到:{slug!r}")
    return slug


def main():
    _load_company_seeds()
    ap = argparse.ArgumentParser(description="招聘信号雷达 — 读公司 ATS 直出在招岗位(全字段)")
    ap.add_argument("--version", action="version", version=f"Hiring Radar v{__version__}")
    ap.add_argument("company", nargs="?", default="")
    ap.add_argument("--keyword", default="", help="逗号分隔，过滤 标题/部门/地点/JD/薪资")
    ap.add_argument("--recent-days", type=int, default=0, help="只看近 N 天发布的（有日期时）")
    ap.add_argument("--limit", type=int, default=40, help="终端摘要显示条数(--json 不受限，出全量)")
    ap.add_argument("--jd", action="store_true", help="Workday：逐岗补抓完整 JD/薪资(慢)。GH/Ashby/Lever 默认已含")
    ap.add_argument("--greenhouse")
    ap.add_argument("--ashby")
    ap.add_argument("--lever")
    ap.add_argument("--workday", help="host,tenant,site")
    ap.add_argument("--smartrecruiters", help="SmartRecruiters 公司 slug")
    ap.add_argument("--recruitee", help="Recruitee 租户 slug（{slug}.recruitee.com）")
    ap.add_argument("--breezy", help="Breezy 租户 slug（{slug}.breezy.hr）")
    ap.add_argument("--bamboohr", help="BambooHR 租户 slug（{slug}.bamboohr.com）")
    ap.add_argument("--personio", help="Personio slug（{slug}.jobs.personio.de）")
    ap.add_argument("--board", help="聚合板模式(跨公司广撒网): remoteok/remotive/weworkremotely/workingnomads/all")
    ap.add_argument("--local", help="本地解析器(自建/中国招聘页)：parsers 注册名，如 bytedance")
    ap.add_argument("--script", help="临时本地解析脚本(PARSER_ROOT 内路径)，解释器按扩展名推断；首个关键词会作为参数传入")
    ap.add_argument("--list", action="store_true", help="列出所有可查的公司/聚合板(全球内置 + --board + --local)")
    ap.add_argument("--debug", action="store_true", help="打印 auto-probe 被吞的异常(排错用)")
    ap.add_argument("--json", action="store_true", help="出全量原始 JSON(含完整 JD/薪资/日期)")
    a = ap.parse_args()
    global _DEBUG
    _DEBUG = a.debug

    if a.list:
        print(f"== 全球内置（给公司名即可，或任意公司名 auto-probe 8 ATS）：{len(COMPANIES)} ==")
        print("  " + " ".join(sorted(COMPANIES.keys())))
        print("== 聚合板 --board（跨公司）==")
        print("  remoteok  remotive  weworkremotely  workingnomads  all")
        print(f"== 中国/本地 --local：{len(LOCAL_PARSERS)} ==")
        print("  " + "  ".join(sorted(LOCAL_PARSERS.keys())))
        return

    explicit = None
    if a.greenhouse:
        explicit = ("greenhouse", _safe_slug("greenhouse", a.greenhouse))
    elif a.ashby:
        explicit = ("ashby", _safe_slug("ashby", a.ashby))
    elif a.lever:
        explicit = ("lever", _safe_slug("lever", a.lever))
    elif a.workday:
        parts = a.workday.split(",")
        if len(parts) != 3:
            sys.exit("[x] --workday 格式: host,tenant,site")
        if not re.fullmatch(r"[A-Za-z0-9.-]+\.myworkdayjobs\.com", parts[0].strip()):
            sys.exit("[x] --workday host 应为 *.myworkdayjobs.com 域名（防 SSRF）")
        explicit = ("workday", parts[0].strip(), parts[1].strip(), parts[2].strip())
    elif a.smartrecruiters:
        explicit = ("smartrecruiters", _safe_slug("smartrecruiters", a.smartrecruiters))
    elif a.recruitee:
        explicit = ("recruitee", _safe_slug("recruitee", a.recruitee))
    elif a.breezy:
        explicit = ("breezy", _safe_slug("breezy", a.breezy))
    elif a.bamboohr:
        explicit = ("bamboohr", _safe_slug("bamboohr", a.bamboohr))
    elif a.personio:
        explicit = ("personio", _safe_slug("personio", a.personio))

    first_kw = a.keyword.split(",")[0].strip() if a.keyword else ""
    if a.board:
        # 聚合板模式（跨公司）：忽略 company/显式 ATS 旗标，直接抓板
        try:
            items, src = fetch_boards(a.board)
        except Exception as e:
            sys.exit(f"[x] 聚合板取数失败: {e}")
    elif a.local or a.script:
        # 本地解析器模式（自建/中国招聘页）
        if a.local:
            spec = LOCAL_PARSERS.get(a.local.lower().strip())
            if not spec:
                sys.exit(f"[x] 未注册的 local 解析器: {a.local}（可选: {', '.join(LOCAL_PARSERS) or '无'}）")
            pname = a.local.lower().strip()
        else:
            ext = os.path.splitext(a.script)[1].lower()
            interp = _EXT_INTERP.get(ext)
            if not interp:
                sys.exit(f"[x] 无法按扩展名 {ext} 推断解释器；支持 {sorted(_EXT_INTERP)}")
            spec = {"command": interp, "args": [a.script] + (["{keyword}"] if first_kw else [])}
            pname = os.path.basename(a.script)
        try:
            items, src = fetch_local(spec, name=pname, keyword=first_kw, company=a.company)
        except Exception as e:
            sys.exit(f"[x] 本地解析失败: {e}")
    else:
        # 服务端预筛：Workday 支持 searchText
        kind = explicit[0] if explicit else COMPANIES.get((a.company or "").lower().strip(), (None,))[0]
        wd_search = first_kw if kind == "workday" else ""
        try:
            items, src = resolve_and_fetch(a.company, explicit, wd_search)
        except Exception as e:
            sys.exit(f"[x] 取数失败: {e}")
    if not items:
        if a.local or a.script:   # 数据源已命中、解析正常，只是当前无在招岗位（如招聘周期空档）
            sys.exit(f"[i] {src} 数据源正常，当前无在招岗位（在招总数 0）。")
        sys.exit(f"[x] 没命中 ATS。'{a.company}' 可能用 Workday/Eightfold/自建——"
                 f"需手动找端点后用 --workday host,tenant,site（见 README）。")

    kws = [k.strip().lower() for k in a.keyword.split(",") if k.strip()]

    def match(it):
        if not kws:
            return True
        hay = (it["title"] + " " + it.get("company", "") + " " + it["dept"] + " " + it["team"]
               + " " + it["location"] + " " + it["jd"] + " " + it["comp"]).lower()
        return any(k in hay for k in kws)

    filt = [it for it in items if match(it)]
    if a.recent_days > 0:
        filt = [it for it in filt if (_days_ago(it["date"]) is None or _days_ago(it["date"]) <= a.recent_days)]

    # --jd：Workday 逐岗补抓完整 JD（对【过滤后】的集合做，避免抓全站）
    if a.jd and filt and src and src.startswith("workday"):
        filt = enrich_workday_jds(filt)

    # 清理内部字段
    for it in filt:
        it.pop("_wd", None)

    if a.json:
        # 全量出（不受 --limit 限制）
        print(json.dumps({"source": src, "total": len(items), "matched": len(filt), "jobs": filt},
                         ensure_ascii=False, indent=2))
        return

    head = f"📡 招聘信号雷达 · {a.company or src} · 源: {src} · 在招总数 {len(items)}"
    if kws:
        head += f" · 命中[{a.keyword}] {len(filt)}"
    if a.recent_days:
        head += f" · 近{a.recent_days}天 {len(filt)}"
    print(head)
    with_jd = sum(1 for it in filt if it["jd"])
    with_comp = sum(1 for it in filt if it["comp"])
    print(f"   📦 字段覆盖：含完整 JD {with_jd}/{len(filt)} · 含薪资 {with_comp}/{len(filt)}（完整内容在 --json）")

    comp_c = Counter(it.get("company", "") for it in filt if it.get("company"))
    dep = Counter(it["dept"] for it in filt if it["dept"])
    loc = Counter(it["location"] for it in filt if it["location"])
    if comp_c:
        print("   🏢 公司 Top:", " | ".join(f"{k}×{v}" for k, v in comp_c.most_common(8)))
    if dep:
        print("   📊 部门 Top:", " | ".join(f"{k}×{v}" for k, v in dep.most_common(6)))
    if loc:
        print("   📍 地点 Top:", " | ".join(f"{_short(k, 30)}×{v}" for k, v in loc.most_common(6)))
    print("   —— 岗位 ——")
    for it in filt[:a.limit]:
        who = (it.get("company", "") + " · ") if it.get("company") else ""
        line = f"   • {who}{it['title']}  [{_short(it['location'])}]"
        if it["dept"]:
            line += f" · {it['dept']}"
        if it["comp"]:
            line += f" · 💰{it['comp']}"
        if it["date"]:
            line += f"  ({_fmt_date(it['date'])})"
        print(line)
    if len(filt) > a.limit:
        print(f"   … 还有 {len(filt) - a.limit} 条（--json 出全量）")


if __name__ == "__main__":
    main()
