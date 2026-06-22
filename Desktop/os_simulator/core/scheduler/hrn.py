def hrn(processes):
    """
    HRN（Highest Response Ratio Next，最高响应比优先）调度算法

    算法原理（老师常问）：
    —— 每次选择"响应比"最高的进程运行。响应比公式：

            R = (等待时间 + 服务时间) / 服务时间
              = 1 + 等待时间 / 服务时间

        等待时间越长的进程，响应比越高（"优待老进程"）；
        服务时间越短的进程，响应比也越高（"偏好短进程"）。
        这样就兼顾了短进程优先和避免长进程饥饿。

    为什么 HRN 是对 SJF 的改进？
    —— SJF 可能导致长进程饿死（一直排不上队），
       而 HRN 中随着等待时间增加，长进程的响应比会逐渐爬升，最终必然被选中，
       从而解决了饥饿问题。

    特点 / 优缺点：
    - 优点：兼顾短进程和长进程，不会饥饿
    - 缺点：每次调度都要计算所有进程的响应比，开销较大；非抢占式

    时间复杂度：O(n × total_processes_to_schedule)，
               每次选进程要扫描所有可用进程计算响应比

    参数:
        processes: Process 对象列表

    返回:
        gantt_chart: [(pid, start_time, end_time), ...] 甘特图数据
    """

    n = len(processes)
    completed = 0
    current_time = 0
    visited = set()      # 记录已完成调度的进程 pid，防止重复调度
    gantt_chart = []

    while completed < n:
        # ===== 第一步：筛选"已到达 + 未被调度过"的进程 =====
        available = [
            p for p in processes
            if p.arrive_time <= current_time
            and p.pid not in visited
        ]

        # ===== 第二步：如果没有可用进程，CPU 空转 =====
        if not available:
            current_time += 1
            continue

        # ===== 第三步：计算响应比，选择最高的进程 =====
        def response_ratio(p):
            """
            R = (等待时间 + 服务时间) / 服务时间
              = 1 + 等待时间 / 服务时间

            等待时间 = 当前时间 - 到达时间
            """
            waiting_time = current_time - p.arrive_time
            return (
                waiting_time + p.burst_time
            ) / p.burst_time

        process = max(
            available,
            key=response_ratio
        )

        # ===== 第四步：非抢占式运行到底 =====
        process.start_time = current_time

        start = current_time
        current_time += process.burst_time
        end = current_time

        process.finish_time = current_time
        process.calculate_metrics()

        visited.add(process.pid)
        completed += 1

        gantt_chart.append(
            (
                process.pid,
                start,
                end,
            )
        )

    return gantt_chart