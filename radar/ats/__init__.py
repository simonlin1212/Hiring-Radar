"""按公司查：每个招聘系统(ATS)一个模块，统一接口 fetch(slug, meta=None) -> (items, source)。

新增一个 ATS：在本目录加 xxx.py 实现 fetch()，再在下面 REGISTRY 加一行。
slug 一律先过 check_slug（单段字母数字，防把请求改写到别的域名，即 SSRF）。
"""
import re

from . import (ashby, bamboohr, breezy, greenhouse, lever, personio, recruitee, smartrecruiters, workable, workday)

# name → (模块, 说明)。顺序即 --list 的展示顺序。
REGISTRY = {
    "greenhouse": (greenhouse, "Greenhouse"),
    "ashby": (ashby, "Ashby"),
    "lever": (lever, "Lever"),
    "workday": (workday, "Workday（需 host+site，名录里有）"),
    "smartrecruiters": (smartrecruiters, "SmartRecruiters"),
    "recruitee": (recruitee, "Recruitee"),
    "breezy": (breezy, "Breezy HR"),
    "bamboohr": (bamboohr, "BambooHR"),
    "personio": (personio, "Personio"),
    "workable": (workable, "Workable"),
}

# 按公司名猜 slug 时依次试的 ATS（v1 的 8 个，顺序不变）。名录查得到时不走这条。
PROBE_ORDER = ["greenhouse", "ashby", "lever", "smartrecruiters", "recruitee", "breezy", "bamboohr", "personio"]

_SLUG = re.compile(r"[A-Za-z0-9_-]{1,100}")


def check_slug(kind, slug):
    slug = (slug or "").strip()
    if not _SLUG.fullmatch(slug):
        raise ValueError(f"{kind} slug 非法：只允许字母/数字/连字符/下划线（防 SSRF），收到 {slug!r}")
    return slug


def fetch(kind, slug, meta=None):
    if kind not in REGISTRY:
        raise ValueError(f"未知 ATS：{kind}（可选：{', '.join(REGISTRY)}）")
    slug = check_slug(kind, slug)
    items, src = REGISTRY[kind][0].fetch(slug, meta)
    for it in items:
        it["source"] = it.get("source") or src
    return items, src
