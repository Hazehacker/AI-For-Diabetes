"""
TTS缓存模型
~~~~~~~~~~~

TTS缓存相关的数据模型，包括：
- TTSCache: 缓存元数据
- TTSCacheStats: 缓存统计

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import json
from utils.database import execute_query, execute_update, get_db_connection, DatabaseTransaction
from utils.logger import get_logger

logger = get_logger(__name__)


class TTSCache:
    """
    TTS缓存元数据模型

    对应表: tts_cache
    """

    def __init__(self, cache_id: int = None, text_content: str = None,
                 voice_id: str = None, speed: float = 1.0,
                 sample_rate: int = 16000, cache_path: str = None,
                 file_size: int = None, codec: str = 'mp3',
                 created_at: datetime = None, last_accessed: datetime = None,
                 access_count: int = 0, is_active: bool = True, **kwargs):
        self.cache_id = cache_id
        self.text_content = text_content
        self.voice_id = voice_id
        self.speed = speed
        self.sample_rate = sample_rate
        self.cache_path = cache_path
        self.file_size = file_size
        self.codec = codec
        self.created_at = created_at
        self.last_accessed = last_accessed
        self.access_count = access_count
        self.is_active = is_active

    @staticmethod
    def generate_cache_key(text: str, voice_id: str, speed: float,
                          sample_rate: int = 16000, codec: str = 'mp3') -> str:
        """
        生成缓存key

        Args:
            text: 文本内容
            voice_id: 语音ID
            speed: 语速
            sample_rate: 采样率
            codec: 编码格式

        Returns:
            str: MD5缓存key
        """
        # 使用实际的TTS参数生成缓存key，确保相同音色能正确复用
        # 这里需要和tts_service.py中的逻辑保持一致
        from utils.config_loader import get_config as _get_config

        # 获取默认TTS语音类型
        default_voice_type = _get_config('TENCENT_TTS.VOICE_TYPE')
        if not default_voice_type:
            default_voice_type = "7426720361753903141"

        # 转换voice_id为实际的TTS voice_type
        if voice_id and voice_id.isdigit() and len(voice_id) == 6:
            actual_voice_type = voice_id
        else:
            actual_voice_type = default_voice_type

        # 将speed转换为TTS实际使用的speed值
        if speed <= 0.5:
            tts_speed = -2
        elif speed >= 2.0:
            tts_speed = 6
        else:
            tts_speed = int((speed - 0.5) / 1.5 * 8 - 2)
            tts_speed = max(-2, min(6, tts_speed))

        # 生成唯一的缓存key（使用实际的TTS参数）
        cache_key = f"{text}_{actual_voice_type}_{tts_speed}_{sample_rate}_{codec}"
        return hashlib.md5(cache_key.encode()).hexdigest()

    @staticmethod
    def find_cache(text: str, voice_id: str, speed: float,
                  sample_rate: int = 16000, codec: str = 'mp3') -> Optional['TTSCache']:
        """
        查找缓存记录

        Args:
            text: 文本内容
            voice_id: 语音ID
            speed: 语速
            sample_rate: 采样率
            codec: 编码格式

        Returns:
            TTSCache: 缓存记录，不存在返回None
        """
        try:
            # 直接使用文本内容进行精确匹配（避免MD5哈希冲突）
            sql = """
                SELECT * FROM tts_cache
                WHERE text_content = %s
                  AND voice_id = %s
                  AND speed = %s
                  AND sample_rate = %s
                  AND codec = %s
                  AND is_active = TRUE
                ORDER BY last_accessed DESC
                LIMIT 1
            """

            row = execute_query(sql, (text, voice_id, speed, sample_rate, codec), fetch_one=True)

            if row:
                # 更新访问时间和访问次数
                TTSCache.update_access(row['cache_id'])
                return TTSCache(**row)

            return None

        except Exception as e:
            logger.error(f"❌ 查找缓存记录失败: {str(e)}")
            return None

    @staticmethod
    def add_cache(text: str, voice_id: str, speed: float, cache_path: str,
                 file_size: int = None, sample_rate: int = 16000,
                 codec: str = 'mp3') -> Optional['TTSCache']:
        """
        添加缓存记录

        Args:
            text: 文本内容
            voice_id: 语音ID
            speed: 语速
            cache_path: 缓存文件路径
            file_size: 文件大小
            sample_rate: 采样率
            codec: 编码格式

        Returns:
            TTSCache: 创建的缓存记录
        """
        try:
            # 检查是否已存在相同记录（应用层唯一性检查）
            existing = TTSCache.find_cache(text, voice_id, speed, sample_rate, codec)
            if existing:
                # 更新文件路径和大小
                TTSCache.update_cache_path(existing.cache_id, cache_path, file_size)
                return existing

            sql = """
                INSERT INTO tts_cache
                (text_content, voice_id, speed, sample_rate, cache_path, file_size, codec)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            execute_update(sql, (text, voice_id, speed, sample_rate, cache_path, file_size, codec))

            logger.info(f"✅ 添加TTS缓存记录: {text[:50]}... -> {cache_path}")
            return TTSCache.find_cache(text, voice_id, speed, sample_rate, codec)

        except Exception as e:
            logger.error(f"❌ 添加缓存记录失败: {str(e)}")
            return None

    @staticmethod
    def update_access(cache_id: int) -> bool:
        """
        更新缓存访问信息

        Args:
            cache_id: 缓存ID

        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                UPDATE tts_cache
                SET last_accessed = CURRENT_TIMESTAMP,
                    access_count = access_count + 1
                WHERE cache_id = %s
            """
            execute_update(sql, (cache_id,))
            return True
        except Exception as e:
            logger.error(f"❌ 更新缓存访问信息失败: {str(e)}")
            return False

    @staticmethod
    def update_cache_path(cache_id: int, cache_path: str, file_size: int = None) -> bool:
        """
        更新缓存文件路径和大小

        Args:
            cache_id: 缓存ID
            cache_path: 新文件路径
            file_size: 文件大小

        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                UPDATE tts_cache
                SET cache_path = %s, file_size = %s, last_accessed = CURRENT_TIMESTAMP
                WHERE cache_id = %s
            """
            execute_update(sql, (cache_path, file_size, cache_id))
            return True
        except Exception as e:
            logger.error(f"❌ 更新缓存路径失败: {str(e)}")
            return False

    @staticmethod
    def deactivate_cache(cache_id: int) -> bool:
        """
        标记缓存为无效

        Args:
            cache_id: 缓存ID

        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE tts_cache SET is_active = FALSE WHERE cache_id = %s"
            execute_update(sql, (cache_id,))
            logger.info(f"✅ 标记缓存无效: {cache_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 标记缓存无效失败: {str(e)}")
            return False

    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            # 基本统计
            sql = """
                SELECT
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size_bytes,
                    AVG(file_size) as avg_file_size,
                    MAX(created_at) as newest_cache,
                    MIN(created_at) as oldest_cache
                FROM tts_cache
                WHERE is_active = TRUE
            """

            stats = execute_query(sql, fetch_one=True) or {}

            # 访问统计
            sql_access = """
                SELECT
                    SUM(access_count) as total_accesses,
                    AVG(access_count) as avg_access_count,
                    MAX(last_accessed) as last_access_time
                FROM tts_cache
                WHERE is_active = TRUE
            """

            access_stats = execute_query(sql_access, fetch_one=True) or {}

            return {
                'total_files': stats.get('total_files', 0),
                'total_size_bytes': stats.get('total_size_bytes', 0),
                'total_size_mb': round((stats.get('total_size_bytes', 0) or 0) / (1024 * 1024), 2),
                'avg_file_size': stats.get('avg_file_size', 0),
                'newest_cache': stats.get('newest_cache'),
                'oldest_cache': stats.get('oldest_cache'),
                'total_accesses': access_stats.get('total_accesses', 0),
                'avg_access_count': round(access_stats.get('avg_access_count', 0) or 0, 2),
                'last_access_time': access_stats.get('last_access_time')
            }

        except Exception as e:
            logger.error(f"❌ 获取缓存统计失败: {str(e)}")
            return {}

    @staticmethod
    def cleanup_expired(older_than_days: int = 30) -> int:
        """
        清理过期缓存记录

        Args:
            older_than_days: 清理多少天前的缓存

        Returns:
            int: 清理的记录数量
        """
        try:
            sql = """
                UPDATE tts_cache
                SET is_active = FALSE
                WHERE last_accessed < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %s DAY)
                  AND is_active = TRUE
            """
            result = execute_update(sql, (older_than_days,))
            logger.info(f"✅ 清理过期缓存记录: {result} 条")
            return result
        except Exception as e:
            logger.error(f"❌ 清理过期缓存失败: {str(e)}")
            return 0

    @staticmethod
    def search_similar_text(search_text: str, limit: int = 10) -> List['TTSCache']:
        """
        搜索相似文本的缓存记录

        Args:
            search_text: 搜索文本
            limit: 返回结果数量限制

        Returns:
            List[TTSCache]: 相似缓存记录列表
        """
        try:
            # 使用LIKE进行简单文本搜索
            sql = """
                SELECT * FROM tts_cache
                WHERE text_content LIKE %s
                  AND is_active = TRUE
                ORDER BY last_accessed DESC
                LIMIT %s
            """

            search_pattern = f"%{search_text}%"
            rows = execute_query(sql, (search_pattern, limit))

            return [TTSCache(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ 搜索相似文本失败: {str(e)}")
            return []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'cache_id': self.cache_id,
            'text_content': self.text_content,
            'voice_id': self.voice_id,
            'speed': self.speed,
            'sample_rate': self.sample_rate,
            'cache_path': self.cache_path,
            'file_size': self.file_size,
            'codec': self.codec,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count,
            'is_active': self.is_active
        }


class TTSCacheStats:
    """
    TTS缓存统计模型

    对应表: tts_cache_stats
    """

    def __init__(self, stat_id: int = None, date: str = None,
                 total_requests: int = 0, cache_hits: int = 0,
                 cache_misses: int = 0, total_files: int = 0,
                 total_size_mb: float = 0.0, hit_rate: float = 0.0, **kwargs):
        self.stat_id = stat_id
        self.date = date
        self.total_requests = total_requests
        self.cache_hits = cache_hits
        self.cache_misses = cache_misses
        self.total_files = total_files
        self.total_size_mb = total_size_mb
        self.hit_rate = hit_rate

    @staticmethod
    def record_request(hit: bool = False) -> bool:
        """
        记录一次请求

        Args:
            hit: 是否缓存命中

        Returns:
            bool: 是否成功
        """
        try:
            today = datetime.now().date().isoformat()

            if hit:
                sql = """
                    INSERT INTO tts_cache_stats (date, total_requests, cache_hits, cache_misses, hit_rate)
                    VALUES (%s, 1, 1, 0, 100.00)
                    ON DUPLICATE KEY UPDATE
                        total_requests = total_requests + 1,
                        cache_hits = cache_hits + 1,
                        hit_rate = (cache_hits + 1) / (total_requests + 1) * 100
                """
            else:
                sql = """
                    INSERT INTO tts_cache_stats (date, total_requests, cache_hits, cache_misses, hit_rate)
                    VALUES (%s, 1, 0, 1, 0.00)
                    ON DUPLICATE KEY UPDATE
                        total_requests = total_requests + 1,
                        cache_misses = cache_misses + 1,
                        hit_rate = cache_hits / (total_requests + 1) * 100
                """

            execute_update(sql, (today,))
            return True

        except Exception as e:
            logger.error(f"❌ 记录请求统计失败: {str(e)}")
            return False

    @staticmethod
    def update_daily_stats() -> bool:
        """
        更新每日统计数据

        Returns:
            bool: 是否成功
        """
        try:
            today = datetime.now().date().isoformat()

            # 获取当天的缓存统计
            cache_stats = TTSCache.get_cache_stats()

            sql = """
                UPDATE tts_cache_stats
                SET total_files = %s, total_size_mb = %s
                WHERE date = %s
            """

            execute_update(sql, (
                cache_stats['total_files'],
                cache_stats['total_size_mb'],
                today
            ))

            return True

        except Exception as e:
            logger.error(f"❌ 更新每日统计失败: {str(e)}")
            return False

    @staticmethod
    def get_stats_history(days: int = 30) -> List['TTSCacheStats']:
        """
        获取统计历史

        Args:
            days: 获取多少天的历史

        Returns:
            List[TTSCacheStats]: 统计历史列表
        """
        try:
            sql = """
                SELECT * FROM tts_cache_stats
                WHERE date >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
                ORDER BY date DESC
            """

            rows = execute_query(sql, (days,))
            return [TTSCacheStats(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ 获取统计历史失败: {str(e)}")
            return []
