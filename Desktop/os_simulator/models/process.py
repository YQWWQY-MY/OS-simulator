class Process:
    """
    进程控制块（PCB）数据模型

    每个字段的含义（面试常问）：
    - pid:             进程唯一标识符
    - arrive_time:     到达时间，模拟进程何时进入就绪队列
    - burst_time:      服务时间（CPU 突发时间），进程总共需要运行多少个时间单位
    - remaining_time:  剩余运行时间，在 RR/SJF 抢占式中每运行一个时间片就递减
    - start_time:      首次获得 CPU 的时间点（用于计算等待时间等）
    - finish_time:     进程运行结束的时间点
    - turnaround_time: 周转时间 = 完成时间 - 到达时间
    - weighted_turnaround_time: 带权周转时间 = 周转时间 / 服务时间（越小越好，表示等待比例低）
    """

    def __init__(self, pid, arrive_time, burst_time):
        self.pid = pid
        self.arrive_time = arrive_time
        self.burst_time = burst_time

        # 初始化剩余时间为服务时间，后续在调度算法中被逐步扣减
        self.remaining_time = burst_time

        # 以下字段在调度完成后由 calculate_metrics() 填充
        self.start_time = None
        self.finish_time = None
        self.turnaround_time = None
        self.weighted_turnaround_time = None

    def calculate_metrics(self):
        """
        在进程完成后调用，计算周转时间和带权周转时间。
        周转时间反映"从提交到完成的总等待+执行时间"，
        带权周转时间反映"每单位服务时间对应的周转时间"——值越接近1越好。
        """
        self.turnaround_time = self.finish_time - self.arrive_time
        self.weighted_turnaround_time = (
            self.turnaround_time / self.burst_time
        )

    def __repr__(self):
        return (
            f"Process({self.pid}, "
            f"arrive={self.arrive_time}, "
            f"burst={self.burst_time})"
        )