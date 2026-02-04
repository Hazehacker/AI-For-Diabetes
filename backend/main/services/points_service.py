"""
积分服务
~~~~~~~

积分管理服务，包括：
- 积分查询
- 积分记录
- 积分增减
- 积分兑换

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, Dict, Any, List
from utils.database import get_db_connection, DatabaseTransaction, execute_query
from utils.logger import get_logger

logger = get_logger(__name__)


class PointsService:
    """积分服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def get_user_points(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户积分余额
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 积分信息
        """
        try:
            sql = """
                SELECT COALESCE(SUM(points), 0) as balance
                FROM point_records
                WHERE user_id = %s
            """
            result = execute_query(sql, (user_id,), fetch_one=True)
            
            return {
                'success': True,
                'user_id': user_id,
                'balance': result['balance']
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户积分失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def add_points(
        self,
        user_id: int,
        points: int,
        source: str = 'manual',
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        增加积分
        
        Args:
            user_id: 用户ID
            points: 积分数量（正数）
            source: 来源
            description: 描述
            
        Returns:
            Dict: 操作结果
        """
        try:
            if points <= 0:
                return {'success': False, 'message': '积分数量必须大于0'}
            
            sql = """
                INSERT INTO point_records 
                (user_id, points, source, description, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (user_id, points, source, description))
            record_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            # 获取新的余额
            balance_result = self.get_user_points(user_id)
            new_balance = balance_result.get('balance', 0)
            
            logger.info(f"✅ 用户 {user_id} 增加积分: +{points}，新余额: {new_balance}")
            
            return {
                'success': True,
                'message': '积分增加成功',
                'record_id': record_id,
                'points_added': points,
                'new_balance': new_balance
            }
            
        except Exception as e:
            logger.error(f"❌ 增加积分失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def deduct_points(
        self,
        user_id: int,
        points: int,
        source: str = 'manual',
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        扣除积分
        
        Args:
            user_id: 用户ID
            points: 积分数量（正数）
            source: 来源
            description: 描述
            
        Returns:
            Dict: 操作结果
        """
        try:
            if points <= 0:
                return {'success': False, 'message': '积分数量必须大于0'}
            
            # 检查余额是否充足
            balance_result = self.get_user_points(user_id)
            current_balance = balance_result.get('balance', 0)
            
            if current_balance < points:
                return {
                    'success': False,
                    'message': f'积分余额不足，当前余额: {current_balance}，需要: {points}'
                }
            
            # 记录负积分
            sql = """
                INSERT INTO point_records 
                (user_id, points, source, description, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (user_id, -points, source, description))
            record_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            new_balance = current_balance - points
            
            logger.info(f"✅ 用户 {user_id} 扣除积分: -{points}，新余额: {new_balance}")
            
            return {
                'success': True,
                'message': '积分扣除成功',
                'record_id': record_id,
                'points_deducted': points,
                'new_balance': new_balance
            }
            
        except Exception as e:
            logger.error(f"❌ 扣除积分失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def get_point_records(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取积分记录
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            source: 来源过滤
            
        Returns:
            Dict: 积分记录
        """
        try:
            offset = (page - 1) * page_size
            
            # 构建条件
            conditions = ["user_id = %s"]
            params = [user_id]
            
            if source:
                conditions.append("source = %s")
                params.append(source)
            
            where_clause = " AND ".join(conditions)
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM point_records WHERE {where_clause}"
            total = execute_query(count_sql, tuple(params), fetch_one=True)['total']
            
            # 查询记录
            params.extend([page_size, offset])
            list_sql = f"""
                SELECT * FROM point_records
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            records = execute_query(list_sql, tuple(params))
            
            # 获取余额
            balance_result = self.get_user_points(user_id)
            
            return {
                'success': True,
                'total': total,
                'page': page,
                'page_size': page_size,
                'balance': balance_result.get('balance', 0),
                'records': records
            }
            
        except Exception as e:
            logger.error(f"❌ 获取积分记录失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def transfer_points(
        self,
        from_user_id: int,
        to_user_id: int,
        points: int,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        积分转移
        
        Args:
            from_user_id: 转出用户ID
            to_user_id: 转入用户ID
            points: 积分数量
            description: 描述
            
        Returns:
            Dict: 操作结果
        """
        try:
            if points <= 0:
                return {'success': False, 'message': '积分数量必须大于0'}
            
            if from_user_id == to_user_id:
                return {'success': False, 'message': '不能向自己转移积分'}
            
            # 使用事务确保原子性
            with DatabaseTransaction() as (conn, cursor):
                # 检查余额
                cursor.execute("""
                    SELECT COALESCE(SUM(points), 0) as balance
                    FROM point_records
                    WHERE user_id = %s
                """, (from_user_id,))
                balance = cursor.fetchone()['balance']
                
                if balance < points:
                    raise Exception(f'积分余额不足，当前: {balance}，需要: {points}')
                
                # 扣除转出方积分
                cursor.execute("""
                    INSERT INTO point_records 
                    (user_id, points, source, description, created_at)
                    VALUES (%s, %s, 'transfer_out', %s, NOW())
                """, (from_user_id, -points, description or f'转给用户{to_user_id}'))
                
                # 增加转入方积分
                cursor.execute("""
                    INSERT INTO point_records 
                    (user_id, points, source, description, created_at)
                    VALUES (%s, %s, 'transfer_in', %s, NOW())
                """, (to_user_id, points, description or f'来自用户{from_user_id}'))
            
            logger.info(f"✅ 积分转移成功: {from_user_id} -> {to_user_id}, {points}积分")
            
            return {
                'success': True,
                'message': '积分转移成功',
                'points': points
            }
            
        except Exception as e:
            logger.error(f"❌ 积分转移失败: {str(e)}")
            return {'success': False, 'message': str(e)}


# 全局单例
_points_service_instance = None

def get_points_service() -> PointsService:
    """获取积分服务单例"""
    global _points_service_instance
    if _points_service_instance is None:
        _points_service_instance = PointsService()
    return _points_service_instance

