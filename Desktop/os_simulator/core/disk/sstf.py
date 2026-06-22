def sstf(requests, initial_position):
    """
    SSTF（Shortest Seek Time First，最短寻道时间优先）磁盘调度算法

    算法原理（老师常问）：
    —— 每次选择"距离当前磁头位置最近"的请求来服务。
       相当于贪心策略：总是挑最近的去。

    与调度算法的对比：
    —— SSTF 在磁盘调度中的地位，类似于 SJF 在 CPU 调度中的地位：
       短请求优先，减少平均寻道时间。

    特点 / 优缺点：
    - 优点：平均寻道时间较短，吞吐量较高
    - 缺点：
      * 饥饿问题 —— 如果不断有离磁头近的新请求加入，
        远处的请求可能永远得不到服务
      * 不是最优解（贪心 ≠ 全局最优）

    为什么 SCAN 要解决 SSTF 的饥饿？
    —— SCAN 强制磁头沿固定方向移动，保证了每个请求最终都会被访问到。

    参数:
        requests:         磁道请求序列，如 [98, 183, 37, 122, 14, 124, 65, 67]
        initial_position: 磁头初始位置

    返回:
        dict: {
            'sequence':       服务顺序列表
            'total_distance': 磁头移动总距离
            'movements':      每次移动的 {from, to, distance}
        }
    """
    remaining = list(requests)      # 尚未服务的请求（每次服务一个就从中移除）
    current = initial_position
    sequence = []
    total_distance = 0
    movements = []

    while remaining:
        # 贪心选择：找距离当前磁头位置最近的请求
        closest = min(remaining, key=lambda x: abs(x - current))
        distance = abs(closest - current)
        total_distance += distance
        sequence.append(closest)
        movements.append({
            'from': current,
            'to': closest,
            'distance': distance
        })
        current = closest           # 磁头移动到该位置
        remaining.remove(closest)   # 服务完毕，从等待列表中移除

    return {
        'sequence': sequence,
        'total_distance': total_distance,
        'movements': movements
    }