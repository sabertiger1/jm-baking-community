#!/bin/bash
# Docker 镜像构建和推送脚本

# 配置 - 请修改为你的信息
DOCKERHUB_USERNAME="YOUR_DOCKERHUB_USERNAME"
IMAGE_NAME="mealie"
VERSION=${1:-latest}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Docker 镜像构建和推送${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 检查是否登录 Docker Hub
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}提示: 未检测到 Docker Hub 登录，请先执行: docker login${NC}"
    read -p "是否现在登录? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login
    else
        echo -e "${RED}取消操作${NC}"
        exit 1
    fi
fi

# 检查配置
if [ "$DOCKERHUB_USERNAME" = "YOUR_DOCKERHUB_USERNAME" ]; then
    echo -e "${RED}错误: 请先修改脚本中的 DOCKERHUB_USERNAME${NC}"
    exit 1
fi

# 构建镜像
echo -e "${GREEN}[1/4] 构建镜像...${NC}"
if docker build -f docker/Dockerfile.fnos -t ${IMAGE_NAME}:${VERSION} --target production .; then
    echo -e "${GREEN}✓ 构建成功${NC}"
else
    echo -e "${RED}✗ 构建失败${NC}"
    exit 1
fi

# 标记镜像
echo -e "${GREEN}[2/4] 标记镜像...${NC}"
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
if [ "$VERSION" != "latest" ]; then
    docker tag ${IMAGE_NAME}:${VERSION} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest
    echo -e "${GREEN}✓ 已标记为 ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION} 和 latest${NC}"
else
    echo -e "${GREEN}✓ 已标记为 ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}${NC}"
fi

# 推送镜像
echo -e "${GREEN}[3/4] 推送镜像...${NC}"
if docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}; then
    echo -e "${GREEN}✓ 推送成功${NC}"
    if [ "$VERSION" != "latest" ]; then
        docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest
        echo -e "${GREEN}✓ latest 标签推送成功${NC}"
    fi
else
    echo -e "${RED}✗ 推送失败${NC}"
    exit 1
fi

# 完成
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "镜像地址："
echo "  ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "  ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
fi
echo ""
echo "在飞牛 NAS 上使用："
echo "  1. 修改 docker/docker-compose.fnos.pull.yml"
echo "  2. 将 YOUR_DOCKERHUB_USERNAME 替换为: ${DOCKERHUB_USERNAME}"
echo "  3. 执行: sudo docker compose -f docker/docker-compose.fnos.pull.yml up -d"
echo ""
