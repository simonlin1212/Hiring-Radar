"""公司名录：哪家公司用哪个招聘系统、账号(slug)是什么。

数据来自 openroles（github.com/datascry/openroles）每晚更新的租户名单（本工具支持的系统里有数万家在线公司）。
名单数据许可是 CC BY-SA 4.0，因此本仓库（MIT）不打包，`--directory-update` 时下载到本机
~/.hiring-radar/directory/，只在本地使用。署名：openroles dataset © datascry, CC BY-SA 4.0。

查名字：把公司名和名单里的 slug 都转成小写字母数字再比（去掉 inc/llc/careers 之类尾巴）。
名单基本只有 slug 没有正式公司名，所以同名不同公司仍可能撞上——命中多个时全部列出，由用户选。
"""
import json
import os
import re
import sys
import time

from .http import Blocked, RateLimited, get_text, safe

SOURCE = "https://raw.githubusercontent.com/datascry/openroles/main/data/tenants/{kind}.json"
ATTRIBUTION = "公司名录数据：openroles dataset © datascry, CC BY-SA 4.0 (github.com/datascry/openroles)"
HOME = os.path.expanduser(os.environ.get("HIRING_RADAR_HOME", "~/.hiring-radar"))
PATH = os.path.join(HOME, "directory", "openroles.json")

# 命中多个系统时的展示/默认优先顺序：带完整 JD 和日期的系统在前
PREFER = ["greenhouse", "ashby", "lever", "workable", "recruitee", "teamtailor", "personio", "smartrecruiters",
          "workday", "pinpointhq", "rippling", "breezy", "jazzhr", "manatal", "hireology", "zohorecruit",
          "ultipro", "jobvite", "icims", "applicantpro", "isolvedhire", "careerplug", "pageup", "bamboohr"]
_TAIL = {"inc", "llc", "ltd", "co", "corp", "careers", "career", "jobs", "job", "hr", "hq", "group", "the",
         "company", "pty", "plc", "gmbh", "usa", "us", "uk", "au", "global", "hiring", "recruiting", "talent"}

# slug 常把这些词直接粘在公司名后面（acmeinc、acmecareers），建索引时也去掉再存一份
_GLUED = ("careers", "career", "recruiting", "hiring", "talent", "jobs", "group", "company", "global",
          "inc", "llc", "ltd", "corp", "pty", "plc", "gmbh", "hq")

_index = None


def norm(s):
    toks = [t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t]
    while len(toks) > 1 and toks[-1] in _TAIL:
        toks.pop()
    while len(toks) > 1 and toks[0] == "the":
        toks.pop(0)
    return "".join(toks)


def _old_tenants():
    try:
        with open(PATH, encoding="utf-8") as f:
            return json.load(f).get("tenants") or {}
    except (OSError, ValueError):
        return {}


def update(kinds):
    """下载名单（只取本工具支持的系统），保存到本机。返回 ({系统: 在线公司数}, [没下载成功的系统])。
    没下载成功的系统保留旧名单；全部失败时不动原文件并抛 RuntimeError。被限流或被拦就停，后面的系统不再请求。"""
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tenants, counts, failed = {}, {}, []
    stop = None
    for k in kinds:
        if stop:
            failed.append(k)
            continue
        try:
            rows = json.loads(get_text(SOURCE.format(kind=k), timeout=120))
        except (Blocked, RateLimited) as e:
            stop = e
            failed.append(k)
            sys.stderr.write(f"[!] 名录下载被限流或拦截，停止：{safe(e)}\n")
            continue
        except Exception as e:  # 某个系统没有名单（如 openroles 不收录）不影响其他
            failed.append(k)
            sys.stderr.write(f"[!] 名录 {k} 下载失败：{type(e).__name__}: {safe(e)}\n")
            continue
        keep = []
        for t in rows:
            if t.get("status") not in ("live", "transient_failure") or not t.get("slug"):
                continue
            meta = {m: v for m, v in (t.get("metadata") or {}).items() if isinstance(v, str)}
            if t.get("display_name"):
                meta["name"] = t["display_name"]
            keep.append([t["slug"], meta] if meta else [t["slug"]])
        tenants[k] = keep
        counts[k] = len(keep)
    if not tenants:
        raise RuntimeError("公司名录一个系统都没下载成功，原有名录保持不变" + (f"（{safe(stop)}）" if stop else ""))
    old = _old_tenants()
    for k in failed:   # 没下载成功的系统沿用旧名单
        if k in old:
            tenants[k] = old[k]
            counts[k] = len(old[k])
    doc = {"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "attribution": ATTRIBUTION,
           "source": SOURCE, "tenants": tenants}
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, PATH)
    global _index
    _index = None
    return counts, failed


def info():
    """名录是否已下载、下载时间、各系统公司数。"""
    if not os.path.exists(PATH):
        return None
    with open(PATH, encoding="utf-8") as f:
        doc = json.load(f)
    return {"fetched_at": doc.get("fetched_at"), "counts": {k: len(v) for k, v in doc["tenants"].items()}}


def _load():
    global _index
    if _index is None:
        _index = {}
        if os.path.exists(PATH):
            with open(PATH, encoding="utf-8") as f:
                doc = json.load(f)
            for kind, rows in doc.get("tenants", {}).items():
                for row in rows:
                    slug, meta = row[0], (row[1] if len(row) > 1 else {})
                    # iCIMS 等常见 careers-acme 这种前缀写法，去掉前缀也存一份
                    keys = {norm(slug), norm(meta.get("name", "")), norm(re.sub(r"^(careers|jobs)-", "", slug))}
                    n = norm(slug)
                    for t in _GLUED:
                        if n.endswith(t) and len(n) - len(t) >= 4:
                            keys.add(n[:-len(t)])
                            break
                    for key in keys - {""}:
                        _index.setdefault(key, []).append({"ats": kind, "slug": slug, "meta": meta})
    return _index


def lookup(name):
    """公司名 → 候选列表 [{ats, slug, meta}]，按 PREFER 排序。名录未下载时返回 []。"""
    hits = _load().get(norm(name), [])
    order = {k: i for i, k in enumerate(PREFER)}
    return sorted(hits, key=lambda h: (order.get(h["ats"], len(order)), h["slug"]))


def meta_for(kind, slug):
    """名录里某个 (系统, slug) 的附加信息（如 Workday 的 host/site）；没有就返回 {}。"""
    for h in _load().get(norm(slug), []):
        if h["ats"] == kind and h["slug"].lower() == slug.lower():
            return dict(h["meta"])
    return {}
