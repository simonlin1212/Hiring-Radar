"""多来源整片拉取：依次跑各来源的 pages()，每页落盘，可断点续跑。

进度存在 ~/.hiring-radar/sweeps/<查询指纹>.json(.jsonl)。某个来源被限流、被拦或出错时，
记下原因、停掉这个来源（不绕过），其他来源照跑；之后同样的命令加 --resume 只补没完成的部分。
Ctrl-C 中断同理。全部跑完才删除进度文件。
上游翻页有上限、只给到一部分时（来源调用 q.truncate() 报告），记为 truncated：结果不全，
续跑也补不回来，要缩小查询。
来源不支持的服务端过滤（关键词/国家/近 N 天），在这里本地补上。
同一来源里同一个职位（来源 + 职位 ID/链接）只算一次：多个关键词都命中、续跑重拉的页都不重复计数。
"""
import hashlib
import json
import os
import re
import sys

from . import boards
from .countries import name as country_name
from .directory import HOME
from .http import safe
from .schema import older_than

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
        if q.recent_days and "recent_days" not in f and older_than(it.get("date"), q.recent_days):
            continue
        out.append(it)
    return out


def _paths(names, q):
    sid = hashlib.sha1(json.dumps([names, q.as_dict()], sort_keys=True).encode()).hexdigest()[:12]
    return os.path.join(DIR, sid + ".json"), os.path.join(DIR, sid + ".jsonl")


def _key(it):
    """同一来源里认同一个职位：来源 + 职位 ID（没有就用链接）。都没有时不去重。"""
    jid = it.get("id") or it.get("url")
    return f"{it.get('source', '')}|{jid}" if jid else None


def _load_spool(spool, st):
    """读已落盘的结果，只认进度文件记下的部分：写到一半的残行、「写了数据还没记进度」的那页都丢掉（会重拉）。
    返回 (items, 是否完好)。已记进度的内容缺了（文件被截短、中间有坏行）就不完好：
    这时旧游标已经对不上，调用方应从头重拉，不能接着跑（否则会悄悄漏掉职位）。"""
    want = st.get("lines", 0)
    if not os.path.exists(spool):
        return [], want == 0
    with open(spool, "rb") as f:
        raw = f.read()
    if "bytes" in st:
        if len(raw) < st["bytes"]:
            return [], False
        raw = raw[:st["bytes"]]
    items = []
    for line in raw.decode("utf-8", "replace").splitlines():
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except ValueError:
            if "bytes" in st:   # 已记进度的范围里出现坏行：文件被改坏了
                return [], False
            break               # 旧版进度文件没记字节数时，尾部残行在这里跳过
    if len(items) < want:
        return [], False
    return (items[:want] if "lines" in st else items), True


def incomplete(report):
    """有来源没拉完：出错停下（可续跑），或上游翻页上限只给了一部分（要缩小查询）。"""
    return any(r.get("error") or r.get("truncated") for r in report.values())


def run(names, q, resume=False):
    """返回 (items, report)。report = {来源: {"n": 条数, "capped": 是否到 --max 上限,
    "error": 出错原因, "truncated": 上游翻页上限的说明}}；有 error 的来源进度保留，可 --resume。"""
    os.makedirs(DIR, exist_ok=True)
    stp, spool = _paths(names, q)
    st, items = {"cursor": {}, "done": {}, "report": {}}, []
    if resume and os.path.exists(stp):
        with open(stp, encoding="utf-8") as f:
            st = json.load(f)
        items, ok = _load_spool(spool, st)
        if not ok:
            sys.stderr.write("[!] 续跑进度和已存结果对不上（结果文件缺了一部分），这次从头重拉\n")
            st, items = {"cursor": {}, "done": {}, "report": {}}, []
            if os.path.exists(spool):
                os.remove(spool)
        elif "bytes" in st:
            if os.path.exists(spool):
                os.truncate(spool, st["bytes"])   # 只截掉没记进度的尾巴，已提交的内容不重写
        else:   # 旧版进度只记了条数：先写临时文件再整体替换，中途再断也不丢已有结果
            tmp = spool + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.writelines(json.dumps(it, ensure_ascii=False) + "\n" for it in items)
            os.replace(tmp, spool)
        if ok:
            sys.stderr.write(f"[i] 续跑：已有 {len(items)} 条，已完成来源 {sorted(st['done'])}\n")
    else:
        for p in (stp, spool):
            if os.path.exists(p):
                os.remove(p)
    seen = {k for k in map(_key, items) if k}

    report = st["report"]
    with open(spool, "a", encoding="utf-8") as fh:
        def save():
            st["lines"] = len(items)
            st["bytes"] = fh.tell()
            tmp = stp + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(st, f, ensure_ascii=False)
            os.replace(tmp, stp)

        for name in names:
            if st["done"].get(name):
                continue
            mod = boards.resolve(name)
            rep = report.setdefault(name, {"n": 0, "capped": False})
            rep.pop("error", None)
            q.truncated = list(rep.get("truncated") or [])
            try:
                for page, nxt in mod.pages(q, st["cursor"].get(name)):
                    fresh = []
                    for it in local_filter(mod, page, q):
                        it["source"] = it.get("source") or name
                        k = _key(it)
                        if k in seen:
                            continue
                        if k:
                            seen.add(k)
                        fresh.append(it)
                    if q.max_items:
                        fresh = fresh[:max(0, q.max_items - rep["n"])]
                    for it in fresh:
                        fh.write(json.dumps(it, ensure_ascii=False) + "\n")
                    fh.flush()
                    items += fresh
                    rep["n"] += len(fresh)
                    st["cursor"][name] = nxt
                    if q.truncated:
                        rep["truncated"] = q.truncated[:20]
                    save()
                    if q.max_items and rep["n"] >= q.max_items:
                        rep["capped"] = True
                        break
            except Exception as e:  # 限流/被拦/接口变了：这个来源先停，其他来源照跑
                rep["error"] = safe(f"{type(e).__name__}: {e}")[:300]   # 先打码再截断
                sys.stderr.write(f"[!] {name} 停止：{rep['error']}\n")
                save()
                continue
            st["done"][name] = True
            save()
    if not any(r.get("error") for r in report.values()):   # 只有上游截断时续跑也补不回来，进度不留
        for p in (stp, spool):
            os.remove(p)
    return items, report
