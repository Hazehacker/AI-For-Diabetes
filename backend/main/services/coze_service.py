"""
Coze集成服务 (极简化版 - 仅ASR)
~~~~~~~~~~~

Coze API集成服务，仅保留：
✅ ASR语音识别 (speech_to_text)
✅ TTS文字转语音 (text_to_speech)

以下功能已禁用：
❌ Bot对话 (chat_with_stream)
❌ 变量管理 (set_bot_variables, get_bot_variables)
❌ 知识库 (upload_knowledge, list_knowledge_datasets)
❌ 用户变量初始化 (initialize_user_variables)

作者: 智糖团队
日期: 2025-01-15
"""

import sys
import os
from typing import Optional, List, Dict, Any

# 添加当前目录到sys.path以导入coze模块
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from coze_api_wrapper import CozeAPIWrapper
# from coze_stream_chat import CozeStreamChat  # 注释掉，对话功能不需要
from utils.logger import get_logger
from utils.config_loader import get_config

logger = get_logger(__name__)


class CozeService:
    """
    Coze服务类 (简化版)

    主要用于ASR语音识别，其他功能已禁用
    """

    def __init__(self):
        """初始化Coze服务"""
        self.config = get_config()
        self.bot_id = get_config('COZE.BOT_ID')

        # 初始化API客户端
        try:
            self.api_wrapper = CozeAPIWrapper()
            # self.stream_chat = CozeStreamChat()  # 注释掉，对话功能不需要
            logger.info("✅ Coze服务初始化成功 (简化版，仅ASR功能)")
        except Exception as e:
            logger.error(f"❌ Coze服务初始化失败: {str(e)}")
            self.api_wrapper = None
            self.stream_chat = None
    
    # 对话功能已禁用，仅保留ASR功能
    def chat_with_stream(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ):
        """
        流式对话 (已禁用)

        仅保留方法签名以保持API兼容性
        """
        yield {'event': 'error', 'data': {'message': 'Coze对话功能已禁用，仅保留ASR功能'}}
    
    # 变量管理功能已禁用
    def set_bot_variables(
        self,
        user_id: int,
        variables: List[Dict[str, str]]
    ) -> bool:
        """
        设置Bot变量 (已禁用)
        """
        logger.warning("⚠️ Coze变量管理功能已禁用")
        return False
    
    # 变量获取功能已禁用
    def get_bot_variables(
        self,
        user_id: int,
        keywords: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        获取Bot变量 (已禁用)
        """
        logger.warning("⚠️ Coze变量获取功能已禁用")
        return None
    
    def speech_to_text(
        self,
        user_id: int,
        audio_data: bytes = None,
        audio_file_path: str = None,
        audio_format: str = 'wav',
        mime_type: str = 'audio/wav'
    ) -> Optional[Dict]:
        """
        语音转文本
        
        Args:
            user_id: 用户ID
            audio_data: 音频数据
            audio_file_path: 音频文件路径
            
        Returns:
            Dict: 识别结果
        """
        if not self.api_wrapper:
            return None
        
        try:
            result = self.api_wrapper.speech_to_text(
                user_id=user_id,
                audio_data=audio_data,
                audio_file_path=audio_file_path,
                audio_format=audio_format,
                mime_type=mime_type
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 语音转文本失败: {str(e)}")
            return None
    
    def text_to_speech(
        self,
        user_id: int,
        text: str,
        voice_id: str = "7426720361753903141",
        speed: float = 1.0
    ) -> Optional[bytes]:
        """
        文本转语音
        
        Args:
            user_id: 用户ID
            text: 文本内容
            voice_id: 语音ID
            speed: 语速
            
        Returns:
            bytes: 音频数据
        """
        if not self.api_wrapper:
            return None
        
        try:
            result = self.api_wrapper.text_to_speech(
                user_id=user_id,
                text=text,
                voice_id=voice_id,
                speed=speed
            )
            
            if result and result.get('audio'):
                return result['audio']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 文本转语音失败: {str(e)}")
            return None
    
    # 知识库功能已禁用
    def upload_knowledge(
        self,
        user_id: int,
        file_path: str,
        file_name: Optional[str] = None,
        dataset_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        上传知识库文件 (已禁用)
        """
        logger.warning("⚠️ Coze知识库功能已禁用")
        return None
    
    # 知识库功能已禁用
    def list_knowledge_datasets(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Optional[Dict]:
        """
        列出知识库数据集 (已禁用)
        """
        logger.warning("⚠️ Coze知识库功能已禁用")
        return None
    
    # 用户变量初始化功能已禁用
    def initialize_user_variables(
        self,
        user_id: int,
        user_data: Dict[str, Any]
    ) -> bool:
        """
        初始化用户变量 (已禁用)
        """
        logger.warning("⚠️ Coze用户变量初始化功能已禁用")
        return False


# 全局单例
_coze_service_instance = None

def get_coze_service() -> CozeService:
    """获取Coze服务单例"""
    global _coze_service_instance
    if _coze_service_instance is None:
        _coze_service_instance = CozeService()
    return _coze_service_instance

