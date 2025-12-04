# MCMF 实现说明（`mcmf.c`）

本文档简要说明仓库中 `Mcmf/mcmf.c` 的输入格式、主要数据结构、各函数功能与整体代码设计思路。

---

## 一、概要

该程序实现了最小费用最大流（Min-Cost Max-Flow）算法，当前版本使用基于队列的 SPFA（BFS 风格）在残量图(residual graph)中每轮寻找最小费用路径并增广流量。程序以命令行标准输入读取图数据并输出最大流与对应最小费用。

使用 `gcc` 编译 `mcmf.c`， `gcc -std=c11 -O2 Mcmf/mcmf.c -o Mcmf/mcmf`

---

## 二、输入数据格式

标准输入格式（stdin）：

第一行：`n m`  — 顶点数 n、边数 m（节点编号假定为 0-based）

接下来 m 行，每行一条边：`u v cap cost`
- `u`、`v`：起点和终点（整型，0-based）
- `cap`：整型，边的容量
- `cost`：长整型，单位流量费用

最后一行：`s t` — 源点与汇点（0-based）

Example：

```
4 4
0 1 3 1
1 3 2 2
0 2 2 2
2 3 2 1
0 3
```

输出：两个整数 `flow cost`，分别表示最大流和对应的最小总费用，例如 `4 12`。

---

## 三、主要数据结构（全局）

- `int N`：顶点数。
- 邻接表（并行数组实现）：
  - `int *head`：`head[u]` 指向以 `u` 为起点的第一条边的索引；`-1` 表示无出边。
  - `int *to_`：`to_[e]` 为边 `e` 的终点。
  - `int *next_`：`next_[e]` 为与 `e` 同起点的下一条边的索引（链表指针）。
  - `int *cap_`：`cap_[e]` 为边 `e` 的剩余容量。
  - `long long *cost_`：`cost_[e]` 为边 `e` 的单位费用；反向边存 `-cost`。
  - `int edge_cnt`：当前边数组中已使用的条目数量。（每插入一条原始边实际插入两条数组项：正向与反向。）

备注：程序在启动时根据输入的 `m` 调用 `ensure_edge_alloc(m)` 为并行数组分配 `2*m+5` 的空间，未实现动态扩容。

---

## 四、主要函数说明

- `void ensure_edge_alloc(int m2)`
  - 作用：为边的并行数组一次性分配空间（大小为 `2*m2 + 5`）。
  - 注意：仅在第一次调用时分配，不会动态 `realloc`，因此应确保传入的 `m2` 足够。

- `void add_edge(int u, int v, int c, ll w)`
  - 作用：向图中添加有向边 `u->v`（容量 `c`，单位费用 `w`），同时添加反向边 `v->u`（容量 `0`，费用 `-w`）。
  - 实现细节：使用并行数组 `to_`/`cap_`/`cost_`/`next_`，并通过 `head[u]` 链式连接。

- `void heap_push(ll d, int v)` / `Pair heap_pop()`
  - 作用：二叉堆实现的最小优先队列，原先用于 Dijkstra 的版本（现在代码主路径不再用 Dijkstra，但堆实现保留）。
  - 特性：不支持 decrease-key，采用重复插入并在弹出时通过比对 `dist[v]` 跳过过时条目。

- `void min_cost_max_flow(int s, int t, long long *out_flow, long long *out_cost)`
  - 作用：核心函数，计算从 `s` 到 `t` 的最大流及对应最小费用。当前实现采用 SPFA（基于队列）每轮寻找最小费用增广路径，并沿路径增广尽可能多的流量。
  - 主要局部数组：
    - `dist[]`：SPFA 维护的最小费用距离（从 `s` 到各点的费用）。
    - `prevv[]` / `preve[]`：用于记录最短路树，`prevv[v]` 为 `v` 的前驱顶点，`preve[v]` 为到达 `v` 的边索引。
    - `inqueue[]`：标记顶点是否在队列中，避免重复入队。
  - 算法流程（高层）：
    1. 初始化 `dist` 为 +INF，`dist[s]=0`，将 `s` 入队。
    2. 用队列执行松弛（SPFA）：对于队列中顶点 `v`，遍历其出边 `e`，若 `cap_[e] > 0` 且 `dist[to] > dist[v] + cost_[e]`，则更新并将 `to` 入队。
    3. 若 `t` 不可达（`prevv[t] == -1`），算法结束；否则沿 `prevv`/`preve` 回溯得到一条最小费用路径。
    4. 计算该路径的瓶颈容量 `d`，沿路径增广 `d`，更新 `cap_` 与反向 `cap_`，并累加 `cost += d * edge_cost`，`flow += d`。
    5. 重复步骤 1-4，直到无法再找到增广路径。

