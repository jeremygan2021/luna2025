#!/bin/bash

# =============================================================================
# Docker 全栈部署自动化脚本 (Frontend + Backend + MQTT)
# chmod u+x docker_deplay.sh
# 用法:
#   ./docker_deplay.sh          # 完整构建和部署流程 (默认AMD64架构)
#   ./docker_deplay.sh -amd     # 构建和部署AMD64架构
#   ./docker_deplay.sh -arm     # 构建和部署ARM64架构
#   ./docker_deplay.sh -upload -arm # 仅上传已存在的tar文件并部署
#   ./docker_deplay.sh -upload -amd # 仅上传已存在的tar文件并部署
# =============================================================================

# 配置变量 - 请根据实际情况修改
SERVER_HOST="6.6.6.86"           # 服务器IP地址
SERVER_USER="ubuntu"             # 服务器用户名
SERVER_PASSWORD="qweasdzxc1"     # 服务器密码
SERVER_PORT="22"                 # SSH端口，默认22

# 项目部署目录 (服务器上)
DEPLOY_DIR="/mnt/server/luna_project"

# 镜像信息
APP_IMAGE="luna-app:latest"
    SERVER_IMAGE="luna-server:latest"
MQTT_IMAGE="eclipse-mosquitto:2.0"
TAR_FILE="luna_full_stack.tar"

# 架构相关变量
PLATFORM="linux/amd64"           # 默认架构
ARCH_SUFFIX=""                   # 架构后缀

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    if ! command -v sshpass &> /dev/null; then
        log_error "sshpass 未安装，请先安装 sshpass"
        log_info "macOS: brew install sshpass"
        log_info "Ubuntu: sudo apt-get install sshpass"
        exit 1
    fi
    log_success "依赖检查完成"
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -amd)
                PLATFORM="linux/amd64"
                ARCH_SUFFIX="-amd64"
                log_info "设置目标架构为 AMD64"
                shift
                ;;
            -arm)
                PLATFORM="linux/arm64"
                ARCH_SUFFIX="-arm64"
                log_info "设置目标架构为 ARM64"
                shift
                ;;
            -upload)
                UPLOAD_ONLY=true
                log_info "设置为仅上传模式"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                log_info "支持的参数: -amd, -arm, -upload"
                exit 1
                ;;
        esac
    done
    
    TAR_FILE="luna_full_stack${ARCH_SUFFIX}.tar"
    log_info "打包文件名: ${TAR_FILE}"
}

# 构建Docker镜像
build_images() {
    log_info "开始构建 Docker 镜像 (架构: $PLATFORM)..."
    
    if [ -f "$TAR_FILE" ]; then
        log_warning "发现旧的tar文件，正在删除..."
        rm -f "$TAR_FILE"
    fi
    
    # 1. 构建前端 App
    log_info "构建前端应用 (${APP_IMAGE})..."
    docker buildx build --platform $PLATFORM -t "${APP_IMAGE}" --load .
    if [ $? -ne 0 ]; then log_error "前端应用构建失败"; exit 1; fi

    # 2. 构建后端 Server
    log_info "构建后端服务 (${SERVER_IMAGE})..."
    docker buildx build --platform $PLATFORM -t "${SERVER_IMAGE}" --load ./ESP32_GDEY042T81_server
    if [ $? -ne 0 ]; then log_error "后端服务构建失败"; exit 1; fi

    # 3. 拉取/准备 MQTT 镜像
    log_info "准备 MQTT 镜像 (${MQTT_IMAGE})..."
    docker pull --platform $PLATFORM "${MQTT_IMAGE}"
    if [ $? -ne 0 ]; then log_error "MQTT 镜像拉取失败"; exit 1; fi

    # 4. 导出所有镜像到同一个 tar
    log_info "正在导出所有镜像到 ${TAR_FILE}..."
    docker save -o "${TAR_FILE}" "${APP_IMAGE}" "${SERVER_IMAGE}" "${MQTT_IMAGE}"
    
    if [ $? -eq 0 ]; then
        log_success "所有镜像构建并打包完成: ${TAR_FILE}"
    else
        log_error "镜像打包失败"
        exit 1
    fi
}

