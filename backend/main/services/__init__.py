"""
智糖小助手 - 业务逻辑层
~~~~~~~~~~~~~~~~~~~~~~~

提供核心业务逻辑服务，包括：
- TTS语音服务
- 新手引导服务
- 标签管理服务
- Coze集成服务
- 认证服务
- 用户管理服务
- 对话管理服务
- 打卡服务
- 积分服务
- 知识库服务

作者: 智糖团队
日期: 2025-01-15
"""

from .tts_service import TTSService, get_tts_service
from .onboarding_service import OnboardingService, get_onboarding_service
from .tag_service import TagService, get_tag_service
from .coze_service import CozeService, get_coze_service
from .auth_service import AuthService, get_auth_service
from .user_service import UserService, get_user_service
from .chat_service import ChatService, get_chat_service
from .checkin_service import CheckinService, get_checkin_service
from .points_service import PointsService, get_points_service
from .knowledge_service import KnowledgeService, get_knowledge_service

__all__ = [
    # 类
    'TTSService',
    'OnboardingService',
    'TagService',
    'CozeService',
    'AuthService',
    'UserService',
    'ChatService',
    'CheckinService',
    'PointsService',
    'KnowledgeService',
    
    # 单例获取函数
    'get_tts_service',
    'get_onboarding_service',
    'get_tag_service',
    'get_coze_service',
    'get_auth_service',
    'get_user_service',
    'get_chat_service',
    'get_checkin_service',
    'get_points_service',
    'get_knowledge_service',
]

