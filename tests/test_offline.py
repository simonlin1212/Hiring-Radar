#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线单元测试：不连外网（http 层用本机 127.0.0.1 临时服务测）。
用法: python3 tests/test_offline.py   或   python3 -m unittest discover tests"""
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix="hiring-radar-test-")
os.environ["HIRING_RADAR_HOME"] = TMP          # 名录、存档、续跑进度都写到临时目录
os.environ["HIRING_RADAR_DELAY"] = "0"
sys.path.insert(0, ROOT)

from radar import ats, boards, cli, directory, http, plugins, process, store, sweep  # noqa: E402
from radar.boards import freehire, workable  # noqa: E402
from radar.schema import FIELDS, FIELDS_V1, age_of, days_ago, rec  # noqa: E402

NOW = datetime(2026, 10, 12, tzinfo=timezone.utc)


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            cli.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return code, out.getvalue(), err.getvalue()


class Schema(unittest.TestCase):
    def test_fields(self):
        self.assertEqual(FIELDS[:15], FIELDS_V1)
        self.assertEqual(len(set(FIELDS)), len(FIELDS))

    def test_dates(self):
        self.assertEqual(days_ago("2026-10-02T08:00:00Z", NOW), 10)   # 按日计
        self.assertEqual(days_ago(str(int(datetime(2026, 9, 12, tzinfo=timezone.utc).timestamp() * 1000)), NOW), 30)
        self.assertEqual(days_ago("Wed, 01 Jul 2026 10:00:00 +0000", NOW), 102)
        self.assertEqual(days_ago("Posted 30+ Days Ago", NOW), 30)
        self.assertIsNone(days_ago("", NOW))
        self.assertIsNone(days_ago("soon", NOW))

    def test_age_buckets(self):
        self.assertEqual(age_of("2026-07-12", NOW), "0-3m")   # 92 天
        self.assertEqual(age_of("2026-07-11", NOW), "3-6m")   # 93 天
        self.assertEqual(age_of("2026-04-12", NOW), "3-6m")   # 183 天
        self.assertEqual(age_of("2026-04-11", NOW), "6m+")
        self.assertEqual(age_of("", NOW), "unknown")


class Process(unittest.TestCase):
    def test_agency(self):
        self.assertEqual(process.agency_of({"company": "Hays Recruitment"}), "hays")
        self.assertEqual(process.agency_of({"company": "SmartRecruiters Inc"}), "")
        self.assertEqual(process.agency_of({"company": "Acme", "jd": "We are recruiting on behalf of our client, a firm"}),
                         "jd:our client")
        self.assertEqual(process.agency_of({"company": "Acme Dental", "jd": "Join our clinic"}), "")

    def test_dedupe(self):
        a = rec(title="Receptionist", company="Acme Pty Ltd", country="AU", source="freehire/workable",
                jd="x" * 400, date="", industry="")
        b = rec(title="Receptionist ", company="ACME", country="AU", source="workable/search", jd="short",
                date="2026-10-01", industry="Dental")
        c = rec(title="Receptionist", company="Acme", country="NZ", source="workable/search")
        out = process.dedupe([b, a, c], order=["workable", "freehire"])
        self.assertEqual(len(out), 2)
        au = [r for r in out if r["country"] == "AU"][0]
        self.assertEqual(au["source"], "freehire/workable")    # 完整 JD 优先
        self.assertEqual(au["also"], "workable/search")
        self.assertEqual(au["date"], "2026-10-01")             # 日期从副本补
        self.assertEqual(au["industry"], "Dental")

    def test_annotate_keeps_existing(self):
        it = rec(company="Hays", age="0-3m", agency="plugin-said")
        process.annotate([it], NOW)
        self.assertEqual((it["age"], it["agency"]), ("0-3m", "plugin-said"))


class Mappings(unittest.TestCase):
    def test_freehire(self):
        r = freehire.to_rec({
            "public_slug": "abc", "source": "workday", "title": "Bookkeeper", "company": "Acme",
            "location": "Sydney", "description": "Do books", "countries": ["au"], "work_mode": "onsite",
            "posted_at": "2026-10-01T00:00:00Z", "url": "https://x/1",
            "enrichment": {"category": "Finance", "employment_type": "full_time", "salary_min": 70000,
                           "salary_max": 80000, "salary_currency": "AUD", "salary_period": "year",
                           "company_size": "11-50", "domains": ["accounting"]}})
        self.assertEqual(r["country"], "AU")
        self.assertEqual(r["source"], "freehire/workday")
        self.assertEqual(r["comp"], "AUD 70000-80000/year")
        self.assertEqual((r["size"], r["industry"], r["dept"]), ("11-50", "accounting", "Finance"))
        self.assertEqual(set(r), set(FIELDS))

    def test_workable(self):
        r = workable.to_rec({"id": 7, "title": "Office Admin", "company": {"title": "Beta"},
                             "location": {"city": "Auckland", "countryName": "New Zealand"},
                             "locations": ["TELECOMMUTE"], "description": "<p>Hi</p>", "benefitsSection": "<li>Fun</li>",
                             "created": "2026-09-30", "url": "https://jobs.workable.com/view/7"})
        self.assertEqual((r["country"], r["remote"], r["company"]), ("NZ", "Remote", "Beta"))
        self.assertIn("Hi", r["jd"])
        self.assertIn("Fun", r["jd"])

    def test_jsonld(self):
        html = """<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization"},
        {"@type":"JobPosting","title":"Receptionist","datePosted":"2026-10-01","description":"<p>Answer calls</p>",
         "hiringOrganization":{"name":"Acme Dental"},"employmentType":["FULL_TIME","PART_TIME"],"identifier":{"value":"R1"},
         "jobLocation":{"address":{"addressLocality":"Perth","addressRegion":"WA","addressCountry":"AUS"}},
         "baseSalary":{"currency":"AUD","value":{"minValue":30,"maxValue":35,"unitText":"HOUR"}}}]}</script>"""
        jp = ats._jsonld.postings(html)
        self.assertEqual(len(jp), 1)
        r = ats._jsonld.to_rec(jp[0], "https://x/1")
        self.assertEqual((r["title"], r["company"], r["id"], r["date"]), ("Receptionist", "Acme Dental", "R1", "2026-10-01"))
        self.assertEqual((r["location"], r["country"]), ("Perth, WA, AU", "AU"))
        self.assertEqual((r["comp"], r["type"], r["jd"]), ("AUD 30-35/hour", "FULL_TIME, PART_TIME", "Answer calls"))
        self.assertEqual(ats._jsonld.postings("<script type='application/ld+json'>{bad json</script>"), [])

    def test_gov_boards(self):
        from radar.boards import arbeitsagentur, jobtech, mycareersfuture, reed
        r = jobtech.to_rec({"id": "1", "headline": "Receptionist", "employer": {"name": "IES"},
                            "workplace_address": {"municipality": "Trelleborg", "region": "Skåne län", "country": "Sverige"},
                            "description": {"text": "Svara i telefon"}, "publication_date": "2026-10-09T15:39:28",
                            "occupation": {"label": "Kontorsreceptionist"}, "webpage_url": "https://af/1"})
        self.assertEqual((r["country"], r["location"], r["jd"], r["source"]), ("SE", "Trelleborg, Skåne län", "Svara i telefon", "gov/jobtech"))
        r = mycareersfuture.to_rec({"title": "Admin", "postedCompany": {"name": "Acme Pte"}, "uuid": "u1",
                                    "salary": {"minimum": 2700, "maximum": 3100, "type": {"salaryType": "Monthly"}},
                                    "metadata": {"jobPostId": "MCF-1", "newPostingDate": "2026-10-12", "isPostedOnBehalf": True}})
        self.assertEqual((r["comp"], r["id"], r["country"], r["agency"]), ("SGD 2700-3100/monthly", "MCF-1", "SG", "posted on behalf"))
        r = arbeitsagentur.to_rec({"stellenangebotsTitel": "Buchhalter/in", "firma": "X GmbH", "referenznummer": "R-1",
                                   "stellenlokationen": [{"adresse": {"ort": "Salzburg", "land": "OESTERREICH"}}],
                                   "arbeitszeitVollzeit": True, "vertragsdauer": "KEINE_ANGABE",
                                   "datumErsteVeroeffentlichung": "2026-10-11"})
        self.assertEqual((r["country"], r["type"], r["date"]), ("AT", "Vollzeit", "2026-10-11"))
        self.assertEqual(reed._date("09/10/2026"), "2026-10-09")

    def test_board_country_skip(self):
        """单一国家的来源：查别的国家时一条请求都不发。"""
        from radar.boards import arbeitsagentur, jobtech, mycareersfuture, reed, usajobs
        q = boards.Query(countries=["AU"])
        for m in (jobtech, mycareersfuture, arbeitsagentur, reed, usajobs):
            self.assertEqual(list(m.pages(q)), [])

    def test_careerplug_card(self):
        html = ('<a aria-label="x" href="/jobs/42"><div class="row"><div class="job-title col-sm-7">'
                '<span class="name">Office Admin</span></div><div class="job-location col-md-3">\n<div>\n'
                "<span class='job-row-title hidden-md'>Location:</span>\nVT-South Burlington-05403\n</div>\n</div>"
                '<div class="job-post-date col-md-2">\n<div>\n<span class=\'job-row-title\'>Post Date:</span>\n10-10-26\n'
                "</div>\n</div></div></a>")
        m = ats.careerplug._CARD.search(html)
        f = [ats.careerplug._field(m.group(2), c) for c in ("job-title", "job-location", "job-post-date")]
        self.assertEqual(f, ["Office Admin", "VT-South Burlington-05403", "10-10-26"])
        self.assertEqual((ats.careerplug._loc(f[1]), ats.careerplug._date(f[2])), ("South Burlington, VT", "2026-10-10"))

    def test_pageup_detail(self):
        html = ('<div id="job-content"><h2>Store Manager</h2><div class=\'jobdets\'><p><b>Job no:</b> 1<br>'
                '<b>Work type:</b> <span class="work-type permanent">Permanent / Full time</span></p>'
                '<b>Advertised:</b> <span class="open-date">\n<time datetime="2026-10-12T01:00:00Z">12 Oct 2026</time></span>'
                '<p>Lead the team.</p><!-- hidden --></div><a class="back-link button" href="/">Back</a>')
        jd, wt, adv = ats.pageup._detail(html)
        self.assertEqual((wt, adv), ("Permanent / Full time", "2026-10-12T01:00:00Z"))
        self.assertIn("Lead the team.", jd)
        self.assertNotIn("hidden", jd)


class Security(unittest.TestCase):
    def test_slug(self):
        for bad in ("a/b", "evil.com", "x@y", "", "a b", "../x"):
            with self.assertRaises(ValueError):
                ats.check_slug("greenhouse", bad)
        self.assertEqual(ats.check_slug("greenhouse", " Acme_1-x "), "Acme_1-x")

    def test_workday_host(self):
        self.assertEqual(ats.workday.check("NVIDIA.wd5.myworkdayjobs.com", "nvidia", "Ext")[0],
                         "nvidia.wd5.myworkdayjobs.com")
        for host in ("evil.com", "x.myworkdayjobs.com.evil.com", "a.b.wd5.myworkdayjobs.com", "x.wd5.myworkdayjobs.com/"):
            with self.assertRaises(ValueError):
                ats.workday.check(host, "t", "s")
        with self.assertRaises(ValueError):
            ats.workday.check("x.wd5.myworkdayjobs.com", "t", "../s")

    def test_keys_not_leaked(self):
        self.assertEqual(http.safe("https://a/x?app_id=ID1&what=a&app_key=SEC&page=2"),
                         "https://a/x?app_id=***&what=a&app_key=***&page=2")
        from radar.boards import adzuna
        old = {k: os.environ.pop(k, None) for k in ("ADZUNA_APP_ID", "ADZUNA_APP_KEY")}
        try:
            with self.assertRaises(ValueError) as cm:
                list(adzuna.pages(boards.Query(countries=["AU"])))
            self.assertIn("ADZUNA_APP_KEY", str(cm.exception))
        finally:
            os.environ.update({k: v for k, v in old.items() if v})

    def test_meta_hosts(self):
        """名录给的 host/board_id 也要过检查，防止被改写到别的域名（这些检查在发请求之前）。"""
        for meta in ({"host": "evil.com", "instance": "1", "clientkey": "a"},
                     {"host": "careers.pageuppeople.com.evil.com", "instance": "1", "clientkey": "a"},
                     {"host": "careers.pageuppeople.com", "instance": "1/../x", "clientkey": "a"},
                     {"host": "careers.pageuppeople.com", "instance": "1", "clientkey": "a/b"}):
            with self.assertRaises(ValueError):
                ats.fetch("pageup", "x", meta)
        for meta in ({}, {"board_id": "../../x"}, {"board_id": "de1785c1-76c7-4265-b621-ebc07480ed5d/x"}):
            with self.assertRaises(ValueError):
                ats.fetch("ultipro", "x", meta)


class Directory(unittest.TestCase):
    def setUp(self):
        os.makedirs(os.path.dirname(directory.PATH), exist_ok=True)
        doc = {"fetched_at": "2026-10-12T00:00:00Z", "tenants": {
            "bamboohr": [["acme"]],
            "greenhouse": [["acmeinc"], ["other"]],
            "workday": [["acme", {"host": "acme.wd3.myworkdayjobs.com", "site": "Careers"}]]}}
        with open(directory.PATH, "w") as f:
            json.dump(doc, f)
        directory._index = None

    def tearDown(self):
        os.remove(directory.PATH)
        directory._index = None

    def test_lookup_order(self):
        self.assertEqual([h["ats"] for h in directory.lookup("Acme, Inc.")], ["greenhouse", "workday", "bamboohr"])
        self.assertEqual(directory.lookup("The Acme Careers")[0]["slug"], "acmeinc")
        self.assertEqual(directory.lookup("nobody"), [])
        self.assertEqual(directory.meta_for("workday", "ACME")["site"], "Careers")
        self.assertEqual(directory.info()["counts"]["greenhouse"], 2)


class Store(unittest.TestCase):
    def test_new_and_gone(self):
        db = os.path.join(TMP, "t.db")
        j = lambda i: rec(title=f"T{i}", source="greenhouse/x", id=str(i))  # noqa: E731
        s1 = store.save([j(1), j(2)], "greenhouse/x", {}, db)
        self.assertIsNone(s1["new"])
        items = [j(2), j(3), j(4)]
        s2 = store.save(items, "greenhouse/x", {}, db)
        self.assertEqual((s2["new"], s2["gone"]), (2, 1))
        self.assertTrue(all(it["first_seen"] and it["last_seen"] for it in items))
        h = store.history("greenhouse", db)
        self.assertEqual([(r["n"], r["new"], r["gone"]) for r in h], [(2, None, None), (3, 2, 1)])


class FakeBoard:
    """测试用来源：两页；fail_at 指定在第几页抛错（模拟限流）。"""
    FILTERS = {"keyword"}

    def __init__(self, name, n=4, fail_at=None):
        self.NAME, self.DESC, self.n, self.fail_at, self.calls = name, "fake", n, fail_at, 0

    def pages(self, q, state=None):
        start = (state or {}).get("p", 0)
        for p in range(start, 2):
            self.calls += 1
            if self.fail_at is not None and p == self.fail_at:
                self.fail_at = None   # 只失败一次，续跑时成功
                raise http.RateLimited("429")
            rows = [rec(title=f"{self.NAME} job {p}-{i}", company="Co", country="AU" if i % 2 else "NZ",
                        location="", date="2026-10-01", id=f"{p}-{i}") for i in range(self.n // 2)]
            yield rows, {"p": p + 1}


class Sweep(unittest.TestCase):
    def setUp(self):
        self.a, self.b = FakeBoard("fake_a"), FakeBoard("fake_b", fail_at=1)
        boards.BOARDS.update({"fake_a": self.a, "fake_b": self.b})

    def tearDown(self):
        for k in ("fake_a", "fake_b"):
            boards.BOARDS.pop(k, None)

    def test_error_then_resume(self):
        q = boards.Query(countries=["AU"])
        with redirect_stderr(io.StringIO()):
            items, rep = sweep.run(["fake_a", "fake_b"], q)
        self.assertEqual(rep["fake_a"], {"n": 2, "capped": False})           # 本地按国家补过滤
        self.assertIn("error", rep["fake_b"])
        self.assertEqual(rep["fake_b"]["n"], 1)
        with redirect_stderr(io.StringIO()):
            items, rep = sweep.run(["fake_a", "fake_b"], q, resume=True)
        self.assertNotIn("error", rep["fake_b"])
        self.assertEqual(len(items), 4)
        self.assertEqual(self.a.calls, 2)                                      # 已完成的来源不重拉
        self.assertEqual(os.listdir(sweep.DIR), [])                            # 跑完删进度

    def test_resume_ignores_unsaved_lines(self):
        q = boards.Query(keywords=["x-only-this-test"])
        self.a.FILTERS = {"keyword"}
        stp, spool = sweep._paths(["fake_a"], q)
        os.makedirs(sweep.DIR, exist_ok=True)
        with open(stp, "w") as f:
            json.dump({"cursor": {"fake_a": {"p": 1}}, "done": {}, "report": {"fake_a": {"n": 2, "capped": False}},
                       "lines": 2}, f)
        with open(spool, "w") as f:
            for i in range(3):   # 第 3 行是「写了但没记进度」的
                f.write(json.dumps(rec(title=f"old {i}", id=f"o{i}")) + "\n")
        with redirect_stderr(io.StringIO()):
            items, rep = sweep.run(["fake_a"], q, resume=True)
        self.assertEqual([it["id"] for it in items], ["o0", "o1", "1-0", "1-1"])
        self.assertEqual(rep["fake_a"]["n"], 4)

    def test_max_items(self):
        items, rep = sweep.run(["fake_a"], boards.Query(max_items=3))
        self.assertEqual((len(items), rep["fake_a"]["capped"]), (3, True))


class Plugins(unittest.TestCase):
    def test_load_and_cli(self):
        d = tempfile.mkdtemp(dir=TMP)
        with open(os.path.join(d, "mysite.py"), "w") as f:
            f.write("NAME='mysite'\nDESC='demo'\nFILTERS={'country'}\n"
                    "def pages(q, state=None):\n"
                    "    yield [dict(title='Receptionist', company='Hays Recruitment', country='AU', jd='', id='1',\n"
                    "                date='2026-10-01', source='plugin/mysite'),\n"
                    "           dict(title='Receptionist', company='Hays', country='AU', jd='', id='2',\n"
                    "                date='2025-01-01', source='plugin/mysite')], None\n")
        with open(os.path.join(d, "_skip.py"), "w") as f:
            f.write("raise SystemExit('must not load')\n")
        try:
            code, out, err = run_cli("--plugins", d, "--board", "mysite", "--country", "AU", "--recent-days", "0",
                                     "--no-agency", "--json")
            self.assertEqual(code, 0, err)
            env = json.loads(out)
            for k in ("source", "total", "matched", "jobs", "version", "ages", "sources"):
                self.assertIn(k, env)
            self.assertEqual(env["total"], 2)
            self.assertEqual(env["matched"], 0)   # 两条都被判为中介后去掉
            code, out, err = run_cli("--board", "mysite", "--json")
            env = json.loads(out)
            self.assertEqual(env["total"], 1)     # 默认近半年：2025-01-01 那条被滤掉
            self.assertEqual(env["ages"]["0-3m"], 1)
        finally:
            boards.BOARDS.pop("mysite", None)


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hits = cls.hits = {}

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                hits[self.path] = hits.get(self.path, 0) + 1
                ua = self.headers.get("User-Agent", "")
                if self.path == "/flaky" and hits[self.path] == 1:
                    self.send_response(429)
                    self.send_header("Retry-After", "0")
                    self.end_headers()
                    return
                if self.path == "/always429":
                    self.send_response(429)
                    self.send_header("Retry-After", "0")
                    self.end_headers()
                    return
                if self.path == "/forbidden":
                    self.send_response(403)
                    self.end_headers()
                    return
                if self.path == "/challenge":
                    body = b"<html><title>Just a moment...</title></html>"
                else:
                    body = json.dumps({"ok": True, "ua": ua}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

        cls.srv = HTTPServer(("127.0.0.1", 0), H)
        cls.base = f"http://127.0.0.1:{cls.srv.server_port}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_honest_ua(self):
        self.assertIn("HiringRadar/", http.get_json(self.base + "/ok")["ua"])

    def test_retry_then_ok(self):
        with redirect_stderr(io.StringIO()):
            self.assertTrue(http.get_json(self.base + "/flaky")["ok"])
        self.assertEqual(self.hits["/flaky"], 2)

    def test_rate_limited(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(http.RateLimited):
            http.get_json(self.base + "/always429", tries=2)

    def test_blocked(self):
        with self.assertRaises(http.Blocked):
            http.get_json(self.base + "/forbidden")
        self.assertEqual(self.hits["/forbidden"], 1)   # 403 不重试
        with self.assertRaises(http.Blocked):
            http.get_text(self.base + "/challenge")


class Mcp(unittest.TestCase):
    def talk(self, *msgs):
        from radar import mcp
        out = io.StringIO()
        lines = [m if isinstance(m, str) else json.dumps(m) for m in msgs]
        with redirect_stderr(io.StringIO()):
            mcp.serve(io.StringIO("\n".join(lines) + "\n"), out)
        return [json.loads(l) for l in out.getvalue().splitlines()]

    def test_protocol(self):
        r = self.talk({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
                      {"jsonrpc": "2.0", "method": "notifications/initialized"},
                      {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                      {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_sources", "arguments": {}}},
                      {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nope"}},
                      {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                       "params": {"name": "company_jobs", "arguments": {"company": "x", "ats": "greenhouse", "slug": "a/b"}}},
                      "not json",
                      {"jsonrpc": "2.0", "id": 6, "method": "ping"})
        self.assertEqual([m.get("id") for m in r], [1, 2, 3, 4, 5, None, 6])   # 通知不回
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual({t["name"] for t in r[1]["result"]["tools"]},
                         {"company_jobs", "search_jobs", "find_company", "list_sources", "job_history"})
        src = json.loads(r[2]["result"]["content"][0]["text"])
        self.assertIn("pageup", src["ats"])
        self.assertEqual(src["boards"]["reed"]["needs_key"], "REED_API_KEY")
        self.assertEqual(r[3]["error"]["code"], -32602)
        self.assertTrue(r[4]["result"]["isError"])          # 非法 slug 被拦下，不发请求
        self.assertEqual(r[5]["error"]["code"], -32700)

    def test_slim(self):
        from radar import mcp
        s = mcp._slim(rec(title="A", jd="<p>" + "x" * 2000 + "</p>", _wd="tmp"))
        self.assertEqual(set(s), {"title", "jd"})
        self.assertEqual(len(s["jd"]), mcp.JD_CHARS + 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
