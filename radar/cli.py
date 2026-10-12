"""命令行：v1 的全部用法不变，v2 新增名录、整片拉取、存档和 MCP。见 README。"""
import argparse
import json
import os
import re
import sys
from collections import Counter

from . import __version__, ats, boards, directory, http, local, plugins, process, store, sweep
from .schema import AGE_LABEL, AGES, fmt_date, older_than, short

# 内置：已实测命中的公司 → ATS（新公司加一行即可）。名录里查得到的公司不必加。
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

SWEEP_DEFAULT_DAYS = 183  # 跨公司来源默认只看近半年；--recent-days 0 看全量
SWEEP_DEFAULT_MAX = 1000  # 每个跨公司来源默认最多拉 1000 条；--max 0 不限


def _err(msg, code=1):
    sys.stderr.write(msg + "\n")
    sys.exit(code)


def _company_items(company, explicit, search, use_directory):
    """按公司取数。返回 (items, src, candidates)。"""
    if explicit:
        kind = explicit[0]
        if kind == "workday":
            items, src = ats.REGISTRY["workday"][0].fetch_board(explicit[1], explicit[2], explicit[3], search)
            for it in items:
                it["source"] = src
            return items, src, []
        meta = directory.meta_for(kind, explicit[1]) if use_directory else {}
        items, src = ats.fetch(kind, explicit[1], meta)
        return items, src, []
    key = (company or "").lower().strip()
    if key in COMPANIES:
        cfg = COMPANIES[key]
        if cfg[0] == "workday":
            return _company_items(company, cfg, search, False)
        items, src = ats.fetch(cfg[0], cfg[1])
        return items, src, []
    cands = directory.lookup(company) if use_directory else []
    blocked = {}   # 被拦/限流的系统：按约定不再请求它（包括同系统的其他候选）
    for c in cands:
        if c["ats"] in blocked:
            continue
        try:
            meta = dict(c["meta"], search=search) if c["ats"] == "workday" else c["meta"]
            items, src = ats.fetch(c["ats"], c["slug"], meta)
        except (http.Blocked, http.RateLimited) as e:
            blocked[c["ats"]] = e
            sys.stderr.write(f"[!] {c['ats']} 拦截或限流，不再请求这个系统：{e}\n")
            continue
        except Exception as e:
            if http.DEBUG:
                sys.stderr.write(f"[debug] 名录候选 {c['ats']}/{c['slug']} 失败: {type(e).__name__}: {e}\n")
            continue
        if items:
            if len(cands) > 1:
                others = ", ".join(f"{x['ats']}/{x['slug']}" for x in cands if x is not c)
                sys.stderr.write(f"[i] 名录里「{company}」有 {len(cands)} 个候选，用了 {src}；其他：{others}"
                                 f"（可能是同名的别家公司，用 --ats 系统 slug 指定）\n")
            return items, src, cands
    if use_directory and directory.info() is None:
        sys.stderr.write("[i] 提示：运行 --directory-update 下载公司名录（数万家公司），查公司更准、覆盖更多招聘系统\n")
    # auto-probe（最佳猜测）：先试常见 GH/Ashby/Lever，再试另外 5 个 ATS，命中第一个非空即返回。
    # ⚠️ 跨 ATS 探测有「同名不同公司」撞库风险（如 figure），精确查询用显式 --xxx 旗标。
    slug = re.sub(r"[^a-z0-9-]", "", key.replace(" ", "-"))
    for kind in ats.PROBE_ORDER if slug else ():
        if kind in blocked:
            continue
        try:
            items, src = ats.fetch(kind, slug)
            if items:
                return items, src, cands
        except (http.Blocked, http.RateLimited) as e:
            blocked[kind] = e
            sys.stderr.write(f"[!] {kind} 拦截或限流，不再请求这个系统：{e}\n")
        except Exception as e:
            if http.DEBUG:
                sys.stderr.write(f"[debug] auto-probe {kind}({slug}) 失败: {type(e).__name__}: {e}\n")
    if blocked:   # 没查到，而且有系统拦了我们：报拦截，不报「没命中」
        raise next(iter(blocked.values()))
    return [], None, cands


