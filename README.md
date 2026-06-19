# HwTextEngine · 作业文本处理引擎

> 数算 B 课程大作业 ｜ 选题方向：**算法应用工具**（文本处理）
> 核心算法全部**从零实现**：KMP · Aho–Corasick · 编辑距离 DP · 栈 · 递归下降 · Huffman（+ 手写最小堆）

把课程公告与教材当作纯文本，跑一条端到端流水线——**从一堆通知里挖出"隐藏作业"，
在教材里按题号定位题目，把整理好的答案做结构解析与公式定界符修复**。整条链路上的
检索 / 匹配 / 解析 / 压缩算法都是手写的；第三方库只在"把 PDF 解码成字符串"这一个
I/O 边界出现。

```
公告(.txt/PDF) ──mine──▶ 隐藏作业候选(题号/截止)      [Aho-Corasick]
教材(.txt/PDF) ──locate─▶ 题面切片 / 找不到给候选       [KMP + 编辑距离]
答案(.md)      ──fix────▶ 定界符规整 + 配对校验          [栈 + 状态机]
答案(.md)      ──analyze▶ 结构大纲(AST) + 压缩比          [递归下降 + Huffman]
```

---

## 一、项目背景

北大同学每周都要在教学网 / 微信群 / Canvas 之间，从一堆通知里辨认出"哪条其实布置了
作业"，再翻教材找到对应题号，做完后把答案整理成可渲染的 Markdown。这些事都是**文本
处理**，而文本处理正是一批经典数据结构与算法的用武之地：

- 一段公告里要同时命中"作业 / 习题 / 截止 / deadline / 第 N 题 / 页码"等**一大批**关键词
  → 多模式串匹配（**Aho–Corasick 自动机**）；
- 在整本教材里定位"习题 3.2"这种**单一模式**的标记 → **KMP**；
- 题号写错或对不上时给出最接近的候选 → **编辑距离（动态规划）**；
- 校验人/AI 贴来的答案里 `()[]{}\[\]\(\)` 与 `$ $$` 是否配对 → **栈**；
- 把答案解析成块结构（标题/代码/公式/列表）→ **递归下降 + 抽象语法树**；
- 统计题面文本的可压缩性 → **Huffman 编码（贪心 + 二叉树 + 优先队列）**。

本项目把这些需求做成一个统一的命令行工具 `hwtext`。

