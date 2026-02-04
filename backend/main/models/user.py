"""
用户模型
~~~~~~~

用户相关的数据模型

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, Dict, Any
from utils.database import execute_query
from utils.logger import get_logger

logger = get_logger(__name__)


class User:
    """
    用户模型
    
    对应表: users
    """
    
    def __init__(self, user_id: int = None, username: str = None, 
                 nickname: str = None, phone_number: str = None,
                 email: str = None, **kwargs):
        self.user_id = user_id
        self.username = username
        self.nickname = nickname
        self.phone_number = phone_number
        self.email = email
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象
        """
        sql = "SELECT * FROM users WHERE user_id = %s AND is_active = TRUE"
        row = execute_query(sql, (user_id,), fetch_one=True)
        return User(**row) if row else None
    
    @staticmethod
    def get_by_phone(phone_number: str) -> Optional['User']:
        """
        根据手机号获取用户
        
        Args:
            phone_number: 手机号
            
        Returns:
            User: 用户对象
        """
        sql = "SELECT * FROM users WHERE phone_number = %s AND is_active = TRUE"
        row = execute_query(sql, (phone_number,), fetch_one=True)
        return User(**row) if row else None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'nickname': self.nickname,
            'phone_number': self.phone_number,
            'email': self.email
        }

