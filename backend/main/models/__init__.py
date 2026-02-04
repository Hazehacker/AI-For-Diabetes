"""
智糖小助手 - 数据模型层
~~~~~~~~~~~~~~~~~~~~~~~

提供数据库模型和ORM封装，包括：
- 用户模型
- 标签模型
- 新手引导模型
- 对话模型
- 打卡模型

作者: 智糖团队
日期: 2025-01-15
"""

from .tag import Tag, TagDefinition, TagValue, TagHistory
from .onboarding import OnboardingStatus, OnboardingAnswer, OnboardingQuestion
from .user import User

__all__ = [
    # 标签相关
    'Tag',
    'TagDefinition',
    'TagValue',
    'TagHistory',
    
    # 新手引导相关
    'OnboardingStatus',
    'OnboardingAnswer',
    'OnboardingQuestion',
    
    # 用户相关
    'User',
]

