# Docker 部署指南

本项目已配置 Docker 和 Docker Compose，可以一键部署整个应用环境。

## 快速启动

1. 确保已安装 Docker 和 Docker Compose
2. 在项目根目录执行以下命令：

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看应用日志
docker-compose logs -f luna-app
```

3. 访问应用：
   - API 文档：http://localhost:9999/docs
   - 管理后台：http://localhost:9999/admin

## 服务说明

- **luna-app**: 主应用服务，运行在 9999 端口
- **luna-mqtt**: MQTT 服务，运行在 1883 端口

注意：本项目使用外部PostgreSQL数据库，数据库地址已在.env.docker文件中配置。

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（注意：这将删除所有数据）
docker-compose down -v
```

## 注意事项

1. 首次启动可能需要几分钟等待数据库初始化完成
2. 应用配置通过.env.docker文件传递，该文件已配置为使用Docker内部服务名
3. 静态文件通过 volume 挂载，可以直接在宿主机修改
4. 数据持久化通过 Docker volumes 实现
5. 如需修改配置，请编辑.env.docker文件，而不是.env文件

## 国内镜像源

本项目已配置使用国内镜像源，包括：
- Python 基础镜像：阿里云镜像
- pip 包源：阿里云 pip 源
- PostgreSQL：阿里云镜像
- Mosquitto：阿里云镜像

这样可以大大提高在国内的构建和拉取速度。