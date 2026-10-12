"""多来源整片拉取：依次跑各来源的 pages()，每页落盘，可断点续跑。

进度存在 ~/.hiring-radar/sweeps/<查询指纹>.json(.jsonl)。某个来源被限流、被拦或出错时，
记下原因、停掉这个来源（不绕过），其他来源照跑；之后同样的命令加 --resume 只补没完成的部分。
Ctrl-C 中断同理。全部跑完才删除进度文件。
来源不支持的服务端过滤（关键词/国家/近 N 天），在这里本地补上。
"""
import hashlib
import json
import os
import re
import sys

from . import boards
from .countries import name as country_name
from .directory import HOME
from .schema import days_ago

DIR = os.path.join(HOME, "sweeps")


def keyword_match(it, kws):
    if not kws:
        return True
    hay = " ".join(str(it.get(k, "")) for k in ("title", "company", "dept", "team", "location", "jd", "comp")).lower()
    return any(k.lower() in hay for k in kws)


def country_match(it, ccs):
    if not ccs:
        return True
    have = {c for c in (it.get("country") or "").upper().split(",") if c}
    if have:
        return bool(have & set(ccs))
    loc = (it.get("location") or "").lower()
    return any(re.search(r"\b" + re.escape(country_name(c).lower()) + r"\b", loc) for c in ccs)


def local_filter(mod, page, q):
    f = getattr(mod, "FILTERS", set())
    out = []
    for it in page:
        if "keyword" not in f and not keyword_match(it, q.keywords):
            continue
        if "country" not in f and not country_match(it, q.countries):
            continue
        if q.recent_days and "recent_days" not in f:
            n = days_ago(it.get("date"))
            if n is not None and n > q.recent_days:
                continue
        out.append(it)
    return out


def _paths(names, q):
    sid = hashlib.sha1(json.dumps([names, q.as_dict()], sort_keys=True).encode()).hexdigest()[:12]
    return os.path.join(DIR, sid + ".json"), os.path.join(DIR, sid + ".jsonl")


def run(names, q, resume=False):
    """返回 (items, report)。report = {来源: {"n": 条数, "capped": 是否到 --max 上限, "error": 出错原因}}；
    有 error 的来源没拉完，进度保留，可 --resume。"""
    os.makedirs(DIR, exist_ok=True)
    stp, spool = _paths(names, q)
    st, items = {"cursor": {}, "done": {}, "report": {}}, []
    if resume and os.path.exists(stp):
        with open(stp, encoding="utf-8") as f:
            st = json.load(f)
        if os.path.exists(spool):
            with open(spool, encoding="utf-8") as f:
                items = [json.loads(l) for l in f if l.strip()]
            # 只认进度文件记下的条数：中断恰好发生在「写了数据、还没记进度」之间时，多出的那页会重拉
            items = items[:st.get("lines", len(items))]
            with open(spool, "w", encoding="utf-8") as f:
                f.writelines(json.dumps(it, ensure_ascii=False) + "\n" for it in items)
        sys.stderr.write(f"[i] 续跑：已有 {len(items)} 条，已完成来源 {sorted(st['done'])}\n")
    else:
        for p in (stp, spool):
            if os.path.exists(p):
                os.remove(p)

    def save():
        st["lines"] = len(items)
        tmp = stp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, stp)

    report = st["report"]
    with open(spool, "a", encoding="utf-8") as fh:
        for name in names:
            if st["done"].get(name):
                continue
            mod = boards.resolve(name)
            rep = report.setdefault(name, {"n": 0, "capped": False})
            rep.pop("error", None)
            try:
                for page, nxt in mod.pages(q, st["cursor"].get(name)):
                    page = local_filter(mod, page, q)
                    if q.max_items:
                        page = page[:max(0, q.max_items - rep["n"])]
                    for it in page:
                        fh.write(json.dumps(it, ensure_ascii=False) + "\n")
                    fh.flush()
                    items += page
                    rep["n"] += len(page)
                    st["cursor"][name] = nxt
                    save()
                    if q.max_items and rep["n"] >= q.max_items:
                        rep["capped"] = True
                        break
            except Exception as e:  # 限流/被拦/接口变了：这个来源先停，其他来源照跑
                rep["error"] = f"{type(e).__name__}: {e}"[:300]
                sys.stderr.write(f"[!] {name} 停止：{rep['error']}\n")
                save()
                continue
            st["done"][name] = True
            save()
    if not any("error" in r for r in report.values()):
        for p in (stp, spool):
            os.remove(p)
    return items, report
