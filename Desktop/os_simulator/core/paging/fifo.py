from collections import deque

from utils.paging_result import PagingResult


def fifo_page_replacement(reference_string, frame_size):
    """
    FIFO（First In First Out，先进先出）页面置换算法

    算法原理（老师常问）：
    —— 维护一个队列记录页面进入内存的顺序。当缺页且内存已满时，
       淘汰"最早进入内存"的那个页面，新页面加入队列末尾。

    实现细节：
    - 用 deque（双端队列）模拟页面进入顺序
    - memory 列表表示当前驻留在内存中的页面集合
    - 命中的页面不移到队尾（FIFO 严格按进入顺序淘汰）

    特点 / 优缺点：
    - 优点：实现简单，O(1) 淘汰
    - 缺点：
      * Belady 异常 —— 增加物理块数有时反而导致缺页率上升
        （这是 FIFO 独有的反常现象，LRU 和 OPT 不会出现）
      * 没考虑页面使用频率，可能淘汰常用页面
    - 为什么会有 Belady 异常？
      因为 FIFO 只按"谁先进来"淘汰，不考虑页面访问模式。
      增加块数后，旧的访问序列在更大的空间里可能"恰好"把
      常用页面提前淘汰了。

    参数:
        reference_string: 页面访问序列，如 [1, 2, 3, 1, 2, 4, ...]
        frame_size:       物理块数

    返回:
        PagingResult 对象
    """

    memory = []                 # 当前内存中的页面列表
    queue = deque()             # FIFO 队列，记录页面进入顺序
    result = PagingResult()

    for page in reference_string:
        # ===== 命中（Hit）：页面已在内存中 =====
        if page in memory:
            result.add_step(
                memory,
                False,         # fault=False
                None,          # 没有淘汰
            )
            continue

        # ===== 缺页（Page Fault） =====
        result.page_faults += 1
        replaced = None

        # 内存未满 → 直接放入
        if len(memory) < frame_size:
            memory.append(page)
            queue.append(page)
        else:
            # 内存已满 → FIFO 淘汰：弹出队首（最早进入的页面）
            old_page = queue.popleft()
            replaced = old_page

            # 找到旧页面在 memory 中的位置，替换为新页面
            index = memory.index(old_page)
            memory[index] = page

            # 新页面入队
            queue.append(page)

        result.add_step(
            memory,
            True,              # fault=True
            replaced,
        )

    return result