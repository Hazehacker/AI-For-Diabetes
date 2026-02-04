"""
配置加载模块
~~~~~~~~~~~

提供配置文件的加载和管理功能

功能：
- 从YAML文件加载配置
- 环境变量支持
- 配置验证
- 默认值管理

作者: 智糖团队
日期: 2025-01-15
"""

import os
import yaml
from typing import Any, Optional

# 全局配置字典
_config = {}


def load_config(config_path: Optional[str] = None) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径（可选）
        
    Returns:
        dict: 配置字典
    """
    global _config
    
    # 如果已加载，直接返回
    if _config:
        return _config
    
    # 确定配置文件路径
    if config_path is None:
        # 尝试多个可能的路径
        possible_paths = [
            os.environ.get('CONFIG_PATH'),
            '../config.yaml',
            '../../config.yaml',
            'config.yaml'
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                config_path = path
                break
    
    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到，尝试的路径: {possible_paths}")
    
    # 加载YAML配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _config = yaml.safe_load(f) or {}
        
        # 如果YAML解析失败，尝试旧格式（key=value）
        if not _config:
            _config = {}
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        _config[key.strip()] = value.strip()
        
        # 环境变量覆盖
        _apply_env_overrides()
        
        return _config
        
    except Exception as e:
        raise Exception(f"加载配置文件失败: {str(e)}")


def _apply_env_overrides():
    """
    应用环境变量覆盖
    """
    # 敏感配置可以通过环境变量覆盖
    env_keys = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME',
        'JWT_SECRET_KEY',
        'COZE_BOT_ID', 'COZE_ACCESS_TOKEN',
        'REDIS_HOST', 'REDIS_PORT'
    ]
    
    for key in env_keys:
        env_value = os.environ.get(key)
        if env_value:
            _config[key] = env_value


def get_config(key: Optional[str] = None, default: Any = None) -> Any:
    """
    获取配置值

    Args:
        key: 配置键（支持点分隔的嵌套键，如 'DATABASE.HOST'）
        default: 默认值

    Returns:
        配置值或默认值

    Example:
        >>> db_host = get_config('DATABASE.HOST', 'localhost')
        >>> jwt_secret = get_config('JWT.SECRET_KEY')
        >>> all_config = get_config()
    """
    global _config

    # 如果未加载，先加载
    if not _config:
        load_config()

    # 返回整个配置
    if key is None:
        return _config

    # 支持点分隔的嵌套键
    keys = key.split('.')
    value = _config

    try:
        for k in keys:
            if isinstance(value, dict):
                value = value[k]
            else:
                return default
        return value
    except (KeyError, TypeError):
        return default


def reload_config():
    """
    重新加载配置文件
    """
    global _config
    _config = {}
    return load_config()