def _explicit(a):
    for kind in ("greenhouse", "ashby", "lever", "smartrecruiters", "recruitee", "breezy", "bamboohr", "personio"):
        v = getattr(a, kind)
        if v:
            try:
                return (kind, ats.check_slug(kind, v))
            except ValueError as e:
                _err(f"[x] --{kind} {e}")
    if a.workday:
        parts = [p.strip() for p in a.workday.split(",")]
        if len(parts) != 3:
            _err("[x] --workday 格式: host,tenant,site")
        try:
            return ("workday",) + ats.workday.check(*parts)
        except ValueError as e:
            _err(f"[x] --workday {e}（防 SSRF）")
    if a.ats:
        kind, slug = a.ats[0].lower().strip(), a.ats[1]
        if kind not in ats.REGISTRY:
            _err(f"[x] 未知 ATS：{kind}（可选：{', '.join(ats.REGISTRY)}）")
        if kind == "workday":
            _err("[x] Workday 用 --workday host,tenant,site，或直接给公司名查名录")
        try:
            return (kind, ats.check_slug(kind, slug))
        except ValueError as e:
            _err(f"[x] {e}")
    return None


def _print_list():
    print(f"== 按公司查：{len(ats.REGISTRY)} 个招聘系统（给公司名先查名录，查不到再猜 {len(ats.PROBE_ORDER)} 个）==")
    print("  " + "  ".join(ats.REGISTRY))
    print(f"   内置公司：{' '.join(sorted(COMPANIES))}")
    inf = directory.info()
    if inf:
        print(f"   公司名录：{sum(inf['counts'].values())} 家（{inf['fetched_at'][:10]} 下载）· {directory.ATTRIBUTION}")
    else:
        print("   公司名录：未下载（--directory-update）")
    print("== 跨公司来源 --board（逗号可多选；all = 4 个远程板）==")
    for n in sorted(boards.BOARDS):
        m = boards.BOARDS[n]
        f = "/".join(sorted(m.FILTERS)) or "无"
        print(f"  {n:16} {m.DESC}  [服务端过滤: {f}]")
    print(f"== 中国/本地 --local：{len(local.LOCAL_PARSERS)} ==")
    print("  " + "  ".join(sorted(local.LOCAL_PARSERS)))


def _print_history(rows):
    if not rows:
        print("（存档里还没有记录。拉取时加 --save 会记一次）")
        return
    cur = None
    for r in rows:
        if r["scope"] != cur:
            cur = r["scope"]
            print(f"== {cur}")
        delta = "不完整，不比较" if not r["complete"] else "首次" if r["new"] is None else f"新增 {r['new']} · 下架 {r['gone']}"
        print(f"   {r['at'][:16].replace('T', ' ')}  {r['n']:>6} 条  {delta}")


