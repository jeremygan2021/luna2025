#!/bin/bash

# 创建MQTT密码文件
docker exec luna-mqtt mosquitto_passwd -c -b /mosquitto/config/passwd luna2025 123luna2021

# 重启MQTT服务以应用新的认证配置
docker restart luna-mqtt

echo "MQTT用户名和密码已配置完成"
echo "用户名: luna2025"
echo "密码: 123luna2021"