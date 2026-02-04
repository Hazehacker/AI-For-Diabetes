"""
标签管理服务
~~~~~~~~~~~

用户标签管理服务，包括：
- 标签CRUD
- 标签同步到Coze
- AI标签提取
- 批量标签操作

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any
from models.tag import TagDefinition, TagValue, TagHistory
from utils.logger import get_logger
from utils.decorators import log_execution_time
from utils.database import execute_query

logger = get_logger(__name__)


class TagService:
    """
    标签管理服务类
    """
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def get_user_tags(
        self,
        user_id: int,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        获取用户的所有标签（支持分页）
        
        Args:
            user_id: 用户ID
            category: 标签分类过滤
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Dict: 标签信息
        """
        try:
            tags, total = TagValue.get_user_tags(user_id, category, page, page_size)
            
            # 按分类分组
            grouped_tags = {
                'basic': [],
                'health': [],
                'behavior': [],
                'stats': []
            }
            
            for tag in tags:
                cat = tag.get('tag_category', 'basic')
                if cat in grouped_tags:
                    grouped_tags[cat].append(tag)
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1

            return {
                'code': 200,
                'data': {
                    'user_id': user_id,
                    'tags': grouped_tags,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户标签失败: {str(e)}")
            return {
                'code': 500,
                'data': {
                    'user_id': user_id,
                    'tags': {'basic': [], 'health': [], 'behavior': [], 'stats': []},
                    'total': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0,
                    'has_next': False,
                    'has_prev': False
                },
                'success': False,
                'message': str(e)
            }
    
    def set_user_tag(
        self,
        user_id: int,
        tag_key: str,
        tag_value: str,
        source: str = 'manual',
        conversation_id: str = None,
        auto_sync_coze: bool = False
    ) -> Dict[str, Any]:
        """
        设置用户标签

        Args:
            user_id: 用户ID
            tag_key: 标签键
            tag_value: 标签值
            source: 数据来源
            conversation_id: 关联的对话ID
            auto_sync_coze: 是否自动同步到Coze

        Returns:
            Dict: 操作结果
        """
        try:
            logger.info(f"🔧 TagService.set_user_tag: user_id={user_id}, tag_key={tag_key}, tag_value={tag_value}, source={source}")
            # 设置标签
            success = TagValue.set_value(
                user_id=user_id,
                tag_key=tag_key,
                tag_value=tag_value,
                source=source,
                conversation_id=conversation_id
            )
            
            if not success:
                return {
                    'code': 500,
                    'data': {},
                    'success': False,
                    'message': '设置标签失败'
                }
            
            # 自动同步到Coze
            if auto_sync_coze:
                tag_def = TagDefinition.get_by_key(tag_key)
                if tag_def and tag_def.is_coze_synced:
                    self._sync_single_tag_to_coze(user_id, tag_key, tag_value)
            
            return {
                'code': 200,
                'data': {
                    'tag_key': tag_key,
                    'tag_value': tag_value
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ 设置标签失败: {str(e)}")
            return {
                'code': 500,
                'data': {},
                'success': False,
                'message': str(e)
            }
    
    def batch_set_tags(
        self,
        user_id: int,
        tags: Dict[str, str],
        source: str = 'manual'
    ) -> Dict[str, Any]:
        """
        批量设置标签
        
        Args:
            user_id: 用户ID
            tags: {tag_key: tag_value}
            source: 数据来源
            
        Returns:
            Dict: 操作结果
        """
        success_count = 0
        failed_tags = []
        
        for tag_key, tag_value in tags.items():
            result = self.set_user_tag(
                user_id, tag_key, tag_value,
                source=source,
                auto_sync_coze=False  # 批量操作时最后统一同步
            )
            
            if result['success']:
                success_count += 1
            else:
                failed_tags.append(tag_key)
        
        # 批量同步到Coze（失败不影响结果）
        try:
            self.sync_user_tags_to_coze(user_id)
        except Exception as e:
            logger.warning(f"⚠️ 批量标签设置成功，但Coze同步失败: {str(e)}")
        
        return {
            'code': 200,
            'data': {
                'total': len(tags),
                'success_count': success_count,
                'failed_count': len(failed_tags),
                'failed_tags': failed_tags
            },
            'success': True
        }
    
    @log_execution_time
    def sync_user_tags_to_coze(self, user_id: int) -> bool:
        """
        同步用户标签到Coze

        注意：根据用户要求，标签服务不再依赖Coze，此方法仅返回成功，不执行实际同步

        Args:
            user_id: 用户ID

        Returns:
            bool: 始终返回True（标签功能正常）
        """
        # 完全禁用Coze同步，只记录信息日志
        logger.info(f"ℹ️ 用户 {user_id} 标签同步已跳过 (Coze同步已禁用)")
        return True
    
    def _sync_single_tag_to_coze(
        self,
        user_id: int,
        tag_key: str,
        tag_value: str
    ):
        """
        同步单个标签到Coze

        注意：根据用户要求，标签服务不再依赖Coze，此方法仅记录日志，不执行实际同步

        Args:
            user_id: 用户ID
            tag_key: 标签键
            tag_value: 标签值
        """
        # 完全禁用Coze同步，只记录信息日志
        logger.info(f"ℹ️ 标签 {tag_key} 设置成功 (Coze同步已禁用)")
    
    def get_tag_definitions(self, category: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict:
        """
        获取所有标签定义（支持分页）
        
        Args:
            category: 分类过滤
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Dict: 包含分页信息的标签定义列表
        """
        try:
            definitions, total = TagDefinition.get_all(category=category, page=page, page_size=page_size)

            # 计算总页数
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1

            return {
                'code': 200,
                'data': {
                    'definitions': [d.to_dict() for d in definitions],
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                },
                'success': True
            }
        except Exception as e:
            logger.error(f"❌ 获取标签定义失败: {str(e)}")
            return {
                'code': 500,
                'data': {
                    'definitions': [],
                    'total': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0,
                    'has_next': False,
                    'has_prev': False
                },
                'success': False,
                'message': str(e)
            }
    
    def get_tag_history(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        获取标签更新历史（支持分页）
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Dict: 历史记录数据（包含分页信息）
        """
        try:
            history, total = TagHistory.get_user_history(user_id, page, page_size)

            # 计算总页数
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1

            return {
                "records": history,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        except Exception as e:
            logger.error(f"❌ 获取标签历史失败: {str(e)}")
            raise
        
    
    def extract_tags_from_conversation(
        self,
        user_id: int,
        conversation_id: str,
        message_content: str
    ) -> Dict[str, Any]:
        """
        从对话中提取标签（AI驱动）
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID
            message_content: 消息内容
            
        Returns:
            Dict: 提取结果
        """
        # 这里可以集成AI模型或使用规则引擎
        # 暂时使用简单的关键词匹配
        
        extracted_tags = {}
        content_lower = message_content.lower()
        
        # 运动相关
        if any(word in content_lower for word in ['运动', '锻炼', '跑步', '走路']):
            extracted_tags['exercise_frequency'] = '有运动习惯'
        
        # 饮食相关
        if any(word in content_lower for word in ['饮食', '吃', '食物']):
            extracted_tags['diet_habits'] = '关注饮食'
        
        # 血糖相关
        if any(word in content_lower for word in ['血糖', '测血糖']):
            extracted_tags['blood_glucose_control'] = '关注血糖'
        
        # 保存提取的标签
        for tag_key, tag_value in extracted_tags.items():
            self.set_user_tag(
                user_id=user_id,
                tag_key=tag_key,
                tag_value=tag_value,
                source='ai_extract',
                auto_sync_coze=False
            )
        
        # 批量同步
        if extracted_tags:
            self.sync_user_tags_to_coze(user_id)
        
        return {
            'code': 200,
            'data': {
                'user_id': user_id,
                'extracted_count': len(extracted_tags),
                'tags': extracted_tags
            },
            'success': True
        }

    def delete_user_tag(
        self,
        user_id: int,
        tag_key: str
    ) -> Dict[str, Any]:
        """
        删除用户标签（重置为默认值）

        Args:
            user_id: 用户ID
            tag_key: 标签键

        Returns:
            Dict: 操作结果
        """
        try:
            success = TagValue.delete_value(user_id, tag_key)

            if success:
                # 同步到Coze（如果标签原本存在且需要同步）
                tag_def = TagDefinition.get_by_key(tag_key)
                if tag_def and tag_def.is_coze_synced:
                    self.sync_user_tags_to_coze(user_id)

                return {
                    'code': 200,
                    'data': {
                        'tag_key': tag_key
                    },
                    'success': True
                }
            else:
                return {
                    'code': 500,
                    'data': {},
                    'success': False,
                    'message': f'标签 {tag_key} 删除失败或标签不存在',
                }

        except Exception as e:
            logger.error(f"❌ 删除用户标签失败: {str(e)}")
            return {
                'code': 500,
                'data': {},
                'success': False,
                'message': str(e)
            }

    def batch_delete_tags(
        self,
        user_id: int,
        tag_keys: List[str] = None
    ) -> Dict[str, Any]:
        """
        批量删除用户标签

        Args:
            user_id: 用户ID
            tag_keys: 要删除的标签键列表，如果为None则删除所有标签

        Returns:
            Dict: 操作结果
        """
        try:
            result = TagValue.delete_user_tags(user_id, tag_keys)

            if result['success'] and result.get('deleted_count', 0) > 0:
                # 同步到Coze
                self.sync_user_tags_to_coze(user_id)

            return {
                'code': 200,
                'data': result,
                'success': True
            }

        except Exception as e:
            logger.error(f"❌ 批量删除标签失败: {str(e)}")
            return {
                'code': 500,
                'data': {},
                'success': False,
                'message': str(e)
            }

    def clear_all_user_tags(self, user_id: int) -> Dict[str, Any]:
        """
        清空用户所有标签

        Args:
            user_id: 用户ID

        Returns:
            Dict: 操作结果
        """
        try:
            result = TagValue.delete_user_tags(user_id, None)
            return {
                'code': 200,
                'data': {
                    'deleted_count': result.get('deleted_count', 0)
                },
                'success': True,
                'message': result.get('message', f'成功清空用户 {user_id} 的所有标签')
            }
        except Exception as e:
            logger.error(f"❌ 清空用户标签失败: {str(e)}")
            return {
                'code': 500,
                'data': {},
                'success': False,
                'message': str(e)
            }

    def get_user_tag_mappings(
        self,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        phone_number: Optional[str] = None,
        tag_key: Optional[str] = None,
        tag_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户和标签的映射关系列表（支持筛选和分页）

        Args:
            page: 页码
            page_size: 每页数量
            user_id: 用户ID（可选，精确匹配）
            username: 用户名或昵称（可选，支持模糊搜索，会同时搜索username和nickname字段）
            phone_number: 手机号（可选，支持模糊搜索）
            tag_key: 标签键（可选，筛选特定标签）
            tag_category: 标签分类（可选）

        Returns:
            Dict: 映射关系列表
        """
        try:
            offset = (page - 1) * page_size

            # 构建查询条件
            where_conditions = []
            params = []

            # user_id 精确匹配（可选）
            if user_id:
                try:
                    user_id = int(user_id)
                    where_conditions.append("u.user_id = %s")
                    params.append(user_id)
                except (ValueError, TypeError):
                    pass

            # username 模糊搜索（可选）
            if username:
                username = username.strip()
                if username:
                    where_conditions.append("(u.username LIKE %s OR u.nickname LIKE %s)")
                    params.append(f"%{username}%")
                    params.append(f"%{username}%")

            # phone_number 模糊搜索（可选）
            if phone_number:
                phone_number = phone_number.strip()
                if phone_number:
                    where_conditions.append("u.phone_number LIKE %s")
                    params.append(f"%{phone_number}%")

            if tag_key:
                where_conditions.append("td.tag_key = %s")
                params.append(tag_key)

            if tag_category:
                where_conditions.append("td.tag_category = %s")
                params.append(tag_category)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            # 查询总数
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM users u
                CROSS JOIN user_tag_definitions td
                LEFT JOIN user_tag_values tv ON u.user_id = tv.user_id AND td.tag_id = tv.tag_id
                {where_clause}
            """
            total = execute_query(count_sql, tuple(params) if params else None, fetch_one=True)['total']
            
            # 查询列表
            list_sql = f"""
                SELECT 
                    u.user_id,
                    u.username,
                    u.nickname,
                    u.phone_number,
                    td.tag_id,
                    td.tag_key,
                    td.tag_name,
                    td.tag_category,
                    td.tag_type,
                    COALESCE(tv.tag_value, td.default_value) as tag_value,
                    tv.source,
                    tv.confidence_score,
                    tv.last_updated
                FROM users u
                CROSS JOIN user_tag_definitions td
                LEFT JOIN user_tag_values tv ON u.user_id = tv.user_id AND td.tag_id = tv.tag_id
                {where_clause}
                ORDER BY u.user_id, td.display_order
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            mappings = execute_query(list_sql, tuple(params))
            
            return {
                'success': True,
                'total': total,
                'page': page,
                'page_size': page_size,
                'mappings': mappings
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户标签映射关系失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def export_user_tag_mappings(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        phone_number: Optional[str] = None,
        tag_key: Optional[str] = None,
        tag_category: Optional[str] = None,
        format: str = 'excel'
    ) -> Dict[str, Any]:
        """
        导出用户和标签的映射关系

        Args:
            user_id: 用户ID（可选，精确匹配）
            username: 用户名或昵称（可选，支持模糊搜索，会同时搜索username和nickname字段）
            phone_number: 手机号（可选，支持模糊搜索）
            tag_key: 标签键（可选，筛选特定标签）
            tag_category: 标签分类（可选）
            format: 导出格式（csv或excel，默认excel）

        Returns:
            Dict: 导出结果
        """
        try:
            # 构建查询条件
            where_conditions = []
            params = []

            # user_id 精确匹配（可选）
            if user_id:
                try:
                    user_id = int(user_id)
                    where_conditions.append("u.user_id = %s")
                    params.append(user_id)
                except (ValueError, TypeError):
                    pass

            # username 模糊搜索（可选）
            if username:
                username = username.strip()
                if username:
                    where_conditions.append("(u.username LIKE %s OR u.nickname LIKE %s)")
                    params.append(f"%{username}%")
                    params.append(f"%{username}%")

            # phone_number 模糊搜索（可选）
            if phone_number:
                phone_number = phone_number.strip()
                if phone_number:
                    where_conditions.append("u.phone_number LIKE %s")
                    params.append(f"%{phone_number}%")

            if tag_key:
                where_conditions.append("td.tag_key = %s")
                params.append(tag_key)
            
            if tag_category:
                where_conditions.append("td.tag_category = %s")
                params.append(tag_category)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            # 查询所有数据
            sql = f"""
                SELECT 
                    u.user_id,
                    u.username,
                    u.nickname,
                    u.phone_number,
                    td.tag_key,
                    td.tag_name,
                    td.tag_category,
                    COALESCE(tv.tag_value, td.default_value) as tag_value,
                    tv.source,
                    tv.last_updated
                FROM users u
                CROSS JOIN user_tag_definitions td
                LEFT JOIN user_tag_values tv ON u.user_id = tv.user_id AND td.tag_id = tv.tag_id
                {where_clause}
                ORDER BY u.user_id, td.display_order
            """
            mappings = execute_query(sql, tuple(params) if params else None)
            
            if format.lower() == 'csv':
                # 导出为CSV
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow(['用户ID', '用户名', '用户昵称', '手机号', '标签键', '标签名称', '标签分类', '标签值', '数据来源', '更新时间'])
                
                # 写入数据
                for mapping in mappings:
                    writer.writerow([
                        mapping.get('user_id', ''),
                        mapping.get('username', ''),
                        mapping.get('nickname', ''),
                        mapping.get('phone_number', ''),
                        mapping.get('tag_key', ''),
                        mapping.get('tag_name', ''),
                        mapping.get('tag_category', ''),
                        mapping.get('tag_value', ''),
                        mapping.get('source', ''),
                        str(mapping.get('last_updated', '')) if mapping.get('last_updated') else ''
                    ])
                
                output.seek(0)
                
                return {
                    'success': True,
                    'data': {
                        'content': output.getvalue(),
                        'mimetype': 'text/csv',
                        'filename': 'user_tag_mappings.csv'
                    }
                }
            else:
                # 导出为Excel
                import pandas as pd
                from io import BytesIO
                
                # 转换为DataFrame
                data = []
                for mapping in mappings:
                    data.append({
                        '用户ID': mapping.get('user_id', ''),
                        '用户名': mapping.get('username', ''),
                        '用户昵称': mapping.get('nickname', ''),
                        '手机号': mapping.get('phone_number', ''),
                        '标签键': mapping.get('tag_key', ''),
                        '标签名称': mapping.get('tag_name', ''),
                        '标签分类': mapping.get('tag_category', ''),
                        '标签值': mapping.get('tag_value', ''),
                        '数据来源': mapping.get('source', ''),
                        '更新时间': str(mapping.get('last_updated', '')) if mapping.get('last_updated') else ''
                    })
                
                df = pd.DataFrame(data)
                
                # 创建Excel文件
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='用户标签映射', index=False)
                    
                    # 获取工作簿和工作表
                    workbook = writer.book
                    worksheet = writer.sheets['用户标签映射']
                    
                    # 设置列宽
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                output.seek(0)
                
                return {
                    'success': True,
                    'data': {
                        'content': output.getvalue(),
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'filename': 'user_tag_mappings.xlsx'
                    }
                }
            
        except Exception as e:
            logger.error(f"❌ 导出用户标签映射关系失败: {str(e)}")
            return {'success': False, 'message': str(e)}


# 全局单例
_tag_service_instance = None

def get_tag_service() -> TagService:
    """获取标签服务单例"""
    global _tag_service_instance
    if _tag_service_instance is None:
        _tag_service_instance = TagService()
    return _tag_service_instance

