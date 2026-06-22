def scan_disk(requests, initial_position, direction='up'):
    """
    SCAN（电梯算法）磁盘调度算法

    算法原理（老师常问——为什么叫"电梯算法"？）：
    —— 磁头像电梯一样沿一个方向移动到最远的请求处，
       到达该方向最边缘后折返，沿相反方向继续服务。
       这样保证了"一个方向上的请求都被服务完"，
       不像 SSTF 那样可能来回跳导致某些请求饿死。

    两个版本的区别：
    - direction='up'   → 磁头向磁道号增大方向移动（先扫右边，折返后扫左边）
    - direction='down' → 磁头向磁道号减小方向移动（先扫左边，折返后扫右边）

    与 SSTF 的关系：
    —— SCAN 解决了 SSTF 的饥饿问题：磁头在一个方向走到尽头后
       必然会回头处理另一端的请求，远处请求不会永久被跳过。

    SCAN 的变种（老师可能扩展问）：
    - C-SCAN（循环扫描）：磁头移到一端后立即跳到另一端开始，
      只在一个方向服务
    - LOOK / C-LOOK：到最远请求就折返，而不是到物理边界

    参数:
        requests:         磁道请求序列
        initial_position: 磁头初始位置
        direction:        'up'（向大磁道号）或 'down'（向小磁道号）

    返回:
        dict: {
            'sequence':       服务顺序列表
            'total_distance': 磁头移动总距离
            'movements':      每次移动的 {from, to, distance}
            'direction':      方向
        }
    """
    remaining = sorted(requests)     # 排序后方便划分"左边"和"右边"
    current = initial_position
    sequence = []
    total_distance = 0
    movements = []

    if direction == 'up':
        # direction='up' → 先服务 >= 当前磁道的请求（向右），再折返服务 < 当前磁道的（向左）
        greater = [r for r in remaining if r >= current]
        lesser = sorted([r for r in remaining if r < current], reverse=True)

        # 向右扫描
        for r in greater:
            distance = abs(r - current)
            total_distance += distance
            sequence.append(r)
            movements.append({
                'from': current,
                'to': r,
                'distance': distance
            })
            current = r

        # 到最右端后折返，向左扫描
        for r in lesser:
            distance = abs(r - current)
            total_distance += distance
            sequence.append(r)
            movements.append({
                'from': current,
                'to': r,
                'distance': distance
            })
            current = r
    else:
        # direction='down' → 先服务 <= 当前磁道的请求（向左），再折返服务 > 当前磁道的（向右）
        lesser = sorted([r for r in remaining if r <= current], reverse=True)
        greater = sorted([r for r in remaining if r > current])

        # 向左扫描
        for r in lesser:
            distance = abs(r - current)
            total_distance += distance
            sequence.append(r)
            movements.append({
                'from': current,
                'to': r,
                'distance': distance
            })
            current = r

        # 到最左端后折返，向右扫描
        for r in greater:
            distance = abs(r - current)
            total_distance += distance
            sequence.append(r)
            movements.append({
                'from': current,
                'to': r,
                'distance': distance
            })
            current = r

    return {
        'sequence': sequence,
        'total_distance': total_distance,
        'movements': movements,
        'direction': direction
    }