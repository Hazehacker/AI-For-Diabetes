"""
智糖小助手 - 工具模块
~~~~~~~~~~~~~~~~~~~~~~~

提供通用的工具函数和辅助类，包括：
- 数据库连接管理
- JWT认证工具
- 日志记录
- 配置加载
- 装饰器
- 验证器

作者: 智糖团队
日期: 2025-01-15
"""

from .database import get_db_connection, get_db_pool
from .jwt_helper import generate_token, verify_token, token_required
from .logger import setup_logger, get_logger
from .config_loader import load_config, get_config
from .decorators import async_task, retry_on_failure, log_execution_time
from .validators import validate_phone, validate_email, validate_password

__all__ = [
    # 数据库
    'get_db_connection',
    'get_db_pool',
    
    # JWT
    'generate_token',
    'verify_token',
    'refresh_token',
    'token_required',
    'generate_admin_token',
    'verify_admin_token',
    'get_keycloak_client',
    'get_keycloak_admin_client',
    'token_required',
    
    # 日志
    'setup_logger',
    'get_logger',
    
    # 配置
    'load_config',
    'get_config',
    
    # 装饰器
    'async_task',
    'retry_on_failure',
    'log_execution_time',
    
    # 验证器
    'validate_phone',
    'validate_email',
    'validate_password',
]

