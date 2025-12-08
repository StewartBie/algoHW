#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCMF 性能测试结果可视化脚本
读取 CSV 结果并生成可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 配置中文字体支持
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK JP', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

CSV_FILE = "Mcmf/performance_test_results.csv"
OUTPUT_DIR = "Mcmf/performance_plots"


def plot_vertex_scaling(df):
    """绘制顶点数缩放关系"""
    data = df[df['test'] == 'vertex_scaling'].copy()
    if data.empty:
        print("没有顶点数缩放数据")
        return
    
    # 按 n 分组，计算平均时间
    grouped = data.groupby('n')['time_ms'].agg(['mean', 'std']).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 时间 vs n
    ax1.errorbar(grouped['n'], grouped['mean'], yerr=grouped['std'], 
                 marker='o', capsize=5, label='实测时间')
    
    # 线性拟合
    coeffs = np.polyfit(grouped['n'], grouped['mean'], 1)
    fit_line = np.poly1d(coeffs)
    ax1.plot(grouped['n'], fit_line(grouped['n']), 'r--', 
             label=f'线性拟合 (y={coeffs[0]:.4f}x+{coeffs[1]:.2f})')
    
    ax1.set_xlabel('顶点数 n')
    ax1.set_ylabel('运行时间 (ms)')
    ax1.set_title('运行时间 vs 顶点数 (m=5n)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: 时间/n vs n (验证线性)
    grouped['time_per_n'] = grouped['mean'] / grouped['n']
    ax2.plot(grouped['n'], grouped['time_per_n'], 'go-')
    ax2.set_xlabel('顶点数 n')
    ax2.set_ylabel('时间/n (ms)')
    ax2.set_title('单位时间复杂度（应接近常数）')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/vertex_scaling.png", dpi=300, bbox_inches='tight')
    print(f"已保存: {OUTPUT_DIR}/vertex_scaling.png")
    
    # 打印相关系数
    corr = np.corrcoef(grouped['n'], grouped['mean'])[0, 1]
    print(f"  线性相关系数 R = {corr:.6f}")


def plot_edge_scaling(df):
    """绘制边数缩放关系"""
    data = df[df['test'] == 'edge_scaling'].copy()
    if data.empty:
        print("没有边数缩放数据")
        return
    
    grouped = data.groupby('m')['time_ms'].agg(['mean', 'std']).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 时间 vs m
    ax1.errorbar(grouped['m'], grouped['mean'], yerr=grouped['std'], 
                 marker='o', capsize=5, label='实测时间')
    
    # 线性拟合
    coeffs = np.polyfit(grouped['m'], grouped['mean'], 1)
    fit_line = np.poly1d(coeffs)
    ax1.plot(grouped['m'], fit_line(grouped['m']), 'r--', 
             label=f'线性拟合 (y={coeffs[0]:.6f}x+{coeffs[1]:.2f})')
    
    ax1.set_xlabel('边数 m')
    ax1.set_ylabel('运行时间 (ms)')
    ax1.set_title('运行时间 vs 边数 (n=500)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: 时间/m vs m
    grouped['time_per_m'] = grouped['mean'] / grouped['m']
    ax2.plot(grouped['m'], grouped['time_per_m'], 'go-')
    ax2.set_xlabel('边数 m')
    ax2.set_ylabel('时间/m (ms)')
    ax2.set_title('单位时间复杂度（应接近常数）')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/edge_scaling.png", dpi=300, bbox_inches='tight')
    print(f"已保存: {OUTPUT_DIR}/edge_scaling.png")
    
    corr = np.corrcoef(grouped['m'], grouped['mean'])[0, 1]
    print(f"  线性相关系数 R = {corr:.6f}")


def plot_capacity_impact(df):
    """绘制容量分布影响"""
    data = df[df['test'] == 'capacity_impact'].copy()
    if data.empty:
        print("没有容量分布数据")
        return
    
    grouped = data.groupby('config')['time_ms'].agg(['mean', 'std']).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 时间对比
    x_pos = np.arange(len(grouped))
    ax1.bar(x_pos, grouped['mean'], yerr=grouped['std'], 
            capsize=5, alpha=0.7, color=['blue', 'green', 'orange', 'red'])
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(grouped['config'], rotation=15, ha='right')
    ax1.set_ylabel('运行时间 (ms)')
    ax1.set_title('不同容量分布的运行时间')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 图2: 流量对比
    flow_grouped = data.groupby('config')['flow'].agg(['mean', 'std']).reset_index()
    ax2.bar(x_pos, flow_grouped['mean'], yerr=flow_grouped['std'], 
            capsize=5, alpha=0.7, color=['blue', 'green', 'orange', 'red'])
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(flow_grouped['config'], rotation=15, ha='right')
    ax2.set_ylabel('最大流量')
    ax2.set_title('不同容量分布的流量大小')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/capacity_impact.png", dpi=300, bbox_inches='tight')
    print(f"已保存: {OUTPUT_DIR}/capacity_impact.png")


def plot_sparse_vs_dense(df):
    """绘制稀疏图 vs 稠密图"""
    data = df[df['test'] == 'sparse_vs_dense'].copy()
    if data.empty:
        print("没有稀疏/稠密对比数据")
        return
    
    grouped = data.groupby('type')['time_ms'].agg(['mean', 'std']).reset_index()
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    x_pos = np.arange(len(grouped))
    bars = ax.bar(x_pos, grouped['mean'], yerr=grouped['std'], 
                   capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(grouped['type'])
    ax.set_ylabel('运行时间 (ms)')
    ax.set_title('稀疏图 vs 稠密图性能对比')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar, mean_val in zip(bars, grouped['mean']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mean_val:.1f}ms',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/sparse_vs_dense.png", dpi=300, bbox_inches='tight')
    print(f"已保存: {OUTPUT_DIR}/sparse_vs_dense.png")


def plot_combined_scaling(df):
    """绘制组合缩放（n 和 m 同时变化）"""
    # 从顶点缩放数据中提取（因为 m = 5n）
    data = df[df['test'] == 'vertex_scaling'].copy()
    if data.empty:
        return
    
    data['n_plus_m'] = data['n'] + data['m']
    grouped = data.groupby('n_plus_m')['time_ms'].agg(['mean', 'std']).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 时间 vs (n+m)
    ax1.errorbar(grouped['n_plus_m'], grouped['mean'], yerr=grouped['std'], 
                 marker='o', capsize=5, label='实测时间')
    
    coeffs = np.polyfit(grouped['n_plus_m'], grouped['mean'], 1)
    fit_line = np.poly1d(coeffs)
    ax1.plot(grouped['n_plus_m'], fit_line(grouped['n_plus_m']), 'r--', 
             label=f'线性拟合 (y={coeffs[0]:.6f}x+{coeffs[1]:.2f})')
    
    ax1.set_xlabel('n + m')
    ax1.set_ylabel('运行时间 (ms)')
    ax1.set_title('运行时间 vs (n+m)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: 时间/(n+m) vs (n+m)
    grouped['time_per_sum'] = grouped['mean'] / grouped['n_plus_m']
    ax2.plot(grouped['n_plus_m'], grouped['time_per_sum'], 'go-')
    ax2.set_xlabel('n + m')
    ax2.set_ylabel('时间/(n+m) (ms)')
    ax2.set_title('单位时间复杂度（验证 O(n+m)）')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/combined_scaling.png", dpi=300, bbox_inches='tight')
    print(f"已保存: {OUTPUT_DIR}/combined_scaling.png")


def main():
    print("=" * 60)
    print("MCMF 性能测试结果可视化")
    print("=" * 60)
    
    if not Path(CSV_FILE).exists():
        print(f"\n错误: 找不到结果文件 {CSV_FILE}")
        print("请先运行 test_performance.py 生成测试数据")
        return
    
    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # 读取数据
    print(f"\n读取数据: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    print(f"共 {len(df)} 条记录")
    
    # 生成各类图表
    print("\n生成图表...")
    plot_vertex_scaling(df)
    plot_edge_scaling(df)
    plot_capacity_impact(df)
    plot_sparse_vs_dense(df)
    plot_combined_scaling(df)
    
    print("\n" + "=" * 60)
    print("可视化完成！")
    print("=" * 60)
    print(f"图表已保存到: {OUTPUT_DIR}/")
    print("\n生成的图表:")
    print("  - vertex_scaling.png     : 顶点数缩放分析")
    print("  - edge_scaling.png       : 边数缩放分析")
    print("  - capacity_impact.png    : 容量分布影响")
    print("  - sparse_vs_dense.png    : 稀疏/稠密对比")
    print("  - combined_scaling.png   : 组合缩放 (n+m)")


if __name__ == "__main__":
    main()
