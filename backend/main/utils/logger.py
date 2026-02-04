"""
日志工具模块
~~~~~~~~~~~

提供统一的日志记录功能

功能：
- 日志记录器初始化
- 多种日志级别（DEBUG/INFO/WARNING/ERROR）
- 日志文件轮转
- 彩色终端输出

作者: 智糖团队
日期: 2025-01-15
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 全局日志记录器字典
_loggers = {}


def setup_logger(
    name: str = 'zhitang',
    log_dir: str = '../logs',
    log_level: str = 'INFO',
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置并返回日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        log_level: 日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的日志文件数量
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 如果已存在，直接返回
    if name in _loggers:
        return _loggers[name]
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带轮转）
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 缓存logger
    _loggers[name] = logger
    
    return logger


def get_logger(name: str = 'zhitang') -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    if name not in _loggers:
        return setup_logger(name)
    return _loggers[name]

