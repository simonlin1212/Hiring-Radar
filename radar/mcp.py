"""MCP 服务（stdio）：让 Claude / Codex 等 AI 助手直接调用 Hiring Radar。

协议：JSON-RPC 2.0，每行一条消息（MCP stdio 传输）。只依赖标准库。
stdout 只用来回消息；各来源的提示和日志一律走 stderr，工具执行期间把 stdout 临时指到 stderr，防止串进协议。

配置示例（Claude Code）：claude mcp add hiring-radar -- python3 /path/to/hiring_radar.py --mcp
"""
import contextlib
import json
import sys
import traceback

from . import __version__, ats, boards, directory, http, process, store, sweep
from .schema import days_ago, strip_html

PROTOCOL = "2025-06-18"
JD_CHARS = 800

_STR_LIST = {"type": "array", "items": {"type": "string"}}

TOOLS = [
    {
        "name": "company_jobs",
        "description": "查一家公司当前在招的全部岗位（读它的招聘系统公开职位板）。给公司名即可：先查公司名录，"
                       "查不到再猜常见系统；也可用 ats+slug 精确指定。返回统一字段：职位、地点、部门、发布日期、薪资、JD 摘要。",
        "inputSchema": {"type": "object", "properties": {
            "company": {"type": "string", "description": "公司名，如 Anthropic、Xero"},
            "ats": {"type": "string", "description": "可选：招聘系统名（list_sources 里的 ats 列表），与 slug 一起用"},
            "slug": {"type": "string", "description": "可选：该系统里的公司账号名"},
            "keywords": dict(_STR_LIST, description="可选：关键词（任一命中即保留），匹配标题/部门/地点/JD"),
            "recent_days": {"type": "integer", "description": "可选：只看近 N 天发布的（无日期的保留）"},
            "limit": {"type": "integer", "description": "最多返回多少条（默认 50，最多 500）"},
        }, "required": ["company"]},
    },
    {
        "name": "search_jobs",
        "description": "跨公司搜职位：从聚合来源/政府职位库按国家、关键词、近 N 天拉取，多来源自动去重，"
                       "标出疑似中介和发布时间分档（近3个月/3-6个月/半年以前/无日期）。来源见 list_sources。",
        "inputSchema": {"type": "object", "properties": {
            "boards": dict(_STR_LIST, description="来源名，如 [\"freehire\"]、[\"workable\",\"jobtech\"]；[\"all\"] = 4 个远程板"),
            "keywords": dict(_STR_LIST, description="可选：关键词（任一命中）"),
            "countries": dict(_STR_LIST, description="可选：两位国家码，如 [\"AU\",\"NZ\"]"),
            "recent_days": {"type": "integer", "description": "只看近 N 天（默认 183；0 = 不限）"},
            "max_per_source": {"type": "integer", "description": "每个来源最多拉多少条（默认 200）"},
            "limit": {"type": "integer", "description": "最多返回多少条（默认 50，最多 500）"},
            "no_agency": {"type": "boolean", "description": "去掉疑似中介/猎头发的职位"},
        }, "required": ["boards"]},
    },
    {
        "name": "find_company",
        "description": "在公司名录（openroles，数万家公司）里查某公司用哪个招聘系统、账号名是什么。",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    {
        "name": "list_sources",
        "description": "列出支持的招聘系统（按公司查）和跨公司来源（含是否需要密钥、能在服务端过滤哪些条件）。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "job_history",
        "description": "看本地存档里的历次拉取记录和新增/下架数量（需要之前用命令行 --save 存过）。",
        "inputSchema": {"type": "object", "properties": {
            "scope": {"type": "string", "description": "可选：范围关键字，如 greenhouse/anthropic"}}},
    },
]


def _slim(it):
    out = {k: v for k, v in it.items() if v not in ("", None) and not k.startswith("_")}
    if "<" in out.get("jd", ""):   # 少数系统（如 Greenhouse）给的是 HTML
        out["jd"] = strip_html(out["jd"])
    if len(out.get("jd", "")) > JD_CHARS:
        out["jd"] = out["jd"][:JD_CHARS] + "…"
    return out


def _limit(args):
    return max(1, min(int(args.get("limit") or 50), 500))


def _kws(v):
    if isinstance(v, str):
        v = v.split(",")
    return [str(x).strip() for x in (v or []) if str(x).strip()]


def company_jobs(args):
    from .cli import _company_items
    explicit = None
    if args.get("ats") or args.get("slug"):
        kind = str(args.get("ats") or "").lower().strip()
        if kind not in ats.REGISTRY or kind == "workday":
            raise ValueError(f"ats 需为以下之一（Workday 请只给公司名，走名录）：{', '.join(k for k in ats.REGISTRY if k != 'workday')}")
        explicit = (kind, ats.check_slug(kind, args.get("slug") or ""))
    kws = _kws(args.get("keywords"))
    items, src, cands = _company_items(args.get("company", ""), explicit, "", True)
    process.annotate(items)
    filt = [it for it in items if sweep.keyword_match(it, kws)]
    if args.get("recent_days"):
        filt = [it for it in filt if (days_ago(it.get("date")) or 0) <= int(args["recent_days"])]
    n = _limit(args)
    return {"source": src, "total": len(items), "matched": len(filt), "returned": min(n, len(filt)),
            "ages": process.age_counts(filt), "candidates": [f"{c['ats']}/{c['slug']}" for c in cands],
            "jobs": [_slim(it) for it in filt[:n]]}


def search_jobs(args):
    names = []
    for n in _kws(args.get("boards")):
        names += boards.REMOTE if n.lower() in ("all", "*") else [boards.resolve(n).NAME]
    names = list(dict.fromkeys(names))
    if not names:
        raise ValueError("boards 不能为空，可选来源见 list_sources")
    days = args.get("recent_days")
    q = boards.Query(_kws(args.get("keywords")), _kws(args.get("countries")),
                     183 if days is None else int(days), int(args.get("max_per_source") or 200))
    items, report = sweep.run(names, q)
    process.annotate(items)
    if len(names) > 1:
        items = process.dedupe(items, order=names)
    if args.get("no_agency"):
        items = [it for it in items if not it.get("agency")]
    n = _limit(args)
    return {"sources": report, "incomplete": any("error" in r for r in report.values()), "matched": len(items),
            "returned": min(n, len(items)), "ages": process.age_counts(items),
            "agency": sum(1 for it in items if it.get("agency")), "jobs": [_slim(it) for it in items[:n]]}


def find_company(args):
    if directory.info() is None:
        raise ValueError("公司名录未下载：先在命令行运行 hiring_radar.py --directory-update")
    return {"hits": directory.lookup(args.get("name", "")), "attribution": directory.ATTRIBUTION}


def list_sources(args):
    return {"ats": list(ats.REGISTRY), "directory": directory.info(),
            "boards": {n: {"desc": m.DESC, "server_filters": sorted(m.FILTERS),
                           "needs_key": getattr(boards, "NEEDS_KEY", {}).get(n, "")}
                       for n, m in sorted(boards.BOARDS.items())}}


def job_history(args):
    return {"runs": store.history(args.get("scope") or "")}


HANDLERS = {"company_jobs": company_jobs, "search_jobs": search_jobs, "find_company": find_company,
            "list_sources": list_sources, "job_history": job_history}


def handle(msg):
    """处理一条消息，返回要回的消息（通知返回 None）。"""
    mid, method = msg.get("id"), msg.get("method")
    if mid is None:   # 通知（如 notifications/initialized），不回
        return None
    if method == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL
        res = {"protocolVersion": ver, "capabilities": {"tools": {}},
               "serverInfo": {"name": "hiring-radar", "version": __version__}}
    elif method == "ping":
        res = {}
    elif method == "tools/list":
        res = {"tools": TOOLS}
    elif method == "tools/call":
        p = msg.get("params") or {}
        fn = HANDLERS.get(p.get("name"))
        if not fn:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"未知工具：{p.get('name')}"}}
        try:
            with contextlib.redirect_stdout(sys.stderr):
                data = fn(p.get("arguments") or {})
            res = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}], "isError": False}
        except Exception as e:   # 工具出错按 MCP 约定放进结果里，让调用方看到原因
            sys.stderr.write(f"[hiring-radar] {p.get('name')} 出错：{type(e).__name__}: {e}\n")
            if http.DEBUG:
                traceback.print_exc(file=sys.stderr)
            res = {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"不支持的方法：{method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": res}


def serve(inp=None, out=None):
    inp, out = inp or sys.stdin, out or sys.stdout
    sys.stderr.write(f"[hiring-radar] MCP 服务已启动（v{__version__}，stdio）\n")
    for line in inp:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "不是合法 JSON"}}
        else:
            reply = handle(msg) if isinstance(msg, dict) else \
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "不支持批量请求"}}
        if reply is not None:
            out.write(json.dumps(reply, ensure_ascii=False) + "\n")
            out.flush()
