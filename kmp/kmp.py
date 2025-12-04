def build_next(pattern):
    """
    构建 KMP 前缀表（next 数组）
    next[i] 表示 pattern[0:i] 的最长前后缀长度
    """
    m = len(pattern)
    nxt = [0] * m # 创建长m列表初始值为0
    j = 0

    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = nxt[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        nxt[i] = j

    return nxt


def kmp_search_all(text, pattern):
    """
    查找 text 中所有 pattern 的出现位置
    返回一个列表 positions，包含所有匹配的起始下标
    """
    if not pattern:
        return [0]

    n, m = len(text), len(pattern)
    nxt = build_next(pattern)
    positions = []
    j = 0  # pattern index

    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = nxt[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == m:
            # 匹配成功：记录起始位置
            positions.append(i - m + 1)
            j = nxt[j - 1]  # 继续寻找下一个匹配

    return positions

if __name__ == "__main__":
    text = input("请输入text:")
    pattern = input("请输入pattern:")

    positions = kmp_search_all(text,pattern)

    print()
    print("匹配总次数：",len(positions))
    print("每次匹配起始位置：",positions)

