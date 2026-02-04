"""
WebSocket流式语音识别服务
支持实时语音识别和流式返回结果
"""

import json
import logging
from typing import Optional
from flask_sock import Sock

from utils.jwt_helper import verify_token
from services.coze_service import CozeService

logger = logging.getLogger(__name__)


class WebSocketASRService:
    """WebSocket ASR服务类"""
    
    def __init__(self, app=None):
        """
        初始化WebSocket ASR服务
        
        Args:
            app: Flask应用实例
        """
        self.sock = Sock(app) if app else None
        self.coze_service = CozeService()
        self.active_connections = {}  # 存储活跃的WebSocket连接
        
        if app:
            self.register_routes()
    
    def register_routes(self):
        """注册WebSocket路由"""
        @self.sock.route('/api/chat/asr/stream')
        def handle_asr_stream(ws):
            """处理流式ASR WebSocket连接"""
            return self.handle_asr_connection(ws)
    
    def handle_asr_connection(self, ws):
        """
        处理ASR WebSocket连接
        
        Args:
            ws: WebSocket连接对象
        """
        user_id = None
        audio_buffer = []  # 音频数据缓冲区
        
        try:
            logger.info("📡 新的ASR WebSocket连接建立")
            
            # 1. 等待认证消息
            auth_data = ws.receive()
            if not auth_data:
                logger.error("❌ 未收到认证消息")
                ws.send(json.dumps({'type': 'error', 'message': '需要认证'}))
                return
            
            # 解析认证消息
            try:
                auth_msg = json.loads(auth_data)
            except json.JSONDecodeError:
                logger.error("❌ 认证消息格式错误")
                ws.send(json.dumps({'type': 'error', 'message': '认证消息格式错误'}))
                return
            
            if auth_msg.get('type') != 'auth':
                logger.error("❌ 第一条消息必须是认证消息")
                ws.send(json.dumps({'type': 'error', 'message': '第一条消息必须是认证消息'}))
                return
            
            # 验证token
            token = auth_msg.get('token', '').replace('Bearer ', '')
            if not token:
                logger.error("❌ 未提供token")
                ws.send(json.dumps({'type': 'error', 'message': '未提供token'}))
                return
            
            # 解析token获取user_id
            payload = verify_token(token)
            if not payload:
                logger.error("❌ token验证失败")
                ws.send(json.dumps({'type': 'error', 'message': 'token验证失败'}))
                return
            
            user_id = payload.get('user_id')
            if not user_id:
                logger.error("❌ token中未找到user_id")
                ws.send(json.dumps({'type': 'error', 'message': 'token无效'}))
                return
            
            logger.info(f"✅ 用户 {user_id} 认证成功")
            
            # 发送认证成功消息
            ws.send(json.dumps({'type': 'auth_success', 'message': '认证成功'}))
            
            # 存储连接
            self.active_connections[user_id] = ws
            
            # 2. 接收音频数据并进行流式识别
            while True:
                data = ws.receive(timeout=60)  # 60秒超时
                
                if data is None:
                    logger.info("📡 连接关闭")
                    break
                
                # 如果是文本消息（控制消息）
                if isinstance(data, str):
                    try:
                        control_msg = json.loads(data)
                        
                        # 结束信号
                        if control_msg.get('type') == 'end':
                            logger.info("🏁 收到结束信号")
                            
                            # 处理缓冲区中的所有音频
                            if audio_buffer:
                                final_text = self._process_audio_batch(
                                    user_id, 
                                    audio_buffer, 
                                    is_final=True
                                )
                                
                                # 发送最终结果
                                ws.send(json.dumps({
                                    'type': 'result',
                                    'text': final_text,
                                    'is_final': True
                                }))
                            
                            break
                        
                    except json.JSONDecodeError:
                        logger.error("❌ 控制消息格式错误")
                        continue
                
                # 如果是二进制数据（音频数据）
                elif isinstance(data, bytes):
                    logger.info(f"📦 收到音频数据: {len(data)} bytes")
                    
                    # 将音频数据添加到缓冲区
                    audio_buffer.append(data)
                    
                    # 当缓冲区达到一定大小时，进行识别（例如：每1秒的音频）
                    # 假设16kHz采样率，每秒约32KB数据
                    total_size = sum(len(chunk) for chunk in audio_buffer)
                    
                    if total_size >= 32000:  # 约1秒的音频
                        # 处理音频并获取中间识别结果
                        text = self._process_audio_batch(
                            user_id, 
                            audio_buffer, 
                            is_final=False
                        )
                        
                        # 发送中间结果
                        if text:
                            ws.send(json.dumps({
                                'type': 'result',
                                'text': text,
                                'is_final': False
                            }))
                        
                        # 清空缓冲区（但保留最后一部分用于上下文）
                        # 保留最后500ms的数据作为上下文
                        if len(audio_buffer) > 5:
                            audio_buffer = audio_buffer[-5:]
                        else:
                            audio_buffer = []
            
        except Exception as e:
            logger.error(f"❌ ASR WebSocket错误: {e}", exc_info=True)
            try:
                ws.send(json.dumps({'type': 'error', 'message': str(e)}))
            except:
                pass
        
        finally:
            # 清理连接
            if user_id and user_id in self.active_connections:
                del self.active_connections[user_id]
            logger.info(f"🔌 用户 {user_id} WebSocket连接已关闭")
    
    def _process_audio_batch(
        self, 
        user_id: int, 
        audio_chunks: list, 
        is_final: bool = False
    ) -> Optional[str]:
        """
        处理音频批次并调用ASR API
        
        Args:
            user_id: 用户ID
            audio_chunks: 音频数据块列表
            is_final: 是否是最终识别
        
        Returns:
            识别的文本
        """
        try:
            if not audio_chunks:
                return None
            
            # 合并音频块
            audio_data = b''.join(audio_chunks)
            
            logger.info(f"🎤 处理音频批次: {len(audio_data)} bytes, 最终={is_final}")
            
            # 调用Coze ASR API
            # 注意：Coze API可能不支持真正的流式识别，这里是模拟实现
            # 实际应该根据Coze文档使用正确的API
            result = self.coze_service.speech_to_text(
                user_id=user_id,
                audio_data=audio_data,
                audio_format='webm',
                mime_type='audio/webm;codecs=opus'
            )
            
            if result and result.get('success'):
                text = result.get('text', '')
                logger.info(f"✅ 识别结果: {text[:50]}...")
                return text
            else:
                logger.warning(f"⚠️ 识别失败: {result}")
                return None
        
        except Exception as e:
            logger.error(f"❌ 处理音频批次失败: {e}", exc_info=True)
            return None
    
    def broadcast_to_user(self, user_id: int, message: dict):
        """
        向特定用户发送消息
        
        Args:
            user_id: 用户ID
            message: 消息内容
        """
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ 发送消息失败: {e}")
    
    def close_connection(self, user_id: int):
        """
        关闭特定用户的连接
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                ws.close()
                del self.active_connections[user_id]
                logger.info(f"🔌 关闭用户 {user_id} 的WebSocket连接")
            except Exception as e:
                logger.error(f"❌ 关闭连接失败: {e}")


# 全局WebSocket ASR服务实例
websocket_asr_service = None


def init_websocket_asr(app):
    """
    初始化WebSocket ASR服务
    
    Args:
        app: Flask应用实例
    
    Returns:
        WebSocketASRService实例
    """
    global websocket_asr_service
    
    logger.info("🚀 初始化WebSocket ASR服务...")
    websocket_asr_service = WebSocketASRService(app)
    logger.info("✅ WebSocket ASR服务初始化成功")
    
    return websocket_asr_service

