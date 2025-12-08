#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCMF 算法性能测试脚本
测试运行时间与输入数据规模（n, m, 流量）的关系
"""

import subprocess
import time
import random
import os
import sys
import csv
from pathlib import Path

# 配置
MCMF_EXECUTABLE = "./Mcmf/mcmf"
OUTPUT_CSV = "Mcmf/performance_test_results.csv"
TEST_DATA_DIR = "Mcmf/performance_tests"


def ensure_compiled():
    """确保 C 程序已编译"""
    if not os.path.exists(MCMF_EXECUTABLE):
        print("编译 mcmf.c...")
        result = subprocess.run(
            ["gcc", "-std=c11", "-O2", "Mcmf/mcmf.c", "-o", MCMF_EXECUTABLE],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"编译失败: {result.stderr}")
            sys.exit(1)
        print("编译成功！")
    else:
        print(f"使用已存在的可执行文件: {MCMF_EXECUTABLE}")


def generate_random_graph(n, m, max_cap=100, max_cost=100, seed=None):
    """
    生成随机有向图
    
    Args:
        n: 顶点数
        m: 边数
        max_cap: 最大容量
        max_cost: 最大费用
        seed: 随机种子
    
    Returns:
        (n, edges, s, t) 其中 edges 是 [(u, v, cap, cost), ...]
    """
    if seed is not None:
        random.seed(seed)
    
    edges = []
    edge_set = set()
    
    # 确保从源点到汇点有路径
    s, t = 0, n - 1
    
    # 先生成一条从 s 到 t 的路径，确保连通
    path_len = min(5, n - 1)
    path = [s]
    for i in range(1, path_len):
        path.append(random.randint(1, n - 2))
    path.append(t)
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if u != v and (u, v) not in edge_set:
            cap = random.randint(max_cap // 2, max_cap)
            cost = random.randint(1, max_cost)
            edges.append((u, v, cap, cost))
            edge_set.add((u, v))
    
    # 生成剩余的随机边
    attempts = 0
    while len(edges) < m and attempts < m * 10:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and (u, v) not in edge_set:
            cap = random.randint(1, max_cap)
            cost = random.randint(1, max_cost)
            edges.append((u, v, cap, cost))
            edge_set.add((u, v))
        attempts += 1
    
    return n, edges[:m], s, t


def generate_input_string(n, edges, s, t):
    """生成输入字符串"""
    lines = [f"{n} {len(edges)}"]
    for u, v, cap, cost in edges:
        lines.append(f"{u} {v} {cap} {cost}")
    lines.append(f"{s} {t}")
    return "\n".join(lines) + "\n"


def run_mcmf(input_str, timeout=10):
    """
    运行 MCMF 程序并测量时间
    
    Returns:
        (flow, cost, elapsed_time) 或 None（如果超时或出错）
    """
    try:
        start_time = time.perf_counter()
        result = subprocess.run(
            [MCMF_EXECUTABLE],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        end_time = time.perf_counter()
        
        if result.returncode != 0:
            print(f"运行错误: {result.stderr}")
            return None
        
        elapsed = end_time - start_time
        output = result.stdout.strip().split()
        if len(output) >= 2:
            flow = int(output[0])
            cost = int(output[1])
            return flow, cost, elapsed
        return None
    except subprocess.TimeoutExpired:
        print(f"超时（> {timeout}s）")
        return None
    except Exception as e:
        print(f"运行异常: {e}")
        return None


def test_vertex_scaling():
    """测试 1: 顶点数缩放（固定边数比例）"""
    print("\n" + "=" * 60)
    print("测试 1: 顶点数缩放分析（m = 5n）")
    print("=" * 60)
    
    results = []
    vertex_counts = [50, 100, 200, 500, 1000, 2000]
    edge_ratio = 5  # m = 5n
    
    print(f"{'n':>6} {'m':>6} {'flow':>8} {'cost':>10} {'时间(ms)':>10}")
    print("-" * 50)
    
    for n in vertex_counts:
        m = n * edge_ratio
        for trial in range(3):  # 每个规模运行 3 次
            n_val, edges, s, t = generate_random_graph(n, m, seed=trial * 1000 + n)
            input_str = generate_input_string(n_val, edges, s, t)
            
            result = run_mcmf(input_str, timeout=30)
            if result:
                flow, cost, elapsed = result
                elapsed_ms = elapsed * 1000
                results.append({
                    'test': 'vertex_scaling',
                    'n': n,
                    'm': m,
                    'trial': trial + 1,
                    'flow': flow,
                    'cost': cost,
                    'time_ms': elapsed_ms
                })
                print(f"{n:>6} {m:>6} {flow:>8} {cost:>10} {elapsed_ms:>10.2f}")
            else:
                print(f"{n:>6} {m:>6} {'FAILED':>8}")
    
    return results


def test_edge_scaling():
    """测试 2: 边数缩放（固定顶点数）"""
    print("\n" + "=" * 60)
    print("测试 2: 边数缩放分析（n = 500）")
    print("=" * 60)
    
    results = []
    n = 500
    edge_counts = [1000, 2000, 5000, 10000, 15000]
    
    print(f"{'n':>6} {'m':>6} {'flow':>8} {'cost':>10} {'时间(ms)':>10}")
    print("-" * 50)
    
    for m in edge_counts:
        if m > n * (n - 1):  # 避免超过最大可能边数
            continue
        for trial in range(3):
            n_val, edges, s, t = generate_random_graph(n, m, seed=trial * 2000 + m)
            input_str = generate_input_string(n_val, edges, s, t)
            
            result = run_mcmf(input_str, timeout=30)
            if result:
                flow, cost, elapsed = result
                elapsed_ms = elapsed * 1000
                results.append({
                    'test': 'edge_scaling',
                    'n': n,
                    'm': m,
                    'trial': trial + 1,
                    'flow': flow,
                    'cost': cost,
                    'time_ms': elapsed_ms
                })
                print(f"{n:>6} {m:>6} {flow:>8} {cost:>10} {elapsed_ms:>10.2f}")
            else:
                print(f"{n:>6} {m:>6} {'FAILED':>8}")
    
    return results


def test_capacity_impact():
    """测试 3: 容量分布对增广轮数的影响"""
    print("\n" + "=" * 60)
    print("测试 3: 容量分布影响分析")
    print("=" * 60)
    
    results = []
    n, m = 300, 1500
    capacity_configs = [
        ("小容量(1-10)", 1, 10),
        ("中容量(10-100)", 10, 100),
        ("大容量(100-1000)", 100, 1000),
        ("混合容量(1-1000)", 1, 1000),
    ]
    
    print(f"{'配置':>15} {'n':>6} {'m':>6} {'flow':>8} {'cost':>10} {'时间(ms)':>10}")
    print("-" * 65)
    
    for config_name, min_cap, max_cap in capacity_configs:
        for trial in range(3):
            random.seed(trial * 3000 + min_cap)
            n_val, edges_base, s, t = generate_random_graph(n, m, max_cap=max_cap)
            
            # 重新设置容量
            edges = []
            for u, v, _, cost in edges_base:
                cap = random.randint(min_cap, max_cap)
                edges.append((u, v, cap, cost))
            
            input_str = generate_input_string(n_val, edges, s, t)
            
            result = run_mcmf(input_str, timeout=30)
            if result:
                flow, cost, elapsed = result
                elapsed_ms = elapsed * 1000
                results.append({
                    'test': 'capacity_impact',
                    'config': config_name,
                    'n': n,
                    'm': m,
                    'trial': trial + 1,
                    'flow': flow,
                    'cost': cost,
                    'time_ms': elapsed_ms
                })
                print(f"{config_name:>15} {n:>6} {m:>6} {flow:>8} {cost:>10} {elapsed_ms:>10.2f}")
            else:
                print(f"{config_name:>15} {n:>6} {m:>6} {'FAILED':>8}")
    
    return results


def test_sparse_vs_dense():
    """测试 4: 稀疏图 vs 稠密图"""
    print("\n" + "=" * 60)
    print("测试 4: 稀疏图 vs 稠密图")
    print("=" * 60)
    
    results = []
    test_cases = [
        ("稀疏图", 500, 1000),   # m ≈ 2n
        ("中等稠密", 500, 5000),  # m ≈ 10n
        ("稠密图", 300, 15000),   # m ≈ 50n
    ]
    
    print(f"{'类型':>10} {'n':>6} {'m':>6} {'m/n':>6} {'flow':>8} {'时间(ms)':>10}")
    print("-" * 55)
    
    for graph_type, n, m in test_cases:
        for trial in range(3):
            n_val, edges, s, t = generate_random_graph(n, m, seed=trial * 4000 + m)
            input_str = generate_input_string(n_val, edges, s, t)
            
            result = run_mcmf(input_str, timeout=30)
            if result:
                flow, cost, elapsed = result
                elapsed_ms = elapsed * 1000
                ratio = m / n
                results.append({
                    'test': 'sparse_vs_dense',
                    'type': graph_type,
                    'n': n,
                    'm': m,
                    'ratio': ratio,
                    'trial': trial + 1,
                    'flow': flow,
                    'cost': cost,
                    'time_ms': elapsed_ms
                })
                print(f"{graph_type:>10} {n:>6} {m:>6} {ratio:>6.1f} {flow:>8} {elapsed_ms:>10.2f}")
            else:
                print(f"{graph_type:>10} {n:>6} {m:>6} {'FAILED':>8}")
    
    return results


def save_results(all_results):
    """保存结果到 CSV 文件"""
    if not all_results:
        print("没有结果可保存")
        return
    
    # 创建目录
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    
    # 获取所有可能的字段
    fieldnames = set()
    for result in all_results:
        fieldnames.update(result.keys())
    fieldnames = sorted(fieldnames)
    
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n结果已保存到: {OUTPUT_CSV}")


def analyze_results(all_results):
    """分析结果并打印统计信息"""
    print("\n" + "=" * 60)
    print("结果分析")
    print("=" * 60)
    
    # 按测试类型分组
    by_test = {}
    for r in all_results:
        test = r.get('test', 'unknown')
        if test not in by_test:
            by_test[test] = []
        by_test[test].append(r)
    
    for test_name, results in by_test.items():
        print(f"\n{test_name}:")
        times = [r['time_ms'] for r in results]
        if times:
            print(f"  平均时间: {sum(times) / len(times):.2f} ms")
            print(f"  最小时间: {min(times):.2f} ms")
            print(f"  最大时间: {max(times):.2f} ms")
            
            # 计算时间/规模比（如果适用）
            if test_name == 'vertex_scaling':
                # 分析时间 vs n 的关系
                n_values = sorted(set(r['n'] for r in results))
                print(f"  顶点数范围: {min(n_values)} - {max(n_values)}")
                print(f"  时间增长倍数: {max(times) / min(times):.2f}x")
                print(f"  规模增长倍数: {max(n_values) / min(n_values):.2f}x")
            
            elif test_name == 'edge_scaling':
                # 分析时间 vs m 的关系
                m_values = sorted(set(r['m'] for r in results))
                print(f"  边数范围: {min(m_values)} - {max(m_values)}")
                print(f"  时间增长倍数: {max(times) / min(times):.2f}x")
                print(f"  规模增长倍数: {max(m_values) / min(m_values):.2f}x")


def main():
    print("=" * 60)
    print("MCMF 算法性能测试")
    print("=" * 60)
    
    ensure_compiled()
    
    all_results = []
    
    # 运行各项测试
    try:
        all_results.extend(test_vertex_scaling())
        all_results.extend(test_edge_scaling())
        all_results.extend(test_capacity_impact())
        all_results.extend(test_sparse_vs_dense())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    
    # 保存和分析结果
    if all_results:
        save_results(all_results)
        analyze_results(all_results)
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print(f"总测试数: {len(all_results)}")
        print(f"结果文件: {OUTPUT_CSV}")
        print("\n建议：")
        print("1. 使用 Excel/LibreOffice 打开 CSV 文件查看详细数据")
        print("2. 绘制时间-规模关系图验证复杂度")
        print("3. 关注增广轮数（flow）与运行时间的关系")
    else:
        print("\n没有生成测试结果")


if __name__ == "__main__":
    main()
