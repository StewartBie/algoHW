# KMP 字符串匹配算法

## 算法简介

KMP 算法是一种高效的字符串匹配算法，用于在文本串中查找模式串的所有出现位置。该算法通过预处理模式串构建部分匹配表（next 数组），避免了朴素算法中的大量重复比较，将时间复杂度从 O(n×m) 优化到 O(n+m)。

## 算法设计思路

### 核心思想

KMP 算法的核心在于利用已经匹配过的信息，避免重复比较：

1. **前缀表（next 数组）**：记录模式串每个位置之前的子串中，最长相等前后缀的长度
2. **失配跳转**：当匹配失败时，根据 next 数组快速确定下一次匹配的起始位置
3. **不回溯文本指针**：文本串的指针始终向前移动，不会回退

### 算法流程

#### 1. 构建 next 数组（`build_next` 函数）

```
目标：计算 pattern[0:i] 的最长相等前后缀长度

算法步骤：
- 初始化：next[0] = 0
- 遍历模式串（i = 1 到 m-1）：
  - 如果 pattern[i] == pattern[j]：匹配成功，j++
  - 如果不匹配：根据 next[j-1] 回退 j，直到匹配或 j=0
  - 记录 next[i] = j

时间复杂度：O(m)
```

**示例**：
```
模式串：A B A B A
next:   0 0 1 2 3

解释：
- next[0] = 0（约定）
- next[1] = 0（"AB" 无相等前后缀）
- next[2] = 1（"ABA" 的前缀"A"等于后缀"A"）
- next[3] = 2（"ABAB" 的前缀"AB"等于后缀"AB"）
- next[4] = 3（"ABABA" 的前缀"ABA"等于后缀"ABA"）
```

#### 2. 字符串匹配（`kmp_search_all` 函数）

```
目标：在文本串中查找所有模式串的出现位置

算法步骤：
- 初始化：j = 0（模式串指针）
- 遍历文本串（i = 0 到 n-1）：
  - 如果 text[i] != pattern[j]：根据 next[j-1] 回退 j
  - 如果 text[i] == pattern[j]：j++
  - 如果 j == m（完全匹配）：
    - 记录匹配位置：i - m + 1
    - 继续查找下一个匹配：j = next[j-1]

时间复杂度：O(n)
总时间复杂度：O(n + m)
```

### 算法优势

- **时间高效**：O(n+m) 线性时间复杂度，即使在最坏情况下也保持线性
- **不回溯**：文本指针不回退，适合处理流式数据
- **空间优化**：只需要 O(m) 的额外空间存储 next 数组

## 环境要求

### 基础运行环境

- **Python**：3.13 , 未在其他环境测试,后文提到的 python 均指 python3
- **操作系统**：Linux 6.12.60-1-lts

### 测试脚本依赖

如需运行复杂度分析脚本，需要安装以下 Python 库：

```bash
pip install matplotlib numpy
```

针对特别的包管理器 pacman：

```bash
pacman -S python-matplotlib python-numpy
```

## 文件说明

```
kmp/
├── kmp.py                        # KMP 算法核心实现
├── run_correctness_tests.sh      # 正确性测试脚本
├── test_complexity.py            # 时间复杂度分析脚本
├── README.md                     # 本文档
└── test_cases/                   # 测试用例目录(ignored)
```

## 代码运行方法

### 1. 基础使用（交互式）

直接运行 `kmp.py` 进行交互式字符串匹配：

```bash
python kmp.py
```

**交互示例**：
```
请输入text: ABABCABABA
请输入pattern: ABA

匹配总次数： 3
每次匹配起始位置： [0, 5, 7]
```

### 2. 在代码中调用

```python
from kmp import kmp_search_all, build_next

# 示例 1：查找所有匹配位置
text = "ABABCABABA"
pattern = "ABA"
positions = kmp_search_all(text, pattern)
print(f"匹配位置：{positions}")  # 输出：[0, 5, 7]

# 示例 2：构建 next 数组
pattern = "ABABC"
next_array = build_next(pattern)
print(f"next 数组：{next_array}")  # 输出：[0, 0, 1, 2, 0]
```

### 3. 正确性测试

运行大规模正确性测试脚本，验证算法的正确性：

```bash
cd kmp
chmod +x run_correctness_tests.sh  # 首次运行需要添加执行权限
./run_correctness_tests.sh
```

**测试内容**：
- 10 个基础测试用例（基本匹配、无匹配、边界情况等）
- 40 个随机生成测试用例（不同规模：100-10000 字符）
- 与 Python 内置 `str.find()` 方法进行结果对比验证

**输出示例**：
```
===================================
KMP 算法大规模正确性测试
===================================

运行基础测试用例...

✓ PASS: 基本匹配
✓ PASS: 无匹配
✓ PASS: 完全匹配
...

随机测试统计: 40/40 通过

===================================
测试结果汇总
===================================
基础测试: 10/10 通过
随机测试: 全部通过

所有测试通过！
```

### 4. 时间复杂度分析

运行复杂度分析脚本，验证算法的 O(n+m) 时间复杂度：

