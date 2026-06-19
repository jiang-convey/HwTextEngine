"""为 pytest 用户把 ``src`` 加入导入路径（unittest 用户由各测试文件顶部的
路径插入处理）。无第三方依赖。"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
