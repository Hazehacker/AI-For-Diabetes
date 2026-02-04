"""
标签提取调度路由 - 【核心文件】
~~~~~~~~~~~~

标签提取调度服务的管理API端点

核心接口：
- GET /api/tag-scheduler/status: 获取调度服务状态
- POST /api/tag-scheduler/start: 启动调度服务
- POST /api/tag-scheduler/stop: 停止调度服务
- POST /api/tag-scheduler/trigger: 手动触发一次标签提取
- POST /api/tag-scheduler/process-conversation: 处理单个对话
- GET /api/tag-scheduler/stats: 获取提取统计信息

功能：
- 调度服务生命周期管理
- 手动触发和单对话处理
- 统计信息查询
- 状态监控

作者: 智糖团队
日期: 2025-01-21
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from utils.logger import get_logger
from services.tag_extraction_scheduler import get_tag_extraction_scheduler

logger = get_logger(__name__)

# 创建Blueprint
tag_scheduler_bp = Blueprint('tag_scheduler', __name__, url_prefix='/api/tag-scheduler')


@tag_scheduler_bp.route('/status', methods=['GET'], endpoint='get_scheduler_status')
@token_required
def get_scheduler_status(user_id):
    """
    获取调度服务状态

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON: 服务状态信息
    """
    try:
        scheduler = get_tag_extraction_scheduler()
        status = scheduler.get_scheduler_status()

        return jsonify({
            'code': 200,
            'data': {'status': status},
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取调度服务状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_scheduler_bp.route('/start', methods=['POST'], endpoint='start_scheduler')
@token_required
def start_scheduler(user_id):
    """
    启动调度服务

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "check_interval": 300  // 可选，检查间隔（秒），默认300秒
        }

    Returns:
        JSON: 启动结果
    """
    try:
        data = request.get_json() or {}
        check_interval = data.get('check_interval', 300)

        # 重新初始化调度服务（如果需要改变间隔）
        from services.tag_extraction_scheduler import TagExtractionScheduler
        global _scheduler_instance
        _scheduler_instance = TagExtractionScheduler(check_interval=check_interval)

        scheduler = get_tag_extraction_scheduler()
        scheduler.start()

        return jsonify({
            'code': 200,
            'data': {
                'message': '标签提取调度服务已启动',
                'check_interval': check_interval
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 启动调度服务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_scheduler_bp.route('/stop', methods=['POST'], endpoint='stop_scheduler')
@token_required
def stop_scheduler(user_id):
    """
    停止调度服务

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON: 停止结果
    """
    try:
        scheduler = get_tag_extraction_scheduler()
        scheduler.stop()

        return jsonify({
            'code': 200,
            'data': {
                'message': '标签提取调度服务已停止'
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 停止调度服务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_scheduler_bp.route('/trigger', methods=['POST'], endpoint='trigger_extraction')
@token_required
def trigger_extraction(user_id):
    """
    手动触发一次标签提取任务

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON: 执行结果
    """
    try:
        scheduler = get_tag_extraction_scheduler()
        scheduler._process_tag_extractions()

        return jsonify({
            'code': 200,
            'data': {
                'message': '标签提取任务已手动触发'
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 手动触发标签提取失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_scheduler_bp.route('/process-conversation', methods=['POST'], endpoint='process_single_conversation')
@token_required
def process_single_conversation(user_id):
    """
    处理单个对话的标签提取

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "conversation_id": "对话ID"
        }

    Returns:
        JSON: 处理结果
    """
    try:
        data = request.get_json()

        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': 'conversation_id不能为空'
            }), 400

        scheduler = get_tag_extraction_scheduler()
        result = scheduler.process_single_conversation(user_id, conversation_id)

        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"❌ 处理单个对话失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_scheduler_bp.route('/stats', methods=['GET'], endpoint='get_extraction_stats')
@token_required
def get_extraction_stats(user_id):
    """
    获取标签提取统计信息

    Headers:
        Authorization: Bearer <token>

    Query Parameters:
        days: 统计最近多少天的数据，默认7天

    Returns:
        JSON: 统计信息
    """
    try:
        days = int(request.args.get('days', 7))

        # 计算时间范围
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)

        # 统计标签提取历史
        from utils.database import execute_query

        sql = """
            SELECT
                DATE(updated_at) as date,
                source,
                COUNT(*) as count
            FROM user_tag_history
            WHERE updated_at >= %s
              AND source = 'ai_extract'
            GROUP BY DATE(updated_at), source
            ORDER BY date DESC
        """

        stats = execute_query(sql, (start_date,))

        # 计算总数
        total_extractions = sum(stat['count'] for stat in stats)

        return jsonify({
            'code': 200,
            'data': {
                'total_extractions': total_extractions,
                'period_days': days,
                'daily_stats': stats
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500
