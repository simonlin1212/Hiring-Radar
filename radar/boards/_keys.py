"""需要自己申请密钥的官方接口：密钥只从环境变量读，不写进代码、命令行参数或输出。"""
import os


def need(source, signup, *names):
    vals = [os.environ.get(n, "").strip() for n in names]
    if not all(vals):
        raise ValueError(f"{source} 需要你自己的免费密钥：到 {signup} 注册后设置环境变量 {' / '.join(names)}")
    return vals
