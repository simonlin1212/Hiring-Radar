#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线烟测：不联网，只验证编译 + 注册表加载 + 关键结构。
用法: python3 tests/smoke_test.py   （CI 可直接跑）"""
import os, sys, glob, importlib.util, py_compile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fail = []

# 1) 全部 .py 编译
for f in [os.path.join(ROOT, "hiring_radar.py")] + sorted(glob.glob(os.path.join(ROOT, "parsers", "*.py"))):
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        fail.append(f"编译失败 {os.path.relpath(f, ROOT)}: {e}")

# 2) 加载主模块 + 种子表，检查注册表
spec = importlib.util.spec_from_file_location("hiring_radar", os.path.join(ROOT, "hiring_radar.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m._load_company_seeds()

checks = [
    ("COMPANIES 含 figure", "figure" in m.COMPANIES),
    ("BOARDS 含 remoteok", "remoteok" in m.BOARDS),
    ("LOCAL_PARSERS 含内置 tencent", "tencent" in m.LOCAL_PARSERS),
    ("种子表已加载(>100 家)", len(m.LOCAL_PARSERS) > 100),
    ("FIELDS 为 15 字段", len(m.FIELDS) == 15),
]
for name, ok in checks:
    if not ok:
        fail.append(f"断言失败: {name}")

if fail:
    print("❌ SMOKE TEST FAILED:")
    for x in fail:
        print("  -", x)
    sys.exit(1)
print(f"✅ smoke test passed | 注册公司 {len(m.LOCAL_PARSERS)} 家 | 字段 {len(m.FIELDS)} 个")
