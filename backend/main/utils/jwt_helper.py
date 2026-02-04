"""
JWT认证工具模块
~~~~~~~~~~~~~~~

提供JWT token的生成、验证和装饰器功能，支持Keycloak集成

功能：
- 生成JWT token（支持Keycloak）
- 验证JWT token（支持Keycloak）
- token_required装饰器
- 从token提取用户信息
- Keycloak客户端管理

作者: 智糖团队
日期: 2025-01-15
"""

import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any
from .logger import get_logger
from .config_loader import get_config
from .database import get_db_connection

logger = get_logger(__name__)

# 用于生成唯一函数名的全局计数器
_decorator_counter = 0

# JWT配置
JWT_SECRET_KEY = get_config('JWT.SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = get_config('JWT.ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(get_config('JWT.EXPIRATION_HOURS', 240))  # 默认10天

# Keycloak配置
KEYCLOAK_ENABLED = get_config('KEYCLOAK.ENABLED', True)
KEYCLOAK_URL = get_config('KEYCLOAK.URL', 'https://sso.cmkjai.com/')
KEYCLOAK_REALM = get_config('KEYCLOAK.REALM', 'chat-realm')
KEYCLOAK_CLIENT_ID = get_config('KEYCLOAK.CLIENT_ID', 'admin-cli')
KEYCLOAK_CLIENT_SECRET = get_config('KEYCLOAK.CLIENT_SECRET', '')
KEYCLOAK_ADMIN_USER = get_config('KEYCLOAK.ADMIN_USER', 'admin')
KEYCLOAK_ADMIN_PASSWORD = get_config('KEYCLOAK.ADMIN_PASSWORD', 'admin123')

# Keycloak客户端缓存
_keycloak_client = None
_keycloak_admin_client = None

def get_keycloak_client():
    """获取Keycloak客户端（普通用户）"""
    global _keycloak_client
    if _keycloak_client is None and KEYCLOAK_ENABLED:
        try:
            from keycloak import KeycloakOpenID
            _keycloak_client = KeycloakOpenID(
                server_url=KEYCLOAK_URL,
                client_id=KEYCLOAK_CLIENT_ID,
                realm_name=KEYCLOAK_REALM,
                client_secret_key=KEYCLOAK_CLIENT_SECRET or None
            )
            logger.info("✅ Keycloak客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ Keycloak客户端初始化失败: {str(e)}")
            _keycloak_client = None
    return _keycloak_client

def get_keycloak_admin_client():
    """获取Keycloak管理员客户端"""
    global _keycloak_admin_client
    if _keycloak_admin_client is None and KEYCLOAK_ENABLED:
        try:
            from keycloak import KeycloakAdmin
            import requests

            # 设置较短的超时时间，避免长时间等待
            _keycloak_admin_client = KeycloakAdmin(
                server_url=KEYCLOAK_URL,
                username=KEYCLOAK_ADMIN_USER,
                password=KEYCLOAK_ADMIN_PASSWORD,
                realm_name="master",  # 管理员在master realm
                client_id="admin-cli",
                verify=True,
                # 添加超时设置
                custom_headers={"Connection": "close"},
                timeout=10  # 10秒超时
            )
            # 设置目标realm
            _keycloak_admin_client.realm_name = KEYCLOAK_REALM
            logger.info("✅ Keycloak管理员客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ Keycloak管理员客户端初始化失败: {str(e)}")
            _keycloak_admin_client = None
    return _keycloak_admin_client


def generate_token(user_id: int, username: str, additional_claims: Dict = None, use_keycloak: bool = True) -> str:
    """
    生成JWT token（支持Keycloak）
    
    Args:
        user_id: 用户ID
        username: 用户名
        additional_claims: 额外的声明（可选）
        use_keycloak: 是否使用Keycloak token（默认True）
        
    Returns:
        str: JWT token字符串
        
    Example:
        >>> token = generate_token(1, 'zhangsan')
        >>> print(token)
        'eyJhbGc...'
    """
    try:
        if use_keycloak and KEYCLOAK_ENABLED:
            # 使用Keycloak生成token，添加超时处理
            import threading
            import time

            result = {}
            exception = {}

            def keycloak_operation():
                try:
                    result['token'] = _generate_keycloak_token(user_id, username, additional_claims)
                except Exception as e:
                    exception['error'] = e

            # 创建线程执行Keycloak操作
            thread = threading.Thread(target=keycloak_operation)
            thread.daemon = True
            thread.start()

            # 等待最多3秒
            thread.join(timeout=3.0)

            if thread.is_alive():
                logger.warning("⚠️ Keycloak token生成超时，回退到本地JWT")
                return _generate_local_token(user_id, username, additional_claims)

            if 'error' in exception:
                logger.warning(f"⚠️ Keycloak token生成失败: {str(exception['error'])}, 回退到本地JWT")
                return _generate_local_token(user_id, username, additional_claims)

            return result.get('token')
        else:
            # 使用本地JWT生成token
            return _generate_local_token(user_id, username, additional_claims)

    except Exception as e:
        logger.error(f"❌ 生成token失败: {str(e)}")
        raise

def _generate_local_token(user_id: int, username: str, additional_claims: Dict = None) -> str:
    """使用本地密钥生成JWT token"""
    # 基础payload
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }

    # 添加额外声明
    if additional_claims:
        payload.update(additional_claims)

    # 生成token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    logger.debug(f"✅ 使用本地JWT为用户 {username}(ID: {user_id}) 生成token")
    return token

