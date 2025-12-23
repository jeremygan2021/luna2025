使用fastAPI框架
python 3.12

- 使用pg数据库 url http://121.43.104.161:6432
- 用户名：luna
- 密码：123luna

用uvicorn运行
uvicorn main:app --host 0.0.0.0 --port 9999

用 conda activate luna 来激活环境 或者使用uv 来启动

使用./start.sh 来启动服务

服务器项目配置：
墨水屏硬件使用
ESP32-S3 micropython 编写固件
显示模块	GDEY042T81

通信协议	MQTT 3.1.1 + HTTP/HTTPS + NTP	MQTT 保障即时性，HTTP 方便下载资源，NTP 保障时间准确
图片处理	Pillow（Python）	服务端快速预处理图片为墨水屏兼容格式
