"""
装饰器工具模块
~~~~~~~~~~~~~~

提供常用的装饰器功能

功能：
- 异步任务执行
- 失败重试
- 执行时间记录
- 缓存

作者: 智糖团队
日期: 2025-01-15
"""

import time
import functools
from threading import Thread
from typing import Callable, Any
from .logger import get_logger

logger = get_logger(__name__)


def async_task(func: Callable) -> Callable:
    """
    异步任务装饰器：在新线程中执行函数
    
    Example:
        @async_task
        def send_email(user_id):
            # 发送邮件逻辑
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    失败重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
    
    Example:
        @retry_on_failure(max_attempts=3, delay=2.0)
        def fetch_data():
            # API调用逻辑
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"⚠️ {func.__name__} 第 {attempt}/{max_attempts} 次尝试失败: {str(e)}"
                    )
                    
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        logger.error(f"❌ {func.__name__} 所有尝试均失败")
            
            raise last_exception
        
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    执行时间记录装饰器
    
    Example:
        @log_execution_time
        def process_data():
            # 处理逻辑
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            logger.info(f"⏱️ {func.__name__} 执行耗时: {elapsed:.2f}秒")
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {func.__name__} 执行失败 (耗时{elapsed:.2f}秒): {str(e)}")
            raise
    
    return wrapper


def cache_result(ttl: int = 300):
    """
    结果缓存装饰器（简单的内存缓存）
    
    Args:
        ttl: 缓存有效期（秒）
    
    Example:
        @cache_result(ttl=600)
        def get_user_info(user_id):
            # 查询数据库
            pass
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = str(args) + str(kwargs)
            current_time = time.time()
            
            # 检查缓存是否有效
            if cache_key in cache:
                cached_time = cache_times.get(cache_key, 0)
                if current_time - cached_time < ttl:
                    logger.debug(f"✅ 使用缓存: {func.__name__}")
                    return cache[cache_key]
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = current_time
            
            return result
        
        return wrapper
    return decorator


def singleton(cls):
    """
    单例模式装饰器
    
    Example:
        @singleton
        class DatabaseManager:
            pass
    """
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

