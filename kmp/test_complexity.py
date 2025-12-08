#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KMP 算法时间复杂度分析脚本
测试算法运行时间与输入规模之间的关系，验证 O(n+m) 的时间复杂度
此脚本由 Claude Sonnet 4.5 辅助完成
"""

import time
import random
import string
import matplotlib.pyplot as plt
import numpy as np
from kmp import kmp_search_all, build_next

# 配置 matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK JP', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def measure_time(func, *args, repeat=5):
    """
    测量函数执行时间，取多次运行的平均值
    
    Args:
        func: 要测试的函数
        *args: 函数参数
        repeat: 重复次数
    
    Returns:
        平均执行时间（秒）
    """
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)
    return np.mean(times)


def generate_text(length, alphabet_size=4):
    """
    生成指定长度的随机文本
    
    Args:
        length: 文本长度
        alphabet_size: 字母表大小
    
    Returns:
        随机文本字符串
    """
    alphabet = string.ascii_uppercase[:alphabet_size]
    return ''.join(random.choices(alphabet, k=length))


def test_text_length_scaling():
    """
    测试文本长度对运行时间的影响（固定模式长度）
    验证时间复杂度关于文本长度 n 是线性的
    """
    print("=" * 60)
    print("测试 1: 文本长度缩放分析（固定模式长度）")
    print("=" * 60)
    print("目标: 验证时间复杂度 O(n)，其中 n 为文本长度\n")
    
    pattern_length = 100
    pattern = generate_text(pattern_length, alphabet_size=4)
    
    # 不同的文本长度
    text_lengths = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
    times = []
    
    print(f"模式长度: {pattern_length}")
    print(f"字母表大小: 4 (A, B, C, D)\n")
    print(f"{'文本长度':>10} {'时间(秒)':>12} {'时间/n(微秒)':>15}")
    print("-" * 40)
    
    for n in text_lengths:
        text = generate_text(n, alphabet_size=4)
        elapsed = measure_time(kmp_search_all, text, pattern, repeat=3)
        times.append(elapsed)
        time_per_n = (elapsed / n) * 1e6  # 转换为微秒
        print(f"{n:>10} {elapsed:>12.6f} {time_per_n:>15.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 5))
    
    # 子图1: 时间 vs 文本长度
    plt.subplot(1, 2, 1)
    plt.plot(text_lengths, times, 'bo-', label='实际测量时间')
    
    # 拟合线性曲线
    coeffs = np.polyfit(text_lengths, times, 1)
    fitted_line = np.poly1d(coeffs)
    plt.plot(text_lengths, fitted_line(text_lengths), 'r--', label=f'线性拟合 (y={coeffs[0]:.2e}x+{coeffs[1]:.2e})')
    
    plt.xlabel('文本长度 n')
    plt.ylabel('运行时间 (秒)')
    plt.title('KMP 搜索时间 vs 文本长度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 时间/n vs 文本长度（验证常数因子）
    plt.subplot(1, 2, 2)
    time_per_n = [t / n * 1e6 for t, n in zip(times, text_lengths)]
    plt.plot(text_lengths, time_per_n, 'go-')
    plt.xlabel('文本长度 n')
    plt.ylabel('时间/n (微秒)')
    plt.title('单位时间复杂度（应接近常数）')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kmp_text_length_scaling.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: kmp_text_length_scaling.png")
    
    # 计算线性相关系数
    correlation = np.corrcoef(text_lengths, times)[0, 1]
    print(f"\n线性相关系数 R: {correlation:.6f}")
    print(f"线性拟合公式: t = {coeffs[0]:.6e} * n + {coeffs[1]:.6e}")
    print(f"\n结论: {'时间复杂度接近 O(n) ✓' if correlation > 0.98 else '需要进一步检查'}\n")


def test_pattern_length_scaling():
    """
    测试模式长度对运行时间的影响（固定文本长度）
    验证时间复杂度关于模式长度 m 是线性的
    """
    print("=" * 60)
    print("测试 2: 模式长度缩放分析（固定文本长度）")
    print("=" * 60)
    print("目标: 验证时间复杂度 O(m)，其中 m 为模式长度\n")
    
    text_length = 100000
    text = generate_text(text_length, alphabet_size=4)
    
    # 不同的模式长度
    pattern_lengths = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    times = []
    
    print(f"文本长度: {text_length}")
    print(f"字母表大小: 4 (A, B, C, D)\n")
    print(f"{'模式长度':>10} {'时间(秒)':>12} {'时间/m(微秒)':>15}")
    print("-" * 40)
    
    for m in pattern_lengths:
        pattern = generate_text(m, alphabet_size=4)
        elapsed = measure_time(kmp_search_all, text, pattern, repeat=3)
        times.append(elapsed)
        time_per_m = (elapsed / m) * 1e6  # 转换为微秒
        print(f"{m:>10} {elapsed:>12.6f} {time_per_m:>15.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 5))
    
    # 子图1: 时间 vs 模式长度
    plt.subplot(1, 2, 1)
    plt.plot(pattern_lengths, times, 'bo-', label='实际测量时间')
    
    # 拟合线性曲线
    coeffs = np.polyfit(pattern_lengths, times, 1)
    fitted_line = np.poly1d(coeffs)
    plt.plot(pattern_lengths, fitted_line(pattern_lengths), 'r--', label=f'线性拟合 (y={coeffs[0]:.2e}x+{coeffs[1]:.2e})')
    
    plt.xlabel('模式长度 m')
    plt.ylabel('运行时间 (秒)')
    plt.title('KMP 搜索时间 vs 模式长度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 时间/m vs 模式长度
    plt.subplot(1, 2, 2)
    time_per_m = [t / m * 1e6 for t, m in zip(times, pattern_lengths)]
    plt.plot(pattern_lengths, time_per_m, 'go-')
    plt.xlabel('模式长度 m')
    plt.ylabel('时间/m (微秒)')
    plt.title('单位时间复杂度（应接近常数）')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kmp_pattern_length_scaling.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: kmp_pattern_length_scaling.png")
    
    # 计算线性相关系数
    correlation = np.corrcoef(pattern_lengths, times)[0, 1]
    print(f"\n线性相关系数 R: {correlation:.6f}")
    print(f"线性拟合公式: t = {coeffs[0]:.6e} * m + {coeffs[1]:.6e}")
    print(f"\n结论: {'时间复杂度接近 O(m) ✓' if correlation > 0.98 else '需要进一步检查'}\n")


def test_combined_scaling():
    """
    测试文本长度和模式长度同时变化的情况
    验证总体时间复杂度 O(n + m)
    """
    print("=" * 60)
    print("测试 3: 组合缩放分析（n + m）")
    print("=" * 60)
    print("目标: 验证总体时间复杂度 O(n + m)\n")
    
    # 保持 n 和 m 的比例，同时增加
    sizes = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    pattern_ratio = 0.1  # 模式长度为文本长度的 10%
    
    times = []
    n_plus_m_values = []
    
    print(f"模式长度 / 文本长度比例: {pattern_ratio}")
    print(f"字母表大小: 4 (A, B, C, D)\n")
    print(f"{'n':>8} {'m':>8} {'n+m':>10} {'时间(秒)':>12} {'时间/(n+m)(微秒)':>20}")
    print("-" * 62)
    
    for n in sizes:
        m = int(n * pattern_ratio)
        text = generate_text(n, alphabet_size=4)
        pattern = generate_text(m, alphabet_size=4)
        
        elapsed = measure_time(kmp_search_all, text, pattern, repeat=3)
        times.append(elapsed)
        n_plus_m = n + m
        n_plus_m_values.append(n_plus_m)
        
        time_per_sum = (elapsed / n_plus_m) * 1e6  # 转换为微秒
        print(f"{n:>8} {m:>8} {n_plus_m:>10} {elapsed:>12.6f} {time_per_sum:>20.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 5))
    
    # 子图1: 时间 vs (n+m)
    plt.subplot(1, 2, 1)
    plt.plot(n_plus_m_values, times, 'bo-', label='实际测量时间')
    
    # 拟合线性曲线
    coeffs = np.polyfit(n_plus_m_values, times, 1)
    fitted_line = np.poly1d(coeffs)
    plt.plot(n_plus_m_values, fitted_line(n_plus_m_values), 'r--', 
             label=f'线性拟合 (y={coeffs[0]:.2e}x+{coeffs[1]:.2e})')
    
    plt.xlabel('n + m')
    plt.ylabel('运行时间 (秒)')
    plt.title('KMP 搜索时间 vs (n + m)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 时间/(n+m) vs (n+m)
    plt.subplot(1, 2, 2)
    time_per_sum = [t / s * 1e6 for t, s in zip(times, n_plus_m_values)]
    plt.plot(n_plus_m_values, time_per_sum, 'go-')
    plt.xlabel('n + m')
    plt.ylabel('时间/(n+m) (微秒)')
    plt.title('单位时间复杂度（应接近常数）')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kmp_combined_scaling.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: kmp_combined_scaling.png")
    
    # 计算线性相关系数
    correlation = np.corrcoef(n_plus_m_values, times)[0, 1]
    print(f"\n线性相关系数 R: {correlation:.6f}")
    print(f"线性拟合公式: t = {coeffs[0]:.6e} * (n+m) + {coeffs[1]:.6e}")
    print(f"\n结论: {'时间复杂度接近 O(n+m) ✓' if correlation > 0.98 else '需要进一步检查'}\n")


def test_worst_case():
    """
    测试最坏情况：高度重复的文本和模式
    """
    print("=" * 60)
    print("测试 4: 最坏情况分析（高度重复）")
    print("=" * 60)
    print("目标: 验证即使在最坏情况下，时间复杂度仍为 O(n+m)\n")
    
    pattern_length = 1000
    # 创建高度重复的模式
    pattern = 'A' * (pattern_length - 1) + 'B'
    
    text_lengths = [10000, 20000, 50000, 100000, 200000, 500000]
    times = []
    
    print(f"模式: {'A' * (min(20, pattern_length-1))}...B (长度 {pattern_length})")
    print(f"文本: 全为 'A' (最坏情况)\n")
    print(f"{'文本长度':>10} {'时间(秒)':>12} {'时间/n(微秒)':>15}")
    print("-" * 40)
    
    for n in text_lengths:
        text = 'A' * n  # 最坏情况：全是 'A'
        elapsed = measure_time(kmp_search_all, text, pattern, repeat=3)
        times.append(elapsed)
        time_per_n = (elapsed / n) * 1e6  # 转换为微秒
        print(f"{n:>10} {elapsed:>12.6f} {time_per_n:>15.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 5))
    
    # 子图1: 时间 vs 文本长度
    plt.subplot(1, 2, 1)
    plt.plot(text_lengths, times, 'ro-', label='最坏情况实际时间')
    
    # 拟合线性曲线
    coeffs = np.polyfit(text_lengths, times, 1)
    fitted_line = np.poly1d(coeffs)
    plt.plot(text_lengths, fitted_line(text_lengths), 'b--', label=f'线性拟合 (y={coeffs[0]:.2e}x+{coeffs[1]:.2e})')
    
    plt.xlabel('文本长度 n')
    plt.ylabel('运行时间 (秒)')
    plt.title('KMP 最坏情况: 时间 vs 文本长度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 时间/n vs 文本长度
    plt.subplot(1, 2, 2)
    time_per_n = [t / n * 1e6 for t, n in zip(times, text_lengths)]
    plt.plot(text_lengths, time_per_n, 'mo-')
    plt.xlabel('文本长度 n')
    plt.ylabel('时间/n (微秒)')
    plt.title('最坏情况单位时间复杂度')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kmp_worst_case.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: kmp_worst_case.png")
    
    # 计算线性相关系数
    correlation = np.corrcoef(text_lengths, times)[0, 1]
    print(f"\n线性相关系数 R: {correlation:.6f}")
    print(f"线性拟合公式: t = {coeffs[0]:.6e} * n + {coeffs[1]:.6e}")
    print(f"\n结论: {'即使最坏情况，时间复杂度仍为 O(n) ✓' if correlation > 0.98 else '需要进一步检查'}\n")


def test_build_next_complexity():
    """
    单独测试 build_next 函数的时间复杂度
    """
    print("=" * 60)
    print("测试 5: build_next 函数复杂度分析")
    print("=" * 60)
    print("目标: 验证 build_next 的时间复杂度为 O(m)\n")
    
    pattern_lengths = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    times = []
    
    print(f"{'模式长度':>10} {'时间(秒)':>12} {'时间/m(微秒)':>15}")
    print("-" * 40)
    
    for m in pattern_lengths:
        pattern = generate_text(m, alphabet_size=4)
        elapsed = measure_time(build_next, pattern, repeat=5)
        times.append(elapsed)
        time_per_m = (elapsed / m) * 1e6  # 转换为微秒
        print(f"{m:>10} {elapsed:>12.6f} {time_per_m:>15.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 5))
    
    # 子图1: 时间 vs 模式长度
    plt.subplot(1, 2, 1)
    plt.plot(pattern_lengths, times, 'bo-', label='实际测量时间')
    
    # 拟合线性曲线
    coeffs = np.polyfit(pattern_lengths, times, 1)
    fitted_line = np.poly1d(coeffs)
    plt.plot(pattern_lengths, fitted_line(pattern_lengths), 'r--', 
             label=f'线性拟合 (y={coeffs[0]:.2e}x+{coeffs[1]:.2e})')
    
    plt.xlabel('模式长度 m')
    plt.ylabel('运行时间 (秒)')
    plt.title('build_next 时间 vs 模式长度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 时间/m vs 模式长度
    plt.subplot(1, 2, 2)
    time_per_m = [t / m * 1e6 for t, m in zip(times, pattern_lengths)]
    plt.plot(pattern_lengths, time_per_m, 'go-')
    plt.xlabel('模式长度 m')
    plt.ylabel('时间/m (微秒)')
    plt.title('单位时间复杂度（应接近常数）')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kmp_build_next_complexity.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: kmp_build_next_complexity.png")
    
    # 计算线性相关系数
    correlation = np.corrcoef(pattern_lengths, times)[0, 1]
    print(f"\n线性相关系数 R: {correlation:.6f}")
    print(f"线性拟合公式: t = {coeffs[0]:.6e} * m + {coeffs[1]:.6e}")
    print(f"\n结论: {'build_next 时间复杂度为 O(m) ✓' if correlation > 0.98 else '需要进一步检查'}\n")


def main():
    """
    主函数：运行所有测试
    """
    print("\n" + "=" * 60)
    print(" " * 15 + "KMP 算法时间复杂度分析")
    print("=" * 60 + "\n")
    
    random.seed(42)  # 设置随机种子以便复现
    
    # 运行所有测试
    test_text_length_scaling()
    test_pattern_length_scaling()
    test_combined_scaling()
    test_worst_case()
    test_build_next_complexity()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print("\n生成的图表文件:")
    print("  - kmp_text_length_scaling.png     : 文本长度缩放分析")
    print("  - kmp_pattern_length_scaling.png  : 模式长度缩放分析")
    print("  - kmp_combined_scaling.png        : 组合缩放分析 (n+m)")
    print("  - kmp_worst_case.png              : 最坏情况分析")
    print("  - kmp_build_next_complexity.png   : build_next 复杂度分析")
    print("\n总结:")
    print("  KMP 算法的时间复杂度为 O(n + m)，其中:")
    print("  - n 是文本长度")
    print("  - m 是模式长度")
    print("  - build_next 的时间复杂度为 O(m)")
    print("  - 搜索阶段的时间复杂度为 O(n)")
    print("  - 即使在最坏情况下，时间复杂度仍然保持线性\n")


if __name__ == "__main__":
    main()
