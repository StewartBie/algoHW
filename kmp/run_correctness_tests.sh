#!/bin/bash

# KMP 算法大规模正确性测试脚本
# 自动生成测试用例并验证 KMP 算法的正确性

echo "==================================="
echo "KMP 算法大规模正确性测试"
echo "==================================="
echo ""

# 创建测试目录
mkdir -p test_cases

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
run_test() {
    local test_name=$1
    local text=$2
    local pattern=$3
    local expected=$4
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # 运行 KMP 算法
    result=$(python3 -c "
from kmp import kmp_search_all
text = '''$text'''
pattern = '''$pattern'''
positions = kmp_search_all(text, pattern)
print(','.join(map(str, positions)) if positions else '')
")
    
    # 比较结果
    if [ "$result" == "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        echo "  Expected: $expected"
        echo "  Got:      $result"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo "运行基础测试用例..."
echo ""

# 测试 1: 基本匹配
run_test "基本匹配" "ABABCABABA" "ABA" "0,5,7"

# 测试 2: 无匹配
run_test "无匹配" "ABABCABABA" "XYZ" ""

# 测试 3: 完全匹配
run_test "完全匹配" "ABCDEF" "ABCDEF" "0"

# 测试 4: 单字符匹配
run_test "单字符匹配" "AAAAAA" "A" "0,1,2,3,4,5"

# 测试 5: 重复模式
run_test "重复模式" "ABABABABAB" "AB" "0,2,4,6,8"

# 测试 6: 模式在末尾
run_test "模式在末尾" "XYZABC" "ABC" "3"

# 测试 7: 模式在开头
run_test "模式在开头" "ABCXYZ" "ABC" "0"

# 测试 8: 重叠匹配
run_test "重叠匹配" "AAAA" "AA" "0,1,2"

# 测试 9: 长文本单次匹配
run_test "长文本单次匹配" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "XYZ" "23"

# 测试 10: 空模式
run_test "空模式" "ABCDEF" "" "0"

echo ""
echo "运行随机生成测试用例..."
echo ""

# 使用 Python 生成并测试随机用例
python3 << 'EOF'
import random
import string
from kmp import kmp_search_all

def generate_random_test(test_num, text_len, pattern_len):
    """生成随机测试用例"""
    # 生成随机文本和模式
    alphabet = 'ABCD'  # 使用小字母表增加匹配概率
    text = ''.join(random.choices(alphabet, k=text_len))
    pattern = ''.join(random.choices(alphabet, k=pattern_len))
    
    # 使用 KMP 算法
    kmp_result = kmp_search_all(text, pattern)
    
    # 使用 Python 内置方法验证
    expected = []
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        expected.append(pos)
        start = pos + 1
    
    # 比较结果
    if kmp_result == expected:
        print(f"✓ PASS: 随机测试 {test_num} (text_len={text_len}, pattern_len={pattern_len})")
        return True
    else:
        print(f"✗ FAIL: 随机测试 {test_num}")
        print(f"  Text: {text[:50]}...")
        print(f"  Pattern: {pattern}")
        print(f"  Expected: {expected}")
        print(f"  Got: {kmp_result}")
        return False

# 运行多组随机测试
random.seed(42)  # 设置随机种子以便复现
total = 0
passed = 0

# 不同规模的测试
test_configs = [
    (10, 100, 5),      # 10 个测试，文本长度 100，模式长度 5
    (10, 500, 10),     # 10 个测试，文本长度 500，模式长度 10
    (10, 1000, 20),    # 10 个测试，文本长度 1000，模式长度 20
    (5, 5000, 50),     # 5 个测试，文本长度 5000，模式长度 50
    (5, 10000, 100),   # 5 个测试，文本长度 10000，模式长度 100
]

for num_tests, text_len, pattern_len in test_configs:
    for i in range(num_tests):
        total += 1
        if generate_random_test(total, text_len, pattern_len):
            passed += 1

print(f"\n随机测试统计: {passed}/{total} 通过")
exit(0 if passed == total else 1)
EOF

RANDOM_EXIT=$?

echo ""
echo "==================================="
echo "测试结果汇总"
echo "==================================="
echo -e "基础测试: ${PASSED_TESTS}/${TOTAL_TESTS} 通过"

if [ $RANDOM_EXIT -eq 0 ]; then
    echo -e "随机测试: ${GREEN}全部通过${NC}"
else
    echo -e "随机测试: ${RED}存在失败${NC}"
fi

echo ""
if [ $FAILED_TESTS -eq 0 ] && [ $RANDOM_EXIT -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}部分测试失败！${NC}"
    exit 1
fi
