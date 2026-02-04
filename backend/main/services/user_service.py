"""
用户管理服务
~~~~~~~~~~~

用户信息管理服务，包括：
- 用户信息查询
- 用户信息更新
- 用户列表
- 用户状态管理

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any
from utils.database import get_db_connection, DatabaseTransaction, execute_query
from utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """用户管理服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户信息
        """
        try:
            sql = """
                SELECT user_id, username, nickname, email, phone_number,
                       date_of_birth, created_at, last_login, is_active
                FROM users
                WHERE user_id = %s
            """
            result = execute_query(sql, (user_id,), fetch_one=True)
            
            # 格式化日期字段
            if result and result.get('date_of_birth'):
                from datetime import date
                if isinstance(result['date_of_birth'], date):
                    result['date_of_birth'] = result['date_of_birth'].isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 获取用户信息失败: {str(e)}")
            return None
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户完整资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户资料
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 获取用户标签
            from services.tag_service import get_tag_service
            tag_service = get_tag_service()
            tags_result = tag_service.get_user_tags(user_id)

            # 获取统计信息
            stats = self._get_user_stats(user_id)

            return {
                'success': True,
                'user': user,
                'tags': tags_result.get('data', {}).get('tags', {}),
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户资料失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def update_user_profile(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        date_of_birth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            nickname: 昵称
            email: 邮箱
            phone_number: 手机号
            date_of_birth: 出生日期 (YYYY-MM-DD格式)
            
        Returns:
            Dict: 更新结果
        """
        try:
            update_fields = []
            params = []
            
            if nickname is not None:
                update_fields.append("nickname = %s")
                params.append(nickname)
            
            if email is not None:
                update_fields.append("email = %s")
                params.append(email)
            
            if phone_number is not None:
                update_fields.append("phone_number = %s")
                params.append(phone_number)
            
            if date_of_birth is not None:
                update_fields.append("date_of_birth = %s")
                params.append(date_of_birth)
            
            if not update_fields:
                return {'success': False, 'message': '没有要更新的字段'}
            
            params.append(user_id)
            
            sql = f"""
                UPDATE users
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE user_id = %s
            """
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 用户 {user_id} 资料更新成功")
            
            return {
                'success': True,
                'message': '资料更新成功'
            }
            
        except Exception as e:
            logger.error(f"❌ 更新用户资料失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def update_user_profile_admin(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        管理员更新用户资料（支持更新管理员权限）

        Args:
            user_id: 用户ID
            nickname: 昵称
            email: 邮箱
            phone_number: 手机号
            date_of_birth: 出生日期 (YYYY-MM-DD格式)
            is_admin: 是否为管理员

        Returns:
            Dict: 更新结果
        """
        try:
            update_fields = []
            params = []

            if nickname is not None:
                update_fields.append("nickname = %s")
                params.append(nickname)

            if email is not None:
                update_fields.append("email = %s")
                params.append(email)

            if phone_number is not None:
                update_fields.append("phone_number = %s")
                params.append(phone_number)

            if date_of_birth is not None:
                update_fields.append("date_of_birth = %s")
                params.append(date_of_birth)

            if is_admin is not None:
                update_fields.append("is_admin = %s")
                params.append(1 if is_admin else 0)

            if not update_fields:
                return {'success': False, 'message': '没有要更新的字段'}

            params.append(user_id)

            sql = f"""
                UPDATE users
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE user_id = %s
            """

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(sql, params)
            conn.commit()

            cursor.close()
            conn.close()

            # 获取更新后的用户信息
            updated_user = self.get_user_by_id(user_id)
            if updated_user:
                return {'success': True, 'data': updated_user, 'message': '用户资料更新成功'}
            else:
                return {'success': False, 'message': '获取更新后的用户信息失败'}

        except Exception as e:
            logger.error(f"❌ 管理员更新用户资料失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def get_users_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        username: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        获取用户列表
        
        Args:
            page: 页码
            page_size: 每页数量
            keyword: 搜索关键词（用户名/昵称/手机号）
            is_active: 是否激活
            username: 用户名（精确或模糊查询）
            phone_number: 手机号（精确或模糊查询）
            is_admin: 是否为管理员
            
        Returns:
            Dict: 用户列表
        """
        try:
            offset = (page - 1) * page_size
            
            # 构建查询条件
            conditions = []
            params = []
            
            if keyword:
                conditions.append("(username LIKE %s OR nickname LIKE %s OR phone_number LIKE %s)")
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            
            if username:
                conditions.append("username LIKE %s")
                params.append(f"%{username}%")
            
            if phone_number:
                conditions.append("phone_number LIKE %s")
                params.append(f"%{phone_number}%")
            
            if is_active is not None:
                conditions.append("is_active = %s")
                params.append(is_active)
            
            if is_admin is not None:
                conditions.append("is_admin = %s")
                params.append(1 if is_admin else 0)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM users {where_clause}"
            total = execute_query(count_sql, tuple(params) if params else None, fetch_one=True)['total']
            
            # 查询列表
            params.extend([page_size, offset])
            list_sql = f"""
                SELECT user_id, username, nickname, email, phone_number,
                       created_at, last_login, is_active, is_admin
                FROM users
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            users = execute_query(list_sql, tuple(params))
            
            return {
                'success': True,
                'total': total,
                'page': page,
                'page_size': page_size,
                'users': users
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户列表失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def toggle_user_status(self, user_id: int) -> Dict[str, Any]:
        """
        切换用户状态（启用/禁用）
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 操作结果
        """
        try:
            sql = "UPDATE users SET is_active = NOT is_active WHERE user_id = %s"
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 用户 {user_id} 状态切换成功")
            
            return {
                'success': True,
                'message': '状态切换成功'
            }
            
        except Exception as e:
            logger.error(f"❌ 切换用户状态失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        删除用户
        
        先删除所有相关子表数据，然后删除用户，避免外键约束错误
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 删除结果
        """
        conn = None
        cursor = None
        
        try:
            # 先检查用户是否存在
            user = self.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            conn = get_db_connection()
            # 关闭自动提交，使用事务
            conn.autocommit = False
            cursor = conn.cursor()
            
            # 按顺序删除相关表的数据（先删除子表，再删除父表）
            # 注意：有些表可能有 CASCADE 约束，但为了安全，我们手动删除所有相关数据
            
            delete_tables = [
                # 积分相关
                'point_records',  # 积分记录表
                'points',  # 积分表
                # 标签相关
                'user_tag_history',  # 标签历史
                'user_tag_values',  # 标签值
                # 对话相关
                'chat_messages',  # 对话消息
                'chat_sessions',  # 对话会话
                'chat_logs',  # 旧版对话日志（如果存在）
                # 打卡相关
                'checkin_records',  # 打卡记录
                'check_ins',  # 打卡表（如果存在）
                # 新手引导相关
                'user_onboarding_answers',  # 引导回答
                'user_onboarding_status',  # 引导状态
                # 提示词设置
                'user_prompt_settings',  # 用户提示词设置
                # 其他可能存在的表
                'user_points',  # 用户积分表（如果存在）
            ]
            
            deleted_counts = {}
            
            for table in delete_tables:
                try:
                    # 检查表是否存在
                    cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    if cursor.fetchone():
                        # 删除该用户的数据
                        sql = f"DELETE FROM `{table}` WHERE user_id = %s"
                        cursor.execute(sql, (user_id,))
                        deleted_count = cursor.rowcount
                        if deleted_count > 0:
                            deleted_counts[table] = deleted_count
                            logger.info(f"  ✅ 删除 {table} 表数据: {deleted_count} 条")
                except Exception as e:
                    # 表不存在或删除失败，记录警告但继续
                    logger.warning(f"  ⚠️ 删除 {table} 表数据失败: {str(e)}")
            
            # 最后删除用户
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            user_deleted = cursor.rowcount
            
            if user_deleted == 0:
                conn.rollback()
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                return {'success': False, 'message': '用户删除失败'}
            
            # 提交事务
            conn.commit()
            
            logger.info(f"✅ 用户 {user_id} 删除成功，共删除 {len(deleted_counts)} 个相关表的数据")
            
            return {
                'success': True,
                'message': '用户删除成功',
                'deleted_tables': deleted_counts
            }
            
        except Exception as e:
            # 发生错误，回滚事务
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    logger.warning(f"⚠️ 回滚事务失败: {str(rollback_error)}")
            
            error_msg = str(e)
            logger.error(f"❌ 删除用户失败: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 返回更详细的错误信息
            return {
                'success': False, 
                'message': f'删除用户失败: {error_msg}',
                'error_type': type(e).__name__
            }
            
        finally:
            # 确保关闭连接
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def _get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 统计信息
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 对话次数（从chat_logs表统计AI回复的消息数）
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM chat_logs 
                WHERE user_id = %s AND sender = 'ai'
            """, (user_id,))
            result = cursor.fetchone()
            chat_count = result['count'] if result else 0
            
            # 打卡次数
            cursor.execute("""
                SELECT COUNT(*) as count FROM checkin_records 
                WHERE user_id = %s
            """, (user_id,))
            checkin_count = cursor.fetchone()['count']
            
            # 积分余额（使用points_change字段，earn类型为正，spend类型为负）
            cursor.execute("""
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN record_type = 'earn' THEN points_change
                        WHEN record_type = 'spend' THEN -points_change
                        WHEN record_type = 'refund' THEN points_change
                        ELSE 0
                    END
                ), 0) as total 
                FROM point_records 
                WHERE user_id = %s
            """, (user_id,))
            points_balance = cursor.fetchone()['total']
            
            cursor.close()
            conn.close()
            
            return {
                'total_conversations': chat_count,
                'total_checkins': checkin_count,
                'points_balance': points_balance
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户统计失败: {str(e)}")
            return {}

    def reset_user_password(self, user_id: int, new_password: Optional[str] = None) -> Dict[str, Any]:
        """
        重置或设置用户密码

        Args:
            user_id: 用户ID
            new_password: 新密码，如果不提供则使用默认密码

        Returns:
            Dict: 操作结果
        """
        try:
            # 如果没有提供新密码，使用默认密码
            if not new_password:
                default_password = "123456"  # 默认密码
            else:
                default_password = new_password

            # 对密码进行哈希处理
            import hashlib
            hashed_password = hashlib.sha256(default_password.encode()).hexdigest()

            conn = get_db_connection()
            cursor = conn.cursor()

            # 更新用户密码
            cursor.execute("""
                UPDATE users
                SET password_hash = %s, updated_at = NOW()
                WHERE user_id = %s
            """, (hashed_password, user_id))

            if cursor.rowcount == 0:
                conn.rollback()
                cursor.close()
                conn.close()
                return {'success': False, 'message': '用户不存在'}

            conn.commit()
            cursor.close()
            conn.close()

            if new_password:
                logger.info(f"✅ 设置用户 {user_id} 密码成功")
                message = '密码已成功设置'
            else:
                logger.info(f"✅ 重置用户 {user_id} 密码成功")
                message = '密码已重置为默认密码'

            return {
                'success': True,
                'message': message,
                'password': default_password
            }

        except Exception as e:
            logger.error(f"❌ 重置用户密码失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def batch_import_users(self, users_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量导入用户

        Args:
            users_data: 用户数据列表
                格式: [{'username': str, 'password': str, 'nickname': str, 'phone_number': str}, ...]

        Returns:
            Dict: 批量导入结果
        """
        try:
            if not users_data:
                return {'success': False, 'message': '用户数据不能为空'}

            success_count = 0
            failed_count = 0
            errors = []

            conn = get_db_connection()
            cursor = conn.cursor()

            import hashlib

            for i, user_data in enumerate(users_data):
                try:
                    # 验证必填字段
                    username = user_data.get('username', '').strip()
                    if not username:
                        errors.append(f"第{i+1}行: 用户名不能为空")
                        failed_count += 1
                        continue

                    # 检查用户名是否已存在
                    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                    if cursor.fetchone():
                        errors.append(f"第{i+1}行: 用户名 '{username}' 已存在")
                        failed_count += 1
                        continue

                    # 处理密码（默认为123456如果未提供）
                    password = user_data.get('password', '123456').strip()
                    if not password:
                        password = '123456'
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()

                    # 处理可选字段
                    nickname = user_data.get('nickname', '').strip() or None
                    phone_number = user_data.get('phone_number', '').strip() or None

                    # 检查手机号是否已存在（如果提供了手机号）
                    if phone_number:
                        cursor.execute("SELECT user_id FROM users WHERE phone_number = %s", (phone_number,))
                        if cursor.fetchone():
                            errors.append(f"第{i+1}行: 手机号 '{phone_number}' 已存在")
                            failed_count += 1
                            continue

                    # 插入用户
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, nickname, phone_number, is_active, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, 1, NOW(), NOW())
                    """, (username, hashed_password, nickname, phone_number))

                    success_count += 1

                except Exception as e:
                    errors.append(f"第{i+1}行: {str(e)}")
                    failed_count += 1

            conn.commit()
            cursor.close()
            conn.close()

            result = {
                'success': failed_count == 0,
                'message': f'批量导入完成，成功: {success_count}，失败: {failed_count}',
                'success_count': success_count,
                'failed_count': failed_count
            }

            if errors:
                result['errors'] = errors[:10]  # 只返回前10个错误信息

            logger.info(f"✅ 批量导入用户完成: 成功{success_count}，失败{failed_count}")
            return result

        except Exception as e:
            logger.error(f"❌ 批量导入用户失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def is_admin(self, user_id: int) -> bool:
        """
        检查用户是否为管理员

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否为管理员
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            return result and result.get('is_admin') == 1

        except Exception as e:
            logger.error(f"❌ 检查管理员权限失败: {str(e)}")
            return False


# 全局单例
_user_service_instance = None

def get_user_service() -> UserService:
    """获取用户服务单例"""
    global _user_service_instance
    if _user_service_instance is None:
        _user_service_instance = UserService()
    return _user_service_instance