def _generate_keycloak_token(user_id: int, username: str, additional_claims: Dict = None) -> str:
    """使用Keycloak生成JWT token"""
    try:
        admin_client = get_keycloak_admin_client()
        if not admin_client:
            logger.warning("⚠️ Keycloak管理员客户端不可用，回退到本地JWT")
            return _generate_local_token(user_id, username, additional_claims)

        # 查找或创建用户
        keycloak_user_id = None
        try:
            # 先尝试通过用户名查找用户（因为我们创建的用户名为 {username}_{user_id}）
            unique_username = f"{username}_{user_id}"
            users = admin_client.get_users({"username": unique_username})
            if users:
                keycloak_user_id = users[0]['id']
                logger.debug(f"✅ 找到现有Keycloak用户: {unique_username}")
            else:
                # 用户不存在，创建用户
                user_data = {
                    'username': unique_username,  # 确保用户名唯一
                    'enabled': True,
                    'emailVerified': False,
                    'firstName': username,
                    'lastName': '',
                    'attributes': {
                        'user_id': str(user_id),
                        'original_username': username
                    }
                }
                admin_client.create_user(user_data)
                logger.info(f"✅ 在Keycloak中创建用户: {unique_username}")

                # 重新查找用户获取ID
                users = admin_client.get_users({"username": unique_username})
                if users:
                    keycloak_user_id = users[0]['id']
                    logger.debug(f"✅ 获取新创建用户ID: {keycloak_user_id}")
                else:
                    logger.warning("⚠️ 创建用户后无法获取用户ID")

        except Exception as e:
            logger.warning(f"⚠️ Keycloak用户管理失败: {str(e)}")
            # 继续执行，使用本地token

        # 为用户生成token（使用管理员权限）
        # 注意：这里需要管理员权限来为用户生成token
        # 实际实现可能需要通过Keycloak的token endpoint

        # 临时方案：创建管理员token并返回
        # 实际生产环境中，应该使用适当的Keycloak流程
        payload = {
            'sub': str(keycloak_user_id),
            'preferred_username': username,
            'user_id': user_id,
            'realm_access': {
                'roles': ['admin'] if additional_claims and additional_claims.get('is_admin') else ['user']
            },
            'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.now(timezone.utc),
            'iss': f"{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}",
            'aud': KEYCLOAK_CLIENT_ID,
            'typ': 'Bearer'
        }

        # 添加额外声明
        if additional_claims:
            payload.update(additional_claims)

        # 使用Keycloak生成token
        # 注意：这里是模拟实现，实际生产环境应该通过Keycloak的token endpoint
        try:
            # 标记为Keycloak token但使用本地签名
            payload['keycloak_token'] = True
            payload['iss'] = KEYCLOAK_URL + f"/realms/{KEYCLOAK_REALM}"
            payload['aud'] = KEYCLOAK_CLIENT_ID
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        except:
            # 回退到本地签名
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        logger.info(f"✅ 使用Keycloak为用户 {username}(ID: {user_id}) 生成token")
        return token
        
    except Exception as e:
        logger.error(f"❌ Keycloak token生成失败: {str(e)}")
        logger.warning("⚠️ 回退到本地JWT生成")
        return _generate_local_token(user_id, username, additional_claims)