> 说明：本项目的需求来源，是课程自动化辅助仓库 **AutoPku**——原版见 [ICUlizhi/AutoPku](https://github.com/ICUlizhi/AutoPku)，作者在其基础上扩展的版本见 [jiang-convey/docforge_autopku_extend](https://github.com/jiang-convey/docforge_autopku_extend)。本大作业**重新立项、从零编写算法内核**，与上述仓库均不共享代码，仅借用其真实使用场景。

## 二、核心算法（对应课程知识点）

| 模块 | 算法（自实现） | 课程知识点 | 时间复杂度 | 应用到的功能 |
|---|---|---|---|---|
| `matching/kmp.py` | KMP，失配函数 | 字符串匹配 | 预处理 O(m)，匹配 O(n) | `locate` 定位题号标记 |
| `matching/aho_corasick.py` | Trie + AC 自动机，BFS 建失配指针 | 字典树 / 自动机 / 队列(BFS) | 构建 O(Σ\|pᵢ\|)，扫描 O(n+z) | `mine` 一遍命中所有关键词 |
| `matching/edit_distance.py` | Levenshtein DP（滚动数组 + 回溯表） | 动态规划 | O(m·n) | `locate` 失败时给候选题号 |
| `parsing/bracket_stack.py` | 栈配对（左到右扫描） | 栈 (LIFO) | O(n) | `fix` 定界符配对校验 |
| `parsing/tokenizer.py` / `delim_fix.py` | 三态有限状态机 | 有限状态机 | O(n) | 跳过代码块 + 分隔符规整 |
| `parsing/md_parser.py` | 递归下降 → AST | 树 / 递归 / 语法分析 | O(n) | `analyze` 文档结构大纲 |
| `compress/heap.py` | 二叉最小堆（数组表示，上浮/下沉） | 堆 / 优先队列 | push/pop O(log n) | Huffman 取最小频率结点 |
| `compress/huffman.py` | Huffman 前缀码（贪心建树） | 贪心 / 二叉树 / 前缀码 | 建树 O(k log k) | `analyze` 压缩比统计 |

每个算法的思路、伪代码、复杂度推导与边界，见 [`docs/DESIGN.md`](docs/DESIGN.md)。

## 三、运行指南

环境：Python ≥ 3.8，**算法与测试零第三方依赖**。仅当输入是 PDF 时才需要装可选的解码库。

```bash
# 1) 跑测试（无需任何第三方库）
python -m unittest discover -s tests -p "test_*.py" -v
#   或： make test

# 2) 直接运行（把 src 加入路径；或先 `pip install -e .` 后用 `hwtext` 命令）
export PYTHONPATH=src        # Windows PowerShell: $env:PYTHONPATH="src"

# 从公告目录里挖作业
python -m hwtext mine examples/notices

# 在教材里定位题目（找不到的题号会给出最接近的候选）
python -m hwtext locate examples/textbook.txt --problems 3.2,9.9

# 校验并规整答案里的公式定界符（代码块内不动）
python -m hwtext fix examples/answer.md -o examples/answer.fixed.md

# 解析文档结构(AST) + 报告 Huffman 压缩比
python -m hwtext analyze examples/answer.md

# 读取 PDF 需要可选依赖：
pip install -r requirements.txt    # 或 make install；之后 locate book.pdf ...
```

所有子命令都支持 `--json` 输出，便于接入下游脚本。一键演示：`make demo`。

## 四、项目结构

```
HwTextEngine/
├─ src/hwtext/
│  ├─ matching/   kmp.py  aho_corasick.py  edit_distance.py   # 匹配 / DP
│  ├─ parsing/    tokenizer.py  bracket_stack.py  delim_fix.py  md_parser.py
│  ├─ compress/   heap.py  huffman.py
│  ├─ io/         pdf_text.py  notices.py        # 唯一调用第三方库处（仅解码）
│  ├─ apps/       locate_problem.py  mine_homework.py  fix_answer.py  analyze.py
│  ├─ cli.py      __main__.py                     # 界面层：参数解析 + 输出
│  └─ __init__.py
├─ tests/         test_*.py（47 个用例，纯 unittest）
├─ docs/          DESIGN.md（算法说明与设计）
├─ examples/      textbook.txt  notices/  answer.md
├─ README.md  LICENSE  requirements.txt  pyproject.toml  Makefile
```

**逻辑 / 界面 / IO 三层分离**：`matching` `parsing` `compress` 是纯算法（吃字符串、吐
数据结构）；`apps` 把算法串成功能；`cli` 只管参数与打印；`io` 把第三方库隔离在边界。

## 五、AI 工具声明

本项目在开发过程中使用了 AI 编程助手（**Claude / Claude Code**），用途如下，特此声明：

- **用于**：脚手架搭建、按标准教科书算法把代码落成 Python、补全 docstring 与注释、
  编写单元测试、撰写文档。
- **算法来源**：KMP、Aho–Corasick、Levenshtein、Huffman、二叉堆等均为公开的经典算法，
  按教材标准描述实现。
- **作者主导**：选题与问题建模（把"作业文本处理"映射到这组算法）、模块架构（逻辑/界面/
  IO 分层、算法零依赖的边界设计）、流水线设计与示例，由作者构思与决定。

## 六、学术诚信声明

- 本项目核心算法逻辑与整体架构由作者独立设计与实现，**未抄袭**他人代码仓库。
- 所有借鉴的算法思想均来自公开教材 / 资料，已在下方列出；AI 协助情况见第五节。
- 严禁将本仓库用于违反课程学术规范的用途。

**参考文献**

1. T. H. Cormen et al. *Introduction to Algorithms* (CLRS), 3rd ed. — KMP、动态规划、贪心、堆。
2. 邓俊辉.《数据结构（C++ 语言版）》. 清华大学出版社. — 栈、树、字符串匹配。
3. A. V. Aho, M. J. Corasick. *Efficient string matching: an aid to bibliographic search*. CACM, 1975.
4. D. A. Huffman. *A Method for the Construction of Minimum-Redundancy Codes*. 1952.

## 许可

[MIT License](LICENSE) © 2026 蒋名仪 (Jiang Mingyi)
