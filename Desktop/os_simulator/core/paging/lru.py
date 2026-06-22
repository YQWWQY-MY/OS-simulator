from utils.paging_result import PagingResult


def lru_page_replacement(reference_string, frame_size):
    """
    LRU（Least Recently Used，最近最久未使用）页面置换算法

    算法原理（老师常问）：
    —— 基于"局部性原理"：最近被访问过的页面，在不久的将来很可能再次被访问；
       反之，很久没被访问的页面，很可能以后也不会被访问。
       所以淘汰"距离上次访问时间最久"的那个页面。

    实现方式（这里用的是"时间戳法"）：
    - 用字典 last_used 记录每个页面最后一次被访问的时间
    - 每次访问时递增全局时钟 time
    - 缺页时淘汰 last_used 值最小的页面（即最久未访问）

    其他实现方式（面试可能问）：
    - 栈法：每次访问把页面移到栈顶，淘汰栈底元素
    - 计数器法（硬件）：CPU 内置计数器，每次内存访问自动更新
    - 移位寄存器法：用移位寄存器跟踪访问历史

    特点 / 优缺点：
    - 优点：基于局部性原理，缺页率通常远低于 FIFO
    - 缺点：
      * 需要维护时间戳或栈结构，每次访问都要更新（O(1) 但常数大）
      * 实际 OS 中纯 LRU 硬件支持成本高，通常用近似 LRU（Clock 算法）
    - 不会出现 Belady 异常（LRU 属于栈类算法）

    参数:
        reference_string: 页面访问序列
        frame_size:       物理块数

    返回:
        PagingResult 对象
    """

    memory = []              # 当前内存中的页面列表
    last_used = {}           # {页面号: 最后一次访问的时间戳}
    result = PagingResult()
    time = 0                 # 全局逻辑时钟

    for page in reference_string:
        time += 1            # 每次访问时钟+1

        # ===== 命中：页面已在内存中 =====
        if page in memory:
            last_used[page] = time    # 更新最近访问时间（关键！）
            result.add_step(memory, False, None)
            continue

        # ===== 缺页 =====
        result.page_faults += 1
        replaced = None

        # 内存未满 → 直接放入
        if len(memory) < frame_size:
            memory.append(page)
            last_used[page] = time
        else:
            # 内存已满 → 淘汰 last_used 最小的页面（最久未使用）
            lru_page = min(memory, key=lambda p: last_used.get(p, 0))
            replaced = lru_page
            index = memory.index(lru_page)
            memory[index] = page
            del last_used[lru_page]   # 清理被淘汰页面的记录
            last_used[page] = time    # 新页面的访问时间

        result.add_step(memory, True, replaced)

    return result