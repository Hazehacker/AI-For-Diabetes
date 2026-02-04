"""
认证路由
~~~~~~~

用户认证相关的API端点：
- 注册
- 登录
- Token刷新

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify
from . import auth_bp
from utils.jwt_helper import no_auth_required as token_required
from services.auth_service import get_auth_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 获取服务实例
auth_service = get_auth_service()


@auth_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'code': 200,
        'data': {
            'message': '智糖小助手API服务正常运行',
            'version': '2.0.0'
        },
        'success': True
    }), 200


@auth_bp.route('/db-pool/status', methods=['GET'])
@token_required
def get_db_pool_status(user_id):
    """
    获取数据库连接池状态（管理员功能）
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: 连接池状态信息
    """
    try:
        from utils.database import get_pool_status
        status = get_pool_status()
        return jsonify({
            'code': 200,
            'data': status,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"❌ 获取连接池状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册

    Body:
        {
            "username": "用户名",
            "password": "密码",
            "email": "邮箱（可选）",
            "phone_number": "手机号（可选）",
            "nickname": "昵称（可选）",
            "is_admin": false  // 管理员标记（可选）
        }
    """
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone_number = data.get('phone_number')
        nickname = data.get('nickname')
        is_admin = data.get('is_admin', False)
        
        if not username or not password:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        result = auth_service.register(username, password, nickname, email, phone_number, is_admin)

        if result['success']:
            # 注册成功：返回标准格式
            return jsonify({
                'code': 200,
                'data': {
                    'user_id': result.get('user_id'),
                    'username': result.get('username'),
                    'token': result.get('token')
                },
                'message': result.get('message', '注册成功'),
                'success': True
            }), 200
        else:
            # 注册失败：返回标准错误格式
            return jsonify({
                'code': 400,
                'data': {},
                'message': result.get('message', '注册失败'),
                'success': False
            }), 400
        
    except Exception as e:
        logger.error(f"❌ 注册失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/register/phone', methods=['POST'])
def register_by_phone():
    """
    手机号注册
    
    Body:
        {
            "phone_number": "手机号",
            "password": "密码",
            "nickname": "昵称",
            "verification_code": "验证码"
        }
    """
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number')
        password = data.get('password')
        nickname = data.get('nickname')
        verification_code = data.get('verification_code')
        
        if not phone_number or not password:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '手机号和密码不能为空'
            }), 400
        
        result = auth_service.register_by_phone(
            phone_number, password, nickname, verification_code
        )
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"❌ 手机号注册失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    Body:
        {
            "username": "用户名或手机号",
            "password": "密码"
        }
    """
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        result = auth_service.login(username, password)
        logger.info(f"🔍 登录结果: success={result.get('success')}, token={result.get('token')[:50] if result.get('token') else 'None'}...")

        if result['success']:
            # 登录成功：返回标准格式
            response_data = {
                'code': 200,
                'data': {
                    'user_id': result.get('user_id'),
                    'username': result.get('username'),
                    'nickname': result.get('nickname'),
                    'token': result.get('token')
                },
                'message': result.get('message', '登录成功'),
                'success': True
            }
            logger.info(f"🔍 返回数据: token={response_data['data']['token'][:50] if response_data['data']['token'] else 'None'}...")
            return jsonify(response_data), 200
        else:
            # 登录失败：返回标准错误格式
            return jsonify({
                'code': 400,
                'data': {},
                'message': result.get('message', '登录失败'),
                'success': False
            }), 400
        
    except Exception as e:
        logger.error(f"❌ 登录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/login/phone', methods=['POST'])
def login_by_phone():
    """
    手机号登录
    
    Body:
        {
            "phone_number": "手机号",
            "password": "密码",  // 密码登录
            "verification_code": "验证码"  // 或验证码登录
        }
    """
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not phone_number:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '手机号不能为空'
            }), 400
        
        result = auth_service.login_by_phone(phone_number, password, verification_code)
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"❌ 手机号登录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500



