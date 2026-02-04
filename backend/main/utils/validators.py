"""
验证器工具模块
~~~~~~~~~~~~~~

提供数据验证功能

功能：
- 手机号验证
- 邮箱验证
- 密码强度验证
- 通用数据验证

作者: 智糖团队
日期: 2025-01-15
"""

import re
from typing import Optional


def validate_phone(phone_number: str) -> bool:
    """
    验证中国大陆手机号
    
    Args:
        phone_number: 手机号字符串
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_phone("13800138000")
        True
        >>> validate_phone("12345678901")
        False
    """
    if not phone_number:
        return False
    
    # 中国大陆手机号规则：1开头，第二位是3-9，总共11位
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone_number))


def validate_email(email: str) -> bool:
    """
    验证邮箱地址
    
    Args:
        email: 邮箱地址字符串
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email:
        return False
    
    # 基本的邮箱格式验证
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    验证密码强度
    
    Args:
        password: 密码字符串
        min_length: 最小长度
        
    Returns:
        tuple: (是否有效, 错误信息)
        
    Example:
        >>> validate_password("Abc123456")
        (True, None)
        >>> validate_password("123")
        (False, "密码长度不能少于8位")
    """
    if not password:
        return False, "密码不能为空"
    
    if len(password) < min_length:
        return False, f"密码长度不能少于{min_length}位"
    
    # 检查是否包含数字
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    # 检查是否包含字母
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含至少一个字母"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    验证用户名
    
    Args:
        username: 用户名字符串
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not username:
        return False, "用户名不能为空"
    
    if len(username) < 3:
        return False, "用户名长度不能少于3位"
    
    if len(username) > 20:
        return False, "用户名长度不能超过20位"
    
    # 只允许字母、数字、下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    
    return True, None


def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
    """
    验证必填字段
    
    Args:
        data: 数据字典
        required_fields: 必填字段列表
        
    Returns:
        tuple: (是否有效, 错误信息)
        
    Example:
        >>> data = {"name": "张三", "age": 20}
        >>> validate_required_fields(data, ["name", "age", "email"])
        (False, "缺少必填字段: email")
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, None

