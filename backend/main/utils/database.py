"""
数据库工具模块
~~~~~~~~~~~~~~

提供数据库连接和连接池管理功能

功能：
- 数据库连接创建
- 连接池管理
- 事务管理
- 查询辅助函数

作者: 智糖团队
日期: 2025-01-15
"""

import pymysql
from dbutils.pooled_db import PooledDB
from typing import Optional, Dict, Any
from .logger import get_logger
from .config_loader import get_config

logger = get_logger(__name__)

# 全局连接池实例
_db_pool: Optional[PooledDB] = None


def init_db_pool():
    """
    初始化数据库连接池
    
    Returns:
        PooledDB: 数据库连接池实例
    """
    global _db_pool
    
    if _db_pool is not None:
        logger.warning("数据库连接池已初始化")
        return _db_pool
    
    try:
        config = get_config()

        # 从配置文件获取连接池参数
        pool_size = int(get_config('DATABASE.POOL_SIZE', 20))
        max_overflow = int(get_config('DATABASE.MAX_OVERFLOW', 10))

        _db_pool = PooledDB(
            creator=pymysql,
            maxconnections=pool_size + max_overflow,  # 最大连接数 = 基础池大小 + 溢出
            mincached=min(5, pool_size // 4),         # 最小空闲连接数（至少5个）
            maxcached=pool_size,                      # 最大空闲连接数（等于池大小）
            maxshared=min(10, pool_size // 2),       # 最大共享连接数
            blocking=True,                            # 连接池满时是否阻塞
            maxusage=None,                            # 单个连接最大使用次数（无限制）
            setsession=[],                            # 连接前执行的SQL
            ping=1,                                   # ping MySQL服务器检查连接（每次使用前检查）
            host=get_config('DATABASE.HOST', 'localhost'),
            port=int(get_config('DATABASE.PORT', 3306)),
            user=get_config('DATABASE.USER', 'root'),
            password=get_config('DATABASE.PASSWORD', ''),
            database=get_config('DATABASE.NAME', 'zhitang'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,  # 使用字典游标
            connect_timeout=5,                        # 连接超时（秒）
            read_timeout=10,                          # 读取超时（秒）
            write_timeout=10,                         # 写入超时（秒）
            autocommit=False                          # 默认不自动提交
        )
        
        logger.info("✅ 数据库连接池初始化成功")
        return _db_pool
        
    except Exception as e:
        logger.error(f"❌ 数据库连接池初始化失败: {str(e)}")
        raise


def get_db_pool() -> PooledDB:
    """
    获取数据库连接池实例
    
    Returns:
        PooledDB: 数据库连接池
    """
    global _db_pool
    
    if _db_pool is None:
        _db_pool = init_db_pool()
    
    return _db_pool


def get_pool_status() -> Dict[str, Any]:
    """
    获取连接池状态信息
    
    Returns:
        Dict: 连接池状态信息
    """
    try:
        pool = get_db_pool()
        return {
            'success': True,
            'maxconnections': pool._maxconnections,
            'mincached': pool._mincached,
            'maxcached': pool._maxcached,
            'maxshared': pool._maxshared,
            'current_connections': len(pool._connections) if hasattr(pool, '_connections') else 0,
            'idle_connections': len([c for c in pool._connections if not c._con._closed]) if hasattr(pool, '_connections') else 0
        }
    except Exception as e:
        logger.error(f"❌ 获取连接池状态失败: {str(e)}")
        return {'success': False, 'message': str(e)}


def get_db_connection():
    """
    从连接池获取数据库连接
    
    Returns:
        pymysql.Connection: 数据库连接对象
        
    Example:
        >>> conn = get_db_connection()
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM users")
        >>> result = cursor.fetchall()
        >>> cursor.close()
        >>> conn.close()
    """
    try:
        pool = get_db_pool()
        connection = pool.connection()
        return connection
    except Exception as e:
        logger.error(f"❌ 获取数据库连接失败: {str(e)}")
        raise


class DatabaseTransaction:
    """
    数据库事务上下文管理器
    
    Example:
        >>> with DatabaseTransaction() as (conn, cursor):
        >>>     cursor.execute("INSERT INTO users ...")
        >>>     cursor.execute("INSERT INTO points ...")
        >>>     # 自动提交或回滚
    """
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """进入事务"""
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        self.conn.begin()
        return self.conn, self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出事务"""
        try:
            if exc_type is None:
                # 没有异常，提交事务
                self.conn.commit()
                logger.debug("✅ 事务提交成功")
            else:
                # 发生异常，回滚事务
                self.conn.rollback()
                logger.warning(f"⚠️ 事务回滚: {exc_val}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()


def execute_query(sql: str, params: tuple = None, fetch_one: bool = False):
    """
    执行查询并返回结果（辅助函数）
    
    Args:
        sql: SQL语句
        params: 查询参数
        fetch_one: 是否只获取一条结果
        
    Returns:
        查询结果（字典或字典列表）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 查询执行失败: {sql}, 错误: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def execute_update(sql: str, params: tuple = None) -> int:
    """
    执行更新/插入/删除操作（辅助函数）
    
    Args:
        sql: SQL语句
        params: 参数
        
    Returns:
        int: 影响的行数或插入的ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        
        # 如果是INSERT，返回插入的ID
        if sql.strip().upper().startswith('INSERT'):
            return cursor.lastrowid
        # 否则返回影响的行数
        else:
            return cursor.rowcount

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 更新执行失败: {sql}, 错误: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_pool_status() -> Dict[str, Any]:
    """
    获取数据库连接池状态信息

    Returns:
        Dict: 连接池状态信息
    """
    try:
        global _db_pool
        if not _db_pool:
            return {
                'pool_initialized': False,
                'message': '数据库连接池未初始化'
            }

        # 获取连接池的基本信息
        pool_info = {
            'pool_initialized': True,
            'max_connections': getattr(_db_pool, '_maxcached', 0),
            'min_cached': getattr(_db_pool, '_mincached', 0),
            'max_cached': getattr(_db_pool, '_maxcached', 0),
            'max_shared': getattr(_db_pool, '_maxshared', 0),
            'max_usage': getattr(_db_pool, '_maxusage', 0),
        }

        # 尝试获取当前连接数（如果可用）
        try:
            # 获取一个连接来测试连接池状态
            conn = get_db_connection()
            if conn:
                pool_info['connection_test'] = 'success'
                conn.close()
            else:
                pool_info['connection_test'] = 'failed'
        except Exception as e:
            pool_info['connection_test'] = f'error: {str(e)}'

        # 添加数据库配置信息（不包含密码）
        config = get_config()
        db_config = config.get('database', {})
        pool_info['database_info'] = {
            'host': db_config.get('host', 'unknown'),
            'port': db_config.get('port', 'unknown'),
            'database': db_config.get('database', 'unknown'),
            'charset': db_config.get('charset', 'utf8mb4'),
            'autocommit': db_config.get('autocommit', True)
        }

        return pool_info

    except Exception as e:
        logger.error(f"❌ 获取连接池状态失败: {str(e)}")
        return {
            'pool_initialized': False,
            'error': str(e)
        }

