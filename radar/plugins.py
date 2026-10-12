"""私有插件：放在仓库之外、不提交的来源（例如条款不允许公开分发抓取代码的大平台）。

启用：环境变量 HIRING_RADAR_PLUGINS=插件目录（或 --plugins 目录）。目录里每个不以 _ 开头的 .py 是一个来源，
需定义 NAME、DESC、FILTERS 和 pages(q, state=None)（接口同 radar/boards/__init__.py），
加载后可像内置来源一样用：--board NAME。

插件是你自己放的本地代码，以你的权限运行；只加载你指定目录里的文件，从不从当前目录或网络加载。
使用插件访问的网站，其条款由你自行遵守。
"""
import glob
import importlib.util
import os
import sys

from . import boards

loaded = []


def load(path):
    path = os.path.expanduser(path or "")
    if not path:
        return []
    if not os.path.isdir(path):
        sys.stderr.write(f"[!] 插件目录不存在：{path}\n")
        return []
    for f in sorted(glob.glob(os.path.join(path, "*.py"))):
        base = os.path.basename(f)
        if base.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"hiring_radar_plugin_{base[:-3]}", f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for attr in ("NAME", "pages"):
                if not hasattr(mod, attr):
                    raise ValueError(f"缺少 {attr}")
            mod.DESC = getattr(mod, "DESC", "") + "（私有插件）"
            mod.FILTERS = set(getattr(mod, "FILTERS", set()))
            boards.register(mod)
            loaded.append(mod.NAME)
        except Exception as e:
            sys.stderr.write(f"[!] 插件 {base} 加载失败：{type(e).__name__}: {e}\n")
    return loaded