```bash
python test_complexity.py
```

**测试内容**：
1. **文本长度缩放分析**：固定模式长度，测试不同文本长度（1K-500K），验证 O(n)
2. **模式长度缩放分析**：固定文本长度，测试不同模式长度（10-10K），验证 O(m)
3. **组合缩放分析**：同时增加文本和模式长度，验证 O(n+m)
4. **最坏情况分析**：高度重复文本，验证最坏情况仍为线性
5. **build_next 复杂度**：单独测试前缀表构建时间

**输出内容**：
- 详细的数值数据表格（时间、单位时间复杂度等）
- 线性拟合公式和相关系数
- 5 张可视化图表（PNG 格式，300 DPI）

**生成的图表文件**：
```
kmp_text_length_scaling.png       # 文本长度缩放分析
kmp_pattern_length_scaling.png    # 模式长度缩放分析
kmp_combined_scaling.png          # 组合缩放分析 (n+m)
kmp_worst_case.png                # 最坏情况分析
kmp_build_next_complexity.png     # build_next 复杂度分析
```

## 输入输出说明

### 函数接口

#### `build_next(pattern)`

**功能**：构建 KMP 算法的 next 数组（前缀表）

**输入**：
- `pattern` (str)：模式串，要查找的字符串

**输出**：
- `nxt` (list[int])：next 数组，长度为 len(pattern)
  - `nxt[i]` 表示 `pattern[0:i]` 的最长相等前后缀长度

**示例**：
```python
>>> build_next("ABABC")
[0, 0, 1, 2, 0]

>>> build_next("AAAA")
[0, 1, 2, 3]
```

#### `kmp_search_all(text, pattern)`

**功能**：在文本串中查找所有模式串的出现位置

**输入**：
- `text` (str)：文本串，被搜索的字符串
- `pattern` (str)：模式串，要查找的字符串

**输出**：
- `positions` (list[int])：所有匹配的起始位置列表（从 0 开始计数）
  - 空列表表示未找到匹配
  - 位置按升序排列

**特殊情况**：
- 如果 `pattern` 为空字符串，返回 `[0]`
- 如果 `pattern` 长度大于 `text`，返回空列表 `[]`

**示例**：
```python
>>> kmp_search_all("ABABCABABA", "ABA")
[0, 5, 7]

>>> kmp_search_all("AAAA", "AA")
[0, 1, 2]  # 允许重叠匹配

>>> kmp_search_all("ABCDEF", "XYZ")
[]  # 未找到

>>> kmp_search_all("HELLO", "")
[0]  # 空模式串
```

### 交互式程序

运行 `python kmp.py` 时：

**输入格式**：
```
请输入text: <文本串>
请输入pattern: <模式串>
```

**输出格式**：
```
匹配总次数： <匹配数量>
每次匹配起始位置： [位置1, 位置2, ...]
```

**完整示例**：
```
请输入text: She sells seashells by the seashore
请输入pattern: sea

匹配总次数： 2
每次匹配起始位置： [10, 27]
```

## 算法复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|-----------|-----------|------|
| 构建 next 数组 | O(m) | O(m) | m 为模式串长度 |
| 字符串匹配 | O(n) | O(1) | n 为文本串长度（不含输出） |
| 总体复杂度 | **O(n+m)** | O(m) | 线性时间复杂度 |

**实验验证结果**（来自 `test_complexity.py`）：
- 文本长度缩放：线性相关系数 R > 0.999
- 模式长度缩放：线性相关系数 R > 0.999
- 最坏情况：仍保持线性复杂度

## 应用场景

1. **文本搜索**：在大型文档中快速查找关键词
2. **DNA 序列匹配**：在基因序列中查找特定模式
3. **数据流处理**：实时监控流数据中的特定模式
4. **编译器词法分析**：识别源代码中的关键字和标识符
5. **入侵检测系统**：在网络流量中匹配攻击特征

## 常见问题

### Q1: KMP 算法与朴素算法的区别？

**朴素算法**：
- 时间复杂度：O(n×m)
- 失配时文本指针回退，重复比较

**KMP 算法**：
- 时间复杂度：O(n+m)
- 文本指针不回退，利用已匹配信息

### Q2: 为什么 next 数组能避免重复比较？

next 数组记录了模式串的自相似性。当失配时，我们知道之前已经匹配的部分中，哪些前缀等于后缀，可以直接跳过这些已知相等的部分。

### Q3: KMP 算法适用于所有字符串吗？

是的，KMP 算法适用于任何字符集的字符串，包括：
- ASCII 字符
- Unicode 字符（中文、日文等）
- 二进制数据

### Q4: 如何处理大小写敏感/不敏感匹配？

```python
# 大小写不敏感匹配
text_lower = text.lower()
pattern_lower = pattern.lower()
positions = kmp_search_all(text_lower, pattern_lower)
```

## 参考资料

- Knuth, D.E., Morris, J.H., and Pratt, V.R. (1977). "Fast Pattern Matching in Strings"
- 算法导论（Introduction to Algorithms），第 32 章：字符串匹配



---

**最后更新日期**：2025-12-08
