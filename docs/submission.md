<p class="subtitle">数算 B 课程大作业 ｜ 选题方向：算法应用工具（文本处理）</p>
<p class="author">作者：蒋名仪（Jiang Mingyi）　学号：2500010771　北京大学　2026 年 6 月</p>

## 提交信息

| 项目 | 内容 |
|---|---|
| 项目英文名 | **HwTextEngine**（作业文本处理引擎） |
| 选题方向 | 算法应用工具（文本处理） |
| 代码仓库 | `https://github.com/jiang-convey/HwTextEngine` |
| 运行环境 | Python ≥ 3.8；**算法与测试零第三方依赖**，仅 PDF 输入需可选 `pymupdf` / `pdfplumber` |
| 单元测试 | 47 个用例全部通过（标准库 `unittest`，无需第三方库） |
| 许可证 | MIT |

> 一句话：把课程公告与教材当作纯文本，跑一条端到端流水线——**从一堆通知里挖出"隐藏作业"、
> 在教材里按题号定位题目、把整理好的答案做结构解析与公式定界符修复**。整条链路上的检索 /
> 匹配 / 解析 / 压缩算法**全部从零手写**；第三方库只在"把 PDF 解码成字符串"这一个 I/O 边界出现。

```text
公告(.txt/PDF) ──mine──▶ 隐藏作业候选(题号/截止)      [Aho-Corasick]
教材(.txt/PDF) ──locate─▶ 题面切片 / 找不到给候选       [KMP + 编辑距离]
答案(.md)      ──fix────▶ 定界符规整 + 配对校验          [栈 + 状态机]
答案(.md)      ──analyze▶ 结构大纲(AST) + 压缩比          [递归下降 + Huffman]
```

## 一、项目背景与选题

北大同学每周都要在教学网 / 微信群 / Canvas 之间，从一堆通知里辨认出"哪条其实布置了作业"，
再翻教材找到对应题号，做完后把答案整理成可渲染的 Markdown。这些事都是**文本处理**，而文本
处理正是一批经典数据结构与算法的用武之地：

- 一段公告里要同时命中"作业 / 习题 / 截止 / deadline / 第 N 题 / 页码"等**一大批**关键词
  → 多模式串匹配（**Aho–Corasick 自动机**）；
- 在整本教材里定位"习题 3.2"这种**单一模式**的标记 → **KMP**；
- 题号写错或对不上时给出最接近的候选 → **编辑距离（动态规划）**；
- 校验人 / AI 贴来的答案里 `()[]{}` 与 `\[\] \(\)`、`$ $$` 是否配对 → **栈**；
- 把答案解析成块结构（标题 / 代码 / 公式 / 列表）→ **递归下降 + 抽象语法树**；
- 统计题面文本的可压缩性 → **Huffman 编码（贪心 + 二叉树 + 优先队列）**。

本项目把这些需求做成一个统一的命令行工具 `hwtext`，**用自己实现的算法**支撑每一步，而不是
调用现成库函数——直接对应评分标准里"知识点应用 30 分 + 反对大量依赖外部库"的要求。

> 需求来源说明：本项目的场景来自课程自动化辅助仓库 **AutoPku**——原版见 [ICUlizhi/AutoPku](https://github.com/ICUlizhi/AutoPku)，作者在其基础上扩展的版本见 [jiang-convey/docforge_autopku_extend](https://github.com/jiang-convey/docforge_autopku_extend)。本大作业**重新立项、从零编写算法内核**，与上述仓库均不共享任何代码，仅借用其真实使用场景。

## 二、核心算法（对应课程知识点）

| 模块 | 算法（自实现） | 课程知识点 | 时间复杂度 | 应用到的功能 |
|---|---|---|---|---|
| `matching/kmp.py` | KMP，失配函数 | 字符串匹配 | 预处理 O(m)，匹配 O(n) | `locate` 定位题号标记 |
| `matching/aho_corasick.py` | Trie + AC 自动机，BFS 建失配指针 | 字典树 / 自动机 / 队列(BFS) | 构建 O(Σ\|pᵢ\|)，扫描 O(n+z) | `mine` 一遍命中所有关键词 |
| `matching/edit_distance.py` | Levenshtein DP（滚动数组 + 回溯表） | 动态规划 | O(m·n) | `locate` 失败时给候选题号 |
| `parsing/bracket_stack.py` | 栈配对（左到右扫描） | 栈 (LIFO) | O(n) | `fix` 定界符配对校验 |
| `parsing/tokenizer.py`·`delim_fix.py` | 三态有限状态机 | 有限状态机 | O(n) | 跳过代码块 + 分隔符规整 |
| `parsing/md_parser.py` | 递归下降 → AST | 树 / 递归 / 语法分析 | O(n) | `analyze` 文档结构大纲 |
| `compress/heap.py` | 二叉最小堆（数组表示，上浮 / 下沉） | 堆 / 优先队列 | push/pop O(log n) | Huffman 取最小频率结点 |
| `compress/huffman.py` | Huffman 前缀码（贪心建树） | 贪心 / 二叉树 / 前缀码 | 建树 O(k log k) | `analyze` 压缩比统计 |

> **关于"底层实现"**：上述算法均不调用任何第三方库；连 `heapq`、`re` 也未使用（`heapq` 用
> 手写 `MinHeap` 取代，行 / 标记识别用手写谓词取代正则）。第三方库 `pymupdf` / `pdfplumber`
> **只**出现在 `src/hwtext/io/`，且只负责"把 PDF 解码成字符串"。每个算法的思路、复杂度推导与
> 边界，见仓库内 `docs/DESIGN.md`。

## 三、运行指南

环境：Python ≥ 3.8，**算法与测试零第三方依赖**。仅当输入是 PDF 时才需装可选解码库。

```bash
# 1) 跑测试（无需任何第三方库）
python -m unittest discover -s tests -p "test_*.py" -v        # 或 make test

# 2) 直接运行（把 src 加入路径；或先 pip install -e . 后用 hwtext 命令）
export PYTHONPATH=src          # Windows PowerShell: $env:PYTHONPATH="src"

python -m hwtext mine    examples/notices                      # 从公告目录挖作业
python -m hwtext locate  examples/textbook.txt --problems 3.2,9.9   # 按题号定位
python -m hwtext fix     examples/answer.md -o examples/answer.fixed.md  # 修复定界符
python -m hwtext analyze examples/answer.md                    # 结构(AST)+压缩比

# 读取 PDF 需可选依赖：pip install -r requirements.txt（或 make install）
```

所有子命令均支持 `--json` 输出，便于接入下游脚本。一键演示：`make demo`。

## 四、运行结果展示

以下为在 `examples/` 示例数据上的真实运行输出。

**单元测试**——47 个用例全部通过：

```text
$ python -m unittest discover -s tests -p "test_*.py"
----------------------------------------------------------------------
Ran 47 tests in 0.003s

OK
```

**mine**——从一目录公告里挖出"隐藏作业"（自动跳过"本通知不涉及作业"类干扰）：

```text
$ python -m hwtext mine examples/notices
发现 1 条疑似作业：

- 来源：week6_shusuan.txt
  关键词：第×2，课后×1，作业×1，习题×2，截止×1，提交×1
  题号线索：习题3.2，习题3.5，第7题
  截止线索：截止时间：本周五 23:59 前提交到 Canvas，逾期不候。  如有疑问请在
  摘要：同学好：本周我们讲完了平衡二叉树（AVL）与并查集。  课后作业：请完成教材 习题3.2、习题3.5，以及补充的 第 7 题 编程题。 截止时间：本周五 23:59 前提交到 Canvas，逾期不候。
```

**locate**——在教材里按题号定位题面；找不到的题号给出最接近的候选（编辑距离）：

```text
$ python -m hwtext locate examples/textbook.txt --problems 3.2,9.9
教材：examples/textbook.txt ｜ 方案：习题

【3.2】(字符 43–136，标记 '习题3.2')
习题3.2 设 $a_n > 0$，证明：若 $\sum a_n$ 收敛，则 $\sum a_n^2$ 也收敛。
提示：利用比较判别法，注意当 $n$ 充分大时 $a_n < 1$。

【9.9】未找到。候选题号：3.1，3.2，3.3
```

**fix**——校验并规整答案里的公式定界符，**代码块内不动**：

```text
$ python -m hwtext fix examples/answer.md -o examples/answer.fixed.md
修复前：OK：所有定界符配对正确。
替换 6 处 \[\] / \(\) 分隔符。
修复后：OK：所有定界符配对正确。
已写出：examples/answer.fixed.md
```

**analyze**——递归下降解析出文档结构(AST)，并报告 Huffman 压缩比：

```text
$ python -m hwtext analyze examples/answer.md
== 文档结构 (AST) ==
- H1: 习题 3.2 解答
- paragraph: **证明.** 因为 $\sum a_n$ 收敛，所以 $a_n \to 0$。…
- paragraph: 由比较判别法：
- paragraph: \[ \sum_{n > N} a_n^2 \le \sum_{n > N} a…
- paragraph: 故 $\sum a_n^2$ 收敛。$\blacksquare$
- paragraph: 下面是验证用的小脚本（其中反斜杠形式的定界符只是字符串字面量，不应被改动）：
- code[1 行]

== Huffman 压缩 ==
字符数 330 ｜ 不同符号 110 ｜ 平均码长 5.79 bit ｜ 压缩比 0.72
```

## 五、项目结构（逻辑 / 界面 / IO 三层分离）

```text
HwTextEngine/
├─ src/hwtext/
│  ├─ matching/   kmp.py  aho_corasick.py  edit_distance.py     # 匹配 / DP
│  ├─ parsing/    tokenizer.py  bracket_stack.py  delim_fix.py  md_parser.py
│  ├─ compress/   heap.py  huffman.py
│  ├─ io/         pdf_text.py  notices.py          # 唯一调用第三方库处（仅解码）
│  ├─ apps/       locate_problem.py  mine_homework.py  fix_answer.py  analyze.py
│  ├─ cli.py      __main__.py                       # 界面层：参数解析 + 输出
│  └─ __init__.py
├─ tests/         test_*.py（47 个用例，纯 unittest）
├─ docs/          DESIGN.md（算法说明与设计）  submission.md（本文档）
├─ examples/      textbook.txt  notices/  answer.md
├─ README.md  LICENSE  requirements.txt  pyproject.toml  Makefile
```

`matching` / `parsing` / `compress` 是纯算法（吃字符串、吐数据结构）；`apps` 把算法串成功能；
`cli` 只管参数与打印；`io` 把第三方库隔离在边界。算法层可单独测试、与界面 / IO 完全解耦。

## 六、AI 工具声明

本项目在开发过程中使用了 AI 编程助手（**Claude / Claude Code**），用途如下，特此声明：

- **用于**：脚手架搭建、按标准教科书算法把代码落成 Python、补全 docstring 与注释、编写单元
  测试、撰写文档。
- **算法来源**：KMP、Aho–Corasick、Levenshtein、Huffman、二叉堆等均为公开经典算法，按教材
  标准描述实现。
- **作者主导**：选题与问题建模（把"作业文本处理"映射到这组算法）、模块架构（逻辑 / 界面 / IO
  分层、算法零依赖的边界设计）、流水线设计与示例，由作者构思与决定。

## 七、学术诚信声明

- 本项目核心算法逻辑与整体架构由作者独立设计与实现，**未抄袭**他人代码仓库。
- 所有借鉴的算法思想均来自公开教材 / 资料，已在下方列出；AI 协助情况见第六节。
- 严禁将本仓库用于违反课程学术规范的用途。

**参考文献**

1. T. H. Cormen et al. *Introduction to Algorithms* (CLRS), 3rd ed. — KMP、动态规划、贪心、堆。
2. 邓俊辉. 《数据结构（C++ 语言版）》. 清华大学出版社. — 栈、树、字符串匹配。
3. A. V. Aho, M. J. Corasick. *Efficient string matching: an aid to bibliographic search*. CACM, 1975.
4. D. A. Huffman. *A Method for the Construction of Minimum-Redundancy Codes*. 1952.

---

<p class="author">HwTextEngine · MIT License · © 2026 蒋名仪 (Jiang Mingyi)</p>
