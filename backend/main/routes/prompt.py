"""
提示词路由
~~~~~~~~~

提示词管理的API端点：
- 提示词模板管理
- 用户提示词设置

作者: 智糖团队
日期: 2025-01-17
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from models.prompt import PromptTemplate, UserPromptSetting
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建Blueprint
prompt_bp = Blueprint('prompt', __name__, url_prefix='/api/prompt')


@prompt_bp.route('/templates', methods=['GET'], endpoint='get_templates')
@token_required
def get_templates(user_id):
    """
    获取提示词模板列表

    Headers:
        Authorization: Bearer <token>

    Query:
        type: 提示词类型过滤 (initial/normal/tagging)
        active_only: 是否只获取启用的模板 (默认true)
    """
    try:
        prompt_type = request.args.get('type')
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        templates = PromptTemplate.get_all(prompt_type, active_only)

        result = {
            'success': True,
            'data': [template.to_dict() for template in templates],
            'total': len(templates)
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ 获取提示词模板失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/templates/<int:prompt_id>', methods=['GET'], endpoint='get_template')
@token_required
def get_template(user_id, prompt_id):
    """
    获取指定提示词模板

    Headers:
        Authorization: Bearer <token>
    """
    try:
        template = PromptTemplate.get_by_id(prompt_id)

        if not template:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '提示词模板不存在'
            }), 404

        result = {
            'success': True,
            'data': template.to_dict()
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ 获取提示词模板失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/templates', methods=['POST'], endpoint='create_template')
@token_required
def create_template(user_id):
    """
    创建提示词模板

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "prompt_type": "initial|normal|tagging",
            "prompt_name": "模板名称",
            "prompt_content": "提示词内容",
            "version": 1 (可选，默认为1),
            "is_active": true (可选，默认为true)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '请求体不能为空'
            }), 400

        # 验证必需字段
        required_fields = ['prompt_type', 'prompt_name', 'prompt_content']
        for field in required_fields:
            if field not in data or not str(data.get(field, '')).strip():
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': f'缺少必需字段或字段为空: {field}'
                }), 400

        prompt_type = data.get('prompt_type').strip()
        if prompt_type not in ['initial', 'normal', 'tagging']:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': f'提示词类型无效: {prompt_type}，必须是 initial、normal 或 tagging 之一'
            }), 400

        prompt_name = data.get('prompt_name').strip()
        prompt_content = data.get('prompt_content').strip()
        version = int(data.get('version', 1))
        is_active = bool(data.get('is_active', True))

        # 创建模板
        from utils.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                INSERT INTO prompt_templates 
                (prompt_type, prompt_name, prompt_content, version, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                prompt_type,
                prompt_name,
                prompt_content,
                version,
                is_active
            ))
            
            prompt_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"✅ 创建提示词模板成功: prompt_id={prompt_id}, type={prompt_type}, name={prompt_name}")
            
            # 获取创建后的完整信息
            cursor.execute("SELECT * FROM prompt_templates WHERE prompt_id = %s", (prompt_id,))
            created_template = cursor.fetchone()
            
            result = {
                'success': True,
                'message': '提示词模板创建成功',
                'data': {
                    'prompt_id': prompt_id,
                    'prompt_type': created_template['prompt_type'],
                    'prompt_name': created_template['prompt_name'],
                    'prompt_content': created_template['prompt_content'],
                    'version': created_template['version'],
                    'is_active': bool(created_template['is_active']),
                    'created_at': created_template.get('created_at').isoformat() if created_template.get('created_at') else None
                }
            }
            
            return jsonify(result), 201
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"❌ 数据库操作失败: {str(db_error)}")
            raise
        finally:
            cursor.close()
            conn.close()

    except ValueError as e:
        logger.error(f"❌ 参数验证失败: {str(e)}")
        return jsonify({
            'code': 400,
            'data': {},
            'success': False,
            'message': f'参数错误: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"❌ 创建提示词模板失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/templates/<int:prompt_id>', methods=['PUT'], endpoint='update_template')
@token_required
def update_template(user_id, prompt_id):
    """
    更新提示词模板

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "prompt_name": "更新后的模板名称",
            "prompt_content": "更新后的提示词内容",
            "version": 2,
            "is_active": true
        }
    """
    try:
        template = PromptTemplate.get_by_id(prompt_id)
        if not template:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '提示词模板不存在'
            }), 404

        data = request.get_json()
        
        from utils.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if 'prompt_name' in data:
            update_fields.append('prompt_name = %s')
            params.append(data['prompt_name'])
        
        if 'prompt_content' in data:
            update_fields.append('prompt_content = %s')
            params.append(data['prompt_content'])
        
        if 'version' in data:
            update_fields.append('version = %s')
            params.append(data['version'])
        
        if 'is_active' in data:
            update_fields.append('is_active = %s')
            params.append(data['is_active'])
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '没有要更新的字段'
            }), 400
        
        params.append(prompt_id)
        sql = f"UPDATE prompt_templates SET {', '.join(update_fields)}, updated_at = NOW() WHERE prompt_id = %s"
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        conn.close()
        
        result = {
            'success': True,
            'message': '提示词模板更新成功'
        }
        
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ 更新提示词模板失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/templates/<int:prompt_id>', methods=['DELETE'], endpoint='delete_template')
@token_required
def delete_template(user_id, prompt_id):
    """
    删除提示词模板

    Headers:
        Authorization: Bearer <token>
    """
    try:
        template = PromptTemplate.get_by_id(prompt_id)
        if not template:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '提示词模板不存在'
            }), 404

        from utils.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 软删除：将is_active设置为False，而不是真正删除
        sql = "UPDATE prompt_templates SET is_active = FALSE, updated_at = NOW() WHERE prompt_id = %s"
        cursor.execute(sql, (prompt_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        result = {
            'success': True,
            'message': '提示词模板删除成功'
        }
        
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ 删除提示词模板失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/user-settings', methods=['GET'], endpoint='get_user_settings')
@token_required
def get_user_settings(user_id):
    """
    获取用户提示词设置
    
    说明：
    - 返回用户的自定义提示词设置（如果存在）
    - 如果没有自定义设置，返回空字典，系统会使用默认模板
    - 支持管理员查询其他用户的设置

    Headers:
        Authorization: Bearer <token>
    
    Query:
        user_id: 用户ID（可选，如果提供则查询此用户的设置，否则查询token中的user_id）
        include_defaults: 是否包含默认模板信息（可选，默认false）
    """
    try:
        # 如果查询参数中提供了user_id，则使用此值（支持管理员查询其他用户的设置）
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
        
        include_defaults = request.args.get('include_defaults', 'false').lower() == 'true'
        
        logger.info(f"📋 查询用户提示词设置: user_id={target_user_id}, include_defaults={include_defaults}")
        
        # 获取用户自定义设置
        settings = UserPromptSetting.get_user_settings(target_user_id)
        
        # 如果需要包含默认模板信息
        if include_defaults:
            default_templates = {}
            for prompt_type in ['initial', 'normal', 'tagging']:
                if prompt_type not in settings:
                    # 用户没有自定义设置，获取默认模板
                    template = PromptTemplate.get_by_type(prompt_type)
                    if template:
                        default_templates[prompt_type] = {
                            'prompt_content': template.prompt_content,
                            'is_custom': False,
                            'prompt_name': template.prompt_name,
                            'version': template.version,
                            'prompt_id': template.prompt_id,
                            'custom_content': None,
                            'is_default': True  # 标记为默认模板
                        }
            
            # 合并自定义设置和默认模板
            result_data = {**default_templates, **settings}
        else:
            result_data = settings

        result = {
            'success': True,
            'user_id': target_user_id,
            'data': result_data,
            'has_custom_settings': len(settings) > 0,
            'message': '返回用户自定义提示词设置' if len(settings) > 0 else '用户未设置自定义提示词，将使用默认模板'
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ 获取用户提示词设置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/user-settings', methods=['PUT'], endpoint='update_user_settings')
@token_required
def update_user_settings(user_id):
    """
    更新用户提示词设置

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "settings": {
                "initial": {"prompt_id": 1},
                "normal": {"custom_content": "自定义提示词"},
                "tagging": {"prompt_id": 3}
            }
        }
    """
    try:
        data = request.get_json()

        if 'settings' not in data:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '缺少settings字段'
            }), 400

        settings = data.get('settings', {})
        success_count = 0
        errors = []

        for prompt_type, config in settings.items():
            if prompt_type not in ['initial', 'normal', 'tagging']:
                errors.append(f'无效的提示词类型: {prompt_type}')
                continue

            try:
                if 'custom_content' in config:
                    # 使用自定义提示词
                    success = UserPromptSetting.set_user_prompt(
                        user_id, prompt_type, custom_content=config['custom_content']
                    )
                elif 'prompt_id' in config:
                    # 使用模板提示词
                    success = UserPromptSetting.set_user_prompt(
                        user_id, prompt_type, prompt_id=config['prompt_id']
                    )
                else:
                    errors.append(f'{prompt_type}: 缺少prompt_id或custom_content')
                    continue

                if success:
                    success_count += 1
                else:
                    errors.append(f'{prompt_type}: 设置失败')

            except Exception as e:
                errors.append(f'{prompt_type}: {str(e)}')

        result = {
            'success': success_count > 0,
            'message': f'成功更新 {success_count} 个提示词设置',
            'success_count': success_count,
            'errors': errors
        }

        return jsonify(result), 200 if success_count > 0 else 400

    except Exception as e:
        logger.error(f"❌ 更新用户提示词设置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/user-settings/<prompt_type>', methods=['PUT'], endpoint='update_single_setting')
@token_required
def update_single_setting(user_id, prompt_type):
    """
    更新单个提示词设置

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "prompt_id": 1  // 或
            "custom_content": "自定义提示词"
        }
    """
    try:
        if prompt_type not in ['initial', 'normal', 'tagging']:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '提示词类型无效'
            }), 400

        data = request.get_json()

        if 'custom_content' in data:
            success = UserPromptSetting.set_user_prompt(
                user_id, prompt_type, custom_content=data['custom_content']
            )
        elif 'prompt_id' in data:
            success = UserPromptSetting.set_user_prompt(
                user_id, prompt_type, prompt_id=data['prompt_id']
            )
        else:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '缺少prompt_id或custom_content字段'
            }), 400

        if success:
            result = {
                'success': True,
                'message': f'{prompt_type} 提示词设置更新成功'
            }
            return jsonify(result), 200
        else:
            return jsonify({
                'code': 500,
                'data': {},
                'success': False,
                'message': '设置失败'
            }), 500

    except Exception as e:
        logger.error(f"❌ 更新提示词设置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@prompt_bp.route('/user-settings/<prompt_type>', methods=['DELETE'], endpoint='reset_user_setting')
@token_required
def reset_user_setting(user_id, prompt_type):
    """
    重置用户提示词设置（使用默认模板）

    Headers:
        Authorization: Bearer <token>
    """
    try:
        if prompt_type not in ['initial', 'normal', 'tagging']:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '提示词类型无效'
            }), 400

        # 获取默认模板
        template = PromptTemplate.get_by_type(prompt_type)
        if not template:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '未找到默认模板'
            }), 404

        success = UserPromptSetting.set_user_prompt(
            user_id, prompt_type, prompt_id=template.prompt_id
        )

        if success:
            result = {
                'success': True,
                'message': f'{prompt_type} 提示词已重置为默认设置'
            }
            return jsonify(result), 200
        else:
            return jsonify({
                'code': 500,
                'data': {},
                'success': False,
                'message': '重置失败'
            }), 500

    except Exception as e:
        logger.error(f"❌ 重置提示词设置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500
