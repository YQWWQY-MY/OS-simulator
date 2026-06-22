def sjf(processes):
    """
    SJF（Shortest Job First，短进程优先）—— 抢占式版本（也称为 SRTF）

    算法原理（老师常问）：
    —— 每次调度时，在所有已到达 && 未完成的进程中，选择"剩余运行时间最短"
       的那个进程运行。每运行 1 个时间单位后重新检查是否有更短的进程到达。
       如果新到达的进程剩余时间更短，就会发生抢占。

    为什么抢占式比非抢占式更优？
    —— 抢占式可以让短进程在到达后立即抢占 CPU，进一步降低平均等待时间。
       SRTF（Shortest Remaining Time First）在理论上能获得最小的平均等待时间。

    这里用"步进 1 个时间单位"实现抢占逻辑，而不像 FCFS/HRN 那样一次性跑完。

    特点 / 优缺点：
    - 优点：平均等待时间最短（理论最优）
    - 缺点：
      * 需要预知进程的服务时间（实际上很难精确估计）
      * 长进程可能长期得不到 CPU → 饥饿（Starvation）
      * 抢占有上下文切换开销

    时间复杂度：O(total_time × n)，n 为进程数，total_time 为总运行时间

    参数:
        processes: Process 对象列表

    返回:
        gantt_chart: [(pid, start_time, end_time), ...] 甘特图数据
    """

    n = len(processes)
    completed = 0
    current_time = 0
    gantt_chart = []

    while completed < n:
        # ===== 第一步：筛选所有"已到达 + 未完成"的进程 =====
        available = [
            p for p in processes
            if p.arrive_time <= current_time
            and p.remaining_time > 0
        ]

        # ===== 第二步：如果没有可用进程，CPU 空转 =====
        if not available:
            current_time += 1
            continue

        # ===== 第三步：选择剩余时间最短的进程（SRTF 核心） =====
        process = min(
            available,
            key=lambda p: p.remaining_time
        )

        # 记录首次运行时间
        if process.start_time is None:
            process.start_time = current_time

        start = current_time

        # 只运行 1 个时间单位 —— 这是"抢占"的关键：
        # 每走 1 步就重新评估，如果有更短的进程到达就换人
        current_time += 1
        process.remaining_time -= 1

        end = current_time

        gantt_chart.append(
            (
                process.pid,
                start,
                end,
            )
        )

        # ===== 第四步：如果进程刚好完成 =====
        if process.remaining_time == 0:
            process.finish_time = current_time
            process.calculate_metrics()
            completed += 1

    return gantt_chart