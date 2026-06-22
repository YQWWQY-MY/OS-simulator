class PagingResult:
    """
    页面置换算法的结果封装类

    为什么需要这个类？
    —— 三种页面置换算法（FIFO / LRU / OPT）返回的结果结构一致，
       统一用这个类封装"每一步的内存状态 + 缺页标记 + 被淘汰页面"，
       方便前端用统一的格式展示表格和缺页率。

    字段说明：
    - memory_history:    List[List[int]]，每一步内存中驻留的页面快照
    - page_faults:       int，缺页总次数
    - page_fault_flags:  List[bool]，每一步是否发生了缺页
    - replaced_pages:    List[int|None]，每一步被换出的页面号（None 表示未换出）
    """

    def __init__(self):
        self.memory_history = []
        self.page_faults = 0
        self.page_fault_flags = []
        self.replaced_pages = []

    def add_step(self, memory, fault, replaced):
        """
        记录算法执行过程中的一步。

        参数:
            memory:   当前内存中的页面列表
            fault:    True 表示本次访问是缺页，False 表示命中
            replaced: 被淘汰的页面号；如果没有淘汰则传 None
        """
        self.memory_history.append(memory.copy())
        self.page_fault_flags.append(fault)
        self.replaced_pages.append(replaced)