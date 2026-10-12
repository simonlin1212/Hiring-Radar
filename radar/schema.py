"""统一字段、HTML 转文本、日期与时间分档。"""
import email.utils
import html as _html
import re
from datetime import datetime, timezone

# v1 的 15 个字段（顺序不变，向后兼容）。注意 company=雇主、comp=薪资，两个不同键。
FIELDS_V1 = ["title", "company", "dept", "team", "location", "remote", "type",
             "date", "date_updated", "req_id", "comp", "jd", "url", "apply_url", "id"]
# v2 追加：
#   country     两位国家码（来源给了才有）
#   source      来源，如 greenhouse/anthropic、freehire/workday、board/remoteok
#   age         按发布日期分档：0-3m / 3-6m / 6m+ / unknown（见 AGES）
#   agency      疑似中介/猎头时为命中的词，否则为空
#   also        去重合并时，同一职位出现过的其他来源（逗号分隔）
#   industry / size   行业、公司规模（来源给了才有）
#   first_seen / last_seen   本地存档里首次、最近看到的日期（--save 时才有）
FIELDS = FIELDS_V1 + ["country", "source", "age", "agency", "also", "industry", "size", "first_seen", "last_seen"]

AGES = ["0-3m", "3-6m", "6m+", "unknown"]
AGE_LABEL = {"0-3m": "近3个月", "3-6m": "3-6个月", "6m+": "半年以前", "unknown": "无日期"}


def rec(**kw):
    r = {k: "" for k in FIELDS}
    r.update({k: (v if v is not None else "") for k, v in kw.items()})
    return r


def strip_html(s):
    """HTML → 纯文本（保留全长，不截断）。"""
    if not s:
        return ""
    t = re.sub(r"(?i)<br\s*/?>", "\n", str(s))
    t = re.sub(r"(?i)</(p|li|div|h[1-6])>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t ]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return t.strip()


def _parse(d):
    """各种日期 → aware datetime 或 None：epoch(秒/毫秒)、ISO、RFC 2822（RSS）。"""
    if d in (None, ""):
        return None
    s = str(d).strip()
    if s.isdigit():
        try:
            ts = int(s)
            if ts > 1e12:  # 毫秒
                ts /= 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    if m:
        try:
            return datetime.strptime(m.group(0), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", s)   # 中文日期（腾讯等）
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        except ValueError:
            return None
    try:
        dt = email.utils.parsedate_to_datetime(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, IndexError):
        return None


def fmt_date(d):
    """→ YYYY-MM-DD；认不出时原样截短。"""
    if not d:
        return ""
    dt = _parse(d)
    return dt.strftime("%Y-%m-%d") if dt else str(d)[:16]


def iso_day(d):
    """→ YYYY-MM-DD 或空串（认不出就空，不猜）。"""
    dt = _parse(d)
    return dt.strftime("%Y-%m-%d") if dt else ""


def _relative(d):
    """相对日期（Workday 的 Posted 3 Days Ago 等）→ (天数, 是否只是下界)；认不出返回 (None, False)。"""
    sl = str(d).lower()
    if "today" in sl:
        return 0, False
    if "yesterday" in sl:
        return 1, False
    m = re.search(r"(\d+)(\+?)\s*day", sl)
    if m:
        return int(m.group(1)), bool(m.group(2))
    m = re.search(r"(\d+)(\+?)\s*month", sl)
    if m:
        return int(m.group(1)) * 30, bool(m.group(2))
    return None, False


def days_ago(d, now=None):
    """各种日期字符串 → 距今天数(int) 或 None。另认相对日期（Posted 3 Days Ago）；
    「30+ Days Ago」只是下界，说不准具体多久，按无日期处理（返回 None），能否确定超期见 older_than。"""
    if not d:
        return None
    now = now or datetime.now(timezone.utc)
    dt = _parse(d)
    if dt:
        return (now - dt).days
    n, lower = _relative(d)
    return None if lower else n


def older_than(d, days, now=None):
    """能确定发布早于 days 天前才返回 True；无日期、说不准的（如「30+ 天前」而 days ≥ 30）返回 False（保留）。"""
    n = days_ago(d, now)
    if n is not None:
        return n > days
    if not d or _parse(d):
        return False
    lo, lower = _relative(d)
    return lower and lo > days


def age_of(d, now=None):
    """时间分档：近3个月(≤92天) / 3-6个月(≤183天) / 半年以前 / 无日期。"""
    n = days_ago(d, now)
    if n is None:
        return "unknown"
    return "0-3m" if n <= 92 else "3-6m" if n <= 183 else "6m+"


def short(s, n=48):
    """终端显示截断（仅摘要用；--json 始终全量）。"""
    s = str(s or "")
    return s if len(s) <= n else s[:n - 1] + "…"
