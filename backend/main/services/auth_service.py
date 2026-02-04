"""
认证服务
~~~~~~~

用户认证服务，包括：
- 用户注册
- 用户登录
- Token管理
- Keycloak集成

作者: 智糖团队
日期: 2025-01-15
"""

import hashlib
from typing import Optional, Dict, Any
from utils.database import get_db_connection, DatabaseTransaction
from utils.jwt_helper import generate_token
from utils.logger import get_logger
from utils.validators import validate_phone, validate_password, validate_username
from services.coze_service import get_coze_service

logger = get_logger(__name__)


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.coze_service = get_coze_service()
    
    def register_by_phone(
        self,
        phone_number: str,
        password: str,
        nickname: Optional[str] = None,
        verification_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        手机号注册
        
        Args:
            phone_number: 手机号
            password: 密码
            nickname: 昵称
            verification_code: 验证码
            
        Returns:
            Dict: 注册结果
        """
        try:
            # 验证手机号
            if not validate_phone(phone_number):
                return {'success': False, 'message': '手机号格式不正确'}
            
            # 验证密码
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return {'success': False, 'message': error_msg}
            
            # 检查手机号是否已存在
            if self._check_phone_exists(phone_number):
                return {'success': False, 'message': '该手机号已被注册'}
            
            # 生成用户名（使用手机号）
            username = phone_number
            
            # 密码加密
            password_hash = self._hash_password(password)
            
            # 创建用户
            with DatabaseTransaction() as (conn, cursor):
                sql = """
                    INSERT INTO users (username, password_hash, nickname, phone_number, 
                                     created_at, is_active)
                    VALUES (%s, %s, %s, %s, NOW(), TRUE)
                """
                cursor.execute(sql, (username, password_hash, nickname or f"用户{phone_number[-4:]}", phone_number))
                user_id = cursor.lastrowid
            
            if not user_id:
                return {'success': False, 'message': '注册失败'}
            
            # 初始化Coze变量（异步）
            self._init_coze_variables_async(user_id, username, nickname, phone_number)
            
            # 生成Token（使用Keycloak）
            token = generate_token(user_id, username)
            
            logger.info(f"✅ 用户注册成功: {phone_number}")
            
            return {
                'success': True,
                'message': '注册成功',
                'user_id': user_id,
                'username': username,
                'token': token
            }
            
        except Exception as e:
            logger.error(f"❌ 注册失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def register(
        self,
        username: str,
        password: str,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        用户名注册

        Args:
            username: 用户名
            password: 密码
            nickname: 昵称
            email: 邮箱
            phone_number: 手机号
            is_admin: 是否为管理员

        Returns:
            Dict: 注册结果
        """
        try:
            # 验证用户名
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                return {'success': False, 'message': error_msg}
            
            # 验证密码
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return {'success': False, 'message': error_msg}
            
            # 检查用户名是否已存在
            if self._check_username_exists(username):
                return {'success': False, 'message': '该用户名已被注册'}

            # 检查手机号是否已存在（如果提供了手机号）
            if phone_number and self._check_phone_exists(phone_number):
                return {'success': False, 'message': '该手机号已被注册'}

            # 密码加密
            password_hash = self._hash_password(password)
            
            # 创建用户
            with DatabaseTransaction() as (conn, cursor):
                sql = """
                    INSERT INTO users (username, password_hash, email, phone_number, nickname,
                                     is_admin, created_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), TRUE)
                """
                cursor.execute(sql, (username, password_hash, email, phone_number, nickname or username, 1 if is_admin else 0))
                user_id = cursor.lastrowid
            
            if not user_id:
                return {'success': False, 'message': '注册失败'}
            
            # 初始化Coze变量（异步）
            self._init_coze_variables_async(user_id, username, nickname, phone_number)
            
            # 生成Token（使用Keycloak）
            token = generate_token(user_id, username)
            
            logger.info(f"✅ 用户注册成功: {username}")
            
            return {
                'success': True,
                'message': '注册成功',
                'user_id': user_id,
                'username': username,
                'token': token
            }
            
        except Exception as e:
            logger.error(f"❌ 注册失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def login(
        self,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名或手机号
            password: 密码
            
        Returns:
            Dict: 登录结果
        """
        try:
            # 查询用户
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT user_id, username, password_hash, nickname, is_active, is_admin
                FROM users
                WHERE (username = %s OR phone_number = %s) AND is_active = TRUE
            """
            cursor.execute(sql, (username, username))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not user:
                return {'success': False, 'message': '用户不存在或已被禁用'}
            
            # 验证密码
            password_hash = self._hash_password(password)
            if password_hash != user['password_hash']:
                return {'success': False, 'message': '密码错误'}
            
            # 生成Token（使用Keycloak），包含管理员信息
            additional_claims = {'is_admin': bool(user['is_admin'])}
            token = generate_token(user['user_id'], user['username'], additional_claims)
            
            # 更新最后登录时间
            self._update_last_login(user['user_id'])
            
            logger.info(f"✅ 用户登录成功: {username}")
            
            return {
                'success': True,
                'message': '登录成功',
                'user_id': user['user_id'],
                'username': user['username'],
                'nickname': user['nickname'],
                'token': token
            }
            
        except Exception as e:
            logger.error(f"❌ 登录失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def login_by_phone(
        self,
        phone_number: str,
        password: Optional[str] = None,
        verification_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        手机号登录
        
        Args:
            phone_number: 手机号
            password: 密码（密码登录时提供）
            verification_code: 验证码（验证码登录时提供）
            
        Returns:
            Dict: 登录结果
        """
        try:
            if not validate_phone(phone_number):
                return {'success': False, 'message': '手机号格式不正确'}
            
            # 查询用户
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT user_id, username, password_hash, nickname, is_active, is_admin
                FROM users
                WHERE phone_number = %s AND is_active = TRUE
            """
            cursor.execute(sql, (phone_number,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not user:
                return {'success': False, 'message': '用户不存在或已被禁用'}
            
            # 验证方式1：密码
            if password:
                password_hash = self._hash_password(password)
                if password_hash != user['password_hash']:
                    return {'success': False, 'message': '密码错误'}
            
            # 验证方式2：验证码（TODO: 实现验证码验证逻辑）
            elif verification_code:
                # 这里应该验证验证码
                pass
            else:
                return {'success': False, 'message': '请提供密码或验证码'}
            
            # 生成Token（包含管理员信息）
            additional_claims = {'is_admin': bool(user['is_admin'])}
            token = generate_token(user['user_id'], user['username'], additional_claims)
            
            # 更新最后登录时间
            self._update_last_login(user['user_id'])
            
            logger.info(f"✅ 手机号登录成功: {phone_number}")
            
            return {
                'success': True,
                'message': '登录成功',
                'user_id': user['user_id'],
                'username': user['username'],
                'nickname': user['nickname'],
                'token': token
            }
            
        except Exception as e:
            logger.error(f"❌ 手机号登录失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _hash_password(self, password: str) -> str:
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result['count'] > 0

    def _check_phone_exists(self, phone_number: str) -> bool:
        """检查手机号是否存在"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE phone_number = %s", (phone_number,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result['count'] > 0
    
    def _check_phone_exists(self, phone_number: str) -> bool:
        """检查手机号是否存在"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE phone_number = %s", (phone_number,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result['count'] > 0
    
    def _update_last_login(self, user_id: int):
        """更新最后登录时间"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"❌ 更新登录时间失败: {str(e)}")
    
    def _init_coze_variables_async(self, user_id, username, nickname, phone_number):
        """异步初始化Coze变量"""
        import threading
        
        def init_task():
            try:
                self.coze_service.initialize_user_variables(user_id, {
                    'username': username,
                    'nickname': nickname or username,
                    'phone_number': phone_number or ''
                })
                logger.info(f"✅ 用户 {user_id} Coze变量初始化成功")
            except Exception as e:
                logger.error(f"❌ Coze变量初始化失败: {str(e)}")
        
        thread = threading.Thread(target=init_task, daemon=True)
        thread.start()


# 全局单例
_auth_service_instance = None

def get_auth_service() -> AuthService:
    """获取认证服务单例"""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance

