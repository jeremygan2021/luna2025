# 墨水屏桌面屏幕系统服务端

基于 FastAPI + MQTT + HTTP/HTTPS + NTP 的轻量级墨水屏显示系统服务端。

## 功能特点

- 设备管理：维护设备信息、状态和绑定关系
- 内容管理：为设备创建和管理内容版本
- 图片处理：使用 Pillow 将原始图片预处理为墨水屏兼容格式
- MQTT 推送：实时向设备推送更新指令
- REST API：提供设备管理和内容管理的完整接口

## 技术栈

- FastAPI: Web 框架
- PostgreSQL: 数据库
- Pillow: 图片处理
- Paho-MQTT: MQTT 客户端
- Uvicorn: ASGI 服务器

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 9999
```

## API 接口

### 设备管理
- `POST /api/devices/` - 注册新设备
- `GET /api/devices/{device_id}/bootstrap` - 设备启动获取当前版本
- `GET /api/devices/{device_id}/status` - 获取设备状态

### 内容管理
- `POST /api/devices/{device_id}/content` - 创建新内容版本
- `GET /api/devices/{device_id}/content` - 获取内容列表
- `GET /api/devices/{device_id}/content/{version}` - 获取特定版本内容
- `POST /api/upload` - 上传图片

### 资源下载
- `GET /static/images/{filename}` - 下载处理后的图片