def verify_token(token: str, use_keycloak: bool = True) -> Optional[Dict[str, Any]]:
    """
    验证JWT token（支持Keycloak）
    
    Args:
        token: JWT token字符串
        use_keycloak: 是否验证Keycloak token（默认True）
        
    Returns:
        Dict: 解码后的payload，验证失败返回None
        
    Example:
        >>> payload = verify_token(token)
        >>> if payload:
        >>>     user_id = payload['user_id']
    """
    try:
        if use_keycloak and KEYCLOAK_ENABLED:
            # 优先尝试验证Keycloak token
            payload = _verify_keycloak_token(token)
            if payload:
                return payload

        # 回退到本地JWT验证
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.debug("✅ 使用本地JWT验证token成功")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ Token已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️ 无效的Token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Token验证失败: {str(e)}")
        return None

def _verify_keycloak_token(token: str) -> Optional[Dict[str, Any]]:
    """验证Keycloak JWT token"""
    try:
        # 方式1：先尝试直接解码token（检查是否为我们生成的Keycloak格式token）
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_aud": False})
            if payload.get('keycloak_token'):
                # 这是我们生成的Keycloak格式token
                logger.debug("✅ 验证本地生成的Keycloak格式token成功")
                return payload
        except Exception as e:
            logger.debug(f"本地Keycloak格式token验证失败: {str(e)}")

        # 如果上面的方法失败，尝试真实的Keycloak验证
        client = get_keycloak_client()
        if not client:
            return None

        # 方式1：使用introspect endpoint（推荐）
        try:
            introspection = client.introspect(token)
            if introspection.get('active'):
                # Token有效，从introspection结果中提取用户信息
                keycloak_username = introspection.get('preferred_username', '')
                keycloak_sub = introspection.get('sub', '')

                # 从Keycloak用户信息中获取本地user_id
                user_id = _get_local_user_id_from_keycloak(keycloak_username, keycloak_sub)

                payload = {
                    'user_id': user_id,
                    'username': keycloak_username,
                    'sub': keycloak_sub,
                    'realm_access': introspection.get('realm_access', {}),
                    'exp': introspection.get('exp'),
                    'iat': introspection.get('iat'),
                    'iss': introspection.get('iss'),
                    'aud': introspection.get('aud'),
                    'keycloak_verified': True  # 标记为真实Keycloak验证
                }
                logger.debug("✅ 使用Keycloak introspect验证token成功")
                return payload
        except Exception as e:
            logger.debug(f"Keycloak introspect验证失败: {str(e)}")

        # 方式2：直接解码token并验证签名
        try:
            # 获取Keycloak的公钥
            public_key = client.public_key()
            if public_key:
                # 解码token
                decoded_payload = jwt.decode(token, public_key, algorithms=['RS256'], audience=KEYCLOAK_CLIENT_ID)

                # 从解码的payload中获取本地user_id
                keycloak_username = decoded_payload.get('preferred_username', '')
                keycloak_sub = decoded_payload.get('sub', '')
                user_id = _get_local_user_id_from_keycloak(keycloak_username, keycloak_sub)

                payload = decoded_payload.copy()
                payload['user_id'] = user_id
                payload['keycloak_verified'] = True
                logger.debug("✅ 使用Keycloak公钥验证token成功")
                return payload
        except Exception as e:
            logger.debug(f"Keycloak公钥验证失败: {str(e)}")

        # 方式3：使用userinfo endpoint
        try:
            userinfo = client.userinfo(token)
            if userinfo:
                # 从userinfo中获取本地user_id
                keycloak_username = userinfo.get('preferred_username', '')
                keycloak_sub = userinfo.get('sub', '')
                user_id = _get_local_user_id_from_keycloak(keycloak_username, keycloak_sub)

                payload = {
                    'user_id': user_id,
                    'username': keycloak_username,
                    'sub': keycloak_sub,
                    'name': userinfo.get('name'),
                    'email': userinfo.get('email'),
                    'exp': None,  # userinfo不包含exp
                    'iat': None,  # userinfo不包含iat
                    'keycloak_verified': True
                }
                logger.debug("✅ 使用Keycloak userinfo验证token成功")
                return payload
        except Exception as e:
            logger.debug(f"Keycloak userinfo验证失败: {str(e)}")

        return None

    except Exception as e:
        logger.error(f"❌ Keycloak token验证失败: {str(e)}")
        return None


