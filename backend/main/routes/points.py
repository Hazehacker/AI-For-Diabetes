"""
积分路由
~~~~~~~

积分管理的API端点：
- 积分查询
- 积分记录
- 积分转移

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from services.points_service import get_points_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建Blueprint
points_bp = Blueprint('points', __name__, url_prefix='/api')

# 获取服务实例
points_service = get_points_service()


@points_bp.route('/points/balance', methods=['GET'], endpoint='get_points_balance')
@token_required
def get_points_balance(user_id):
    """
    获取积分余额
    
    Headers:
        Authorization: Bearer <token>
    """
    try:
        result = points_service.get_user_points(user_id)
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取积分余额失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@points_bp.route('/points/records', methods=['GET'], endpoint='get_points_records')
@token_required
def get_points_records(user_id):
    """
    获取积分记录
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        page: 页码
        page_size: 每页数量
        source: 来源过滤
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        source = request.args.get('source')
        
        result = points_service.get_points_records(
            user_id, page, page_size, source
        )
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取积分记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@points_bp.route('/points/transfer', methods=['POST'], endpoint='transfer_points')
@token_required
def transfer_points(user_id):
    """
    积分转移
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "to_user_id": 目标用户ID,
            "points": 积分数量,
            "description": "描述"
        }
    """
    try:
        data = request.get_json()
        
        to_user_id = data.get('to_user_id')
        points = data.get('points')
        description = data.get('description')
        
        if not to_user_id or not points:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '参数不完整'
            }), 400
        
        result = points_service.transfer_points(
            user_id, to_user_id, points, description
        )
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 积分转移失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

