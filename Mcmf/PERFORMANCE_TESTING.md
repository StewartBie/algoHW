# MCMF 性能测试使用说明

## 测试脚本概述

本目录包含两个性能测试脚本：

1. **`test_performance.py`** - 性能测试主脚本
2. **`visualize_performance.py`** - 结果可视化脚本

## 快速开始

### 1. 运行性能测试

```bash
# 在项目根目录执行
python3 Mcmf/test_performance.py
```

测试将自动：
- 编译 `mcmf.c`（如果尚未编译）
- 运行 4 组测试（详见下文）
- 生成 CSV 结果文件：`Mcmf/performance_test_results.csv`
- 显示统计分析

### 2. 生成可视化图表

```bash
python3 Mcmf/visualize_performance.py
```

需要安装依赖：
```bash
pip3 install pandas matplotlib numpy
```

图表将保存到：`Mcmf/performance_plots/`

## 测试内容

### 测试 1: 顶点数缩放（m = 5n）

**目标**：验证时间复杂度与顶点数 n 的关系

**测试参数**：
- 顶点数 n: 50, 100, 200, 500, 1000, 2000
- 边数 m = 5n
- 每个规模运行 3 次

**验证内容**：
- 运行时间是否与 n 呈线性关系
- 计算线性相关系数 R

### 测试 2: 边数缩放（n = 500）

**目标**：验证时间复杂度与边数 m 的关系

**测试参数**：
- 固定顶点数 n = 500
- 边数 m: 1000, 2000, 5000, 10000, 15000
- 每个规模运行 3 次

**验证内容**：
- 运行时间是否与 m 呈线性关系
- 单轮 SPFA 的平均复杂度

### 测试 3: 容量分布影响

**目标**：研究容量分布对增广轮数和运行时间的影响

**测试配置**：
- 小容量 (1-10)：增广轮数多，时间可能更长
- 中容量 (10-100)：平衡
- 大容量 (100-1000)：增广轮数少，时间可能更短
- 混合容量 (1-1000)：实际场景

**验证内容**：
- 容量大小与增广轮数的关系
- 容量大小与运行时间的关系

### 测试 4: 稀疏图 vs 稠密图

**目标**：对比不同图密度下的性能

**测试配置**：
- 稀疏图：m ≈ 2n
- 中等稠密：m ≈ 10n
- 稠密图：m ≈ 50n

**验证内容**：
- 图密度对性能的影响
- SPFA 在不同密度图上的表现

## 输出文件

### CSV 结果文件

**文件路径**：`Mcmf/performance_test_results.csv`

**字段说明**：
- `test`: 测试类型（vertex_scaling, edge_scaling, 等）
- `n`: 顶点数
- `m`: 边数
- `trial`: 试验编号（1-3）
- `flow`: 最大流量
- `cost`: 最小费用
- `time_ms`: 运行时间（毫秒）
- 其他：根据测试类型的特定字段

### 可视化图表

**目录**：`Mcmf/performance_plots/`

**图表列表**：
1. `vertex_scaling.png` - 顶点数缩放分析
   - 左图：时间 vs n + 线性拟合
   - 右图：时间/n vs n（验证线性）

2. `edge_scaling.png` - 边数缩放分析
   - 左图：时间 vs m + 线性拟合
   - 右图：时间/m vs m（验证线性）

3. `capacity_impact.png` - 容量分布影响
   - 左图：不同配置的运行时间对比
   - 右图：不同配置的流量大小对比

4. `sparse_vs_dense.png` - 稀疏/稠密对比
   - 柱状图显示不同密度下的运行时间

5. `combined_scaling.png` - 组合缩放 (n+m)
   - 左图：时间 vs (n+m)
   - 右图：时间/(n+m)（验证 O(n+m)）

## 自定义测试

### 修改测试规模

编辑 `test_performance.py`，修改对应函数中的参数：

```python
# 在 test_vertex_scaling() 中
vertex_counts = [50, 100, 200, 500, 1000, 2000]  # 修改这里

# 在 test_edge_scaling() 中
edge_counts = [1000, 2000, 5000, 10000, 15000]  # 修改这里
```

### 添加新的测试

在 `test_performance.py` 中添加新函数：

```python
def test_custom():
    """自定义测试"""
    results = []
    # ... 测试逻辑 ...
    return results

# 在 main() 中调用
all_results.extend(test_custom())
```

### 调整超时时间

```python
# 默认超时 10 秒
result = run_mcmf(input_str, timeout=10)

# 修改为 30 秒（适合大规模图）
result = run_mcmf(input_str, timeout=30)
```

## 结果分析建议

### 1. 验证时间复杂度

观察图表中的线性拟合：
- **R > 0.95**：说明时间复杂度接近线性
- **时间/规模比接近常数**：进一步验证线性关系

### 2. 分析性能瓶颈

- 如果时间增长快于线性：可能遇到 SPFA 退化
- 如果稠密图明显慢：说明单轮 SPFA 接近 O(nm)
- 如果小容量配置慢：说明增广轮数是主要因素

### 3. 实际应用指导

根据测试结果：
- **n < 1000**：当前实现性能优秀
- **1000 < n < 5000**：性能良好，可用于大多数场景
- **n > 5000**：考虑优化（Dijkstra + 势函数）

## 故障排查

### 编译失败

```bash
# 手动编译
gcc -std=c11 -O2 Mcmf/mcmf.c -o Mcmf/mcmf
```

### Python 依赖缺失

```bash
# 安装必需的库
pip3 install pandas matplotlib numpy
```

### 测试超时

- 减少测试规模
- 增加超时时间
- 检查算法实现是否正确

### 内存不足

- 减少并发测试数量
- 使用较小的 n 和 m
- 关闭其他程序释放内存

## 进阶使用

### 批量测试

```bash
# 运行多次测试并收集数据
for i in {1..5}; do
    python3 Mcmf/test_performance.py
    mv Mcmf/performance_test_results.csv Mcmf/results_$i.csv
done
```

### 与参考实现对比

修改脚本同时测试 C 实现和 Python 实现：
- 对比运行时间
- 验证结果一致性
- 分析性能差异

### 导出数据到其他工具

CSV 文件可以：
- 导入 Excel/LibreOffice 进行分析
- 使用 R/MATLAB 进行统计分析
- 导入 Jupyter Notebook 做交互式分析

## 贡献与反馈

如果发现问题或有改进建议，欢迎：
- 提交 Issue
- 创建 Pull Request
- 分享测试结果和分析

---

**最后更新**：2025-12-08
