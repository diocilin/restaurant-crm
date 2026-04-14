# 🍽️ 餐饮客户管理系统 (Restaurant CRM)

一款专为连锁餐饮店设计的私域客户管理系统，帮助门店高效管理客户信息、追踪就餐记录、处理预订，并在重要日期自动提醒。

## ✨ 功能特性

- **客户管理** — 客户信息录入、标签分类（口味偏好/忌口/环境偏好等）、搜索筛选、客户画像
- **就餐记录** — 消费记录追踪、满意度评分、消费统计
- **预订管理** — 在线预订、状态流转（待确认→已确认→已到店）、到店自动生成就餐记录
- **重要日期提醒** — 生日/纪念日自动扫描、手动创建提醒、处理/忽略
- **数据看板** — 首页统计概览、即将到来的生日、今日预订
- **Django Admin** — 开箱即用的管理后台，支持批量操作
- **多门店支持** — 支持多门店数据隔离与管理

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vue Router + Axios |
| 后端 | Django 5.x + Django REST Framework |
| 数据库 | PostgreSQL（开发环境兼容 SQLite） |
| 定时任务 | Celery + Redis |
| 部署 | Docker Compose + Nginx |

## 📦 项目结构

```
restaurant-crm/
├── backend/                    # Django 后端
│   ├── config/                 # 项目配置（settings, urls, celery）
│   ├── customers/              # 客户管理模块
│   ├── dining/                 # 就餐记录模块
│   ├── reservations/           # 预订管理模块
│   ├── reminders/              # 提醒管理模块
│   └── common/                 # 公共模块（分页、权限）
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/                # API 请求封装
│       ├── router/             # 路由配置
│       ├── views/              # 页面组件
│       └── styles/             # 全局样式
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 多阶段构建
├── nginx.conf                  # Nginx 配置
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
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

部署后访问：
- 前端 + API：`http://localhost`
- Django Admin：`http://localhost/admin`

> Docker 首次启动会自动执行数据库迁移、创建管理员（admin/admin123）、加载初始数据。

## 📖 API 接口

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/token/` | 获取 JWT Token |
| 门店 | `GET /api/customers/stores/` | 门店列表 |
| 标签 | `GET /api/customers/tags/` | 标签列表 |
| 客户 | `GET/POST /api/customers/list/` | 客户列表/创建 |
| 客户 | `GET/PATCH /api/customers/list/{id}/` | 客户详情/更新 |
| 客户统计 | `GET /api/customers/list/stats/` | 客户统计数据 |
| 就餐记录 | `GET/POST /api/dining/records/` | 就餐记录列表/创建 |
| 就餐记录 | `PATCH /api/dining/records/{id}/` | 编辑就餐记录 |
| 预订 | `GET/POST /api/reservations/list/` | 预订列表/创建 |
| 预订 | `POST /api/reservations/list/{id}/confirm/` | 确认预订 |
| 预订 | `POST /api/reservations/list/{id}/arrive/` | 标记到店（自动创建就餐记录） |
| 预订 | `POST /api/reservations/list/{id}/cancel/` | 取消预订 |
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

环境变量通过 `.env` 文件配置：

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
DB_HOST=localhost
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# 跨域
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📄 License

MIT License
