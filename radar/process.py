"""结果处理：时间分档、标疑似中介、多来源去重。规则是粗筛，用于计数和过滤，不是精确判定。"""
import re

from .schema import AGES, age_of, days_ago

# 中介/猎头/劳务派遣：公司名命中下列词，或 JD 里写「代客户招聘」
AGENCY_NAME = re.compile(
    r"recruit|staffing|personnel|employment (services|agency)|labou?r hire|workforce solutions|executive search|"
    r"search partners|talent (solutions|partners|international)|headhunt|\bhays\b|randstad|adecco|manpower|"
    r"robert half|michael page|page personnel|kelly services|hudson|chandler macleod|people2people|aerotek|"
    r"insight global|teksystems|allegis|spherion|express employment|kforce|apex systems|harvey nash|"
    r"hire resolve|pyramid global|programmed skilled", re.I)
AGENCY_JD = re.compile(r"on behalf of (our|a|an) (valued |leading |established )?client|"
                       r"our client,? (is|are|a|an|based)\b|we are (partnering|working) with (our|a|an) client", re.I)
# 招聘系统厂商自己的名字里也带 recruit，排除
ATS_VENDOR = re.compile(r"^(smartrecruiters|zoho ?recruit|jobadder|recruitee|livehire|recruiterflow|recruit ?crm)\b", re.I)

_SUFFIX = re.compile(r"\b(pty|ltd|limited|inc|incorporated|llc|llp|plc|gmbh|ag|bv|sa|sas|ab|oy|as|co|corp|corporation|"
                     r"company|group|holdings|the|australia|aus|nz|new zealand|uk|usa|us|canada)\b")


def agency_of(it):
    """疑似中介时返回命中的词（公司名优先），否则空串。"""
    name = it.get("company", "")
    if name and not ATS_VENDOR.search(name):
        m = AGENCY_NAME.search(name)
        if m:
            return m.group(0).lower()
    m = AGENCY_JD.search(it.get("jd", "")[:3000])
    return "jd:our client" if m else ""


def annotate(items, now=None):
    """补 age（时间分档）和 agency（疑似中介）。已有值的不覆盖（插件可自带判断）。"""
    for it in items:
        it["age"] = it.get("age") or age_of(it.get("date"), now)
        if not it.get("agency"):
            it["agency"] = agency_of(it)
    return items


def norm_company(s):
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    return re.sub(r"\s+", "", _SUFFIX.sub(" ", s))


def norm_title(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def dedupe_key(it):
    return f"{(it.get('country') or '').split(',')[0]}|{norm_company(it.get('company'))}|{norm_title(it.get('title'))}"


def dedupe(items, order=()):
    """多来源去重：按 国家 + 公司名 + 职位名（去标点和公司后缀）合并。
    每组留一条：有完整 JD（>300 字）的优先，其次按 order 里来源的先后；其他来源记进 also。
    注意：同一公司同名职位在同一国家多个城市发布，也会合成一条。"""
    rank = {s: i for i, s in enumerate(order)}

    def top(src):
        return rank.get((src or "").split("/")[0], len(rank))

    groups = {}
    for it in items:
        groups.setdefault(dedupe_key(it), []).append(it)
    out = []
    for rs in groups.values():
        rs.sort(key=lambda r: (len(r.get("jd") or "") <= 300, top(r.get("source"))))
        best = rs[0]
        others = sorted({r.get("source", "") for r in rs[1:]} - {best.get("source", "")})
        if others:
            best["also"] = ",".join(x for x in [best.get("also")] + others if x)
        if not best.get("date"):  # 代表记录没日期时，用其他副本里最新的
            dated = [r["date"] for r in rs if days_ago(r.get("date")) is not None]
            best["date"] = min(dated, key=days_ago) if dated else ""
            best["age"] = age_of(best["date"])
        for f in ("industry", "size", "comp", "agency"):
            if not best.get(f):
                best[f] = next((r[f] for r in rs if r.get(f)), "")
        out.append(best)
    return out


def age_counts(items):
    c = {a: 0 for a in AGES}
    for it in items:
        c[it.get("age") or "unknown"] = c.get(it.get("age") or "unknown", 0) + 1
    return c