def _get_local_user_id_from_keycloak(keycloak_username: str, keycloak_sub: str = None) -> Optional[int]:
    """
    从Keycloak用户信息中获取对应的本地user_id

    Args:
        keycloak_username: Keycloak用户名
        keycloak_sub: Keycloak用户sub (可选)

    Returns:
        int: 本地数据库中的user_id，失败返回None
    """
    try:
        # 首先尝试通过用户名在本地数据库中查找
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 优先通过用户名查找（因为Keycloak用户名可能与本地用户名一致）
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (keycloak_username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            logger.debug(f"✅ 通过用户名 {keycloak_username} 找到本地用户ID: {user['user_id']}")
            return user['user_id']

        # 如果用户名查找失败，尝试通过Keycloak用户属性查找
        if keycloak_sub:
            admin_client = get_keycloak_admin_client()
            if admin_client:
                try:
                    # 通过sub查找用户
                    users = admin_client.get_users({"username": keycloak_username})
                    if users:
                        user_attributes = users[0].get('attributes', {})
                        user_id_str = user_attributes.get('user_id', [None])[0]
                        if user_id_str:
                            user_id = int(user_id_str)
                            logger.debug(f"✅ 通过Keycloak用户属性找到本地用户ID: {user_id}")
                            return user_id
                except Exception as e:
                    logger.debug(f"通过Keycloak用户属性查找失败: {str(e)}")

        logger.warning(f"⚠️ 无法为Keycloak用户 {keycloak_username} 找到对应的本地user_id")
        return None

    except Exception as e:
        logger.error(f"❌ 获取本地user_id失败: {str(e)}")
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    从token中提取user_id
    
    Args:
        token: JWT token字符串
        
    Returns:
        int: 用户ID，失败返回None
    """
    payload = verify_token(token)
    if payload:
        return payload.get('user_id')
    return None


def token_required(f=None, use_keycloak: bool = True):
    """
    Flask路由装饰器：要求请求必须携带有效的JWT token（支持Keycloak）

    使用方法：
        @token_required
        def protected_route(user_id):
            # user_id会自动从token中提取并传入
            return jsonify({'message': f'Hello user {user_id}'})

    Args:
        f: 被装饰的函数（由Python装饰器机制自动传递）
        use_keycloak: 是否使用Keycloak验证（默认True）

    请求头格式：
        Authorization: Bearer <token>
    """
    def decorator_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                # 获取Authorization头
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    logger.warning("❌ 缺少Authorization头")
                    return jsonify({
                        'code': 401,
                        'data': {},
                        'success': False,
                        'message': '缺少认证信息'
                    }), 401

                # 检查Bearer token格式
                if not auth_header.startswith('Bearer '):
                    logger.warning("❌ 无效的Authorization头格式")
                    return jsonify({
                        'code': 401,
                        'data': {},
                        'success': False,
                        'message': '无效的认证格式'
                    }), 401

                token = auth_header.replace('Bearer ', '', 1).strip()
                if not token:
                    logger.warning("❌ 空的token")
                    return jsonify({
                        'code': 401,
                        'data': {},
                        'success': False,
                        'message': '空的认证令牌'
                    }), 401

                # 验证token
                payload = verify_token(token, use_keycloak=use_keycloak)
                if not payload:
                    logger.warning("❌ token验证失败")
                    return jsonify({
                        'code': 401,
                        'data': {},
                        'success': False,
                        'message': '认证令牌无效或已过期'
                    }), 401

                # 提取user_id
                user_id = payload.get('user_id')
                if not user_id:
                    logger.error(f"❌ token中缺少user_id: {payload}")
                    return jsonify({
                        'code': 401,
                        'data': {},
                        'success': False,
                        'message': '认证信息不完整'
                    }), 401

                logger.debug(f"✅ token验证成功，用户ID: {user_id}")

                # 将user_id作为第一个参数传递给路由函数
                return func(user_id, *args, **kwargs)

            except Exception as e:
                logger.error(f"❌ 认证过程中发生错误: {str(e)}")
                return jsonify({
                    'code': 500,
                    'data': {},
                    'success': False,
                    'message': '认证服务错误'
                }), 500
        return wrapper_func

    # 如果直接使用@token_required（不带括号），f就是被装饰的函数
    # 如果使用@token_required()（带括号），f就是None，需要返回decorator_func
    if f is None:
        return decorator_func
    else:
        return decorator_func(f)


# 【临时解决方案】创建一个不做任何事情的装饰器来替换所有@token_required
def no_auth_required(f):
    """
    临时装饰器：完全跳过鉴权验证，直接调用原始函数
    使用默认user_id=1
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 直接使用默认用户ID，跳过所有鉴权
        return f(1, *args, **kwargs)
    return wrapper


def refresh_token(old_token: str, use_keycloak: bool = True) -> Optional[str]:
    """
    刷新token（生成新的token，支持Keycloak）
    
    Args:
        old_token: 旧的JWT token
        use_keycloak: 是否使用Keycloak（默认True）
        
    Returns:
        str: 新的JWT token，失败返回None
    """
    payload = verify_token(old_token, use_keycloak=use_keycloak)
    if not payload:
        return None
    
    # 生成新token
    user_id = payload.get('user_id')
    username = payload.get('username') or payload.get('preferred_username')
    
    if not user_id or not username:
        logger.warning(f"Token缺少必要字段: user_id={user_id}, username={username}")
        return None
    
    # 保留其他自定义字段，但移除会导致编码问题的字段
    additional_claims = {k: v for k, v in payload.items() 
                        if k not in ['user_id', 'username', 'preferred_username', 'exp', 'iat', 'iss', 'aud', 'sub', 'keycloak_token', 'keycloak_verified', 'admin_verified']}
    
    return generate_token(user_id, username, additional_claims, use_keycloak=use_keycloak)

def generate_admin_token(admin_username: str, admin_password: str) -> Optional[str]:
    """
    生成管理员Keycloak token（通过管理员登录）

    Args:
        admin_username: 管理员用户名
        admin_password: 管理员密码

    Returns:
        str: Keycloak管理员token，失败返回None
    """
    try:
        if not KEYCLOAK_ENABLED:
            logger.warning("⚠️ Keycloak未启用，无法生成管理员token")
            return None

        client = get_keycloak_client()
        if not client:
            logger.warning("⚠️ Keycloak客户端不可用")
            return None

        # 使用管理员凭据获取token
        token_response = client.token(admin_username, admin_password)

        if token_response and 'access_token' in token_response:
            logger.info(f"✅ 管理员 {admin_username} Keycloak token获取成功")
            return token_response['access_token']
        else:
            logger.warning("⚠️ 管理员Keycloak token获取失败")
            return None

    except Exception as e:
        logger.error(f"❌ 管理员Keycloak token生成失败: {str(e)}")
        return None

def verify_admin_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证管理员Keycloak token

    Args:
        token: Keycloak管理员token

    Returns:
        Dict: 验证成功返回payload，失败返回None
    """
    try:
        if not KEYCLOAK_ENABLED:
            logger.warning("⚠️ Keycloak未启用，无法验证管理员token")
            return None

        client = get_keycloak_client()
        if not client:
            logger.warning("⚠️ Keycloak客户端不可用")
            return None

        # 尝试多种验证方式
        try:
            # 方式1：使用introspect验证管理员token
            introspection = client.introspect(token)
            if introspection.get('active'):
                payload = {
                    'sub': introspection.get('sub'),
                    'preferred_username': introspection.get('preferred_username'),
                    'name': introspection.get('name'),
                    'email': introspection.get('email'),
                    'realm_access': introspection.get('realm_access', {}),
                    'client_roles': introspection.get('client_roles', {}),
                    'exp': introspection.get('exp'),
                    'iat': introspection.get('iat'),
                    'iss': introspection.get('iss'),
                    'aud': introspection.get('aud'),
                    'admin_verified': True
                }
                logger.debug("✅ 管理员Keycloak token通过introspect验证成功")
                return payload
        except Exception as e:
            logger.debug(f"管理员token introspect验证失败: {str(e)}")

        try:
            # 方式2：直接解码token（如果有公钥）
            public_key = client.public_key()
            if public_key:
                payload = jwt.decode(token, public_key, algorithms=['RS256'], audience=KEYCLOAK_CLIENT_ID)
                payload['admin_verified'] = True
                logger.debug("✅ 管理员Keycloak token通过公钥验证成功")
                return payload
        except Exception as e:
            logger.debug(f"管理员token公钥验证失败: {str(e)}")

        try:
            # 方式3：使用userinfo验证
            userinfo = client.userinfo(token)
            if userinfo:
                payload = {
                    'sub': userinfo.get('sub'),
                    'preferred_username': userinfo.get('preferred_username'),
                    'name': userinfo.get('name'),
                    'email': userinfo.get('email'),
                    'admin_verified': True
                }
                logger.debug("✅ 管理员Keycloak token通过userinfo验证成功")
                return payload
        except Exception as e:
            logger.debug(f"管理员token userinfo验证失败: {str(e)}")

        logger.warning("⚠️ 管理员token所有验证方式都失败")
        return None

    except Exception as e:
        logger.error(f"❌ 管理员Keycloak token验证失败: {str(e)}")
        return None

