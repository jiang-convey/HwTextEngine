# 习题 3.2 解答

**证明.** 因为 $\sum a_n$ 收敛，所以 $a_n \to 0$。于是存在 $N$，当 $n > N$ 时
\(0 < a_n < 1\)，从而 \(a_n^2 < a_n\)。

由比较判别法：

\[
\sum_{n > N} a_n^2 \le \sum_{n > N} a_n < \infty
\]

故 $\sum a_n^2$ 收敛。$\blacksquare$

下面是验证用的小脚本（其中反斜杠形式的定界符只是字符串字面量，不应被改动）：

```python
total = sum(a_n ** 2 for a_n in seq)   # 形如 \(x\) 与 \[y\] 的写法仅作示例
```
