"""
Flask 主程序 —— OS 核心算法模拟系统的 Web 入口

架构说明：
- 本项目采用"前后端分离"架构：
  * 后端（Flask + core/ 算法模块）负责算法计算
  * 前端（HTML + CSS + JS）负责可视化展示
- 用户在前端页面填写参数 → 前端发 AJAX 请求到 /api/* 接口
  → 后端调用 core/ 模块计算 → 返回 JSON 结果 → 前端渲染甘特图/表格/SVG

路由结构：
  页面路由（返回 HTML）：
  - GET  /                    → 首页（模块导航卡片）
  - GET  /scheduler           → 处理器调度模拟页
  - GET  /producer_consumer   → 生产者-消费者同步页
  - GET  /banker              → 银行家算法页
  - GET  /page_replacement    → 页面置换算法页
  - GET  /disk_scheduling     → 磁盘调度算法页

  API 路由（返回 JSON）：
  - POST /api/scheduler/run            → 运行调度算法
  - POST /api/producer_consumer/run    → 运行生产者-消费者模拟
  - GET  /api/banker/example           → 获取银行家示例数据
  - POST /api/banker/check_request     → 检查资源请求
  - POST /api/banker/check             → 检查系统安全性
  - POST /api/page_replacement/run     → 运行页面置换算法
  - POST /api/disk_scheduling/run      → 运行磁盘调度算法
"""

import json
import threading
import time
from flask import Flask, render_template, request, jsonify

# 导入各功能模块的算法实现
from core.scheduler.fcfs import fcfs
from core.scheduler.rr import rr
from core.scheduler.sjf import sjf
from core.scheduler.hrn import hrn
from core.banker.banker import BankerAlgorithm
from core.paging.fifo import fifo_page_replacement
from core.paging.lru import lru_page_replacement
from core.paging.opt import opt_page_replacement
from core.disk.sstf import sstf
from core.disk.scan import scan_disk
from core.producer_consumer.producer_consumer import ProducerConsumerSimulator

app = Flask(__name__)


# ==================== 处理器调度模块 ====================
# 支持四种算法：FCFS / RR / SJF(抢占式SRTF) / HRN
# 输入：进程列表（pid, 到达时间, 服务时间）
# 输出：甘特图、各进程指标、平均周转时间、平均带权周转时间

@app.route('/')
def index():
    """首页：展示 5 个模块的导航卡片"""
    return render_template('index.html')


@app.route('/scheduler')
def scheduler_page():
    """处理器调度页面"""
    return render_template('scheduler.html')


