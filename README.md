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
