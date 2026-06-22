class BankerAlgorithm:
    """
    银行家算法 —— 死锁避免的经典算法

    算法背景（老师常问——为什么叫"银行家"？）：
    —— 算法灵感来自银行放贷：银行家手里有一定数量的资金（系统资源），
       在放贷前会先模拟"如果借出去，还能不能保证所有客户最终都能还钱"。
       如果不能保证，就不放贷。操作系统同理，分配资源前先检查"安全性"。

    核心数据结构：
    - available:   可用资源向量，每种资源还剩多少
    - max_demand:  最大需求矩阵，每个进程对每种资源最多需要多少
    - allocation:  已分配矩阵，每个进程目前已获得多少
    - need:        需求矩阵 = max_demand - allocation（还差多少）

    算法两大核心操作：
    1. is_safe_state()     → 判断当前系统是否处于安全状态（存在安全序列）
    2. request_resources() → 模拟分配请求，如果能保持安全就真正分配，否则拒绝
    """

    def __init__(self, available, max_demand, allocation):
        """
        初始化银行家算法数据结构

        参数:
            available:  [int, int, int] 各资源的可用数量，如 [3, 3, 2]
            max_demand: [[int]] 各进程对各资源的最大需求
            allocation: [[int]] 各进程已分配的资源
        """
        self.resource_count = len(available)     # 资源种类数（本项目默认 3 种：A, B, C）
        self.process_count = len(max_demand)     # 进程数
        self.available = list(available)         # 拷贝一份，避免外部修改
        self.max_demand = [list(m) for m in max_demand]
        self.allocation = [list(a) for a in allocation]

        # Need = Max - Allocation —— 银行家算法的核心推导
        self.need = [
            [self.max_demand[i][j] - self.allocation[i][j]
             for j in range(self.resource_count)]
            for i in range(self.process_count)
        ]

    def is_safe_state(self):
        """
        安全性检查算法

        算法流程（老师一定会问）：
        1. 初始化 Work = Available, Finish[i] = False
        2. 循环查找一个进程 i，满足：
           - Finish[i] == False（还未完成）
           - Need[i] <= Work  （当前可用资源能满足其需求）
        3. 找到这样的进程后：
           - Work += Allocation[i]（假设进程会释放已占用的资源）
           - Finish[i] = True
           - 将其加入安全序列
        4. 重复 2-3，直到找不到这样的进程或全部完成
        5. 如果所有 Finish 都为 True → 安全；否则 → 不安全

        时间复杂度：O(p² × r)，p 为进程数，r 为资源种类数

        返回:
            (is_safe, safety_sequence): 是否安全 + 安全序列
        """
        work = list(self.available)           # 工作向量 = 当前可用资源
        finish = [False] * self.process_count # 标记各进程是否"能完成"
        safety_sequence = []
        steps = []

        while len(safety_sequence) < self.process_count:
            found = False
            # 遍历所有进程，找一个能安全完成的
            for i in range(self.process_count):
                if not finish[i]:
                    # 检查 Need[i] 的每一项是否 <= Work 的对应项
                    if all(self.need[i][j] <= work[j]
                           for j in range(self.resource_count)):
                        # 回收该进程的资源（假设它执行完会释放）
                        work = [work[j] + self.allocation[i][j]
                                for j in range(self.resource_count)]
                        finish[i] = True
                        safety_sequence.append(f"P{i}")
                        steps.append({
                            'process': f"P{i}",
                            'work_before': [w - self.allocation[i][j]
                                            for j, w in enumerate(work)],
                            'work_after': list(work),
                            'need': list(self.need[i]),
                            'allocation': list(self.allocation[i])
                        })
                        found = True
                        break

            # 如果一轮遍历都没找到可完成的进程 → 不安全状态
            if not found:
                return False, None

        return True, safety_sequence

    def request_resources(self, process_index, request):
        """
        进程发起资源请求的处理流程

        算法流程（三步检查 + 试探分配 + 回滚）：
        1. 检查：request <= Need  ？（不能超过声明的最大需求）
        2. 检查：request <= Available？（不能超过当前可用）
        3. 试探分配：把资源"借"出去，然后调用 is_safe_state()
        4. 如果安全 → 批准，正式分配
           如果不安全 → 回滚，拒绝分配

        这是银行家算法的精髓："先试探，安全就做，不安全就撤销"

        参数:
            process_index: 发起请求的进程编号
            request:       [int, int, int] 请求的资源数量

        返回:
            (success, message, safety_sequence): 是否可分配 + 说明 + 安全序列
        """
        pid = process_index

        # ===== 第一步：请求不能超过 Need =====
        for j in range(self.resource_count):
            if request[j] > self.need[pid][j]:
                return (False,
                        f"请求资源超过最大需求！P{pid} 需求: {self.need[pid]}, 请求: {request}",
                        None)

        # ===== 第二步：请求不能超过 Available =====
        for j in range(self.resource_count):
            if request[j] > self.available[j]:
                return (False,
                        f"请求资源超过可用资源！可用: {self.available}, 请求: {request}",
                        None)

        # ===== 第三步：保存现场，试探分配 =====
        old_available = list(self.available)
        old_allocation = list(self.allocation[pid])
        old_need = list(self.need[pid])

        # 模拟分配
        self.available = [self.available[j] - request[j]
                          for j in range(self.resource_count)]
        self.allocation[pid] = [self.allocation[pid][j] + request[j]
                                for j in range(self.resource_count)]
        self.need[pid] = [self.need[pid][j] - request[j]
                          for j in range(self.resource_count)]

        # ===== 第四步：安全性检查 =====
        is_safe, safety_seq = self.is_safe_state()

        if is_safe:
            return (True,
                    f"可以分配资源给 P{pid}。系统仍处于安全状态。",
                    safety_seq)
        else:
            # 不安全 → 回滚到分配前的状态
            self.available = old_available
            self.allocation[pid] = old_allocation
            self.need[pid] = old_need
            return (False,
                    f"分配资源后系统将进入不安全状态，不能分配！",
                    None)