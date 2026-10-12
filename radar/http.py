"""联网：所有来源共用。

原则（与 README「使用边界」一致）：
- 如实报身份（User-Agent 写明 HiringRadar 和项目地址），不伪装浏览器指纹、不用代理池。
  例外：飞书招聘、字节跳动两个解析器用 BROWSER_UA（它们的接口不接受程序身份），其余规则照常；
  USAJobs 官方接口要求 User-Agent 填申请密钥的邮箱（boards/usajobs.py）。
- 429 / 502 / 503 / 504 按 Retry-After 退避重试（对方要求等太久就不等了，抛 RateLimited）；重试用完也抛 RateLimited，由调用方停下并报告。
- 403 或人机验证页（不论状态码）：不重试、不绕过，直接抛 Blocked。
- 报错信息里的密钥一律打码（网址参数、认证请求头、环境变量里读到的密钥），防止进日志、结果和续跑进度文件；
  入口调用 guard_stderr() 后，stderr 上的所有文字（含调试日志和异常堆栈）也会打码。
- 404 等确定性错误、域名不存在：立即抛出（auto-probe 靠它快速换下一个 ATS）。
- 同一主机两次请求之间至少间隔 HIRING_RADAR_DELAY 秒（默认 0.3），翻页时自动生效。
"""
import email.utils
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from . import __version__

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": f"Mozilla/5.0 (compatible; HiringRadar/{__version__}; +https://github.com/simonlin1212/Hiring-Radar)"}
# 唯一的例外：飞书招聘和字节跳动的接口只认浏览器 UA（如实报身份一律回 405），这两个解析器用它（README 已写明）。
# 其他来源一律用上面的 UA。
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TIMEOUT = 30
DELAY = float(os.environ.get("HIRING_RADAR_DELAY", "0.3"))
MAX_WAIT = 300  # Retry-After 超过这么多秒就不在本次运行里等，停下让用户稍后再跑
DEBUG = False  # --debug 时打印重试和被吞的异常

# 人机验证 / 反爬拦截页的特征（只认强特征，避免把正文里的 "captcha" 字样当拦截）
_CHALLENGE = ("cf-chl", "challenge-platform", "<title>just a moment...</title>", "attention required! | cloudflare",
              "px-captcha", "captcha-delivery.com", "_incapsula_resource", "perimeterx")


class Blocked(RuntimeError):
    """被拦截（403 / 人机验证）。按约定不绕过，调用方应停下。"""


class RateLimited(RuntimeError):
    """限流重试用完。调用方应停下，稍后再跑（sweep 可 --resume）。"""


_last = {}
_lock = threading.Lock()


def _space(url):
    host = urllib.parse.urlsplit(url).hostname or ""
    with _lock:
        wait = _last.get(host, 0) + DELAY - time.monotonic()
        _last[host] = max(time.monotonic(), _last.get(host, 0) + DELAY)
    if wait > 0:
        time.sleep(wait)


_SECRET = re.compile(r"([?&](?:app_id|app_key|api_key|apikey|key|token|access_token)=)[^&#]*", re.I)
_SECRET_HEADER = re.compile(r"auth|key|token|secret", re.I)
_secrets = set()


def add_secret(value):
    """登记一个密钥值：之后所有经 safe() 的文本里出现它都会被打码。"""
    v = str(value or "").strip()
    if len(v) >= 4:
        _secrets.add(v)


def safe(text):
    """报错/日志文本打码：网址里的密钥参数（如 Adzuna 的 app_key），以及登记过的密钥值
    （对方在报错正文里回显密钥时也能盖住）。避免密钥进日志、结果和续跑进度文件。"""
    t = _SECRET.sub(r"\1***", str(text))
    for v in sorted(_secrets, key=len, reverse=True):
        t = t.replace(v, "***")
    return t


def _log(msg):
    if DEBUG:
        sys.stderr.write(f"[debug] {safe(msg)}\n")


class _SafeStream:
    """包住 stderr：写出去的文字先打码。调试日志、异常堆栈、插件报错等漏掉 safe() 的地方也盖得住。"""

    def __init__(self, raw):
        self._raw = raw

    def write(self, s):
        return self._raw.write(safe(s))

    def __getattr__(self, name):
        return getattr(self._raw, name)


def guard_stderr():
    """命令行和 MCP 入口调用一次：之后所有写到 stderr 的文字都经过 safe()。"""
    if not isinstance(sys.stderr, _SafeStream):
        sys.stderr = _SafeStream(sys.stderr)


def _looks_blocked(text):
    t = (text or "")[:20000].lower()
    return any(m in t for m in _CHALLENGE)


def _retry_after(e, attempt):
    """对方要求的等待秒数（Retry-After 可以是秒数或 HTTP 日期）；没给就按 5/20/60/120 秒递增。"""
    v = ""
    try:
        v = (e.headers.get("Retry-After") or "").strip()
    except AttributeError:
        pass
    if v.isdigit():
        return int(v)
    if v:
        try:
            dt = email.utils.parsedate_to_datetime(v)
            return max(0, int((dt - datetime.now(timezone.utc)).total_seconds()) + 1)
        except (TypeError, ValueError, IndexError):
            pass
    return (5, 20, 60, 120)[min(attempt, 3)]


def request(url, data=None, headers=None, method=None, tries=4, timeout=None):
    """发请求，返回 (状态码, 响应头, 文本)。按上面的原则处理限流和拦截。"""
    hdr = dict(UA)
    hdr.update(headers or {})
    for k, v in hdr.items():   # 认证类请求头的值登记为密钥，报错时打码
        if _SECRET_HEADER.search(k):
            add_secret(v)
    for attempt in range(tries):
        _space(url)
        req = urllib.request.Request(url, data=data, headers=hdr, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout or TIMEOUT, context=CTX) as r:
                text = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
                return r.status, r.headers, text
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            if e.code == 403 or _looks_blocked(body):   # 先认拦截：503 + 人机验证页也算被拦，不重试
                raise Blocked(f"{safe(url)} 拒绝访问({e.code})，按约定不绕过")
            if e.code in (429, 502, 503, 504):
                wait = _retry_after(e, attempt)
                if wait > MAX_WAIT:   # 不把对方要求的等待缩短；太久就停下，稍后再跑
                    raise RateLimited(f"{safe(url)} 返回 {e.code}，要求等待 {wait} 秒（超过 {MAX_WAIT} 秒），请稍后再跑")
                if attempt + 1 >= tries:   # 重试用完：统一抛 RateLimited，调用方据此停下整个来源
                    raise RateLimited(f"{safe(url)} 返回 {e.code}，重试 {tries} 次仍未恢复，请稍后再跑")
                sys.stderr.write(f"[i] {urllib.parse.urlsplit(url).hostname} 返回 {e.code}，{wait} 秒后重试\n")
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.gaierror) or attempt + 1 >= tries:
                raise  # 域名不存在 / 重试用完
            _log(f"{safe(url)} 网络错误 {e.reason}，重试")
            time.sleep(2 * (attempt + 1))
        except (socket.timeout, ConnectionError) as e:
            if attempt + 1 >= tries:
                raise
            _log(f"{safe(url)} {type(e).__name__}，重试")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"请求失败: {safe(url)}")