@app.route('/api/scheduler/run', methods=['POST'])
def run_scheduler():
    """
    处理器调度 API 接口

    接收前端 JSON：
    {
        "algorithm": "FCFS" | "RR" | "SJF" | "HRN",
        "processes": [{pid, arrive_time, burst_time}, ...],
        "time_quantum": 2        // 仅 RR 时有效
    }

    返回 JSON：
    {
        "gantt": [{pid, start, end}, ...],
        "results": [{pid, arrive_time, burst_time, finish_time,
                      turnaround_time, weighted_turnaround_time}, ...],
        "avg_turnaround": float,
        "avg_weighted": float
    }
    """
    data = request.json
    algorithm = data.get('algorithm', '').upper()
    processes_data = data.get('processes', [])
    time_quantum = data.get('time_quantum', 2)

    # 将前端传来的字典列表转为 Process 对象
    from models.process import Process
    processes = [Process(p['pid'], p['arrive_time'], p['burst_time'])
                 for p in processes_data]

    try:
        # 根据算法选择调用对应的实现
        if algorithm == 'FCFS':
            gantt = fcfs(processes)
        elif algorithm == 'RR':
            gantt = rr(processes, time_quantum)
        elif algorithm == 'SJF':
            gantt = sjf(processes)
        elif algorithm == 'HRN':
            gantt = hrn(processes)
        else:
            return jsonify({'error': '未知算法'}), 400

        # 组装每个进程的结果
        results = []
        for p in processes:
            results.append({
                'pid': p.pid,
                'arrive_time': p.arrive_time,
                'burst_time': p.burst_time,
                'start_time': p.start_time,
                'finish_time': p.finish_time,
                'turnaround_time': p.turnaround_time,
                'weighted_turnaround_time':
                    round(p.weighted_turnaround_time, 2)
                    if p.weighted_turnaround_time else None
            })

        # 甘特图数据格式化为前端可直接渲染的结构
        gantt_data = [{'pid': g[0], 'start': g[1], 'end': g[2]}
                       for g in gantt]

        # 计算平均指标
        avg_turnaround = (sum(r['turnaround_time'] for r in results)
                          / len(results)) if results else 0
        avg_weighted = (sum(r['weighted_turnaround_time']
                            for r in results) / len(results)) if results else 0

        return jsonify({
            'gantt': gantt_data,
            'results': results,
            'avg_turnaround': round(avg_turnaround, 2),
            'avg_weighted': round(avg_weighted, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 生产者-消费者模块 ====================
# 多线程模拟：信号量 + 互斥锁实现缓冲区同步
# 特色：消费者可连续取 n 个产品

@app.route('/producer_consumer')
def producer_consumer_page():
    """生产者-消费者页面"""
    return render_template('producer_consumer.html')


@app.route('/api/producer_consumer/run', methods=['POST'])
def run_producer_consumer():
    """
    生产者-消费者模拟 API 接口

    接收前端 JSON：
    {
        "buffer_size": 5,
        "num_producers": 2,
        "num_consumers": 2,
        "produce_speed": 1,
        "consume_speed": 1,
        "continuous_n": 2,
        "total_items": 10
    }

    返回 JSON：
    {
        "timeline": [{type, message, buffer, count, produced, consumed}, ...],
        "buffer_size": int,
        "total_items": int
    }
    """
    data = request.json
    buffer_size = data.get('buffer_size', 5)
    num_producers = data.get('num_producers', 2)
    num_consumers = data.get('num_consumers', 2)
    produce_speed = data.get('produce_speed', 1)
    consume_speed = data.get('consume_speed', 1)
    continuous_n = data.get('continuous_n', 2)
    total_items = data.get('total_items', 10)

    sim = ProducerConsumerSimulator(
        buffer_size=buffer_size,
        num_producers=num_producers,
        num_consumers=num_consumers,
        produce_speed=produce_speed,
        consume_speed=consume_speed,
        continuous_n=continuous_n,
        total_items=total_items
    )

    timeline = sim.run()

    return jsonify({
        'timeline': timeline,
        'buffer_size': buffer_size,
        'total_items': total_items
    })


# ==================== 银行家算法模块 ====================
# 安全性检查 + 资源请求试探分配
# 经典示例数据来自操作系统教材

@app.route('/banker')
def banker_page():
    """银行家算法页面"""
    return render_template('banker.html')


@app.route('/api/banker/example', methods=['GET'])
def banker_example():
    """
    加载银行家算法经典示例数据（来自操作系统教材的经典例题）

    返回的系统状态：
    - Available:  [3, 3, 2]
    - Max Demand: 5 个进程的最大需求矩阵
    - Allocation: 当前已分配矩阵
    - Need:       自动计算 = Max - Allocation
    - Safety Seq: 安全序列
    """
    available = [3, 3, 2]
    max_demand = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
    banker = BankerAlgorithm(available, max_demand, allocation)
    is_safe, safety_seq = banker.is_safe_state()
    return jsonify({
        'available': available,
        'max_demand': max_demand,
        'allocation': allocation,
        'need': banker.need,
        'is_safe': is_safe,
        'safety_sequence': safety_seq if safety_seq else [],
        'safe_sequence': safety_seq if safety_seq else []
    })


@app.route('/api/banker/check_request', methods=['POST'])
def banker_check_request():
    """
    检查进程资源请求 API

    三步检查 + 试探分配 + 安全性检查：
    1. request <= Need ？（不超过最大需求）
    2. request <= Available？（不超过可用资源）
    3. 试探分配 → is_safe_state() → 安全就批准，不安全就回滚
    """
    data = request.json
    process_id = data.get('process_id', 0)
    request_resources = data.get('request', [])
    state = data.get('state', {})

    available = state.get('available', [3, 3, 2])
    max_demand = state.get('max_demand',
                           [[7, 5, 3], [3, 2, 2], [9, 0, 2],
                            [2, 2, 2], [4, 3, 3]])
    allocation = state.get('allocation',
                           [[0, 1, 0], [2, 0, 0], [3, 0, 2],
                            [2, 1, 1], [0, 0, 2]])

    banker = BankerAlgorithm(available, max_demand, allocation)

    can_allocate, message, safety_seq = banker.request_resources(
        process_id, request_resources)

    return jsonify({
        'granted': can_allocate,
        'reason': message if not can_allocate else '',
        'safe_sequence': safety_seq if safety_seq else [],
        'safety_sequence': safety_seq if safety_seq else [],
        'available': banker.available,
        'allocation': banker.allocation,
        'need': banker.need
    })


@app.route('/api/banker/check', methods=['POST'])
def check_banker():
    """
    综合银行家 API：既可做安全性检查，也可做资源请求检查
    """
    data = request.json
    available = data.get('available', [])
    max_demand = data.get('max_demand', [])
    allocation = data.get('allocation', [])
    request_resources = data.get('request', None)
    request_process = data.get('request_process', None)

    banker = BankerAlgorithm(available, max_demand, allocation)

    if request_resources is not None and request_process is not None:
        # 带请求的资源分配检查
        can_allocate, message, safety_seq = banker.request_resources(
            request_process, request_resources)
        return jsonify({
            'can_allocate': can_allocate,
            'message': message,
            'safety_sequence': safety_seq,
            'need_matrix': banker.need,
            'available': banker.available,
            'allocation': banker.allocation
        })
    else:
        # 仅安全性检查
        is_safe, safety_seq = banker.is_safe_state()
        return jsonify({
            'is_safe': is_safe,
            'safety_sequence': safety_seq,
            'need_matrix': banker.need,
            'available': banker.available,
            'allocation': banker.allocation
        })


# ==================== 页面置换模块 ====================
# 支持三种经典算法：FIFO / LRU / OPT（最优置换作为对照基准）

@app.route('/page_replacement')
def page_replacement_page():
    """页面置换算法页面"""
    return render_template('page_replacement.html')


@app.route('/api/page_replacement/run', methods=['POST'])
def run_page_replacement():
    """
    页面置换算法 API 接口

    接收前端 JSON：
    {
        "algorithm": "FIFO" | "LRU" | "OPT",
        "reference_string": [1, 2, 3, 1, 4, 2, ...],
        "frame_size": 3
    }

    返回 JSON：
    {
        "steps": [{current_page, memory_blocks, page_fault, replaced}, ...],
        "page_faults": int,
        "total_references": int,
        "fault_rate": float
    }
    """
    data = request.json
    algorithm = data.get('algorithm', '').upper()
    reference_string = data.get('reference_string', [])
    frame_size = data.get('frame_size', 3)

    try:
        if algorithm == 'FIFO':
            result = fifo_page_replacement(reference_string, frame_size)
        elif algorithm == 'LRU':
            result = lru_page_replacement(reference_string, frame_size)
        elif algorithm == 'OPT':
            result = opt_page_replacement(reference_string, frame_size)
        else:
            return jsonify({'error': '未知算法'}), 400

        total_references = len(reference_string)
        page_fault_rate = (round(result.page_faults / total_references * 100, 2)
                           if total_references else 0)

        # 构建前端期望的 steps 格式：每步的页面访问结果
        steps = []
        for i, ref_page in enumerate(reference_string):
            mem_full = (list(result.memory_history[i])
                        if i < len(result.memory_history) else [])
            # 用 None 填充不足 frame_size 的槽位（前端需要固定列数）
            while len(mem_full) < frame_size:
                mem_full.append(None)
            page_fault = (result.page_fault_flags[i]
                          if i < len(result.page_fault_flags) else False)
            replaced = (result.replaced_pages[i]
                        if i < len(result.replaced_pages) else None)
            steps.append({
                'current_page': ref_page,
                'memory_blocks': mem_full,
                'memory_state': mem_full,
                'page_fault': page_fault,
                'replaced': replaced
            })

        return jsonify({
            'steps': steps,
            'page_faults': result.page_faults,
            'total_references': total_references,
            'fault_rate': page_fault_rate,
            'page_fault_rate': page_fault_rate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 磁盘调度模块 ====================
# 支持 SSTF（最短寻道时间优先）和 SCAN（电梯算法）

@app.route('/disk_scheduling')
def disk_scheduling_page():
    """磁盘调度算法页面"""
    return render_template('disk_scheduling.html')


@app.route('/api/disk_scheduling/run', methods=['POST'])
def run_disk_scheduling():
    """
    磁盘调度算法 API 接口

    接收前端 JSON：
    {
        "algorithm": "SSTF" | "SCAN",
        "requests": [98, 183, 37, 122, ...],
        "initial_position": 50,
        "direction": "up" | "down"     // 仅 SCAN 时有效
    }

    返回 JSON：
    {
        "sequence": [磁道服务顺序],
        "total_distance": 总寻道距离,
        "movements": [{from, to, distance}, ...],
        "initial_position": int,
        "direction": "up" | "down"
    }
    """
    data = request.json
    algorithm = data.get('algorithm', '').upper()
    requests = data.get('requests', [])
    initial_position = data.get('initial_position', 50)
    direction = data.get('direction', 'up')

    try:
        if algorithm == 'SSTF':
            result = sstf(requests, initial_position)
        elif algorithm == 'SCAN':
            result = scan_disk(requests, initial_position, direction)
        else:
            return jsonify({'error': '未知算法'}), 400

        return jsonify({
            'sequence': result['sequence'],
            'total_distance': result['total_distance'],
            'movements': result['movements'],
            'initial_position': initial_position,
            'direction': result.get('direction', direction)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)


print("服务器已启动，访问 http://localhost:5000 来使用操作系统模拟器")