def build_parser():
    ap = argparse.ArgumentParser(description="招聘雷达 — 读公司招聘系统和公开职位来源，输出统一字段的在招岗位")
    ap.add_argument("--version", action="version", version=f"Hiring Radar v{__version__}")
    ap.add_argument("company", nargs="?", default="")
    ap.add_argument("--keyword", default="", help="逗号分隔(OR)，过滤 标题/公司/部门/地点/JD/薪资")
    ap.add_argument("--recent-days", type=int, default=None,
                    help=f"只看近 N 天发布的（无日期的保留）。按公司查默认不限；--board 默认 {SWEEP_DEFAULT_DAYS}，0=不限")
    ap.add_argument("--limit", type=int, default=40, help="终端摘要显示条数(--json 不受限，出全量)")
    ap.add_argument("--jd", action="store_true", help="Workday：逐岗补抓完整 JD/薪资(慢)。其他多数系统默认已含")
    for kind, hint in (("greenhouse", ""), ("ashby", ""), ("lever", ""), ("smartrecruiters", "SmartRecruiters 公司 slug"),
                       ("recruitee", "{slug}.recruitee.com"), ("breezy", "{slug}.breezy.hr"),
                       ("bamboohr", "{slug}.bamboohr.com"), ("personio", "{slug}.jobs.personio.de")):
        ap.add_argument(f"--{kind}", help=hint or None)
    ap.add_argument("--workday", help="host,tenant,site")
    ap.add_argument("--ats", nargs=2, metavar=("系统", "SLUG"), help="任意已支持的招聘系统，如 --ats teamtailor acme")
    ap.add_argument("--board", help="跨公司来源，逗号可多选：freehire,workable,remoteok,… 或 all（4 个远程板）；--list 看全部")
    ap.add_argument("--country", default="", help="国家码，逗号分隔，如 AU,NZ（用于 --board）")
    ap.add_argument("--max", type=int, default=None, help=f"--board 每个来源最多拉多少条（默认 {SWEEP_DEFAULT_MAX}，0=不限）")
    ap.add_argument("--resume", action="store_true", help="--board 从上次中断处继续（同样的参数）")
    ap.add_argument("--no-dedupe", action="store_true", help="多个来源时不去重")
    ap.add_argument("--no-agency", action="store_true", help="去掉疑似中介/猎头发的职位")
    ap.add_argument("--local", help="本地解析器(自建/中国招聘页)：parsers 注册名，如 bytedance")
    ap.add_argument("--script", help="临时本地解析脚本(PARSER_ROOT 内路径)，解释器按扩展名推断；首个关键词会作为参数传入")
    ap.add_argument("--find", metavar="公司名", help="在公司名录里查这家公司用哪个招聘系统")
    ap.add_argument("--directory-update", action="store_true", help="下载/更新公司名录（openroles 每晚更新，数万家公司）")
    ap.add_argument("--no-directory", action="store_true", help="按公司名查时不用名录，只按 v1 方式猜")
    ap.add_argument("--save", action="store_true", help="把结果存进本地存档(SQLite)，记首次/最近看到，可看环比")
    ap.add_argument("--history", nargs="?", const="", default=None, metavar="范围", help="看存档里的历次拉取和新增/下架")
    ap.add_argument("--db", help="存档路径（默认 ~/.hiring-radar/radar.db）")
    ap.add_argument("--plugins", help="私有插件目录（也可用环境变量 HIRING_RADAR_PLUGINS）")
    ap.add_argument("--mcp", action="store_true", help="以 MCP 服务方式运行（stdio），给 Claude / Codex 等调用")
    ap.add_argument("--list", action="store_true", help="列出所有可查的来源和公司")
    ap.add_argument("--debug", action="store_true", help="打印被吞的异常和重试(排错用)")
    ap.add_argument("--json", action="store_true", help="出全量 JSON(含完整 JD/薪资/日期)")
    return ap


