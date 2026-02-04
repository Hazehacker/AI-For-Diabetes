"""
对话路由 - 【核心文件】
~~~~~~~

对话管理的API端点：
- 流式对话（普通对话和TTS对话）
- 对话历史查询和分页
- 对话会话管理
- 新手引导状态查询
- 语音转文本（ASR）

核心接口：
- POST /api/chat/stream: 普通流式对话
- POST /api/chat/stream_with_tts: 带语音合成的对话
- GET /api/chat/history: 对话历史查询
- GET /api/chat/sessions: 会话列表查询
- GET /api/chat/onboarding/status: 新手引导状态
- POST /api/chat/speech_to_text: 语音转文本

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify, Response, stream_with_context
from . import chat_bp
from utils.jwt_helper import no_auth_required as token_required
from services.chat_service import get_chat_service
from services.coze_service import CozeService
from utils.logger import get_logger
from utils.database import get_db_connection
from datetime import datetime
import base64

logger = get_logger(__name__)

# 获取服务实例
chat_service = get_chat_service()
coze_service = CozeService()


@chat_bp.route('/history', methods=['GET'], endpoint='get_chat_history')
def get_chat_history():
    """
    获取对话历史
    
    Query:
        user_id: 用户ID（可选，如果提供则查询此用户的对话历史，如果不传或传空值则查询所有用户的记录）
        conversation_id: 对话ID（可选，指定对话ID则只返回该对话的消息）
        page: 页码（可选，默认1）
        page_size: 每页数量（可选，默认20）
        limit: 返回消息数量（可选，默认50，如果指定了page和page_size则忽略此参数）
        start_date: 开始日期（可选，格式：YYYY-MM-DD）
        end_date: 结束日期（可选，格式：YYYY-MM-DD）
        username: 用户名称（可选，支持模糊查询，匹配username和nickname）
        phone_number: 手机号（可选，支持模糊查询）
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
        
        # 从请求参数获取user_id（可选）
        user_id_param = request.args.get('user_id')
        target_user_id = None

        if user_id_param and user_id_param.strip():
            try:
                target_user_id = int(user_id_param.strip())
            except (ValueError, TypeError):
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': '无效的用户ID'
                }), 400
        
        conversation_id = request.args.get('conversation_id')
        # 如果conversation_id是空字符串，设为None
        if conversation_id is not None and not conversation_id.strip():
            conversation_id = None
        
        page = safe_int(request.args.get('page'), default=0)
        page_size = safe_int(request.args.get('page_size'), default=0)
        limit = safe_int(request.args.get('limit'), default=50)
        
        start_date = request.args.get('start_date')
        # 如果start_date是空字符串，设为None
        if start_date is not None and not start_date.strip():
            start_date = None
        
        end_date = request.args.get('end_date')
        # 如果end_date是空字符串，设为None
        if end_date is not None and not end_date.strip():
            end_date = None
        
        username = request.args.get('username')
        # 如果username是空字符串，设为None
        if username is not None:
            username = username.strip()
            if not username:
                username = None

        phone_number = request.args.get('phone_number')
        # 如果phone_number是空字符串，设为None
        if phone_number is not None:
            phone_number = phone_number.strip()
            if not phone_number:
                phone_number = None
        
        # 如果指定了分页参数，使用分页；否则使用limit
        use_pagination = page > 0 and page_size > 0
        if use_pagination:
            limit = None  # 分页模式下不使用limit
        
        logger.info(f"📋 查询对话历史: user_id={target_user_id} (None表示查询所有用户), conversation_id={conversation_id}, page={page}, page_size={page_size}, limit={limit}, start_date={start_date}, end_date={end_date}, username={username}, phone_number={phone_number}")
        
        result = chat_service.get_chat_history(
            target_user_id,
            conversation_id,
            limit=limit,
            page=page if use_pagination else None,
            page_size=page_size if use_pagination else None,
            start_date=start_date,
            end_date=end_date,
            username=username,
            phone_number=phone_number
        )
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取对话历史失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/sessions', methods=['GET'], endpoint='get_chat_sessions')
@token_required
def get_chat_sessions(user_id):
    """
    获取对话会话列表
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        page: 页码
        page_size: 每页数量
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
        
        # 从请求参数获取user_id
        user_id_param = request.args.get('user_id')
        if not user_id_param or not user_id_param.strip():
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id_param.strip())
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '无效的用户ID'
            }), 400

        page = safe_int(request.args.get('page'), default=1)
        page_size = safe_int(request.args.get('page_size'), default=20)
        
        result = chat_service.get_chat_sessions(user_id, page, page_size)
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取对话会话失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/sessions/latest', methods=['GET'], endpoint='get_latest_session')
def get_latest_session():
    """
    获取用户最新的对话会话
    
    Query:
        user_id: 用户ID（必须）
    """
    try:
        # 从请求参数获取user_id
        user_id_param = request.args.get('user_id')
        if not user_id_param or not user_id_param.strip():
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id_param.strip())
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '无效的用户ID'
            }), 400

        result = chat_service.get_latest_session(user_id)
        
        if result.get('success'):
            return jsonify({
                'code': 200,
                'data': result.get('data', {}),
                'success': True
            }), 200
        else:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': result.get('message', '未找到会话')
            }), 404
        
    except Exception as e:
        logger.error(f"❌ 获取最新会话失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/onboarding/status', methods=['GET'], endpoint='get_onboarding_status')
@token_required
def get_onboarding_status(user_id):
    """
    获取用户信息收集状态
    
    返回:
        - 是否完成信息收集
        - 缺失的信息项
        - 已收集的信息
        - 当前使用的提示词类型
    """
    try:
        # 从请求参数获取user_id
        user_id_param = request.args.get('user_id')
        if not user_id_param or not user_id_param.strip():
            return jsonify({
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id_param.strip())
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': '无效的用户ID'
            }), 400

        from models.tag import TagValue
        
        # 判断是否为初次对话
        is_initial = chat_service._is_initial_conversation(user_id)
        
        # 获取用户标签
        user_tags, _ = TagValue.get_user_tags(user_id)
        tag_dict = {tag['tag_key']: tag['tag_value'] for tag in user_tags}
        
        # 必要信息项
        required_tags = [
            'age',              # 年龄
            'gender',           # 性别
            'diabetes_type',    # 糖尿病类型
            'disease_duration_years',  # 病程（年）
            'insulin_route',    # 胰岛素给药途径
            'cgm_usage'         # CGM使用情况
        ]
        
        # 检查缺失信息
        missing_tags = []
        collected_tags = {}
        
        for tag_key in required_tags:
            tag_value = tag_dict.get(tag_key)
            if not tag_value or (isinstance(tag_value, str) and tag_value.strip() == ''):
                missing_tags.append(tag_key)
            else:
                collected_tags[tag_key] = tag_value
        
        # 完成状态
        onboarding_completed = tag_dict.get('onboarding_completed', 'false').lower() == 'true'
        
        # 当前提示词类型
        current_prompt_type = "initial" if is_initial else "normal"
        
        return jsonify({
            'success': True,
            'data': {
                'is_completed': not is_initial,
                'onboarding_completed': onboarding_completed,
                'current_prompt_type': current_prompt_type,
                'missing_tags': missing_tags,
                'collected_tags': collected_tags,
                'progress': {
                    'total': len(required_tags),
                    'collected': len(collected_tags),
                    'missing': len(missing_tags),
                    'percentage': round(len(collected_tags) / len(required_tags) * 100, 1) if required_tags else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f"❌ 获取信息收集状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取状态失败: {str(e)}'
        }), 500


@chat_bp.route('/stream', methods=['POST'], endpoint='stream_chat')
@token_required
def stream_chat(user_id):
    """
    流式对话

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "message": "用户消息",
            "conversation_id": "对话ID（可选）"
        }
    """
    try:
        data = request.get_json()

        # 从请求体获取user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '无效的用户ID'
            }), 400

        logger.info(f"🎯 用户 {user_id} 发起流式对话")
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        logger.info(f"📝 用户 {user_id} 消息: '{message}', 会话ID: {conversation_id}")
        
        if not message:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '消息不能为空'
            }), 400
        
        def generate():
            try:
                for event in chat_service.stream_chat(user_id, message, conversation_id):
                    # SSE格式
                    event_type = event.get('event', 'message')
                    event_data = event.get('data', {})
                    
                    yield f"event: {event_type}\n"
                    yield f"data: {jsonify(event_data).get_data(as_text=True)}\n\n"
                    
            except Exception as e:
                logger.error(f"❌ 流式对话错误: {str(e)}")
                yield f"event: error\n"
                yield f"data: {{'message': '{str(e)}'}}\n\n"
        
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 流式对话失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/stream_with_tts', methods=['POST'], endpoint='stream_chat_with_tts')
@token_required
def stream_chat_with_tts(user_id):
    """
    带TTS的流式对话

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "message_content": "用户消息",
            "conversation_id": "对话ID（可选）",
            "enable_tts": true
        }
    """
    try:
        data = request.get_json()

        # 从请求体获取user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '无效的用户ID'
            }), 400

        logger.info(f"🎯 用户 {user_id} 发起流式对话（带TTS）")
        message = data.get('message_content') or data.get('message')
        conversation_id = data.get('conversation_id')
        enable_tts = data.get('enable_tts', True)
        logger.info(f"📝 用户 {user_id} 消息: '{message}', 会话ID: {conversation_id}, TTS: {enable_tts}")
        
        if not message:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '消息不能为空'
            }), 400
        
        def generate():
            try:
                import json
                for event in chat_service.stream_chat_with_tts(
                    user_id, message, conversation_id, enable_tts
                ):
                    # SSE格式
                    event_type = event.get('event', 'message')
                    event_data = event.get('data', {})
                    
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                    
            except Exception as e:
                logger.error(f"❌ 带TTS的流式对话错误: {str(e)}")
                yield f"event: error\n"
                yield f"data: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 带TTS的流式对话失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/speech_to_text', methods=['POST'], endpoint='speech_to_text')
@token_required
def speech_to_text(user_id):
    """
    语音转文本 (ASR) - 支持Base64和文件上传两种方式
    """
    """
    语音转文本 (ASR)
    
    Headers:
        Authorization: Bearer <token>
        Content-Type: multipart/form-data 或 application/json
    
    Body (multipart/form-data):
        audio: 音频文件 (WAV格式)
    
    Body (application/json):
        {
            "audio_base64": "base64编码的音频数据",
            "audio_format": "wav" (可选，默认wav)
        }
    """
    try:
        # 从请求获取user_id
        user_id = None
        if request.content_type and 'multipart/form-data' in request.content_type:
            user_id = request.form.get('user_id')
        elif request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            user_id = data.get('user_id')
        else:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '不支持的Content-Type'
            }), 400

        if not user_id:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须提供user_id参数'
            }), 400

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '无效的用户ID'
            }), 400

        audio_data = None
        audio_file_path = None
        
        # 检查请求类型
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 文件上传方式
            if 'audio' in request.files:
                audio_file = request.files['audio']
                audio_data = audio_file.read()
                logger.info(f"📥 收到音频文件，大小: {len(audio_data)} bytes")
            else:
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': '请提供音频文件'
                }), 400
                
        elif request.content_type and 'application/json' in request.content_type:
            # Base64编码方式
            data = request.get_json()
            audio_base64 = data.get('audio_base64')
            
            if not audio_base64:
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': '请提供audio_base64字段'
                }), 400
            
            try:
                # 解码Base64
                audio_data = base64.b64decode(audio_base64)
                logger.info(f"📥 收到Base64音频，大小: {len(audio_data)} bytes")
            except Exception as e:
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': f'Base64解码失败: {str(e)}'
                }), 400
        else:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '不支持的Content-Type，请使用multipart/form-data或application/json'
            }), 400
        
        if not audio_data:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '音频数据为空'
            }), 400
        
        # 获取音频格式（从请求中获取，默认为wav）
        if request.is_json:
            audio_format = request.json.get('audio_format', 'wav')
        else:
            audio_format = request.form.get('audio_format', 'wav')
        
        # 根据格式设置MIME类型
        mime_type_map = {
            'wav': 'audio/wav',
            'webm': 'audio/webm',
            'mp3': 'audio/mpeg',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg'
        }
        mime_type = mime_type_map.get(audio_format.lower(), 'audio/wav')
        file_extension = audio_format.lower()
        
        # 调用服务进行语音识别
        logger.info(f"🎤 开始语音识别: user_id={user_id}, format={audio_format}, mime_type={mime_type}, size={len(audio_data)} bytes")
        result = coze_service.speech_to_text(
            user_id=user_id,
            audio_data=audio_data,
            audio_format=audio_format,
            mime_type=mime_type
        )
        logger.info(f"🎯 语音识别完成: success={result.get('success') if result else False}, text='{result.get('text', '') if result else ''}'")
        
        if result.get('success'):
            return jsonify({
                'code': 200,
                'data': result.get('data', {}),
                'success': True,
                'text': result.get('text', '')
            }), 200
        else:
            return jsonify({
                'code': 500,
                'data': {},
                'success': False,
                'message': result.get('message', '语音识别失败')
            }), 500
            
    except Exception as e:
        logger.error(f"❌ 语音转文本失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@chat_bp.route('/history/export', methods=['POST'], endpoint='export_chat_history')
def export_chat_history():
    """
    导出聊天历史记录

    Body:
        user_id: 用户ID（可选，如果不提供则导出所有用户的数据）
        conversation_id: 会话ID（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        username: 用户名称（可选，支持模糊查询，匹配username和nickname）
        phone_number: 手机号（可选，支持模糊查询）
        format: 导出格式（可选：csv, excel，默认excel）
    """
    try:
        data = request.get_json() or {}

        # 从请求体获取user_id（可选）
        target_user_id = data.get('user_id')

        # 构建查询条件
        conditions = []
        params = []

        if target_user_id:
            try:
                target_user_id = int(target_user_id)
                conditions.append("cm.user_id = %s")
                params.append(target_user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'code': 400,
                    'data': {},
                    'success': False,
                    'message': '无效的用户ID'
                }), 400

        conversation_id = data.get('conversation_id')
        if conversation_id:
            conditions.append("cm.conversation_id = %s")
            params.append(conversation_id)

        start_date = data.get('start_date')
        if start_date:
            conditions.append("DATE(cm.created_at) >= %s")
            params.append(start_date)

        end_date = data.get('end_date')
        if end_date:
            conditions.append("DATE(cm.created_at) <= %s")
            params.append(end_date)

        # 用户名称过滤（支持模糊查询，匹配username和nickname）
        username = data.get('username')
        if username:
            username = str(username).strip()
            if username:
                conditions.append("(u.username LIKE %s OR u.nickname LIKE %s)")
                username_pattern = f"%{username}%"
                params.extend([username_pattern, username_pattern])

        # 手机号过滤（支持模糊查询）
        phone_number = data.get('phone_number')
        if phone_number:
            phone_number = str(phone_number).strip()
            if phone_number:
                conditions.append("u.phone_number LIKE %s")
                phone_pattern = f"%{phone_number}%"
                params.append(phone_pattern)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询聊天记录
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询消息数据，包含用户昵称和手机号
        cursor.execute(f"""
            SELECT
                cm.conversation_id,
                cm.user_id,
                cm.role,
                cm.content,
                cm.created_at,
                cm.message_id,
                u.username,
                u.nickname,
                u.phone_number
            FROM chat_messages cm
            LEFT JOIN users u ON cm.user_id = u.user_id
            WHERE {where_clause}
            ORDER BY cm.created_at ASC
        """, params)

        messages = cursor.fetchall()
        cursor.close()
        conn.close()

        if not messages:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '没有找到符合条件的聊天记录'
            }), 404

        # 将消息配对成对话轮次
        paired_turns = _pair_messages_into_turns(messages)

        if not paired_turns:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '没有找到完整的对话轮次'
            }), 404

        # 获取导出格式，默认使用excel
        export_format = data.get('format', 'excel').lower()

        if export_format == 'excel':
            return _export_paired_turns_to_excel(paired_turns)
        elif export_format == 'csv':
            return _export_paired_turns_to_csv(paired_turns)
        else:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '不支持的导出格式，仅支持: csv, excel'
            }), 400

    except Exception as e:
        logger.error(f"❌ 导出聊天记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


def _pair_messages_into_turns(messages):
    """将消息列表配对成对话轮次"""
    turns = []
    i = 0

    while i < len(messages) - 1:  # 至少需要两条消息才能配对
        current_message = messages[i]
        next_message = messages[i + 1]

        # 检查是否是user -> assistant配对
        if (current_message.get('role') == 'user' and
            next_message.get('role') == 'assistant' and
            current_message.get('conversation_id') == next_message.get('conversation_id')):

            # 创建对话轮次，包含用户昵称和手机号
            turn = {
                'conversation_id': current_message.get('conversation_id'),
                'user_id': current_message.get('user_id'),
                'username': current_message.get('username'),
                'nickname': current_message.get('nickname'),
                'phone_number': current_message.get('phone_number'),
                'user_question': current_message.get('content'),
                'ai_answer': next_message.get('content'),
                'question_time': current_message.get('created_at'),
                'answer_time': next_message.get('created_at'),
                'user_message_id': current_message.get('message_id'),
                'ai_message_id': next_message.get('message_id')
            }

            turns.append(turn)
            i += 2  # 跳过已配对的两条消息
        else:
            # 如果不是user-assistant配对，跳过当前消息
            i += 1

    return turns


def _export_paired_turns_to_excel(paired_turns):
    """导出配对的对话轮次到Excel格式"""
    try:
        import pandas as pd
        from io import BytesIO

        # 转换为DataFrame，包含用户昵称和手机号
        data = []
        for turn in paired_turns:
            data.append({
                '会话ID': turn.get('conversation_id') or '',
                '用户ID': turn.get('user_id') or '',
                '用户名': turn.get('username') or '',
                '用户昵称': turn.get('nickname') or '',
                '手机号': turn.get('phone_number') or '',
                '用户提问': turn.get('user_message') or turn.get('user_question') or '',
                'AI回答': turn.get('ai_message') or turn.get('ai_answer') or '',
                '提问时间': turn.get('question_time') or '',
                '回答时间': turn.get('answer_time') or ''
            })

        df = pd.DataFrame(data)

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='对话轮次', index=False)

            # 获取工作簿和工作表
            workbook = writer.book
            worksheet = writer.sheets['对话轮次']

            # 设置列宽
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)  # 最大宽度50
                worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)

        # 设置文件名
        filename = f"chat_turns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        response = Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

        logger.info(f"✅ 导出Excel对话轮次成功: 轮次数{len(paired_turns)}")
        return response

    except Exception as e:
        logger.error(f"❌ 导出Excel对话轮次失败: {str(e)}")
        raise


def _export_paired_turns_to_csv(paired_turns):
    """导出配对的对话轮次到CSV格式"""
    # 生成CSV内容
    csv_content = "会话ID,用户ID,用户名,用户昵称,用户提问,AI回答,提问时间,回答时间\n"

    for turn in paired_turns:
        # 处理可能的None值和特殊字符
        conversation_id = turn.get('conversation_id') or ''
        user_id_val = turn.get('user_id') or ''
        username = turn.get('username') or ''
        nickname = turn.get('nickname') or ''
        user_question = turn.get('user_question') or ''
        ai_answer = turn.get('ai_answer') or ''
        question_time = turn.get('question_time') or ''
        answer_time = turn.get('answer_time') or ''

        # 转义CSV中的特殊字符
        user_question = user_question.replace('"', '""')
        ai_answer = ai_answer.replace('"', '""')
        nickname = nickname.replace('"', '""')

        csv_content += f'"{conversation_id}","{user_id_val}","{username}","{nickname}","{user_question}","{ai_answer}","{question_time}","{answer_time}"\n'

    # 设置文件名
    filename = f"chat_turns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # 设置响应头，触发文件下载
    response = Response(
        csv_content,
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )

    logger.info(f"✅ 导出CSV对话轮次成功: 轮次数{len(paired_turns)}")
    return response

