"""联网：所有来源共用。

原则（与 README「使用边界」一致）：
- 如实报身份（User-Agent 写明 HiringRadar 和项目地址），不伪装浏览器指纹、不用代理池。
- 429 / 503 按 Retry-After 退避重试；重试用完抛 RateLimited，由调用方停下并报告。
- 403 或人机验证页：不重试、不绕过，直接抛 Blocked。
- 404 等确定性错误、域名不存在：立即抛出（auto-probe 靠它快速换下一个 ATS）。
- 同一主机两次请求之间至少间隔 HIRING_RADAR_DELAY 秒（默认 0.3），翻页时自动生效。
"""
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

from . import __version__

CTX = ssl.create_default_context()
if os.environ.get("HIRING_RADAR_INSECURE") == "1":  # 默认验证 TLS 证书；仅拦截式代理(证书被替换)时设此环境变量关闭
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": f"Mozilla/5.0 (compatible; HiringRadar/{__version__}; +https://github.com/simonlin1212/Hiring-Radar)"}
TIMEOUT = 30
DELAY = float(os.environ.get("HIRING_RADAR_DELAY", "0.3"))
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


def safe(url):
    """报错/日志里的网址把密钥参数打码（如 Adzuna 的 app_key），避免密钥进日志和续跑进度文件。"""
    return _SECRET.sub(r"\1***", str(url))


def _log(msg):
    if DEBUG:
        sys.stderr.write(f"[debug] {msg}\n")


def _looks_blocked(text):
    t = (text or "")[:20000].lower()
    return any(m in t for m in _CHALLENGE)


def _retry_after(e, attempt):
    try:
        v = int(e.headers.get("Retry-After", ""))
        if 0 <= v <= 300:
            return v
    except (TypeError, ValueError, AttributeError):
        pass
    return (5, 20, 60, 120)[min(attempt, 3)]


def request(url, data=None, headers=None, method=None, tries=4, timeout=None):
    """发请求，返回 (状态码, 响应头, 文本)。按上面的原则处理限流和拦截。"""
    hdr = dict(UA)
    hdr.update(headers or {})
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
            if e.code in (429, 502, 503, 504):
                if attempt + 1 >= tries:
                    if e.code == 429:
                        raise RateLimited(f"{safe(url)} 被限流(429)，重试 {tries} 次仍未恢复")
                    raise
                wait = _retry_after(e, attempt)
                sys.stderr.write(f"[i] {urllib.parse.urlsplit(url).hostname} 返回 {e.code}，{wait} 秒后重试\n")
                time.sleep(wait)
                continue
            if e.code == 403 or _looks_blocked(body):
                raise Blocked(f"{safe(url)} 拒绝访问({e.code})，按约定不绕过")
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
        raise ValueError(f"{safe(url)} 返回的不是 JSON：{text[:120]!r}")


def get_json(url, params=None, headers=None, **kw):
    u = _url(url, params)
    _, _, text = request(u, headers=dict({"Accept": "application/json"}, **(headers or {})), **kw)
    return _json(u, text)


def post_json(url, body, headers=None, **kw):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    h.update(headers or {})
    _, _, text = request(url, data=json.dumps(body).encode(), headers=h, method="POST", **kw)
    return _json(url, text)
