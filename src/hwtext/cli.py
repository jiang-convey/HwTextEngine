"""HwTextEngine 命令行界面（**界面层**：只负责读输入、调用 :mod:`hwtext.apps`、
格式化输出；不含任何算法逻辑）。

子命令
    locate    在教材(.pdf/.txt)里按题号定位题目          (KMP + 编辑距离)
    mine      从公告(.txt/.md 或目录)里挖作业            (Aho-Corasick)
    fix       校验并修复答案里的定界符                    (栈 + 状态机)
    analyze   解析文档结构(AST)并报告 Huffman 压缩比      (递归下降 + Huffman)

示例
    python -m hwtext locate book.pdf --problems 3.2,3.5 [--scheme 习题] [--json]
    python -m hwtext mine notices/ [--json]
    python -m hwtext fix answer.md [-o answer.fixed.md]
    python -m hwtext analyze answer.md [--json]
"""
import argparse
import json
import sys

from . import apps
from .io import iter_notices, load_document


def _jsonable(o):
    if hasattr(o, "_asdict"):            # NamedTuple（BracketReport 等）
        return o._asdict()
    return str(o)


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=_jsonable))


def cmd_locate(a: argparse.Namespace) -> None:
    text = load_document(a.source)
    pids = [p.strip() for p in a.problems.split(",") if p.strip()]
    result = apps.locate(text, pids, scheme=a.scheme)
    if a.json:
        _print_json(result)
        return
    print("教材：%s ｜ 方案：%s" % (a.source, result["scheme"]))
    for p in result["problems"]:
        if p["found"]:
            print("\n【%s】(字符 %d–%d，标记 %r)"
                  % (p["number"], p["char_start"], p["char_end"], p["marker"]))
            body = p["content"]
            print(body[:500] + ("…" if len(body) > 500 else ""))
        else:
            cand = "，".join(p["candidates"]) or "(无)"
            print("\n【%s】未找到。候选题号：%s" % (p["number"], cand))


def cmd_mine(a: argparse.Namespace) -> None:
    cands = apps.mine_all(iter_notices(a.source))
    if a.json:
        _print_json(cands)
        return
    if not cands:
        print("未发现疑似作业。")
        return
    print("发现 %d 条疑似作业：" % len(cands))
    for c in cands:
        kw = "，".join("%s×%d" % (k, v) for k, v in c["keywords"].items())
        print("\n- 来源：%s" % c["source"])
        print("  关键词：%s" % kw)
        if c["problem_refs"]:
            print("  题号线索：%s" % "，".join(c["problem_refs"]))
        if c["due"]:
            print("  截止线索：%s" % c["due"])
        print("  摘要：%s" % c["snippet"])


def cmd_fix(a: argparse.Namespace) -> None:
    with open(a.source, encoding="utf-8") as f:
        src = f.read()
    r = apps.fix(src)
    out = a.output or (a.source.rsplit(".", 1)[0] + ".fixed.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(r["fixed"])
    print("修复前：%s" % r["before"].summary())
    print("替换 %d 处 \\[\\] / \\(\\) 分隔符。" % r["replacements"])
    print("修复后：%s" % r["after"].summary())
    print("已写出：%s" % out)


def cmd_analyze(a: argparse.Namespace) -> None:
    with open(a.source, encoding="utf-8") as f:
        src = f.read()
    r = apps.analyze(src)
    if a.json:
        _print_json({"outline": r["outline"], "compress": r["compress"]})
        return
    print("== 文档结构 (AST) ==")
    print(r["outline"] or "(空文档)")
    c = r["compress"]
    print("\n== Huffman 压缩 ==")
    print("字符数 %d ｜ 不同符号 %d ｜ 平均码长 %.2f bit ｜ 压缩比 %.2f"
          % (c["chars"], c["symbols"], c["avg_code_len"], c["ratio"]))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="hwtext",
                                 description="作业文本处理引擎（算法内核全部自实现）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("locate", help="按题号在教材里定位题目")
    p.add_argument("source", help="教材文件（.pdf 或 .txt）")
    p.add_argument("--problems", required=True, help="题号，逗号分隔，如 3.2,3.5")
    p.add_argument("--scheme", default="习题", help="题号前缀方案（习题/练习/Exercise…）")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_locate)

    p = sub.add_parser("mine", help="从公告里挖作业")
    p.add_argument("source", help="公告文件或目录")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_mine)

    p = sub.add_parser("fix", help="校验并修复答案定界符")
    p.add_argument("source", help="答案 Markdown 文件")
    p.add_argument("-o", "--output", help="输出文件（默认 <name>.fixed.md）")
    p.set_defaults(func=cmd_fix)

    p = sub.add_parser("analyze", help="解析结构 + 压缩统计")
    p.add_argument("source", help="Markdown 文件")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_analyze)
    return ap


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    try:                       # Windows 下重定向也保证 UTF-8 输出
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
