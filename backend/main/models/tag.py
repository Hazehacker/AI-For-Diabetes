"""
标签模型
~~~~~~~

用户标签数据模型，包括：
- TagDefinition: 标签定义
- TagValue: 用户标签值
- TagHistory: 标签更新历史

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from utils.database import execute_query, execute_update, get_db_connection
from utils.logger import get_logger

logger = get_logger(__name__)


class TagDefinition:
    """
    标签定义模型
    
    对应表: user_tag_definitions
    """
    
    def __init__(self, tag_id: int = None, tag_key: str = None, tag_name: str = None,
                 tag_category: str = 'basic', tag_type: str = 'string',
                 is_coze_synced: bool = True, description: str = None,
                 default_value: str = None, **kwargs):
        self.tag_id = tag_id
        self.tag_key = tag_key
        self.tag_name = tag_name
        self.tag_category = tag_category
        self.tag_type = tag_type
        self.is_coze_synced = is_coze_synced
        self.description = description
        self.default_value = default_value
        
    @staticmethod
    def get_all(category: str = None, coze_synced_only: bool = False,
                page: int = 1, page_size: int = 50) -> Tuple[List['TagDefinition'], int]:
        """
        获取所有标签定义（支持分页）
        
        Args:
            category: 标签分类过滤
            coze_synced_only: 只获取需要同步到Coze的标签
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Tuple[List[TagDefinition], int]: (标签定义列表, 总数)
        """
        # 先获取总数
        count_sql = "SELECT COUNT(*) as total FROM user_tag_definitions WHERE is_active = TRUE"
        count_params = []

        if category:
            count_sql += " AND tag_category = %s"
            count_params.append(category)

        if coze_synced_only:
            count_sql += " AND is_coze_synced = TRUE"

        count_row = execute_query(count_sql, tuple(count_params) if count_params else None, fetch_one=True)
        total = count_row['total'] if count_row else 0

        # 获取分页数据
        sql = "SELECT * FROM user_tag_definitions WHERE is_active = TRUE"
        params = []
        
        if category:
            sql += " AND tag_category = %s"
            params.append(category)
        
        if coze_synced_only:
            sql += " AND is_coze_synced = TRUE"
        
        sql += " ORDER BY display_order, tag_id"
        
        # 添加分页
        offset = (page - 1) * page_size
        sql += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        rows = execute_query(sql, tuple(params))
        return [TagDefinition(**row) for row in rows], total
    
    @staticmethod
    def get_by_key(tag_key: str) -> Optional['TagDefinition']:
        """
        根据标签键获取定义
        
        Args:
            tag_key: 标签键
            
        Returns:
            TagDefinition: 标签定义对象
        """
        sql = "SELECT * FROM user_tag_definitions WHERE tag_key = %s AND is_active = TRUE"
        row = execute_query(sql, (tag_key,), fetch_one=True)
        return TagDefinition(**row) if row else None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'tag_id': self.tag_id,
            'tag_key': self.tag_key,
            'tag_name': self.tag_name,
            'tag_category': self.tag_category,
            'tag_type': self.tag_type,
            'is_coze_synced': self.is_coze_synced,
            'description': self.description,
            'default_value': self.default_value
        }


class TagValue:
    """
    用户标签值模型
    
    对应表: user_tag_values
    """
    
    def __init__(self, value_id: int = None, user_id: int = None, tag_id: int = None,
                 tag_value: str = None, source: str = 'manual', confidence_score: float = 1.0,
                 **kwargs):
        self.value_id = value_id
        self.user_id = user_id
        self.tag_id = tag_id
        self.tag_value = tag_value
        self.source = source
        self.confidence_score = confidence_score
    
    @staticmethod
    def get_user_tags(user_id: int, category: str = None, page: int = 1, page_size: int = 50) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取用户的所有标签（支持分页）
        
        Args:
            user_id: 用户ID
            category: 标签分类过滤
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: (标签信息列表, 总数)
        """
        # 先获取总数
        count_sql = """
            SELECT COUNT(*) as total
            FROM user_tag_definitions td
            LEFT JOIN user_tag_values tv ON td.tag_id = tv.tag_id AND tv.user_id = %s
            WHERE td.is_active = TRUE
        """
        count_params = [user_id]

        if category:
            count_sql += " AND td.tag_category = %s"
            count_params.append(category)

        count_row = execute_query(count_sql, tuple(count_params), fetch_one=True)
        total = count_row['total'] if count_row else 0

        # 获取分页数据
        sql = """
            SELECT 
                td.tag_id,
                td.tag_key,
                td.tag_name,
                td.tag_category,
                td.tag_type,
                COALESCE(tv.tag_value, td.default_value) as tag_value,
                tv.source,
                tv.confidence_score,
                tv.last_updated
            FROM user_tag_definitions td
            LEFT JOIN user_tag_values tv ON td.tag_id = tv.tag_id AND tv.user_id = %s
            WHERE td.is_active = TRUE
        """
        params = [user_id]
        
        if category:
            sql += " AND td.tag_category = %s"
            params.append(category)
        
        sql += " ORDER BY td.display_order"
        
        # 添加分页
        offset = (page - 1) * page_size
        sql += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        return execute_query(sql, tuple(params)), total
    
    @staticmethod
    def set_value(user_id: int, tag_key: str, tag_value: str, 
                  source: str = 'manual', confidence_score: float = 1.0,
                  conversation_id: str = None) -> bool:
        """
        设置用户标签值
        
        Args:
            user_id: 用户ID
            tag_key: 标签键
            tag_value: 标签值
            source: 数据来源
            confidence_score: 置信度
            conversation_id: 关联的对话ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取tag_id
            tag_def = TagDefinition.get_by_key(tag_key)
            if not tag_def:
                logger.warning(f"标签 {tag_key} 不存在")
                return False
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 查询旧值（用于历史记录）
            cursor.execute(
                "SELECT tag_value FROM user_tag_values WHERE user_id = %s AND tag_id = %s",
                (user_id, tag_def.tag_id)
            )
            old_value_row = cursor.fetchone()
            old_value = old_value_row['tag_value'] if old_value_row else None
            
            # 插入或更新标签值
            sql = """
                INSERT INTO user_tag_values (user_id, tag_id, tag_value, source, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    tag_value = VALUES(tag_value),
                    source = VALUES(source),
                    confidence_score = VALUES(confidence_score),
                    last_updated = CURRENT_TIMESTAMP
            """
            cursor.execute(sql, (user_id, tag_def.tag_id, tag_value, source, confidence_score))
            
            # 记录历史
            if old_value != tag_value:  # 只有值变化时才记录
                TagHistory.add_history(
                    user_id, tag_def.tag_id, old_value, tag_value,
                    source, confidence_score, conversation_id
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 用户 {user_id} 标签 {tag_key} 更新成功: {tag_value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 设置标签值失败: {str(e)}")
            return False
    
    @staticmethod
    def get_coze_sync_tags(user_id: int) -> List[Dict[str, Any]]:
        """
        获取需要同步到Coze的标签

        Args:
            user_id: 用户ID

        Returns:
            List[Dict]: 标签列表（Coze变量格式）
        """
        sql = """
            SELECT
                td.tag_key as name,
                COALESCE(tv.tag_value, td.default_value) as value,
                td.tag_name as description
            FROM user_tag_definitions td
            LEFT JOIN user_tag_values tv ON td.tag_id = tv.tag_id AND tv.user_id = %s
            WHERE td.is_active = TRUE AND td.is_coze_synced = TRUE
            ORDER BY td.display_order
        """
        return execute_query(sql, (user_id,))

    @staticmethod
    def delete_value(user_id: int, tag_key: str) -> bool:
        """
        删除用户标签值（重置为默认值）

        Args:
            user_id: 用户ID
            tag_key: 标签键

        Returns:
            bool: 是否成功
        """
        try:
            # 获取tag_id
            tag_def = TagDefinition.get_by_key(tag_key)
            if not tag_def:
                logger.warning(f"标签 {tag_key} 不存在")
                return False

            # 查询旧值（用于历史记录）
            old_value_row = execute_query(
                "SELECT tag_value FROM user_tag_values WHERE user_id = %s AND tag_id = %s",
                (user_id, tag_def.tag_id), fetch_one=True
            )
            old_value = old_value_row['tag_value'] if old_value_row else None

            # 删除标签值记录
            sql = "DELETE FROM user_tag_values WHERE user_id = %s AND tag_id = %s"
            execute_update(sql, (user_id, tag_def.tag_id))

            # 记录历史
            if old_value is not None:  # 只有原来有值时才记录历史
                TagHistory.add_history(
                    user_id, tag_def.tag_id, old_value, tag_def.default_value,
                    'manual', 1.0, None
                )

            logger.info(f"✅ 用户 {user_id} 标签 {tag_key} 删除成功")
            return True

        except Exception as e:
            logger.error(f"❌ 删除标签值失败: {str(e)}")
            return False

    @staticmethod
    def delete_user_tags(user_id: int, tag_keys: List[str] = None) -> Dict[str, Any]:
        """
        批量删除用户标签值

        Args:
            user_id: 用户ID
            tag_keys: 要删除的标签键列表，如果为None则删除所有标签

        Returns:
            Dict: 操作结果
        """
        try:
            if tag_keys:
                # 删除指定标签
                deleted_count = 0
                for tag_key in tag_keys:
                    if TagValue.delete_value(user_id, tag_key):
                        deleted_count += 1

                return {
                    'success': True,
                    'message': f'成功删除 {deleted_count}/{len(tag_keys)} 个标签',
                    'deleted_count': deleted_count,
                    'total_requested': len(tag_keys)
                }
            else:
                # 删除所有标签
                sql = "DELETE FROM user_tag_values WHERE user_id = %s"
                deleted_count = execute_update(sql, (user_id,))

                return {
                    'success': True,
                    'message': f'成功清空所有标签，共删除 {deleted_count} 个标签',
                    'deleted_count': deleted_count
                }

        except Exception as e:
            logger.error(f"❌ 批量删除标签失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }


class TagHistory:
    """
    标签更新历史模型
    
    对应表: user_tag_history
    """
    
    @staticmethod
    def add_history(user_id: int, tag_id: int, old_value: str, new_value: str,
                    source: str, confidence_score: float = None,
                    conversation_id: str = None) -> bool:
        """
        添加标签更新历史记录
        
        Args:
            user_id: 用户ID
            tag_id: 标签ID
            old_value: 旧值
            new_value: 新值
            source: 来源
            confidence_score: 置信度
            conversation_id: 对话ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                INSERT INTO user_tag_history 
                (user_id, tag_id, old_value, new_value, source, confidence_score, conversation_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_update(sql, (user_id, tag_id, old_value, new_value, 
                                source, confidence_score, conversation_id))
            return True
        except Exception as e:
            logger.error(f"❌ 添加标签历史失败: {str(e)}")
            return False
    
    @staticmethod
    def get_user_history(user_id: int, page: int = 1, page_size: int = 50) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取用户的标签更新历史（支持分页）
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Tuple[List[Dict], int]: (历史记录列表, 总数)
        """
        # 先获取总数
        count_sql = """
            SELECT COUNT(*) as total
            FROM user_tag_history h
            WHERE h.user_id = %s
        """
        count_row = execute_query(count_sql, (user_id,), fetch_one=True)
        total = count_row['total'] if count_row else 0

        # 获取分页数据
        offset = (page - 1) * page_size
        sql = """
            SELECT 
                h.*,
                td.tag_key,
                td.tag_name
            FROM user_tag_history h
            JOIN user_tag_definitions td ON h.tag_id = td.tag_id
            WHERE h.user_id = %s
            ORDER BY h.updated_at DESC
            LIMIT %s OFFSET %s
        """
        return execute_query(sql, (user_id, page_size, offset)), total


# 别名：为了兼容性
Tag = TagValue

