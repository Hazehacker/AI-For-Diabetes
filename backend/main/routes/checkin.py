"""
打卡路由
~~~~~~~

打卡管理的API端点：
- 每日打卡
- 打卡记录
- 打卡统计

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from services.checkin_service import get_checkin_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建Blueprint
checkin_bp = Blueprint('checkin', __name__, url_prefix='/api')

# 获取服务实例
checkin_service = get_checkin_service()


@checkin_bp.route('/checkin', methods=['POST'], endpoint='checkin')
@token_required
def checkin(user_id):
    """
    用户打卡

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "checkin_type": "blood_glucose",
            "checkin_value": "备注",
            "glucose_status": "一般|良好|好",
            "feeling_text": "今天的感觉..."
        }
    """
    try:
        data = request.get_json() or {}

        checkin_type = data.get('checkin_type', 'blood_glucose')
        checkin_value = data.get('checkin_value')
        glucose_status = data.get('glucose_status')
        feeling_text = data.get('feeling_text')

        result = checkin_service.checkin(
            user_id=user_id,
            checkin_type=checkin_type,
            checkin_value=checkin_value,
            glucose_status=glucose_status,
            feeling_text=feeling_text
        )
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 打卡失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@checkin_bp.route('/checkin/records', methods=['GET'], endpoint='get_checkin_records')
@token_required
def get_checkin_records(user_id):
    """
    获取打卡记录
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回记录数
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 30))
        
        result = checkin_service.get_checkin_records(
            user_id, start_date, end_date, limit
        )
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取打卡记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@checkin_bp.route('/checkin/stats', methods=['GET'], endpoint='get_checkin_stats')
@token_required
def get_checkin_stats(user_id):
    """
    获取打卡统计

    Headers:
        Authorization: Bearer <token>
    """
    try:
        stats = checkin_service.get_checkin_stats(user_id)
        return jsonify({
            'code': 200,
            'data': {'stats': stats},
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取打卡统计失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@checkin_bp.route('/checkin/types', methods=['GET'], endpoint='get_checkin_types')
@token_required
def get_checkin_types(user_id):
    """
    获取打卡类型列表

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON: 打卡类型列表
    """
    try:
        # 定义支持的打卡类型
        checkin_types = [
            {
                'type_id': 'blood_glucose',
                'type_name': '血糖监测',
                'description': '记录血糖值',
                'icon': '🩸',
                'unit': 'mmol/L'
            },
            {
                'type_id': 'exercise',
                'type_name': '运动打卡',
                'description': '记录运动情况',
                'icon': '🏃',
                'unit': '分钟'
            },
            {
                'type_id': 'medication',
                'type_name': '用药记录',
                'description': '记录服药情况',
                'icon': '💊',
                'unit': '次'
            },
            {
                'type_id': 'diet',
                'type_name': '饮食记录',
                'description': '记录饮食情况',
                'icon': '🍎',
                'unit': '餐'
            },
            {
                'type_id': 'weight',
                'type_name': '体重记录',
                'description': '记录体重变化',
                'icon': '⚖️',
                'unit': 'kg'
            },
            {
                'type_id': 'daily',
                'type_name': '日常打卡',
                'description': '每日健康打卡',
                'icon': '✅',
                'unit': '次'
            }
        ]

        logger.info(f"✅ 获取打卡类型列表: {len(checkin_types)} 个类型")

        return jsonify({
            'code': 200,
            'data': {'types': checkin_types},
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取打卡类型失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

