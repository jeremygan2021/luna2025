#!/bin/bash

# 启动脚本

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 复制环境变量文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请根据需要修改 .env 文件中的配置"
fi

# 启动应用
echo "启动墨水屏桌面屏幕系统服务端..."
uvicorn main:app --host 0.0.0.0 --port 9999