def main(argv=None):
    local.load_company_seeds()
    http.guard_stderr()   # 之后写到 stderr 的报错、调试日志、堆栈都先打码
    a = build_parser().parse_args(argv)
    http.DEBUG = a.debug
    plugins.load(a.plugins or os.environ.get("HIRING_RADAR_PLUGINS", ""))

    if a.list:
        return _print_list()
    if a.directory_update:
        try:
            counts, failed = directory.update([k for k in ats.REGISTRY])
        except RuntimeError as e:
            _err(f"[x] {http.safe(e)}")
        print(f"公司名录已更新：{sum(counts.values())} 家 → {directory.PATH}")
        print("  " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])))
        print(f"  {directory.ATTRIBUTION}")
        if failed:
            sys.stderr.write(f"[!] 部分更新：{', '.join(failed)} 没下载成功，保留了旧名单（如有）；稍后再跑 --directory-update\n")
            sys.exit(3)
        return
    if a.find:
        hits = directory.lookup(a.find)
        if directory.info() is None:
            _err("[x] 公司名录未下载，先运行 --directory-update")
        if not hits:
            print(f"名录里没有「{a.find}」（名录按 slug 匹配，可换个写法，或直接给公司名让程序猜）")
        for h in hits:
            extra = " ".join(f"{k}={v}" for k, v in h["meta"].items())
            print(f"  {h['ats']:16} {h['slug']}  {extra}".rstrip())
        print(f"({directory.ATTRIBUTION})")
        return
    if a.history is not None:
        return _print_history(store.history(a.history, a.db))
    if a.mcp:
        from . import mcp
        return mcp.serve()

    kws = [k.strip() for k in a.keyword.split(",") if k.strip()]
    first_kw = kws[0] if kws else ""
    explicit = _explicit(a)
    cands, report, incomplete = [], {}, False

    if a.board:
        names = []
        for n in a.board.split(","):
            n = n.strip().lower()
            if n in ("all", "*"):
                names += boards.REMOTE
            elif n:
                try:
                    names.append(boards.resolve(n).NAME)
                except ValueError as e:
                    _err(f"[x] {e}")
        names = list(dict.fromkeys(names))
        days = SWEEP_DEFAULT_DAYS if a.recent_days is None else a.recent_days
        shown_days = days
        q = boards.Query(kws, a.country.split(","), days, SWEEP_DEFAULT_MAX if a.max is None else a.max)
        try:
            items, report = sweep.run(names, q, resume=a.resume)
        except KeyboardInterrupt:
            _err("\n[i] 已中断，进度已保存；同样的命令加 --resume 继续", 130)
        incomplete = sweep.incomplete(report)
        src = "boards:" + ",".join(names)
        process.annotate(items)
        total = len(items)
        deduped = len(names) > 1 and not a.no_dedupe
        if deduped:
            items = process.dedupe(items, order=names)
        filt = items
        scope = f"boards:{','.join(names)}|{','.join(q.countries)}|{','.join(kws)}"
        query = dict(q.as_dict(), boards=names, dedupe=deduped, no_agency=a.no_agency)
        complete = not incomplete and not any(r.get("capped") for r in report.values())
    else:
        if a.local or a.script:
            if a.local:
                spec = local.LOCAL_PARSERS.get(a.local.lower().strip())
                if not spec:
                    _err(f"[x] 未注册的 local 解析器: {a.local}（可选: {', '.join(local.LOCAL_PARSERS) or '无'}）")
                pname = a.local.lower().strip()
            else:
                ext = os.path.splitext(a.script)[1].lower()
                interp = local.EXT_INTERP.get(ext)
                if not interp:
                    _err(f"[x] 无法按扩展名 {ext} 推断解释器；支持 {sorted(local.EXT_INTERP)}")
                spec = {"command": interp, "args": [a.script] + (["{keyword}"] if first_kw else [])}
                pname = os.path.basename(a.script)
            try:
                items, src = local.fetch_local(spec, name=pname, keyword=first_kw, company=a.company)
            except Exception as e:
                _err(f"[x] 本地解析失败: {http.safe(e)}")
        else:
            if not a.company and not explicit:
                build_parser().print_help()
                return
            # 服务端预筛：Workday 支持 searchText
            kind = explicit[0] if explicit else COMPANIES.get((a.company or "").lower().strip(), (None,))[0]
            wd_search = first_kw if kind == "workday" else ""
            try:
                items, src, cands = _company_items(a.company, explicit, wd_search, not a.no_directory)
            except (http.Blocked, http.RateLimited) as e:
                _err(f"[x] {http.safe(e)}")
            except Exception as e:
                _err(f"[x] 取数失败: {http.safe(e)}")
        if not items:
            if a.local or a.script:   # 数据源已命中、解析正常，只是当前无在招岗位（如招聘周期空档）
                _err(f"[i] {src} 数据源正常，当前无在招岗位（在招总数 0）。")
            _err(f"[x] 没命中 ATS。'{a.company}' 可能用 Workday/Eightfold/自建——"
                 f"先 --directory-update 再查，或手动找端点后用 --workday host,tenant,site（见 README）。")
        total = len(items)
        process.annotate(items)
        filt = [it for it in items if sweep.keyword_match(it, kws)]
        if a.recent_days:
            filt = [it for it in filt if not older_than(it["date"], a.recent_days)]  # 无日期、说不准的保留
        scope = src
        shown_days = a.recent_days or 0
        query = {"company": a.company, "keywords": kws, "recent_days": shown_days, "no_agency": a.no_agency}
        wd = next((it["_wd"] for it in items if it.get("_wd")), None)
        if wd:   # 同一 tenant 可能有多个招聘站点；--jd 会换成真实日期。条件不同的两次不互相比较
            query["workday_site"] = f"{wd[0]}/{wd[2]}"
            query["jd"] = bool(a.jd)
        complete = True

    if a.no_agency:
        filt = [it for it in filt if not it.get("agency")]

    # --jd：Workday 逐岗补抓完整 JD（对【过滤后】的集合做，避免抓全站）
    jd_err = ""
    if a.jd and filt and src and src.startswith("workday"):
        filt, jd_err = ats.workday.enrich_jds(filt)
        if jd_err:   # 没补完 JD：结果不全，也不能当以后比较的基线
            incomplete, complete = True, False
        if shown_days:   # 补到真实日期后，按近 N 天再筛一次
            filt = [it for it in filt if not older_than(it["date"], shown_days)]
    for it in filt:
        it.pop("_wd", None)

    saved = store.save(filt, scope, query, a.db, complete=complete) if a.save else None

    if incomplete:
        bad = ", ".join(k for k, v in report.items() if v.get("error"))
        cut = ", ".join(k for k, v in report.items() if v.get("truncated") and not v.get("error"))
        if bad:
            sys.stderr.write(f"[!] 没拉完的来源：{bad}。已拉到的照常输出；稍后同样的命令加 --resume 只补没完成的部分\n")
        if cut:
            sys.stderr.write(f"[!] 结果不全的来源：{cut}（上游翻页有上限，续跑补不回来；请缩小查询，如加关键词、国家或缩短近 N 天）\n")
    if jd_err:
        sys.stderr.write(f"[!] --jd 没补完（{jd_err}），这次结果标为不全；稍后再跑\n")
    if a.json:
        out = {"source": src, "total": total, "matched": len(filt), "jobs": filt, "version": __version__,
               "query": query, "ages": process.age_counts(filt)}
        if report:
            out["sources"] = report
        if incomplete:
            out["incomplete"] = True
        if cands:
            out["candidates"] = [f"{c['ats']}/{c['slug']}" for c in cands]
        if saved:
            out["saved"] = saved
        print(json.dumps(out, ensure_ascii=False, indent=2))
        if incomplete:
            sys.exit(3)
        return

    head = f"📡 招聘信号雷达 · {a.company or src} · 源: {src} · " + (f"拉到 {total}" if a.board else f"在招总数 {total}")
    if kws:
        head += f" · 命中[{a.keyword}] {len(filt)}"
    if shown_days:
        head += f" · 近{shown_days}天" + ("" if a.board else f" {len(filt)}")
    if a.board and len(filt) != total:
        head += f" · 去重后 {len(filt)}"
    print(head)
    if report:
        print("   🧭 各来源：" + " · ".join(f"{k} {v['n']}" + ("(到上限)" if v["capped"] else "")
                                       + ("(未完成)" if v.get("error") else "(不全)" if v.get("truncated") else "")
                                       for k, v in report.items()))
    with_jd = sum(1 for it in filt if it["jd"])
    with_comp = sum(1 for it in filt if it["comp"])
    print(f"   📦 字段覆盖：含完整 JD {with_jd}/{len(filt)} · 含薪资 {with_comp}/{len(filt)}（完整内容在 --json）")
    ages = process.age_counts(filt)
    print("   🕒 发布时间：" + " · ".join(f"{AGE_LABEL[k]} {ages[k]}" for k in AGES))
    n_ag = sum(1 for it in filt if it.get("agency"))
    if n_ag:
        print(f"   🧑‍💼 疑似中介/猎头：{n_ag}（--no-agency 可去掉）")
    if saved:
        if not saved["complete"]:
            delta = "这次结果不完整，只记录，不和上次比较新增/下架"
        elif saved["new"] is None:
            delta = "首次存档（同样条件下还没有完整的上一次）"
        else:
            delta = f"比上次（{saved['prev_at'][:10]}）新增 {saved['new']} · 下架 {saved['gone']}"
        print(f"   💾 已存档：{delta}")

    comp_c = Counter(it.get("company", "") for it in filt if it.get("company"))
    dep = Counter(it["dept"] for it in filt if it["dept"])
    loc = Counter(it["location"] for it in filt if it["location"])
    if comp_c:
        print("   🏢 公司 Top:", " | ".join(f"{k}×{v}" for k, v in comp_c.most_common(8)))
    if dep:
        print("   📊 部门 Top:", " | ".join(f"{k}×{v}" for k, v in dep.most_common(6)))
    if loc:
        print("   📍 地点 Top:", " | ".join(f"{short(k, 30)}×{v}" for k, v in loc.most_common(6)))
    print("   —— 岗位 ——")
    for it in filt[:a.limit]:
        who = (it.get("company", "") + " · ") if it.get("company") else ""
        line = f"   • {who}{it['title']}  [{short(it['location'])}]"
        if it["dept"]:
            line += f" · {it['dept']}"
        if it["comp"]:
            line += f" · 💰{it['comp']}"
        if it["date"]:
            line += f"  ({fmt_date(it['date'])})"
        print(line)
    if len(filt) > a.limit:
        print(f"   … 还有 {len(filt) - a.limit} 条（--json 出全量）")
    if incomplete:
        sys.exit(3)
