# 🖥️ 操作系统核心算法可视化展示系统

> 根据《操作系统课程设计》B部分（核心功能算法模拟）要求开发  
> Flask Web 应用，包含5大模块的动态可视化模拟

---

## 📁 项目结构

```
os_simulator/
│
├── app.py                              # 🌐 Flask 主应用 (路由层 + API)
│
├── core/                               # 🧠 核心算法层
│   ├── scheduler/                      # 模块1：处理器调度
│   │   ├── fcfs.py                     #   先来先服务 (FCFS)
│   │   ├── rr.py                       #   时间片轮转 (RR，可设置时间片)
│   │   ├── sjf.py                      #   短进程优先 (SJF，抢占式)
│   │   └── hrn.py                      #   最高响应比优先 (HRN)
│   │
│   ├── banker/                         # 模块2：银行家算法
│   │   └── banker.py                   #   安全序列计算 + 资源请求检查
│   │
│   ├── paging/                         # 模块3：页面置换
│   │   ├── fifo.py                     #   先进先出 (FIFO)
│   │   ├── lru.py                      #   最近最久未使用 (LRU)
│   │   └── opt.py                      #   最优置换 (OPT)
│   │
│   ├── disk/                           # 模块4：磁盘调度
│   │   ├── sstf.py                     #   最短寻道时间优先 (SSTF)
│   │   └── scan.py                     #   电梯算法 (SCAN，可设置方向)
│   │
│   └── producer_consumer/              # 模块5：生产者-消费者
│       └── producer_consumer.py        #   信号量同步 + 连续取n个产品
│
├── models/                             # 📊 数据模型层
│   └── process.py                      #   进程数据类 (PID/到达/服务/完成/周转)
│
├── utils/                              # 🔧 工具层
│   └── paging_result.py               #   页面置换结果封装 (内存历史/缺页标记)
│
└── templates/                          # 🎨 前端视图层
    ├── index.html                      #   首页导航 (5模块入口)
    ├── scheduler.html                  #   调度器：甘特图 + 统计表
    ├── banker.html                     #   银行家：矩阵表格 + 安全序列
    ├── page_replacement.html           #   页面置换：内存状态矩阵
    ├── disk_scheduling.html            #   磁盘调度：折线图 + 移动轨迹
    └── producer_consumer.html          #   生产者-消费者：缓冲区动画
```

---

## 🚀 快速启动

### 环境要求
- **Python 3.7+**
- **Flask** (Web框架)

### 安装依赖
```bash
pip install flask
```

### 启动服务
```bash
cd os_simulator
python app.py
```

浏览器打开 **`http://localhost:5000`** 即可访问系统首页。

---

## 🧩 模块详情

### 模块1 — 处理器调度模拟

| 算法 | 代码 | 特性 |
|------|------|------|
| FCFS | `core/scheduler/fcfs.py` | 先来先服务 |
| RR | `core/scheduler/rr.py` | 时间片轮转，时间片可配置(默认2) |
| SJF | `core/scheduler/sjf.py` | 短进程优先，抢占式 |
| HRN | `core/scheduler/hrn.py` | 最高响应比优先 |

**输入**：进程ID、到达时间、服务时间（动态添加）  
**输出**：彩色甘特图 + 完成时间/周转时间/带权周转时间/平均值

**API 端点**: `POST /api/scheduler/run`

---

### 模块2 — 生产者-消费者同步模拟

- 多生产者线程 × 多消费者线程
- 信号量机制：`mutex` + `empty` + `full` + 连续消费锁
- 支持设置：缓冲区大小、生产/消费速度、连续取n个产品数

**可视化**：动态格子展示缓冲区状态（绿色=满 / 灰色=空 / 紫色=占用中）

**API 端点**: `POST /api/producer_consumer/run`

---

### 模块3 — 银行家算法演示

- 死锁避免算法
- 安全状态判断 + 安全序列计算
- 动态请求资源检查（是否可分配 + 分配后是否仍安全）
- 预设经典示例数据

**可视化**：表格展示进程资源矩阵（Max/Allocation/Need/Available）+ 安全序列步骤条

**API 端点**: 
- `GET /api/banker/example` — 加载示例数据
- `POST /api/banker/check` — 检查安全状态
- `POST /api/banker/check_request` — 检查资源请求

---

### 模块4 — 页面置换算法模拟

| 算法 | 代码 | 特性 |
|------|------|------|
| OPT | `core/paging/opt.py` | 最优置换（理论最优） |
| LRU | `core/paging/lru.py` | 最近最久未使用 |
| FIFO | `core/paging/fifo.py` | 先进先出 |

**输入**：页面引用序列 + 内存物理块数（支持随机生成）  
**输出**：缺页次数/缺页率 + 内存状态矩阵（红框高亮缺页 + 蓝框命中）

**API 端点**: `POST /api/page_replacement/run`

---

### 模块5 — 磁盘移臂调度模拟

| 算法 | 代码 | 特性 |
|------|------|------|
| SSTF | `core/disk/sstf.py` | 最短寻道时间优先 |
| SCAN | `core/disk/scan.py` | 电梯算法，支持 Up/Down 方向 |

**输入**：磁道请求序列 + 初始磁头位置  
**输出**：响应顺序 + 总寻道距离 + CSS磁头移动动画轨迹图

**API 端点**: `POST /api/disk_scheduling/run`

---

## 🔧 架构设计

```
┌─────────────────────────────────────────────────┐
│                浏览器 (Browser)                   │
│    Chart.js / Canvas / CSS Animation             │
└──────────────┬──────────────────────────────────┘
               │ HTTP JSON / Template
┌──────────────▼──────────────────────────────────┐
│           app.py (Flask Web层)                    │
│  路由: /scheduler /banker /page_replacement ...  │
│  API: 参数解析 → 算法调用 → JSON返回             │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│           core/ (算法层)                          │
│  纯函数设计，无UI依赖，可独立测试                  │
│  输入: 参数列表    输出: 结果字典/对象            │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│        models/ + utils/ (支撑层)                  │
│  数据类: Process / PagingResult                  │
└─────────────────────────────────────────────────┘
```

**设计原则**：
- **算法与UI分离**：`core/` 中所有算法均为纯Python函数，不依赖Flask或任何UI框架
- **前后端分离**：前端通过Fetch API调用后端JSON接口，渲染由Chart.js完成
- **可测试性**：每个算法模块可在命令行单独运行测试

---

## 📝 课程要求对照

| B部分要求模块 | 实现状态 | 对应代码 |
|-------------|---------|---------|
| 处理器调度 (FCFS, RR, SJF, HRN) | ✅ 4算法 | `core/scheduler/` |
| 生产者-消费者同步 (信号量+连续n个) | ✅ 完整 | `core/producer_consumer/` |
| 银行家算法 (安全序列+请求检查) | ✅ 完整 | `core/banker/` |
| 页面置换 (OPT, LRU, FIFO) | ✅ 3算法 | `core/paging/` |
| 磁盘移臂调度 (SSTF, SCAN) | ✅ 2算法 | `core/disk/` |
| 可视化界面 (Web页面) | ✅ 6页面 | `templates/` |
| 可执行程序 | ✅ Python/Flask | `app.py` |

---

## 📄 许可证

本项目为《操作系统课程设计》作业项目。
