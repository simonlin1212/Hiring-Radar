"""本地存档（SQLite，标准库）：每次 --save 记一次拉取，职位记首次/最近看到的日期，可看环比。

库默认在 ~/.hiring-radar/radar.db（HIRING_RADAR_DB 可改）。只存在本机，不上传。
「范围」(scope) = 这次拉的是什么，如 greenhouse/anthropic、boards:freehire|AU|receptionist。
新增和下架只在「同一范围、同样筛选条件、两次都完整」的相邻拉取之间比较：
条件不同（关键词、近 N 天、上限、去重……）或结果不完整（出错、上游截断、到 --max 上限）的那次只记录，不当比较基线。
设了近 N 天时，上次有、这次因为超出时间窗口而没出现的，不算下架（按上次拉取时记下的发布日期判断）。
每次的新增/下架在存档时算好存进 runs，之后别的查询改写了同一职位，也不会改动历史数字。
"""
import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

from .directory import HOME
from .schema import older_than

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, at TEXT, scope TEXT, query TEXT, n INTEGER,
                                qkey TEXT, complete INTEGER DEFAULT 0, new INTEGER, gone INTEGER);
CREATE TABLE IF NOT EXISTS jobs(key TEXT PRIMARY KEY, source TEXT, company TEXT, title TEXT, location TEXT,
                                country TEXT, url TEXT, date TEXT, first_seen TEXT, last_seen TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS seen(run INTEGER, key TEXT, date TEXT, PRIMARY KEY(run, key));
CREATE INDEX IF NOT EXISTS runs_scope ON runs(scope, id);
"""


def db_path(path=None):
    return path or os.environ.get("HIRING_RADAR_DB") or os.path.join(HOME, "radar.db")


# 早期测试版建的库缺这些列：补上。旧记录 complete=0，算条件未知、不参与比较
_ADD = {"runs": (("qkey", "TEXT"), ("complete", "INTEGER DEFAULT 0"), ("new", "INTEGER"), ("gone", "INTEGER")),
        "seen": (("date", "TEXT"),)}


def _missing(con):
    out = []
    for table, cols in _ADD.items():
        have = {r[1] for r in con.execute(f"PRAGMA table_info({table})")}
        out += [(table, c, t) for c, t in cols if c not in have]
    return out


def connect(path=None):
    p = db_path(path)
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    con = sqlite3.connect(p, timeout=30)
    con.executescript(SCHEMA)
    if _missing(con):
        con.execute("BEGIN IMMEDIATE")   # 先拿写锁再查再改：两个进程同时迁移旧库也不会重复加列
        try:
            for table, col, typ in _missing(con):
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
            con.commit()
        except BaseException:
            con.rollback()
            raise
    return con


def query_key(query):
    """筛选条件的指纹（公司名写法不同不影响，范围里已含招聘系统和账号）。"""
    q = {k: v for k, v in (query or {}).items() if k != "company"}
    return hashlib.sha1(json.dumps(q, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def job_key(it):
    src = it.get("source") or ""
    jid = it.get("id") or it.get("url")
    if jid:
        return f"{src}|{jid}"
    h = hashlib.sha1(f"{it.get('company')}|{it.get('title')}|{it.get('location')}".encode("utf-8")).hexdigest()[:16]
    return f"{src}|h:{h}"


def _when(at):
    """存档时间（本机时间）→ aware datetime。"""
    try:
        return datetime.strptime(at[:19], "%Y-%m-%dT%H:%M:%S").astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _diff(con, run, prev, recent_days=0, at=None):
    """run 比 prev 新增几条、下架几条。设了近 N 天时，因超出时间窗口而消失的不算下架。
    发布日期用上次拉取时记下的（seen.date），旧库没有时才退回职位表里最新的日期。"""
    if not prev:
        return None, None
    new = con.execute("SELECT COUNT(*) FROM seen WHERE run=? AND key NOT IN (SELECT key FROM seen WHERE run=?)",
                      (run, prev)).fetchone()[0]
    rows = con.execute("SELECT s.key, COALESCE(s.date, j.date) FROM seen s LEFT JOIN jobs j ON j.key = s.key "
                       "WHERE s.run=? AND s.key NOT IN (SELECT key FROM seen WHERE run=?)", (prev, run)).fetchall()
    now = _when(at)
    gone = sum(1 for _, d in rows if not (recent_days and older_than(d, recent_days, now)))
    return new, gone


def save(items, scope, query, path=None, complete=True):
    """存一次拉取。给每条补 first_seen / last_seen。
    返回 {run, n, new, gone, prev_at, complete}：没有可比的上一次、或这次不完整时 new/gone 为 None。"""
    con = connect(path)
    today = time.strftime("%Y-%m-%d")
    at = time.strftime("%Y-%m-%dT%H:%M:%S")   # 本机时间，和 --history 显示一致
    qkey = query_key(query)
    with con:
        run = con.execute("INSERT INTO runs(at, scope, query, n, qkey, complete) VALUES(?,?,?,?,?,?)",
                          (at, scope, json.dumps(query, ensure_ascii=False), len(items), qkey,
                           1 if complete else 0)).lastrowid
        for it in items:
            k = job_key(it)
            row = con.execute("SELECT first_seen FROM jobs WHERE key=?", (k,)).fetchone()
            it["first_seen"] = row[0] if row else today
            it["last_seen"] = today
            con.execute("INSERT OR REPLACE INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (k, it.get("source"), it.get("company"), it.get("title"), it.get("location"),
                         it.get("country"), it.get("url"), it.get("date"), it["first_seen"], today,
                         json.dumps(it, ensure_ascii=False)))
            con.execute("INSERT OR IGNORE INTO seen(run, key, date) VALUES(?,?,?)", (run, k, it.get("date")))
        prev = con.execute("SELECT id, at FROM runs WHERE scope=? AND qkey=? AND complete=1 AND id<? "
                           "ORDER BY id DESC LIMIT 1", (scope, qkey, run)).fetchone() if complete else None
        new, gone = _diff(con, run, prev[0] if prev else None, (query or {}).get("recent_days") or 0, at)
        con.execute("UPDATE runs SET new=?, gone=? WHERE id=?", (new, gone, run))   # 存下结果，历史不再重算
    con.close()
    return {"run": run, "n": len(items), "new": new, "gone": gone, "prev_at": prev[1] if prev else None,
            "complete": bool(complete)}


def history(scope_like="", path=None, limit=200):
    """各范围的历次拉取：时间、条数、比上一次新增、下架（存档时算好的数字）。"""
    if not os.path.exists(db_path(path)):
        return []
    con = connect(path)
    rows = con.execute("SELECT at, scope, n, new, gone, complete FROM runs WHERE scope LIKE ? ORDER BY scope, id",
                       (f"%{scope_like}%",)).fetchall()
    con.close()
    out = [{"scope": scope, "at": at, "n": n, "new": new, "gone": gone, "complete": bool(complete)}
           for at, scope, n, new, gone, complete in rows]
    return out[-limit:]
