"""
标签路由 - 【核心文件】
~~~~~~~

标签管理的API端点：
- 获取用户标签
- 设置用户标签
- 删除用户标签（单个/批量/清空）
- 标签定义查询
- 标签历史查询
- 标签同步到Coze

核心接口：
- GET /api/tag/ - 获取用户标签
- POST /api/tag/ - 设置单个标签
- DELETE /api/tag/<tag_key> - 删除单个标签
- POST /api/tag/batch - 批量设置标签
- DELETE /api/tag/batch - 批量删除标签
- POST /api/tag/clear - 清空所有标签
- GET /api/tag/definitions - 获取标签定义
- GET /api/tag/history - 获取标签历史
- POST /api/tag/sync - 同步到Coze

作者: 智糖团队
日期: 2025-01-15
"""

import re
from flask import request, jsonify
from . import tag_bp
from utils.jwt_helper import no_auth_required as token_required
from services.tag_service import get_tag_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 获取服务实例
tag_service = get_tag_service()


@tag_bp.route('/', methods=['GET'], endpoint='get_user_tags')
@token_required
def get_user_tags(user_id):
    """
    获取用户标签（支持分页）
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        user_id: 用户ID（可选，如果提供则查询此用户的标签，否则查询token中的user_id，支持管理员查询其他用户）
        category: 标签分类（可选）
        page: 页码（从1开始，默认1）
        page_size: 每页数量（默认50）
    """
    try:
        # 如果查询参数中提供了user_id，则使用此值（支持管理员查询其他用户的标签）
        target_user_id = request.args.get('user_id')
        if target_user_id:
            try:
                target_user_id = int(target_user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': '无效的用户ID'
                }), 400
        else:
            target_user_id = user_id
        
        category = request.args.get('category')

        # 获取分页参数
        page = request.args.get('page', '1')
        page_size = request.args.get('page_size', '50')

        # 参数验证和转换
        try:
            page = int(page)
            page_size = int(page_size)
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 50
        except ValueError:
            page = 1
            page_size = 50

        logger.info(f"📋 查询用户标签: user_id={target_user_id}, category={category}, page={page}, page_size={page_size}")
        result = tag_service.get_user_tags(target_user_id, category, page, page_size)
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 获取用户标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {
                'user_id': target_user_id if 'target_user_id' in locals() else user_id,
                'tags': {'basic': [], 'health': [], 'behavior': [], 'stats': []},
                'total': 0,
                'page': 1,
                'page_size': 50,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            },
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/', methods=['POST'], endpoint='set_user_tag')
@token_required
def set_user_tag(user_id):
    """
    设置用户标签
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "user_id": 用户ID（可选，如果提供则使用此值，否则使用token中的user_id）,
            "tag_key": "标签键",
            "tag_value": "标签值",
            "source": "数据来源"
        }
    """
    try:
        data = request.get_json()
        
        # 如果请求体中提供了user_id，则使用请求体中的值（支持管理员为其他用户设置标签）
        target_user_id = data.get('user_id', user_id)
        tag_key = data.get('tag_key')
        tag_value = data.get('tag_value')
        source = data.get('source', 'manual')
        
        if not tag_key or tag_value is None:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '标签键和标签值不能为空'
            }), 400
        
        logger.info(f"🔧 设置标签: user_id={target_user_id}, tag_key={tag_key}, tag_value={tag_value}, source={source}")
        result = tag_service.set_user_tag(target_user_id, tag_key, tag_value, source)
        logger.info(f"📋 设置标签结果: {result}")
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 设置用户标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/batch', methods=['POST'], endpoint='batch_set_tags')
@token_required
def batch_set_tags(user_id):
    """
    批量设置标签
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "user_id": 用户ID（可选，如果提供则使用此值，否则使用token中的user_id，支持管理员为其他用户设置标签）,
            "tags": {
                "tag_key1": "value1",
                "tag_key2": "value2"
            },
            "source": "数据来源"
        }
    """
    try:
        data = request.get_json()
        
        # 如果请求体中提供了user_id，则使用请求体中的值（支持管理员为其他用户设置标签）
        target_user_id = data.get('user_id', user_id)
        tags = data.get('tags', {})
        source = data.get('source', 'manual')
        
        if not tags:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '标签不能为空'
            }), 400
        
        logger.info(f"🔧 批量设置标签: user_id={target_user_id}, tags_count={len(tags)}, source={source}")
        result = tag_service.batch_set_tags(target_user_id, tags, source)
        logger.info(f"📋 批量设置标签结果: {result}")
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 批量设置标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/definitions', methods=['GET'], endpoint='get_tag_definitions')
@token_required
def get_tag_definitions(user_id):
    """
    获取标签定义列表（支持分页）
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        category: 分类过滤
        page: 页码（从1开始，默认1）
        page_size: 每页数量（默认50）
    """
    try:
        category = request.args.get('category')

        # 获取分页参数
        page = request.args.get('page', '1')
        page_size = request.args.get('page_size', '50')

        # 参数验证和转换
        try:
            page = int(page)
            page_size = int(page_size)
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 50
        except ValueError:
            page = 1
            page_size = 50

        definitions = tag_service.get_tag_definitions(category=category, page=page, page_size=page_size)
        
        return jsonify(definitions), 200 if definitions.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 获取标签定义失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {
                'definitions': [],
                'total': 0,
                'page': 1,
                'page_size': 50,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            },
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/history', methods=['GET'], endpoint='get_tag_history')
@token_required
def get_tag_history(user_id):
    """
    获取标签更新历史（支持分页）
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        page: 页码（从1开始，默认1）
        page_size: 每页数量（默认50）
        limit: 返回记录数（向后兼容，已废弃，建议使用page_size）
    """
    try:
        # 安全转换整数参数
        def safe_int(value, default=0):
            if not value or not str(value).strip():
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        # 获取分页参数
        page = safe_int(request.args.get('page'), default=1)
        page_size = safe_int(request.args.get('page_size'), default=50)

        # 向后兼容：如果提供了limit参数，则将其作为page_size
        limit = request.args.get('limit')
        if limit and not request.args.get('page_size'):
            try:
                page_size = int(limit)
            except (ValueError, TypeError):
                page_size = 50

        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50

        history = tag_service.get_tag_history(user_id, page, page_size)
        
        return jsonify({
            'code': 200,
            'data': history,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取标签历史失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {
                'records': [],
                'total': 0,
                'page': 1,
                'page_size': 50,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            },
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/sync', methods=['POST'], endpoint='sync_tags_to_coze')
@token_required
def sync_tags_to_coze(user_id):
    """
    同步标签到Coze

    Headers:
        Authorization: Bearer <token>
    """
    try:
        result = tag_service.sync_user_tags_to_coze(user_id)

        return jsonify({
            'code': 200 if result else 500,
            'data': {},
            'success': result,
            'message': '标签同步成功' if result else '标签同步失败'
        }), 200 if result else 500

    except Exception as e:
        logger.error(f"❌ 同步标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/<tag_key>', methods=['DELETE'], endpoint='delete_user_tag') 
@token_required
def delete_user_tag(user_id, tag_key):
    """
    删除单个用户标签（重置为默认值）

    Headers:
        Authorization: Bearer <token>

    Path Parameters:
        tag_key: 标签键
    """
    try:
        result = tag_service.delete_user_tag(user_id, tag_key)
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"❌ 删除用户标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/batch', methods=['DELETE'], endpoint='batch_delete_tags')
@token_required
def batch_delete_tags(user_id):
    """
    批量删除用户标签

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "user_id": 用户ID（可选，如果提供则使用此值，否则使用token中的user_id，支持管理员为其他用户删除标签）,
            "tag_keys": ["tag_key1", "tag_key2"],  // 可选，不传则删除所有标签
            "clear_all": true  // 可选，true表示清空所有标签
        }
    """
    try:
        data = request.get_json() or {}
        # 如果请求体中提供了user_id，则使用请求体中的值（支持管理员为其他用户删除标签）
        target_user_id = data.get('user_id', user_id)
        tag_keys = data.get('tag_keys')
        clear_all = data.get('clear_all', False)

        logger.info(f"🗑️ 批量删除标签: user_id={target_user_id}, clear_all={clear_all}, tag_keys={tag_keys}")

        if clear_all or not tag_keys:
            # 清空所有标签
            result = tag_service.clear_all_user_tags(target_user_id)
        else:
            # 删除指定标签
            result = tag_service.batch_delete_tags(target_user_id, tag_keys)

        logger.info(f"📋 批量删除标签结果: {result}")
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"❌ 批量删除标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/clear', methods=['POST'], endpoint='clear_all_tags')
@token_required
def clear_all_tags(user_id):
    """
    清空用户所有标签

    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "user_id": 用户ID（可选，如果提供则使用此值，否则使用token中的user_id，支持管理员为其他用户删除标签）
        }
    """
    try:
        data = request.get_json() or {}
        # 如果请求体中提供了user_id，则使用请求体中的值（支持管理员为其他用户删除标签）
        target_user_id = data.get('user_id', user_id)
        
        logger.info(f"🗑️ 清空用户所有标签: user_id={target_user_id}")
        result = tag_service.clear_all_user_tags(target_user_id)
        logger.info(f"📋 清空标签结果: {result}")
        return jsonify(result), result.get('code', 500)

    except Exception as e:
        logger.error(f"❌ 清空用户标签失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/mappings', methods=['GET'], endpoint='get_user_tag_mappings')
@token_required
def get_user_tag_mappings(user_id):
    """
    获取用户和标签的映射关系列表（支持筛选和分页）

    Headers:
        Authorization: Bearer <token>

    Query:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        user_id: 用户ID（可选，精确匹配）
        username: 用户名或昵称（可选，支持模糊搜索，会同时搜索username和nickname字段）
        phone_number: 手机号（可选，支持模糊搜索）
        tag_key: 标签键（可选，筛选特定标签）
        tag_category: 标签分类（可选）
        
    注意：username参数会同时匹配username和nickname字段，phone_number支持部分匹配
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        filter_user_id = request.args.get('user_id')
        username = request.args.get('username', '').strip()
        phone_number = request.args.get('phone_number', '').strip()
        tag_key = request.args.get('tag_key')
        tag_category = request.args.get('tag_category')

        result = tag_service.get_user_tag_mappings(
            page=page,
            page_size=page_size,
            user_id=filter_user_id,
            username=username if username else None,
            phone_number=phone_number if phone_number else None,
            tag_key=tag_key,
            tag_category=tag_category
        )
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取用户标签映射关系失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tag_bp.route('/mappings/export', methods=['GET'], endpoint='export_user_tag_mappings')
@token_required
def export_user_tag_mappings(user_id):
    """
    导出用户和标签的映射关系
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        user_id: 用户ID（可选，精确匹配）
        username: 用户名或昵称（可选，支持模糊搜索，会同时搜索username和nickname字段）
        phone_number: 手机号（可选，支持模糊搜索）
        tag_key: 标签键（可选，筛选特定标签）
        tag_category: 标签分类（可选）
        format: 导出格式（csv或excel，默认excel）
    """
    try:
        filter_user_id = request.args.get('user_id')
        username = request.args.get('username', '').strip()
        phone_number = request.args.get('phone_number', '').strip()
        tag_key = request.args.get('tag_key')
        tag_category = request.args.get('tag_category')
        export_format = request.args.get('format', 'excel').lower()
        
        result = tag_service.export_user_tag_mappings(
            user_id=filter_user_id,
            username=username if username else None,
            phone_number=phone_number if phone_number else None,
            tag_key=tag_key,
            tag_category=tag_category,
            format=export_format
        )
        
        if result.get('success'):
            from flask import Response
            return Response(
                result.get('data', {}).get('content', ''),
                mimetype=result.get('data', {}).get('mimetype', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                headers={
                    'Content-Disposition': f'attachment; filename={result.get("data", {}).get("filename", "user_tag_mappings.xlsx")}'
                }
            )
        else:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': result.get('message', '导出失败')
            }), 400
        
    except Exception as e:
        logger.error(f"❌ 导出用户标签映射关系失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

