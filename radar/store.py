"""本地存档（SQLite，标准库）：每次 --save 记一次拉取，职位记首次/最近看到的日期，可看环比。

库默认在 ~/.hiring-radar/radar.db（HIRING_RADAR_DB 可改）。只存在本机，不上传。
「范围」(scope) = 这次拉的是什么，如 greenhouse/anthropic、boards:freehire|AU|receptionist；
同一范围的相邻两次拉取比较，得出新增和下架。
"""
import hashlib
import json
import os
import sqlite3
import time

from .directory import HOME

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, at TEXT, scope TEXT, query TEXT, n INTEGER);
CREATE TABLE IF NOT EXISTS jobs(key TEXT PRIMARY KEY, source TEXT, company TEXT, title TEXT, location TEXT,
                                country TEXT, url TEXT, date TEXT, first_seen TEXT, last_seen TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS seen(run INTEGER, key TEXT, PRIMARY KEY(run, key));
CREATE INDEX IF NOT EXISTS runs_scope ON runs(scope, id);
"""


def db_path(path=None):
    return path or os.environ.get("HIRING_RADAR_DB") or os.path.join(HOME, "radar.db")


def connect(path=None):
    p = db_path(path)
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    con = sqlite3.connect(p)
    con.executescript(SCHEMA)
    return con


def job_key(it):
    src = it.get("source") or ""
    jid = it.get("id") or it.get("url")
    if jid:
        return f"{src}|{jid}"
    h = hashlib.sha1(f"{it.get('company')}|{it.get('title')}|{it.get('location')}".encode("utf-8")).hexdigest()[:16]
    return f"{src}|h:{h}"


def _diff(con, run, prev):
    if not prev:
        return None, None
    new = con.execute("SELECT COUNT(*) FROM seen WHERE run=? AND key NOT IN (SELECT key FROM seen WHERE run=?)",
                      (run, prev)).fetchone()[0]
    gone = con.execute("SELECT COUNT(*) FROM seen WHERE run=? AND key NOT IN (SELECT key FROM seen WHERE run=?)",
                       (prev, run)).fetchone()[0]
    return new, gone


def save(items, scope, query, path=None):
    """存一次拉取。给每条补 first_seen / last_seen。返回 {run, n, new, gone, prev_at}（首次拉取 new/gone 为 None）。"""
    con = connect(path)
    today = time.strftime("%Y-%m-%d")
    with con:
        run = con.execute("INSERT INTO runs(at, scope, query, n) VALUES(?,?,?,?)",
                          (time.strftime("%Y-%m-%dT%H:%M:%S"), scope, json.dumps(query, ensure_ascii=False),
                           len(items))).lastrowid
        for it in items:
            k = job_key(it)
            row = con.execute("SELECT first_seen FROM jobs WHERE key=?", (k,)).fetchone()
            it["first_seen"] = row[0] if row else today
            it["last_seen"] = today
            con.execute("INSERT OR REPLACE INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (k, it.get("source"), it.get("company"), it.get("title"), it.get("location"),
                         it.get("country"), it.get("url"), it.get("date"), it["first_seen"], today,
                         json.dumps(it, ensure_ascii=False)))
            con.execute("INSERT OR IGNORE INTO seen VALUES(?,?)", (run, k))
        prev = con.execute("SELECT id, at FROM runs WHERE scope=? AND id<? ORDER BY id DESC LIMIT 1",
                           (scope, run)).fetchone()
        new, gone = _diff(con, run, prev[0] if prev else None)
    con.close()
    return {"run": run, "n": len(items), "new": new, "gone": gone, "prev_at": prev[1] if prev else None}


def history(scope_like="", path=None, limit=200):
    """各范围的历次拉取：时间、条数、比上一次新增、下架。"""
    if not os.path.exists(db_path(path)):
        return []
    con = connect(path)
    rows = con.execute("SELECT id, at, scope, n FROM runs WHERE scope LIKE ? ORDER BY scope, id",
                       (f"%{scope_like}%",)).fetchall()
    out, last = [], {}
    for rid, at, scope, n in rows:
        new, gone = _diff(con, rid, last.get(scope))
        out.append({"scope": scope, "at": at, "n": n, "new": new, "gone": gone})
        last[scope] = rid
    con.close()
    return out[-limit:]