def _url(url, params):
    if not params:
        return url
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")}, doseq=True)
    return url + ("&" if "?" in url else "?") + q


def get_text(url, params=None, headers=None, **kw):
    _, _, text = request(_url(url, params), headers=headers, **kw)
    if _looks_blocked(text):
        raise Blocked(f"{safe(url)} 返回人机验证页，按约定不绕过")
    return text


def _json(url, text):
    try:
        return json.loads(text)
    except ValueError:
        if _looks_blocked(text):
            raise Blocked(f"{safe(url)} 返回人机验证页，按约定不绕过")
        raise ValueError(f"{safe(url)} 返回的不是 JSON：{safe(text)[:120]!r}")   # 先打码再截断，免得截出半个密钥


def get_json(url, params=None, headers=None, **kw):
    u = _url(url, params)
    _, _, text = request(u, headers=dict({"Accept": "application/json"}, **(headers or {})), **kw)
    return _json(u, text)


def post_json(url, body, headers=None, **kw):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    h.update(headers or {})
    _, _, text = request(url, data=json.dumps(body).encode(), headers=h, method="POST", **kw)
    return _json(url, text)


def post_form(url, form, headers=None, **kw):
    """表单 POST（application/x-www-form-urlencoded），返回 JSON。"""
    h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    h.update(headers or {})
    _, _, text = request(url, data=urllib.parse.urlencode(form).encode(), headers=h, method="POST", **kw)
    return _json(url, text)
