#!/bin/bash
# ============================================================
#  餐饮客户管理系统 - 一键部署脚本
#  使用方法: chmod +x deploy.sh && ./deploy.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "============================================"
echo "   餐饮客户管理系统 - Docker 部署"
echo "============================================"
echo -e "${NC}"

# 1. 检查Docker
echo -e "${YELLOW}[1/5] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose未安装，请先安装Docker Compose${NC}"
    exit 1
fi

COMPOSE_CMD="docker compose"
if ! $COMPOSE_CMD version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi
echo -e "${GREEN}✅ Docker环境正常 (使用: $COMPOSE_CMD)${NC}"

# 2. 获取本机IP
echo -e "${YELLOW}[2/5] 获取本机IP地址...${NC}"
if command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip addr show 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | head -1 | awk '{print $2}' | cut -d/ -f1)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | head -1 | awk '{print $2}')
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="未知（请在系统设置中查看）"
fi
echo -e "${GREEN}✅ 本机IP: $LOCAL_IP${NC}"

# 3. 配置环境变量
echo -e "${YELLOW}[3/5] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# 数据库密码（生产环境请修改）
DB_PASSWORD=postgres

# Django密钥（生产环境请修改为随机字符串）
DJANGO_SECRET_KEY=change-this-in-production-to-random-string

# HTTP端口（如80被占用可改为8080等）
HTTP_PORT=80
EOF
    echo -e "${GREEN}✅ 已创建 .env 配置文件${NC}"
else
    echo -e "${GREEN}✅ .env 配置文件已存在${NC}"
fi

# 4. 构建并启动
echo -e "${YELLOW}[4/5] 构建Docker镜像并启动服务（首次可能需要几分钟）...${NC}"
$COMPOSE_CMD down 2>/dev/null || true
$COMPOSE_CMD up -d --build

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 10

# 检查容器状态
echo ""
$COMPOSE_CMD ps

# 5. 显示访问信息
echo ""
echo -e "${GREEN}"
echo "============================================"
echo "   🎉 部署完成！"
echo "============================================"
echo -e "${NC}"
echo -e "${BLUE}访问地址：${NC}"
echo -e "  📱 本机访问:  ${GREEN}http://localhost${NC}"
echo -e "  🌐 局域网访问: ${GREEN}http://$LOCAL_IP${NC}"
echo ""
echo -e "${BLUE}管理后台：${NC}"
echo -e "  🔧 Admin后台: ${GREEN}http://localhost/admin/${NC}"
echo -e "  🌐 局域网:     ${GREEN}http://$LOCAL_IP/admin/${NC}"
echo ""
echo -e "${BLUE}登录账号：${NC}"
echo -e "  👤 用户名: ${GREEN}admin${NC}"
echo -e "  🔑 密码:   ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}常用命令：${NC}"
echo -e "  查看日志:   $COMPOSE_CMD logs -f django"
echo -e "  停止服务:   $COMPOSE_CMD down"
echo -e "  重启服务:   $COMPOSE_CMD restart"
echo -e "  重新构建:   $COMPOSE_CMD up -d --build"
echo ""
echo -e "${RED}⚠️  生产环境请务必修改 .env 中的密码和密钥！${NC}"
echo ""
