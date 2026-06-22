from models.process import Process


def fcfs(processes):
    """
    FCFS（First Come First Served，先来先服务）调度算法

    算法原理（老师常问）：
    —— 最简单的非抢占式调度算法。按照进程到达时间的先后顺序分配 CPU，
       一个进程运行完整个 burst_time 后才释放 CPU 给下一个进程。

    特点 / 优缺点：
    - 优点：实现简单，无抢占开销，公平（先到先得）
    - 缺点：护航效应（Convoy Effect）——长进程在前会阻塞后面所有短进程，
            导致平均等待时间和平均周转时间偏高
    - 非抢占式，不适合分时系统

    时间复杂度：O(n log n)，主要花在按到达时间排序上

    参数:
        processes: Process 对象列表

    返回:
        gantt_chart: [(pid, start_time, end_time), ...] 甘特图数据
    """

    # 按到达时间升序排序 —— FCFS 的核心：谁先到谁先运行
    processes.sort(key=lambda p: p.arrive_time)

    current_time = 0
    gantt_chart = []

    for process in processes:
        # 如果当前时间还没到进程的到达时间，CPU 空闲等待
        # （模拟真实场景中 CPU 空转，直到有进程到达）
        if current_time < process.arrive_time:
            current_time = process.arrive_time

        # 记录开始运行时间
        process.start_time = current_time

        # 进程独占 CPU，连续运行完整个 burst_time
        current_time += process.burst_time

        # 记录完成时间
        process.finish_time = current_time

        # 计算周转时间和带权周转时间
        process.calculate_metrics()

        # 记录甘特图的一个片段
        gantt_chart.append(
            (
                process.pid,
                process.start_time,
                process.finish_time,
            )
        )

    return gantt_chart