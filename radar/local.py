"""本地解析器：解析【自建 / 中国官方企业招聘页】等无标准 ATS 的来源。

机制：spawn 一个本地脚本(放 parsers/ 下)，脚本自己抓页面 + 把岗位 JSON 打到 stdout，本工具解析+过滤+汇总。
安全：command 只能是已知解释器或 PARSER_ROOT 内文件；解释器情形第一个参数须为 root 内脚本(禁内联代码)；不用 shell。
"""
import json
import os
import subprocess

from .schema import rec, strip_html

PARSER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录
ALLOWED_INTERP = {"python3", "python", "node", "deno", "bun", "sh", "bash"}
EXT_INTERP = {".py": "python3", ".mjs": "node", ".js": "node", ".sh": "bash", ".ts": "deno"}
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


def resolve_inside_root(path):
    """把 path 解析为绝对路径并确认在 PARSER_ROOT 内且存在；否则 None（防路径逃逸）。"""
    try:
        cand = path if os.path.isabs(path) else os.path.join(PARSER_ROOT, path)
        rp = os.path.realpath(cand)
    except (TypeError, ValueError):
        return None
    root = os.path.realpath(PARSER_ROOT)
    if (rp == root or rp.startswith(root + os.sep)) and os.path.exists(rp):
        return rp
    return None


def normalize(j):
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
    return rec(
        title=pick("title", "name", "position"),
        company=pick("company", "company_name", "employer"),
        location=loc,
        dept=pick("dept", "department", "category", "team"),
        type=pick("type", "job_type", "employment_type"),
        date=pick("date", "postedAt", "posted_at", "published_at", "created_at", "pub_date", "publish_time"),
        comp=pick("comp", "salary", "compensation"),
        req_id=str(pick("req_id", "requisition_id") or ""),
        jd=strip_html(pick("jd", "description", "content", "requirement")),
        url=pick("url", "jobUrl", "job_url", "applyUrl", "apply_url", "link", "hostedUrl", "absolute_url"),
        apply_url=pick("apply_url", "applyUrl", "url", "link"),
        id=str(pick("id", "slug", "req_id") or ""),
        country=pick("country"),
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
        rp = resolve_inside_root(first)
        if not rp:
            raise RuntimeError(f"脚本须在 {PARSER_ROOT} 内且存在: {first}")
        args[0] = rp
    else:
        rp = resolve_inside_root(cmd)
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
    except ValueError as e:
        raise RuntimeError(f"local parser 输出非 JSON: {e}；头部: {out[:200]!r}")
    rows = data if isinstance(data, list) else (data.get("jobs") or data.get("results") or data.get("data") or [])
    items = [normalize(j) for j in rows if isinstance(j, dict)]
    items = [it for it in items if it["title"]]
    src = f"local/{name}"
    for it in items:
        it["source"] = src
    return items, src


def load_company_seeds():
    """从 parsers/companies.seed 读中国公司种子表，合并进 LOCAL_PARSERS（内置脚本优先，不覆盖）。
    格式： key | type | 公司名 | arg1 | arg2 | 赛道   （# 开头与空行忽略）
    feishu: arg1=门户域名；moka: arg1=orgId, arg2=siteId；beisen: arg1=slug({slug}.zhiye.com)。扩公司=往该文件加一行，零代码。"""
    path = os.path.join(PARSER_ROOT, "parsers", "companies.seed")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
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