# 上传文件到服务器
upload_to_server() {
    log_info "准备上传文件到服务器..."
    
    # 1. 修复远程目录权限 (防止 Permission denied)
    log_info "检查并修复远程目录权限..."
    FIX_PERM_CMD="
        echo '${SERVER_PASSWORD}' | sudo -S mkdir -p ${DEPLOY_DIR}/ESP32_GDEY042T81_server
        echo '${SERVER_PASSWORD}' | sudo -S chown -R ${SERVER_USER}:${SERVER_USER} ${DEPLOY_DIR}
    "
    sshpass -p "$SERVER_PASSWORD" ssh -t -p "$SERVER_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "$FIX_PERM_CMD"
    
    # 2. 上传 Docker 镜像包
    log_info "上传镜像包 (可能需要几分钟)..."
    sshpass -p "$SERVER_PASSWORD" scp -P "$SERVER_PORT" -o StrictHostKeyChecking=no "$TAR_FILE" "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR}/"
    
    # 3. 上传 docker-compose.yml
    log_info "上传 docker-compose.yml..."
    sshpass -p "$SERVER_PASSWORD" scp -P "$SERVER_PORT" -o StrictHostKeyChecking=no "docker-compose.yml" "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR}/"
    
    # 4. 上传配置文件 (mosquitto.conf, .env.docker)
    log_info "上传配置文件..."
    sshpass -p "$SERVER_PASSWORD" scp -P "$SERVER_PORT" -o StrictHostKeyChecking=no "ESP32_GDEY042T81_server/mosquitto.conf" "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR}/ESP32_GDEY042T81_server/"
    sshpass -p "$SERVER_PASSWORD" scp -P "$SERVER_PORT" -o StrictHostKeyChecking=no "ESP32_GDEY042T81_server/.env.docker" "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR}/ESP32_GDEY042T81_server/"
    
    log_success "文件上传完成"
}

# 在服务器上部署
deploy_on_server() {
    log_info "在服务器上执行部署..."
    
    # 第一次尝试：直接使用 SSH 命令
    # 注意：这里我们移除了 sshpass 并在 EOF 块中直接执行命令
    # 如果您的 SSH 密钥已配置，这将无密码运行
    # 如果没有配置密钥，它会失败，然后我们可能需要另一种方法
    
    # 构建远程命令字符串
    REMOTE_CMD="
        set -e
        cd ${DEPLOY_DIR}
        
        echo '[INFO] 加载 Docker 镜像...'
        echo '${SERVER_PASSWORD}' | sudo -S docker load -i ${TAR_FILE}
        
        echo '[INFO] 使用 Docker Compose 启动服务...'
        mkdir -p ESP32_GDEY042T81_server/static
        
        echo '[INFO] 启动服务...'
        # echo '${SERVER_PASSWORD}' | sudo -S docker-compose up -d --remove-orphans
        echo '${SERVER_PASSWORD}' | sudo -S docker-compose up -d --no-build --remove-orphans
        
        echo '[INFO] 清理镜像包...'
        rm -f ${TAR_FILE}
        
        echo '[INFO] 检查运行状态:'
        echo '${SERVER_PASSWORD}' | sudo -S docker-compose ps
    "

    # 使用 sshpass 执行远程命令
    sshpass -p "$SERVER_PASSWORD" ssh -t -p "$SERVER_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "$REMOTE_CMD"

    if [ $? -eq 0 ]; then
        log_success "服务器部署完成"
    else
        log_error "服务器部署失败"
        exit 1
    fi
}

# 清理本地文件
cleanup_local() {
    log_info "清理本地临时文件..."
    if [ -f "$TAR_FILE" ]; then
        rm -f "$TAR_FILE"
        log_success "本地临时文件已清理"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=========================================="
    echo "部署完成!"
    echo "=========================================="
    echo "服务器地址: ${SERVER_HOST}"
    echo "部署目录: ${DEPLOY_DIR}"
    echo "前端访问: http://${SERVER_HOST}:3031"
    echo "后端 API: http://${SERVER_HOST}:8199"
    echo "MQTT 服务: ${SERVER_HOST}:1883"
    echo "=========================================="
    echo "查看日志: ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${DEPLOY_DIR} && sudo docker-compose logs -f'"
    echo "停止服务: ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${DEPLOY_DIR} && sudo docker-compose down'"
}

# 主函数
main() {
    echo "=========================================="
    echo "Docker 全栈部署脚本 (Compose Version)"
    echo "=========================================="
    
    UPLOAD_ONLY=false
    parse_arguments "$@"
    
    if [ "$SERVER_HOST" = "your-server-ip" ]; then
        log_error "请先配置脚本中的服务器信息 (SERVER_HOST, SERVER_USER, etc)"
        exit 1
    fi
    
    if [ "$UPLOAD_ONLY" = true ]; then
        if [ ! -f "$TAR_FILE" ]; then
            log_error "未找到tar文件: $TAR_FILE"
            
            # 智能检测其他架构的包
            if [ -f "luna_full_stack-arm64.tar" ]; then
                log_info "发现 luna_full_stack-arm64.tar，你是否想上传 ARM64 版本？"
                log_info "请使用命令: ./docker_deplay.sh -upload -arm"
            elif [ -f "luna_full_stack-amd64.tar" ]; then
                log_info "发现 luna_full_stack-amd64.tar，你是否想上传 AMD64 版本？"
                log_info "请使用命令: ./docker_deplay.sh -upload -amd"
            else
                log_info "原因: -upload 模式仅用于上传已存在的构建文件。"
                log_info "解决: 请先运行不带 -upload 参数的命令来构建镜像，例如: ./docker_deplay.sh"
            fi
            exit 1
        fi
        upload_to_server
        deploy_on_server
        cleanup_local
        show_deployment_info
    else
        check_dependencies
        build_images
        upload_to_server
        deploy_on_server
        cleanup_local
        show_deployment_info
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
