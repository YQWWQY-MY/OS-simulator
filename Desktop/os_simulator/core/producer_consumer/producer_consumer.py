import time
import threading


class ProducerConsumerSimulator:
    """
    生产者-消费者同步模拟器

    并发编程的核心问题（老师必问——为什么需要同步？）：
    - 生产者往缓冲区放产品，消费者从缓冲区取产品
    - 如果不同步，可能出现种族条件（Race Condition）：
      两个线程同时修改缓冲区指针，导致数据错乱或丢失

    使用的同步原语（三个关键机制）：
    1. mutex（互斥锁）      → 保护缓冲区临界区，同一时刻只有一个线程访问
    2. empty（空位信号量）   → 初值 = 缓冲区大小，生产者 P(empty) 等待空位，
                                消费者 V(empty) 释放空位
    3. full（满位信号量）    → 初值 = 0，消费者 P(full) 等待有产品可取，
                                生产者 V(full) 通知有新货

    特色需求（本项目特有）：
    —— 消费者需要"连续取 n 个产品"后才释放 consume_lock，
       其他消费者在此期间不能取产品。
       这是用额外的一把锁 consume_lock 来实现的。

    参数说明：
    - buffer_size:     缓冲区容量（默认 5）
    - num_producers:   生产者线程数
    - num_consumers:   消费者线程数
    - produce_speed:   生产速度（每秒生产几个）
    - consume_speed:   消费速度（每秒消费几个）
    - continuous_n:    消费者连续取产品个数
    - total_items:     总共要生产的产品数
    """

    def __init__(self, buffer_size=5, num_producers=2, num_consumers=2,
                 produce_speed=1, consume_speed=1, continuous_n=2, total_items=10):
        self.buffer_size = buffer_size
        self.num_producers = num_producers
        self.num_consumers = num_consumers
        self.produce_speed = produce_speed
        self.consume_speed = consume_speed
        self.continuous_n = continuous_n       # 连续消费个数 n
        self.total_items = total_items

        # 缓冲区：用列表模拟环形缓冲区
        self.buffer = [None] * buffer_size
        self.buffer_status = ['empty'] * buffer_size
        self.in_ptr = 0         # 生产者放入指针（环形）
        self.out_ptr = 0        # 消费者取出指针（环形）
        self.count = 0          # 当前缓冲区内产品数
        self.produced_count = 0
        self.consumed_count = 0

        self.timeline = []      # 事件时间线（每条事件供前端展示）

        # ===== 三大同步原语 =====
        self.mutex = threading.Lock()                # 互斥锁：保护临界区
        self.empty = threading.Semaphore(buffer_size) # 空位数信号量，初值 = buffer_size
        self.full = threading.Semaphore(0)            # 产品数信号量，初值 = 0（缓冲区空）

        # 连续消费锁：确保一个消费者连续取 n 个产品时，其他消费者不能插队
        self.consume_lock = threading.Lock()

    def _add_event(self, event_type, message, buffer_snapshot=None):
        """记录一条事件到时间线，供前端动画展示"""
        if buffer_snapshot is None:
            buffer_snapshot = list(self.buffer)
        self.timeline.append({
            'type': event_type,
            'message': message,
            'buffer': buffer_snapshot,
            'count': self.count,
            'produced': self.produced_count,
            'consumed': self.consumed_count
        })

    def producer(self, producer_id):
        """
        生产者线程函数

        流程（经典 PV 操作顺序——老师会问"为什么先 P(empty) 再 P(mutex)"？）：
        1. 生产产品（sleep 模拟耗时）
        2. P(empty)   —— 等待有空位（在 mutex 外面 wait，避免死锁）
        3. P(mutex)   —— 获取互斥访问权
        4. 把产品放入缓冲区（临界区操作）
        5. V(mutex)   —— 释放互斥锁
        6. V(full)    —— 通知有空位可取（在 mutex 外面 signal，提高并发度）
        """
        while self.produced_count < self.total_items:
            time.sleep(1.0 / self.produce_speed)     # 模拟生产耗时

            item = f"P{producer_id}-{self.produced_count + 1}"

            # P 操作：等待空位
            self.empty.acquire()

            # 进入临界区
            with self.mutex:
                # 放入产品（环形缓冲区的写操作）
                self.buffer[self.in_ptr] = item
                self.buffer_status[self.in_ptr] = 'full'
                self.in_ptr = (self.in_ptr + 1) % self.buffer_size
                self.count += 1
                self.produced_count += 1
                self._add_event('produce', f"生产者{producer_id} 放入: {item}")

                if self.produced_count >= self.total_items:
                    self.full.release()     # 确保消费者可以最终取完
                    break

            # V 操作：通知消费者"有货了"
            self.full.release()

    def consumer(self, consumer_id):
        """
        消费者线程函数

        特殊设计——连续取 n 个产品：
        1. 先用 with self.consume_lock 获取"连续消费权"
        2. 在锁内循环 n 次：
           - P(full) 等待有产品
           - P(mutex) 进入临界区取产品
           - V(mutex) 退出临界区
           - V(empty) 通知有空位
        3. 退出锁，其他消费者才能获取 consume_lock 开始连续消费
        """
        while self.consumed_count < self.total_items:
            time.sleep(1.0 / self.consume_speed)    # 模拟消费耗时

            # 获取连续消费锁 —— 保证我一次取 n 个时没人插队
            with self.consume_lock:
                items_taken = []
                for _ in range(self.continuous_n):
                    if self.consumed_count >= self.total_items:
                        break

                    # P 操作：等待产品
                    self.full.acquire()

                    # 进入临界区
                    with self.mutex:
                        item = self.buffer[self.out_ptr]
                        self.buffer[self.out_ptr] = None
                        self.buffer_status[self.out_ptr] = 'empty'
                        self.out_ptr = (self.out_ptr + 1) % self.buffer_size
                        self.count -= 1
                        self.consumed_count += 1
                        items_taken.append(item)

                        self._add_event('consume',
                                        f"消费者{consumer_id} 取出: {item}"
                                        f" (连续取第{len(items_taken)}个)")

                    # V 操作：释放空位
                    self.empty.release()

            # 连续取完 n 个后短暂休息，让其他消费者有机会获取锁
            time.sleep(0.3)

    def run(self):
        """
        启动所有生产者/消费者线程并等待完成

        返回:
            timeline: 事件时间线列表，每个元素是一次生产/消费事件的记录
        """
        # 重置状态
        self.timeline = []
        self.buffer = [None] * self.buffer_size
        self.buffer_status = ['empty'] * self.buffer_size
        self.in_ptr = 0
        self.out_ptr = 0
        self.count = 0
        self.produced_count = 0
        self.consumed_count = 0

        producers = []
        consumers = []

        # 创建生产者线程
        for i in range(self.num_producers):
            t = threading.Thread(target=self.producer, args=(i + 1,))
            producers.append(t)

        # 创建消费者线程
        for i in range(self.num_consumers):
            t = threading.Thread(target=self.consumer, args=(i + 1,))
            consumers.append(t)

        # 启动所有线程
        for t in producers + consumers:
            t.start()

        # 等待所有消费者完成
        for t in consumers:
            t.join()

        # 确保生产者线程也结束（可能还在 sleep 中）
        for t in producers:
            if t.is_alive():
                t.join(timeout=0.5)

        return self.timeline