"""
打卡服务
~~~~~~~

用户打卡管理服务，包括：
- 每日打卡
- 打卡记录查询
- 连续打卡统计
- 积分奖励

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
from utils.database import get_db_connection, DatabaseTransaction, execute_query
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckinService:
    """打卡服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def checkin(
        self,
        user_id: int,
        checkin_type: str = 'blood_glucose',
        checkin_value: Optional[str] = None,
        glucose_status: Optional[str] = None,
        feeling_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        用户打卡

        Args:
            user_id: 用户ID
            checkin_type: 打卡类型
            checkin_value: 打卡值/备注
            glucose_status: 控糖状态（一般/良好/好）
            feeling_text: 感受文字

        Returns:
            Dict: 打卡结果
        """
        try:
            # 验证控糖状态参数
            if glucose_status and glucose_status not in ['一般', '良好', '好']:
                return {
                    'success': False,
                    'message': '控糖状态必须是：一般、良好、好 中的一个'
                }

            # 检查今天是否已打卡该类型
            if self._has_checked_in_today(user_id, checkin_type):
                return {
                    'success': False,
                    'message': '今天已经打卡过该类型了'
                }

            # 执行打卡
            with DatabaseTransaction() as (conn, cursor):
                # 插入打卡记录（扩展字段）
                sql = """
                    INSERT INTO checkin_records
                    (user_id, checkin_type, checkin_value, glucose_status, feeling_text, timestamp, is_completed)
                    VALUES (%s, %s, %s, %s, %s, NOW(), 1)
                """
                cursor.execute(sql, (user_id, checkin_type, checkin_value or '', glucose_status, feeling_text))
                checkin_id = cursor.lastrowid

                # 获取连续打卡天数
                continuous_days = self._get_continuous_days(user_id, cursor)

                # 计算积分奖励
                points = self._calculate_checkin_points(continuous_days)

                # 添加积分记录
                if points > 0:
                    cursor.execute("""
                        INSERT INTO point_records
                        (user_id, points_change, points_reason, record_type, related_type, created_at)
                        VALUES (%s, %s, %s, 'earn', 'checkin', NOW())
                    """, (user_id, points, f'打卡奖励（连续{continuous_days}天）'))

            logger.info(f"✅ 用户 {user_id} 打卡成功，状态：{glucose_status}，连续 {continuous_days} 天，获得 {points} 积分")

            return {
                'success': True,
                'message': '打卡成功',
                'checkin_id': checkin_id,
                'continuous_days': continuous_days,
                'points_earned': points,
                'glucose_status': glucose_status,
                'feeling_text': feeling_text
            }

        except Exception as e:
            logger.error(f"❌ 打卡失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def get_checkin_records(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        获取打卡记录
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回记录数
            
        Returns:
            Dict: 打卡记录
        """
        try:
            conditions = ["user_id = %s"]
            params = [user_id]
            
            if start_date:
                conditions.append("DATE(timestamp) >= %s")
                params.append(start_date)
            
            if end_date:
                conditions.append("DATE(timestamp) <= %s")
                params.append(end_date)
            
            where_clause = " AND ".join(conditions)
            params.append(limit)
            
            # 使用%%转义%符号，避免f-string格式化错误
            # 使用NULLIF处理空字符串，然后COALESCE设置默认值
            sql = f"""
                SELECT
                    record_id,
                    user_id,
                    COALESCE(NULLIF(checkin_type, ''), 'blood_glucose') as checkin_type,
                    checkin_value,
                    glucose_status,
                    feeling_text,
                    DATE_FORMAT(timestamp, '%%Y-%%m-%%d %%H:%%i:%%s') as timestamp,
                    is_completed
                FROM checkin_records
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            records = execute_query(sql, tuple(params))
            
            # 获取统计信息
            stats = self.get_checkin_stats(user_id)
            
            return {
                'success': True,
                'records': records,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"❌ 获取打卡记录失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def get_checkin_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取打卡统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 统计信息
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 总打卡天数
            cursor.execute("""
                SELECT COUNT(DISTINCT DATE(timestamp)) as total_days
                FROM checkin_records
                WHERE user_id = %s
            """, (user_id,))
            total_days = cursor.fetchone()['total_days']
            
            # 本月打卡天数
            cursor.execute("""
                SELECT COUNT(*) as month_days
                FROM checkin_records
                WHERE user_id = %s 
                AND YEAR(timestamp) = YEAR(CURDATE())
                AND MONTH(timestamp) = MONTH(CURDATE())
            """, (user_id,))
            month_days = cursor.fetchone()['month_days']
            
            # 连续打卡天数
            continuous_days = self._get_continuous_days(user_id, cursor)
            
            # 今天是否已打卡
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM checkin_records
                WHERE user_id = %s AND DATE(timestamp) = CURDATE()
            """, (user_id,))
            has_checked_today = cursor.fetchone()['count'] > 0
            
            cursor.close()
            conn.close()
            
            return {
                'total_days': total_days,
                'month_days': month_days,
                'continuous_days': continuous_days,
                'has_checked_today': has_checked_today
            }
            
        except Exception as e:
            logger.error(f"❌ 获取打卡统计失败: {str(e)}")
            return {}
    
    def _has_checked_in_today(self, user_id: int, checkin_type: str = None) -> bool:
        """检查今天是否已打卡"""
        try:
            if checkin_type:
                sql = """
                    SELECT COUNT(*) as count
                    FROM checkin_records
                    WHERE user_id = %s 
                    AND checkin_type = %s
                    AND DATE(timestamp) = CURDATE()
                """
                result = execute_query(sql, (user_id, checkin_type), fetch_one=True)
            else:
                sql = """
                    SELECT COUNT(*) as count
                    FROM checkin_records
                    WHERE user_id = %s AND DATE(timestamp) = CURDATE()
                """
                result = execute_query(sql, (user_id,), fetch_one=True)
            return result['count'] > 0
        except:
            return False
    
    def _get_continuous_days(self, user_id: int, cursor=None) -> int:
        """
        获取连续打卡天数
        
        Args:
            user_id: 用户ID
            cursor: 数据库游标（可选）
            
        Returns:
            int: 连续天数
        """
        should_close = False
        if cursor is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            should_close = True
        
        try:
            # 获取最近的打卡日期列表
            cursor.execute("""
                SELECT DISTINCT DATE(timestamp) as checkin_date
                FROM checkin_records
                WHERE user_id = %s
                ORDER BY DATE(timestamp) DESC
                LIMIT 100
            """, (user_id,))
            
            dates = [row['checkin_date'] for row in cursor.fetchall()]
            
            if not dates:
                return 0
            
            # 计算连续天数
            continuous = 1
            current_date = dates[0]
            
            for i in range(1, len(dates)):
                prev_date = dates[i]
                # 检查是否连续（相差1天）
                delta = (current_date - prev_date).days
                
                if delta == 1:
                    continuous += 1
                    current_date = prev_date
                else:
                    break
            
            return continuous
            
        finally:
            if should_close:
                cursor.close()
                conn.close()
    
    def _calculate_checkin_points(self, continuous_days: int) -> int:
        """
        计算打卡积分
        
        Args:
            continuous_days: 连续天数
            
        Returns:
            int: 积分
        """
        base_points = 10  # 基础积分
        
        # 连续打卡奖励
        if continuous_days >= 30:
            bonus = 50
        elif continuous_days >= 7:
            bonus = 20
        elif continuous_days >= 3:
            bonus = 10
        else:
            bonus = 0
        
        return base_points + bonus


# 全局单例
_checkin_service_instance = None

def get_checkin_service() -> CheckinService:
    """获取打卡服务单例"""
    global _checkin_service_instance
    if _checkin_service_instance is None:
        _checkin_service_instance = CheckinService()
    return _checkin_service_instance

