from collections import deque


def rr(processes, time_quantum=2):
    """
    RR（Round Robin，时间片轮转）调度算法

    算法原理（老师常问）：
    —— 为每个进程分配一个固定的时间片（time quantum）。进程在 CPU 上最多运行
       一个时间片，如果没运行完就排到就绪队列末尾，CPU 交给下一个进程。
       循环进行，直到所有进程运行完毕。

    关键设计决策：
    - 时间片大小直接影响系统性能：
      * 太小 → 上下文切换频繁，系统开销大
      * 太大 → 退化为 FCFS，响应时间长
      * 经验值：时间片应略大于典型交互时间（通常 10ms~100ms），
        本项目默认用 2 个时间单位（模拟环境中可灵活设置）

    - 这里的实现用 deque（双端队列）模拟就绪队列，新到达的进程在每次调度前
      入队，时间片用完的进程从队尾重新入队。

    特点 / 优缺点：
    - 优点：公平，每个进程都有机会运行；适合分时系统
    - 缺点：平均周转时间通常比 SJF 长；上下文切换有开销

    时间复杂度：O(total_time)，取决于所有进程的总运行时间

    参数:
        processes:    Process 对象列表
        time_quantum: 时间片大小（默认 2 个时间单位）

    返回:
        gantt_chart: [(pid, start_time, end_time), ...] 甘特图数据
    """

    # 按到达时间排序（确保后续按顺序检查新到达的进程）
    processes.sort(key=lambda p: p.arrive_time)

    # 就绪队列 —— 用 deque 实现 O(1) 的队首出队和队尾入队
    queue = deque()

    current_time = 0
    index = 0           # 指向下一个还未加入就绪队列的进程
    completed = 0       # 已完成进程计数器
    n = len(processes)
    gantt_chart = []

    while completed < n:
        # ===== 第一步：把当前时间点之前到达的进程加入就绪队列 =====
        while (
            index < n
            and processes[index].arrive_time <= current_time
        ):
            queue.append(processes[index])
            index += 1

        # ===== 第二步：如果就绪队列为空，CPU 空转 =====
        if not queue:
            current_time += 1
            continue

        # ===== 第三步：从队列头部取出一个进程运行 =====
        process = queue.popleft()

        # 记录首次运行时间（用于计算等待时间等）
        if process.start_time is None:
            process.start_time = current_time

        # 实际运行时间 = min(时间片, 剩余运行时间)
        run_time = min(time_quantum, process.remaining_time)

        start = current_time
        current_time += run_time
        end = current_time

        process.remaining_time -= run_time

        gantt_chart.append(
            (
                process.pid,
                start,
                end,
            )
        )

        # ===== 第四步：运行期间可能有新进程到达，加入队列 =====
        while (
            index < n
            and processes[index].arrive_time <= current_time
        ):
            queue.append(processes[index])
            index += 1

        # ===== 第五步：判断进程是否完成 =====
        if process.remaining_time > 0:
            # 未完成 → 重新加入就绪队列末尾
            queue.append(process)
        else:
            # 已完成 → 记录完成时间，计算各项指标
            process.finish_time = current_time
            process.calculate_metrics()
            completed += 1

    return gantt_chart