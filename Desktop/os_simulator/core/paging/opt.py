from utils.paging_result import PagingResult


def opt_page_replacement(reference_string, frame_size):
    """
    OPT（Optimal Page Replacement，最优置换）页面置换算法

    算法原理（老师常问）：
    —— 淘汰"在未来最长时间内不再被访问"的页面，即：
       在所有内存页面中，找到下一次被访问的时机最远的那个页面来淘汰。

    为什么 OPT 是"理论最优"？
    —— 它等价于"上帝视角"：已知未来的全部页面访问序列，
       做出的决策是最优的。任何实际算法（FIFO、LRU 等）的缺页率
       都不可能低于 OPT，所以 OPT 常被用作理论下界来评估其他算法。

    为什么 OPT 无法实际使用？
    —— 因为操作系统无法预知进程未来会访问哪些页面。
       它只在模拟和离线分析中有用。

    实现细节：
    - 对于内存中的每个页面 p，在 reference_string[i+1:] 中查找它
      下一次出现的索引；如果永不出现，future_use = +∞（优先淘汰）

    参数:
        reference_string: 页面访问序列
        frame_size:       物理块数

    返回:
        PagingResult 对象
    """

    memory = []              # 当前内存中的页面列表
    result = PagingResult()

    for i, page in enumerate(reference_string):
        # ===== 命中 =====
        if page in memory:
            result.add_step(memory, False, None)
            continue

        # ===== 缺页 =====
        result.page_faults += 1
        replaced = None

        # 内存未满 → 直接放入
        if len(memory) < frame_size:
            memory.append(page)
        else:
            # 内存已满 → 找未来最远使用的页面淘汰
            # future_use[p] = 页面 p 下一次出现的索引，
            # 如果永不出现则为 float('inf')，表示"无限远"，优先淘汰
            future_use = {}
            for p in memory:
                try:
                    # 从当前位置 i+1 往后找页面 p 的下一次出现
                    future_use[p] = reference_string.index(p, i + 1)
                except ValueError:
                    # 页面 p 未来不再被访问 → 最佳淘汰候选
                    future_use[p] = float('inf')

            # 选择 future_use 最大的页面淘汰（最远使用或永不使用）
            victim = max(memory, key=lambda p: future_use[p])
            replaced = victim
            index = memory.index(victim)
            memory[index] = page

        result.add_step(memory, True, replaced)

    return result