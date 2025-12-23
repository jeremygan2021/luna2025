import json
import logging
import time
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt
from schemas import MQTTCommand, MQTTStatus
from config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client()
        self.connected = False
        self.setup_client()
    
    def setup_client(self):
        """设置MQTT客户端"""
        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # 设置认证信息（如果有）
        if settings.mqtt_username and settings.mqtt_password:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
    
    def connect(self):
        """连接到MQTT代理"""
        try:
            self.client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port, 60)
            self.client.loop_start()
            logger.info(f"正在连接到MQTT代理 {settings.mqtt_broker_host}:{settings.mqtt_broker_port}")
        except Exception as e:
            logger.error(f"连接MQTT代理失败: {str(e)}")
    
    def disconnect(self):
        """断开MQTT连接"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("已断开MQTT连接")
    
    def on_connect(self, client, userdata, flags, rc):
        """连接回调函数"""
        if rc == 0:
            self.connected = True
            logger.info("成功连接到MQTT代理")
        else:
            logger.error(f"连接MQTT代理失败，返回码: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """断开连接回调函数"""
        self.connected = False
        logger.warning(f"与MQTT代理断开连接，返回码: {rc}")
    
    def on_message(self, client, userdata, msg):
        """消息接收回调函数"""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            logger.info(f"收到MQTT消息 - 主题: {topic}, 内容: {payload}")
            
            # 解析设备状态上报
            if "/status" in topic:
                device_id = topic.split("/")[1]
                status_data = json.loads(payload)
                self.handle_device_status(device_id, status_data)
                
        except Exception as e:
            logger.error(f"处理MQTT消息失败: {str(e)}")
    
    def handle_device_status(self, device_id: str, status_data: Dict[str, Any]):
        """处理设备状态上报"""
        try:
            # 这里可以更新设备状态到数据库
            # 例如：更新最后在线时间、处理错误状态等
            logger.info(f"设备 {device_id} 状态上报: {status_data}")
        except Exception as e:
            logger.error(f"处理设备状态失败: {str(e)}")
    
    def publish_command(self, device_id: str, command: MQTTCommand) -> bool:
        """
        向设备发布命令
        
        Args:
            device_id: 设备ID
            command: 命令对象
            
        Returns:
            是否发布成功
        """
        if not self.connected:
            logger.error("MQTT未连接，无法发布命令")
            return False
        
        try:
            topic = f"esp32/{device_id}/cmd"
            payload = command.model_dump_json()
            
            result = self.client.publish(topic, payload)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"成功向设备 {device_id} 发布命令: {payload}")
                return True
            else:
                logger.error(f"向设备 {device_id} 发布命令失败，错误码: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"发布命令失败: {str(e)}")
            return False
    
    def send_update_command(self, device_id: str, content_version: int) -> bool:
        """
        发送更新命令
        
        Args:
            device_id: 设备ID
            content_version: 内容版本
            
        Returns:
            是否发送成功
        """
        command = MQTTCommand(
            type="update",
            content_version=content_version,
            timestamp=int(time.time())
        )
        return self.publish_command(device_id, command)
    
    def subscribe_to_device_status(self, device_id: str):
        """
        订阅设备状态
        
        Args:
            device_id: 设备ID
        """
        if not self.connected:
            logger.error("MQTT未连接，无法订阅")
            return
        
        try:
            topic = f"esp32/{device_id}/status"
            self.client.subscribe(topic)
            logger.info(f"已订阅设备 {device_id} 状态")
        except Exception as e:
            logger.error(f"订阅设备状态失败: {str(e)}")
    
    def unsubscribe_from_device_status(self, device_id: str):
        """
        取消订阅设备状态
        
        Args:
            device_id: 设备ID
        """
        if not self.connected:
            logger.error("MQTT未连接，无法取消订阅")
            return
        
        try:
            topic = f"esp32/{device_id}/status"
            self.client.unsubscribe(topic)
            logger.info(f"已取消订阅设备 {device_id} 状态")
        except Exception as e:
            logger.error(f"取消订阅设备状态失败: {str(e)}")
    
    def send_todo_command(self, device_id: str, action: str, todo_data: Dict[str, Any]) -> bool:
        """
        发送待办事项命令
        
        Args:
            device_id: 设备ID
            action: 动作类型 (create, update, delete)
            todo_data: 待办事项数据
            
        Returns:
            是否发送成功
        """
        if not self.connected:
            logger.error("MQTT未连接，无法发送待办事项命令")
            return False
        
        try:
            topic = f"esp32/{device_id}/todo"
            payload = {
                "type": "todo",
                "action": action,
                "data": todo_data,
                "timestamp": int(time.time())
            }
            
            result = self.client.publish(topic, json.dumps(payload))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"成功向设备 {device_id} 发送待办事项命令: {action}")
                return True
            else:
                logger.error(f"向设备 {device_id} 发送待办事项命令失败，错误码: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"发送待办事项命令失败: {str(e)}")
            return False

# 全局MQTT管理器实例
mqtt_manager = MQTTManager()