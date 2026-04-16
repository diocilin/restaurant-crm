# 🍽️ 大河有鱼客户管理系统 (Restaurant CRM)

一款专为连锁餐饮店设计的私域客户管理系统，帮助门店高效管理客户信息、追踪就餐记录、处理预订，并在重要日期自动提醒。

本项目由 **[TRAE SOLO](https://solo.ai)** 全程开发完成。

## 🤖 关于开发者

**TRAE SOLO** 是一款由 SOLO AI 推出的智能编程助手，具备完整的全栈开发能力。本项目从需求分析、架构设计、前后端编码到部署配置，均由 TRAE SOLO 独立完成，包括：

- **后端开发** — Django 5.x + DRF RESTful API 设计、数据模型设计、业务逻辑实现
- **前端开发** — Vue 3 + Element Plus 组件化开发、响应式布局、多端适配
- **数据库设计** — PostgreSQL 数据模型、迁移管理、查询优化
- **部署运维** — Docker Compose 多容器编排、Nginx 反向代理、CI/CD 配置
- **项目管理** — 需求迭代、Bug 修复、版本管理、文档编写

> TRAE SOLO 能够理解自然语言需求，自动规划任务，编写高质量代码，并在开发过程中持续迭代优化。本项目是其全栈开发能力的完整体现。

## ✨ 功能特性

### 客户管理
- 客户信息录入、标签分类（口味偏好/忌口/环境偏好等）
- 搜索筛选、客户画像（消费统计、就餐频率、平均客单价）
- 客户等级（普通/VIP/SVIP）

### 就餐记录
- 消费记录追踪、满意度评分、消费统计
- 预订到店自动生成就餐记录，支持编辑消费金额和备注
- **美团收银数据导入** — 上传美团管家导出的Excel文件，自动解析订单明细和菜品明细
- **智能客户匹配** — 通过桌号+日期自动匹配CRM预订记录，关联客户；未匹配的记录标记为散客
- **手动客户匹配** — 散客记录支持编辑时手动搜索客户姓名/手机号进行关联
- **防重复导入** — 相同订单号自动跳过，支持多次导入增量更新

### 预订管理
- 在线预订、状态流转（待确认→已确认→已到店/已取消/未到店）
- **座位资源管理** — 每个门店独立配置包间（自由命名）和大堂桌数（自动编号 01, 02, 03...）
- **时间段翻台机制** — 座位锁定为预订时间前1小时至后2小时，超出时段可翻台再次预订
- **多座位单预订** — 一条预订可同时选择多个大堂桌号和多个包间
- **座位冲突检测** — 基于时间窗口的智能冲突检测，已占用座位灰色不可选
- 到店自动生成就餐记录
- 取消的预订从今日预订中隐藏，保留在预订记录中

### 数据看板
- 首页统计概览（客户总数、本周新增、今日预订、待处理提醒）
- 即将到来的生日/纪念日
- 今日预订列表（显示客户电话、座位信息）
- **未来10天预订概览** — 日历式展示，按门店统计包间和大堂的预订/剩余数量，颜色区分占用率，悬浮显示具体预订座位详情

### 菜品分析
- **菜品销量排名** — 基于美团导入数据，按销售额降序展示菜品排名TOP50
- **销售占比** — 每个菜品的销售额占总销售额的百分比，进度条可视化
- **30天趋势图** — 近30天每日订单数和销售额柱状图
- **多维筛选** — 按门店、日期范围筛选分析数据

### 重要日期提醒
- 生日/纪念日自动扫描（Celery 定时任务）
- 手动创建提醒、处理/忽略

### 多端适配
- **桌面端** — 左侧边栏导航，适合电脑操作
- **手机端** — 底部 Tab 图标导航，自动识别设备切换专属界面
- **平板端** — 自适应布局

### Django Admin 后台
- 开箱即用的管理后台，支持批量操作
- 门店管理（内联管理包间）、座位区域管理
- 预订管理（按座位类型/状态筛选）
- 客户管理（标签内联编辑）

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vue Router + Axios |
| 后端 | Django 5.x + Django REST Framework |
| 数据库 | PostgreSQL（开发环境兼容 SQLite） |
| 定时任务 | Celery + Redis |
| 部署 | Docker Compose（WhiteNoise 静态文件服务） |

## 📦 项目结构

```
restaurant-crm/
├── config/                     # 项目配置（settings, urls, celery）
├── customers/                  # 客户管理模块（Store, Tag, Customer, TableArea）
├── dining/                     # 就餐记录模块（含Excel导入引擎）
├── reservations/               # 预订管理模块
├── reminders/                  # 提醒管理模块
├── common/                     # 公共模块（分页、权限）
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/                # API 请求封装
│       ├── router/             # 路由配置（设备检测自动切换Layout）
│       ├── views/              # 页面组件（Layout + MobileLayout）
│       └── styles/             # 全局样式
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 多阶段构建
├── requirements.txt            # Python 依赖
└── entrypoint.sh               # 容器启动脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+（生产环境）
- Redis 7+（定时任务）

### 开发模式

```bash
# 1. 克隆项目
git clone https://github.com/your-username/restaurant-crm.git
cd restaurant-crm

# 2. 后端安装与启动
pip install -r requirements.txt
python manage.py migrate
python manage.py load_initial_data    # 加载初始门店和标签数据
python manage.py createsuperuser      # 创建管理员账号
python manage.py runserver 8000

# 3. 前端安装与启动
cd frontend
npm install
npm run dev

# 4. 访问系统
# 前端：http://localhost:5173
# 后台：http://localhost:8000/admin
```

### Docker 部署（推荐）

```bash
# 一键启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

部署后访问：
- 前端 + API：`http://<你的IP>`
- Django Admin：`http://<你的IP>/admin`

> Docker 首次启动会自动执行数据库迁移、创建管理员（admin/admin123）、加载初始数据。

## 📖 API 接口

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/token/` | 获取 JWT Token |
| 门店 | `GET /api/customers/stores/` | 门店列表 |
| 标签 | `GET /api/customers/tags/` | 标签列表 |
| 座位区域 | `GET /api/customers/table-areas/` | 包间/大厅列表 |
| 客户 | `GET/POST /api/customers/list/` | 客户列表/创建 |
| 客户 | `GET/PATCH /api/customers/list/{id}/` | 客户详情/更新 |
| 客户统计 | `GET /api/customers/list/stats/` | 客户统计数据 |
| 就餐记录 | `GET/POST /api/dining/records/` | 就餐记录列表/创建 |
| 就餐记录 | `PATCH /api/dining/records/{id}/` | 编辑就餐记录（支持手动匹配客户） |
| 就餐记录 | `POST /api/dining/records/import_excel/` | 导入美团收银Excel |
| 就餐记录 | `GET /api/dining/records/dish_stats/` | 菜品销量统计 |
| 就餐记录 | `GET /api/dining/records/import_logs/` | 导入记录列表 |
| 预订 | `GET/POST /api/reservations/list/` | 预订列表/创建 |
| 预订 | `POST /api/reservations/list/{id}/confirm/` | 确认预订 |
| 预订 | `POST /api/reservations/list/{id}/arrive/` | 标记到店（自动创建就餐记录） |
| 预订 | `POST /api/reservations/list/{id}/cancel/` | 取消预订 |
| 预订 | `GET /api/reservations/list/today/` | 今日预订（排除已取消） |
| 预订 | `GET /api/reservations/list/overview/` | 未来10天预订概览 |
| 预订 | `GET /api/reservations/list/available_seats/` | 查询可用座位 |
| 提醒 | `GET/POST /api/reminders/list/` | 提醒列表/创建 |
| 提醒 | `GET /api/reminders/list/upcoming/` | 即将到来的提醒 |
| 提醒 | `POST /api/reminders/list/{id}/handle/` | 标记已处理 |
| 提醒 | `POST /api/reminders/list/{id}/ignore/` | 标记已忽略 |

## 🔔 预置数据

系统内置以下初始数据，可通过 `python manage.py load_initial_data` 加载：

**门店（3个）：** 总店、分店一、分店二

**标签（18个）：**

| 分类 | 标签 |
|------|------|
| 口味偏好 | 不吃辣、微辣、重口味、清淡、喜欢甜食 |
| 忌口 | 不吃香菜、不吃葱蒜、海鲜过敏、坚果过敏 |
| 环境偏好 | 喜欢靠窗、需要包间、带小孩、需要儿童椅 |
| 消费等级 | 高消费、价格敏感 |
| 其他 | 老客户、企业客户、朋友推荐 |

## 🔧 配置说明

环境变量通过 `.env` 文件或 `docker-compose.yml` 配置：

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# 数据库
DB_ENGINE=django.db.backends.postgresql
DB_NAME=restaurant_crm
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# 跨域
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📋 版本更新

### v1.4（当前版本）

- **美团收银Excel导入** — 上传美团管家导出的"店内订单明细"Excel，自动解析订单明细和菜品明细两个Sheet
- **智能客户匹配** — 通过桌号+日期自动匹配CRM预订记录，关联客户；未匹配的记录标记为散客
- **手动客户匹配** — 就餐记录编辑页面支持搜索客户姓名/手机号，手动关联散客记录
- **菜品分析报表** — 菜品销量排名TOP50、销售占比进度条、近30天趋势图、按门店/日期筛选
- **数据导入管理** — 导入结果展示（成功/跳过/错误）、历史导入记录查看
- **防重复导入** — 相同订单号自动跳过（unique_together约束），支持多次导入增量更新
- **预订编辑功能** — 预订管理操作栏新增编辑按钮，支持修改预订信息
- **数据模型扩展** — DiningRecord新增source（数据来源）和order_no（外部订单号）字段

### v1.3

- **今日预订信息增强** — 首页今日预订列表新增客户电话号码和座位信息列
- **概览悬浮提示** — 未来10天预订概览中，鼠标悬停在座位标签上显示具体预订详情（如"已预订：大河厅、牡丹厅"）
- **概览统计修复** — 修复一条预订选多个座位时只统计为1的BUG，改为按实际座位数量统计
- **后台预订简化** — 移除后台座位选择功能（Django Admin 兼容性问题），新建预订统一使用前端页面操作
- **后台表单优化** — 包间选择改为 `filter_horizontal` 多选框，座位信息区域添加前端操作提示

### v1.2

- **时间段翻台机制** — 座位锁定改为预订时间前1小时至后2小时，超出时段可翻台再次预订
- **多座位单预订** — 一条预订记录可同时选择多个大堂桌号和多个包间，不再拆分为多条记录
- **座位类型同时选择** — 大堂和包间可同时勾选，格子点击多选（前端和后台一致）
- **后台预订座位选择重构** — Django Admin 预订表单改为格子点击多选，AJAX 自动加载可用座位，已占用灰色不可选
- **后台座位冲突检测** — Admin 新建/编辑预订时实时检测时间段冲突
- **Admin 专用座位接口** — 新建 `admin_seats` 内部接口，绕过 JWT 使用 Django Session 认证
- **门店包间数统计修复** — 包间统计和座位查询正确过滤 `area_type='room'`，排除大厅记录
- **客户详情页修复** — 修复基本信息重复显示的 CSS 规则覆盖问题

### v1.1

- **座位资源管理** — 门店可配置包间（自由命名）和大堂桌数（自动编号）
- **预订座位选择** — 新建预订时动态显示可用座位，已占用座位不可再选
- **座位冲突检测** — 同一门店同一天同一座位不可重复预订
- **未来10天预订概览** — 首页看板新增日历式预订概览，颜色区分占用率
- **取消预订优化** — 取消的预订从今日预订中隐藏，保留在预订记录中
- **多端适配** — 手机端底部 Tab 导航，自动识别设备切换专属界面
- **时区修复** — 所有日期计算使用本地时区，修复 UTC 时差问题
- **标签分页修复** — 标签和门店列表不分页，全部返回

### v1.0

- 客户管理（CRUD、标签、搜索筛选、客户画像）
- 就餐记录（CRUD、满意度评分、消费统计）
- 预订管理（状态流转、到店自动生成就餐记录）
- 重要日期提醒（自动扫描、手动创建）
- 首页数据看板
- Django Admin 后台
- Docker Compose 部署

## 📄 License

MIT License
