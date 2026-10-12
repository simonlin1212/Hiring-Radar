"""跨公司来源（聚合板、开放数据、freehire、Workable 搜索）。

每个来源一个模块，统一接口：
    NAME / DESC
    FILTERS   该来源能在服务端过滤的条件子集：{"keyword", "country", "recent_days"}
    pages(q, state=None)  生成器，每拉一页 yield (items, state)；state 可 JSON 序列化，
                          传回 pages(q, state) 能从断点继续（sweep --resume 用）。
没有服务端过滤的条件，由调用方在本地补过滤。私有插件(plugins.py)也注册到这里。
"""
class Query:
    """一次查询的条件。keywords/countries 为列表；recent_days=0 表示不限；max_items=0 表示不限。"""

    def __init__(self, keywords=(), countries=(), recent_days=0, max_items=0):
        self.keywords = [k.strip() for k in keywords if k and k.strip()]
        self.countries = [c.strip().upper() for c in countries if c and c.strip()]
        self.recent_days = int(recent_days or 0)
        self.max_items = int(max_items or 0)

    def as_dict(self):
        return {"keywords": self.keywords, "countries": self.countries,
                "recent_days": self.recent_days, "max_items": self.max_items}


def register(mod):
    """插件或扩展注册一个来源。重名时不覆盖内置来源。"""
    if mod.NAME in BOARDS:
        raise ValueError(f"来源名 {mod.NAME} 已被占用")
    BOARDS[mod.NAME] = mod


def resolve(name):
    key = (name or "").lower().strip()
    key = ALIASES.get(key, key)
    if key not in BOARDS:
        raise ValueError(f"未知来源 '{name}'。可选：{', '.join(sorted(BOARDS))}、all")
    return BOARDS[key]


def single_page(fn):
    """把「一次返回全部」的老式 fetch() 包成 pages() 接口。"""
    def pages(q, state=None):
        items, _ = fn()
        yield items, None
    return pages


# 各来源模块会 from . import single_page，所以放在辅助函数定义之后再导入
from . import (adzuna, arbeitsagentur, freehire, jobtech, mycareersfuture, reed, remoteok, remotive,  # noqa: E402
               usajobs, weworkremotely, workable, workingnomads)

BOARDS = {m.NAME: m for m in (remoteok, remotive, weworkremotely, workingnomads, freehire, workable,
                              jobtech, mycareersfuture, arbeitsagentur, reed, adzuna, usajobs)}
ALIASES = {"wwr": "weworkremotely", "nomads": "workingnomads", "workable-search": "workable",
           "ba": "arbeitsagentur", "mcf": "mycareersfuture", "platsbanken": "jobtech"}
# 需要用户自己申请密钥的来源（密钥放环境变量）；维护者没有 key，未经实网测试
NEEDS_KEY = {"reed": "REED_API_KEY", "adzuna": "ADZUNA_APP_ID + ADZUNA_APP_KEY", "usajobs": "USAJOBS_API_KEY + USAJOBS_EMAIL"}
# --board all 的含义保持 v1：4 个远程板（跨公司大来源要显式点名，避免一次拉几十万条）
REMOTE = ["remoteok", "remotive", "weworkremotely", "workingnomads"]