- `int main()`
  - 作用：读取输入（`n m`、m 条边、`s t`），初始化 `head`、调用 `ensure_edge_alloc(m)`、插入边并调用 `min_cost_max_flow`，最后把结果 `flow cost` 打印到 stdout。

---

## 五、代码设计思路与实现要点

1. 残量图设计：
   - 使用“并行数组 + 链表索引”形式的邻接表，方便在性能敏感的竞赛环境中减少内存开销与分配次数。
   - 每次插入（原始）边同时插入反向边以表示残量。

2. 路径搜索策略：
   - 当前版本使用 SPFA（基于队列），每轮找到一条最小费用路径后按瓶颈容量增广。SPFA 能处理负权边（只要图不存在可导致无限减费的负环），实现简单直观。
   - 早期实现中包含了 Dijkstra+potentials（势）版本，已保留堆实现作为参考。若图无负权或已用势消除了约化负权，Dijkstra+potentials 在大规模图上通常更稳定高效。

3. 数值与类型：
   - 费用使用 `long long`（typedef 为 `ll`）以减少溢出风险；容量使用 `int`。

4. 边界与健壮性：
   - `ensure_edge_alloc` 只做一次分配，未实现动态扩容；若在运行时需要插入更多边会越界。
   - 输入假定 0-based 节点编号；若需要 1-based 支持可在 `main` 中读入后减 1。

5. 性能与改进建议：
   - 若希望处理大规模稠密图或对性能有严格要求，建议恢复并使用 Dijkstra+potentials：先用 Bellman-Ford/ SPFA 计算初始势，再在约化费用非负的图上用 Dijkstra（优先队列）求短路，整体更快且更可控。
   - 可以把并行数组改为动态向量并在插入时 `realloc` 扩容以增强健壮性。
   - 可添加调试模式打印每轮增广路径/剩余容量/费用，便于教学或排错。

---

## 六、快速使用示例

在项目根目录下：

```bash
gcc -std=c11 -O2 Mcmf/mcmf.c -o Mcmf/mcmf
printf "4 4\n0 1 3 1\n1 3 2 2\n0 2 2 2\n2 3 2 1\n0 3\n" | Mcmf/mcmf
# 输出： 4 12
```

---

## 七、测试脚本说明

本仓库包含若干用于验证正确性与基准测试的脚本，改脚本由GPT辅助生成，位于 `Mcmf/` 目录：

- `run_correctness_tests.sh`：正确性测试脚本。
  - 功能：生成多组随机中等规模有向图，分别用 C 程序 `Mcmf/mcmf` 与 Python 参考实现 `Mcmf/mcmf_ref.py` 计算最小费用最大流，并比较两者输出（flow 与 cost）。
  - 用法：在项目根目录运行：
    ```bash
    bash Mcmf/run_correctness_tests.sh
    ```
  - 输出：脚本会在 `Mcmf/correctness_tests/` 下生成输入/输出文件，并在发现不一致时把失败用例保存为 `fail_*` 文件以便调试。

- `run_benchmark.sh`：性能基准测试脚本。
  - 功能：为多组不同规模生成随机图，编译并运行 `Mcmf/mcmf`，记录每次运行的耗时（和在支持 `/usr/bin/time` 时的峰值内存），将汇总写入 `Mcmf/benchmark_results.csv`，并将每次输入/输出日志保存在 `Mcmf/benchmark_logs/`。
  - 用法：在项目根目录运行：
    ```bash
    bash Mcmf/run_benchmark.sh
    ```
  - 可配置项：脚本顶部的 `N_LIST`、`AVG_DEG`、`REPEATS`、`TIMEOUT_SEC` 可根据机器性能调整。

在使用这些脚本前，请确保已编译 C 可执行文件或让脚本自动编译（脚本会尝试编译）。

---

欢迎pr
