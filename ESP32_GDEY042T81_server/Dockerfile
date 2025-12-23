# 使用官方Python基础镜像，配置国内镜像源
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 使用国内pip镜像源
# RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
#     pip config set global.trusted-host mirrors.aliyun.com

# 使用国内apt镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p static/uploads static/processed

# 暴露端口
EXPOSE 9999

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8199"]