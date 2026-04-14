# Build stage - 前端构建
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Final stage
FROM python:3.10-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码（项目根目录结构，无 backend/ 子目录）
COPY config/ ./config/
COPY common/ ./common/
COPY customers/ ./customers/
COPY dining/ ./dining/
COPY reservations/ ./reservations/
COPY reminders/ ./reminders/
COPY manage.py .

# 复制前端构建产物
COPY --from=frontend-build /app/frontend/dist ./static/frontend/

# 复制入口脚本
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 在构建阶段收集静态文件（避免每次启动重新收集导致hash变化）
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
