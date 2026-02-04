"""
对话管理服务 - 【核心文件】
~~~~~~~~~~~

对话管理服务，包括：
- 对话历史查询和分页
- 流式对话（支持SSE）
- 对话记录保存和管理
- TTS集成对话
- 用户标签自动获取和应用
- 知识库FAQ检索和集成
- 新手引导状态判断

核心功能：
- stream_chat(): 普通流式对话
- stream_chat_with_tts(): 带语音合成的对话
- get_chat_history(): 对话历史查询
- _is_initial_conversation(): 判断是否需要信息收集

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any, Generator
from utils.database import get_db_connection, execute_query, execute_update
from utils.logger import get_logger
from services.deepseek_service import get_deepseek_service
from services.tts_service import get_tts_service
from services.knowledge_qa_service import get_knowledge_qa_service
from services.knowledge_service import get_knowledge_service
from services.tag_service import get_tag_service
from models.tag import TagValue

logger = get_logger(__name__)


class ChatService:
    """对话管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.deepseek_service = get_deepseek_service()
        self.tts_service = get_tts_service()
        self.knowledge_qa_service = get_knowledge_qa_service()
        self.dify_knowledge_service = get_knowledge_service()
    
    def _pair_messages_into_turns(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将消息列表配对成对话轮次

        Args:
            messages: 消息列表（按时间顺序排列，最旧的在前）

        Returns:
            List[Dict]: 对话轮次列表，每个轮次包含user_message和assistant_message
        """
        turns = []
        i = 0

        while i < len(messages) - 1:  # 至少需要两条消息才能配对
            current_message = messages[i]
            next_message = messages[i + 1]

            # 检查是否是user -> assistant配对
            if (current_message.get('role') == 'user' and
                next_message.get('role') == 'assistant' and
                current_message.get('conversation_id') == next_message.get('conversation_id')):

                # 创建对话轮次，包含用户信息
                turn = {
                    'conversation_id': current_message.get('conversation_id'),
                    'user_id': current_message.get('user_id'),
                    'username': current_message.get('username'),
                    'nickname': current_message.get('nickname'),
                    'phone_number': current_message.get('phone_number'),
                    'user_message_id': current_message.get('message_id'),
                    'assistant_message_id': next_message.get('message_id'),
                    'query': current_message.get('content'),
                    'ai_content': next_message.get('content'),
                    'created_at': current_message.get('created_at'),
                    'ai_created_at': next_message.get('created_at'),
                    'ai_provider': current_message.get('ai_provider'),
                    'ai_model': current_message.get('ai_model'),
                    'user_token_count': current_message.get('token_count'),
                    'ai_token_count': next_message.get('token_count'),
                    'user_metadata': current_message.get('metadata'),
                    'ai_metadata': next_message.get('metadata')
                }

                turns.append(turn)
                i += 2  # 跳过已配对的两条消息
            else:
                # 如果不是user-assistant配对，跳过当前消息
                i += 1

        return turns

    def get_chat_history(
        self,
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = 50,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        username: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取对话历史（返回配对的对话轮次）

        Args:
            user_id: 用户ID（可选，None表示查询所有用户，管理员功能）
            conversation_id: 对话ID（可选）
            limit: 返回消息数量（当不使用分页时）
            page: 页码（可选，使用分页时）
            page_size: 每页数量（可选，使用分页时）
            start_date: 开始日期（可选，格式：YYYY-MM-DD）
            end_date: 结束日期（可选，格式：YYYY-MM-DD）
            username: 用户名称（可选，支持模糊查询，匹配username和nickname）
            phone_number: 手机号（可选，支持模糊查询）

        Returns:
            Dict: 对话历史，包含配对的对话轮次
        """
        try:
            # 构建WHERE条件，使用JOIN查询用户信息
            where_conditions = []
            params = []
            
            # 如果指定了user_id，则过滤；否则查询所有用户
            if user_id is not None:
                where_conditions.append("cm.user_id = %s")
                params.append(user_id)
            
            if conversation_id:
                where_conditions.append("cm.conversation_id = %s")
                params.append(conversation_id)
            
            # 用户名称过滤（支持模糊查询，匹配username和nickname）
            if username:
                where_conditions.append("(u.username LIKE %s OR u.nickname LIKE %s)")
                username_pattern = f"%{username}%"
                params.extend([username_pattern, username_pattern])

            # 手机号过滤（支持模糊查询）
            if phone_number:
                where_conditions.append("u.phone_number LIKE %s")
                phone_pattern = f"%{phone_number}%"
                params.append(phone_pattern)
            
            # 日期范围过滤
            if start_date:
                where_conditions.append("DATE(cm.created_at) >= %s")
                params.append(start_date)
            
            if end_date:
                where_conditions.append("DATE(cm.created_at) <= %s")
                params.append(end_date)
            
            # 如果没有WHERE条件，使用1=1（查询所有记录）
            if not where_conditions:
                where_clause = "1=1"
            else:
                where_clause = " AND ".join(where_conditions)
            
            # 判断是否使用分页
            use_pagination = page is not None and page_size is not None and page > 0 and page_size > 0
            
            if use_pagination:
                # 分页模式：先获取总数（需要JOIN用户表）
                count_sql = f"""
                    SELECT COUNT(*) as total 
                    FROM chat_messages cm
                    LEFT JOIN users u ON cm.user_id = u.user_id
                    WHERE {where_clause}
                """
                count_result = execute_query(count_sql, tuple(params), fetch_one=True)
                total = count_result['total'] if count_result else 0

                # 计算对话轮次的总数（总数除以2，向下取整）
                total_turns = total // 2

                # 查询时获取双倍的消息数量，以确保有足够的配对数据
                # 因为一个对话轮次需要2条消息（user + assistant）
                query_page_size = page_size * 2
                offset = (page - 1) * query_page_size

                # 获取分页数据，包含用户信息
                sql = f"""
                    SELECT cm.*, u.username, u.nickname, u.phone_number
                    FROM chat_messages cm
                    LEFT JOIN users u ON cm.user_id = u.user_id
                    WHERE {where_clause}
                    ORDER BY cm.created_at DESC
                    LIMIT %s OFFSET %s
                """
                params.extend([query_page_size, offset])
                messages = execute_query(sql, tuple(params))

                # 反转顺序（最旧的在前）
                messages = list(messages)
                messages.reverse()

                # 将消息配对成对话轮次
                turns = self._pair_messages_into_turns(messages)

                # 确保返回的turns数量不超过请求的page_size
                turns = turns[:page_size]

                total_pages = (total_turns + page_size - 1) // page_size if page_size > 0 else 0
                return {
                    'turns': turns,
                    'count': len(turns),
                    'total': total_turns,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            else:
                # 非分页模式：使用limit（对话轮次的数量）
                if limit is None:
                    limit = 50

                # 查询时获取双倍的消息数量，以确保有足够的配对数据
                query_limit = limit * 2

                sql = f"""
                    SELECT cm.*, u.username, u.nickname, u.phone_number
                    FROM chat_messages cm
                    LEFT JOIN users u ON cm.user_id = u.user_id
                    WHERE {where_clause}
                    ORDER BY cm.created_at DESC
                    LIMIT %s
                """
                params.append(query_limit)
                messages = execute_query(sql, tuple(params))

                # 反转顺序（最旧的在前）
                messages = list(messages)
                messages.reverse()

                # 将消息配对成对话轮次
                turns = self._pair_messages_into_turns(messages)

                # 确保返回的turns数量不超过请求的limit
                turns = turns[:limit]

                return {
                    'turns': turns,
                    'count': len(turns)
                }
            
        except Exception as e:
            logger.error(f"❌ 获取对话历史失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'message': str(e)}
    
    def get_chat_sessions(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取对话会话列表
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            Dict: 会话列表
        """
        try:
            offset = (page - 1) * page_size
            
            # 查询总数
            count_sql = "SELECT COUNT(*) as total FROM chat_sessions WHERE user_id = %s"
            total = execute_query(count_sql, (user_id,), fetch_one=True)['total']
            
            # 查询列表
            list_sql = """
                SELECT conversation_id, created_at, updated_at, status,
                       (SELECT COUNT(*) FROM chat_messages 
                        WHERE conversation_id = chat_sessions.conversation_id) as message_count
                FROM chat_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """
            sessions = execute_query(list_sql, (user_id, page_size, offset))
            
            return {
                'success': True,
                'total': total,
                'page': page,
                'page_size': page_size,
                'sessions': sessions
            }
            
        except Exception as e:
            logger.error(f"❌ 获取对话会话失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def get_latest_session(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户最新的对话会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 最新会话信息，如果没有则返回None
        """
        try:
            sql = """
                SELECT conversation_id, created_at, updated_at, status,
                       (SELECT COUNT(*) FROM chat_messages 
                        WHERE conversation_id = chat_sessions.conversation_id) as message_count
                FROM chat_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT 1
            """
            session = execute_query(sql, (user_id,), fetch_one=True)
            
            if session:
                return {
                    'success': True,
                    'data': session
                }
            else:
                return {
                    'success': False,
                    'message': '用户暂无对话会话'
                }
            
        except Exception as e:
            logger.error(f"❌ 获取最新会话失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _update_user_tags_safe(self, user_id: int, tags: List[Dict[str, Any]]) -> int:
        """
        安全地更新用户标签，只设置存在的标签

        Args:
            user_id: 用户ID
            tags: 标签列表 [{"tag_key": "...", "tag_value": "..."}]

        Returns:
            int: 成功更新的标签数量
        """
        try:
            from models.tag import TagDefinition
            tag_service = get_tag_service()

            # 中文标签键名到英文键名的映射
            tag_key_mapping = {
                '用药方式': 'insulin_route',
                '监测设备使用': 'cgm_usage',
                '确诊时间': 'diagnosis_date',
                '用户身份': 'user_identity',
                '与患儿关系': 'relationship_to_child',
                '患儿年龄': 'child_age',
                '患儿性别': 'child_gender',
                '对话频率': 'conversation_frequency',
                '咨询目的': 'consultation_purpose',
                '胰岛素给药方式': 'insulin_route',
                '动态血糖监测使用情况': 'cgm_usage',
                '与患者关系': 'relationship_to_patient',
                '患者年龄': 'patient_age',
            }

            # 过滤掉不存在的标签
            valid_tags = {}
            for tag in tags:
                tag_key = tag['tag_key']
                tag_value = tag['tag_value']

                # 如果是中文键名，尝试映射到英文键名
                if tag_key in tag_key_mapping:
                    tag_key = tag_key_mapping[tag_key]
                    logger.debug(f"🔄 映射中文标签 {tag['tag_key']} -> 英文标签 {tag_key}")

                # 检查标签是否存在
                if TagDefinition.get_by_key(tag_key):
                    valid_tags[tag_key] = tag_value
                    logger.debug(f"✅ 标签 {tag_key} 存在，将设置为: {tag_value}")
                else:
                    logger.warning(f"⚠️ 标签 {tag_key} 不存在，跳过设置")

            if valid_tags:
                # 如果设置了确诊日期，自动计算病程年数
                if 'diagnosis_date' in valid_tags:
                    diagnosis_date_str = valid_tags['diagnosis_date']
                    try:
                        # 尝试解析确诊日期
                        from datetime import datetime
                        current_year = datetime.now().year

                        # 提取年份
                        if '年' in diagnosis_date_str:
                            diagnosis_year = int(diagnosis_date_str.split('年')[0])
                        else:
                            diagnosis_year = int(diagnosis_date_str)

                        # 计算病程年数
                        disease_duration_years = current_year - diagnosis_year
                        if disease_duration_years >= 0:
                            valid_tags['disease_duration_years'] = str(disease_duration_years)
                            logger.info(f"📅 基于确诊日期 {diagnosis_date_str} 计算病程: {disease_duration_years} 年")
                    except Exception as e:
                        logger.warning(f"⚠️ 无法解析确诊日期 {diagnosis_date_str}: {str(e)}")

                # 不指定source参数，使用默认值
                result = tag_service.batch_set_tags(user_id, valid_tags)
                updated_count = result.get('success_count', 0)
                logger.info(f"✅ 为用户 {user_id} 安全更新了 {updated_count} 个有效标签")
                return updated_count
            else:
                logger.warning(f"⚠️ 没有有效的标签需要更新")
                return 0

        except Exception as e:
            logger.error(f"❌ 安全更新用户标签失败: {str(e)}")
            return 0

    def _is_initial_conversation(self, user_id: int) -> bool:
        """
        判断是否为初次对话（信息未收集完整）

        检查用户是否已经收集了必要的基础信息：
        - 年龄
        - 性别
        - 糖尿病类型
        - 病程信息（至少年数）
        - 胰岛素给药途径
        - CGM使用情况

        Args:
            user_id: 用户ID

        Returns:
            bool: True表示需要初次对话收集信息，False表示可以正常对话
        """
        try:

            # 获取用户标签
            user_tags, _ = TagValue.get_user_tags(user_id)
            tag_dict = {tag.get('tag_key'): tag.get('tag_value') for tag in user_tags}
            
            # 检查必要信息是否收集完整
            required_tags = [
                'age',              # 年龄
                'gender',           # 性别
                'diabetes_type',    # 糖尿病类型
                'disease_duration_years',  # 病程（年）
                'insulin_route',    # 胰岛素给药途径
                'cgm_usage'         # CGM使用情况
            ]
            
            # 检查是否有缺失的必要信息
            missing_tags = []
            for tag_key in required_tags:
                tag_value = tag_dict.get(tag_key)
                if not tag_value or (isinstance(tag_value, str) and tag_value.strip() == ''):
                    missing_tags.append(tag_key)
            
            # 如果有缺失信息，需要初次对话
            if missing_tags:
                logger.info(f"📋 用户 {user_id} 信息未收集完整，缺失: {missing_tags}")
                return True
            
            # 检查是否有标记信息收集完成的标签
            onboarding_completed = tag_dict.get('onboarding_completed', 'false').lower() == 'true'
            if not onboarding_completed:
                logger.info(f"📋 用户 {user_id} 未标记信息收集完成")
                return True
            
            logger.info(f"✅ 用户 {user_id} 信息已收集完整，可以使用正常对话")
            return False
            
        except Exception as e:
            logger.error(f"❌ 判断初次对话状态失败: {str(e)}")
            # 出错时默认使用初次对话，确保信息收集
            return True

    def _check_and_mark_onboarding_completed(self, user_id: int) -> None:
        """
        检查并标记信息收集完成

        当用户信息收集完整时，自动标记onboarding_completed为true

        Args:
            user_id: 用户ID
        """
        try:

            # 获取用户标签
            user_tags, _ = TagValue.get_user_tags(user_id)
            tag_dict = {tag.get('tag_key'): tag.get('tag_value') for tag in user_tags}
            
            # 检查必要信息是否收集完整
            required_tags = [
                'age',              # 年龄
                'gender',           # 性别
                'diabetes_type',    # 糖尿病类型
                'disease_duration_years',  # 病程（年）
                'insulin_route',    # 胰岛素给药途径
                'cgm_usage'         # CGM使用情况
            ]
            
            # 检查是否有缺失的必要信息
            missing_tags = []
            for tag_key in required_tags:
                tag_value = tag_dict.get(tag_key)
                if not tag_value or (isinstance(tag_value, str) and tag_value.strip() == ''):
                    missing_tags.append(tag_key)
            
            # 如果信息收集完整，标记完成
            if not missing_tags:
                current_status = tag_dict.get('onboarding_completed', 'false').lower()
                if current_status != 'true':
                    TagValue.set_value(
                        user_id=user_id,
                        tag_key='onboarding_completed',
                        tag_value='true',
                        source='system',
                        confidence_score=1.0
                    )
                    logger.info(f"✅ 用户 {user_id} 信息收集完成，已标记onboarding_completed=true")
            else:
                logger.debug(f"📋 用户 {user_id} 信息尚未收集完整，缺失: {missing_tags}")
                
        except Exception as e:
            logger.error(f"❌ 检查信息收集完成状态失败: {str(e)}")

    def stream_chat(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Generator[Dict, None, None]:
        """
        流式对话

        Args:
            user_id: 用户ID
            message: 消息内容
            conversation_id: 对话ID

        Yields:
            Dict: 流式事件
        """
        try:
            logger.info(f"🚀 开始处理用户 {user_id} 的流式对话，消息: {message[:50]}...")
            logger.info(f"📝 conversation_id: {conversation_id}")
            # 添加一个标记，确保代码执行到这里
            logger.info(f"🔄 进入stream_chat方法主体")

            # 自动判断使用initial还是normal提示词
            is_initial = self._is_initial_conversation(user_id)
            prompt_type = "initial" if is_initial else "normal"

            if is_initial:
                logger.info(f"🆕 用户 {user_id} 使用初次对话模式（信息收集）")
            else:
                logger.info(f"💬 用户 {user_id} 使用正常对话模式")

            # 获取用户标签用于个性化对话
            logger.info(f"🏷️ 获取用户 {user_id} 的标签信息")
            try:
                user_tags, _ = TagValue.get_user_tags(user_id)
                logger.info(f"✅ 用户 {user_id} 共有 {len(user_tags)} 个标签")
            except Exception as e:
                logger.warning(f"⚠️ 获取用户 {user_id} 标签失败: {e}")
                user_tags = []

            # 如果没有提供conversation_id，自动生成一个
            if not conversation_id:
                import time
                conversation_id = f"chat_{user_id}_{int(time.time() * 1000)}"
                logger.info(f"🆕 ChatService自动生成conversation_id: {conversation_id}")

            # 确保会话存在，然后保存用户消息（先保存，再获取历史）
            self.ensure_session_exists(user_id, conversation_id)
            self.save_message(user_id, conversation_id, 'user', message)

            # 记录conversation_id，确保传递给DeepSeek服务
            logger.info(f"📝 使用conversation_id: {conversation_id}")

            # 获取对话历史（用于上下文）- 在保存用户消息后获取，但排除刚保存的消息
            conversation_history = []
            history_result = self.get_chat_history(user_id, conversation_id, limit=50)  # 增加获取的历史消息数量
            if history_result and isinstance(history_result, dict):
                messages = history_result.get('messages', [])
                # 转换为DeepSeek需要的格式，排除刚保存的当前用户消息
                for msg in messages:
                    # 排除当前刚保存的用户消息（通过内容匹配）
                    if msg.get('role') == 'user' and msg.get('content') == message:
                        continue
                    conversation_history.append({
                        'role': msg.get('role'),
                        'content': msg.get('content')
                    })
                logger.info(f"📚 用户 {user_id} 对话历史: {len(conversation_history)} 条消息")
            else:
                logger.warning(f"⚠️ 获取对话历史失败: {history_result}")

            # 知识召回：检索相关FAQ + Dify知识库
            logger.info(f"🔍 开始检索FAQ知识，查询: '{message}'")
            relevant_knowledge = self.knowledge_qa_service.search_knowledge(
                query=message,
                top_k=2,
                min_similarity=0.1
            )
            logger.info(f"📚 FAQ检索完成，找到 {len(relevant_knowledge)} 条相关FAQ")

            # Dify知识库召回
            dify_knowledge_result = self.dify_knowledge_service.retrieve_knowledge(
                user_id=user_id,
                query=message,
                top_k=3,
                score_threshold=0.5
            )

            relevant_dify_docs = []
            if dify_knowledge_result.get('success'):
                relevant_dify_docs = dify_knowledge_result.get('data', {}).get('records', [])
                logger.info(f"📚 为用户 {user_id} 从Dify知识库检索到 {len(relevant_dify_docs)} 条文档片段")

            # 构建增强提示词
            knowledge_context = ""

            # 添加用户标签信息（个性化上下文）
            if user_tags:
                user_info = self._format_user_tags_for_context(user_tags)
                if user_info:
                    knowledge_context += f"\n## 用户个人信息：\n{user_info}\n"
                    logger.info(f"👤 为用户 {user_id} 添加了个性化标签信息到上下文")

            # 添加FAQ知识
            if relevant_knowledge:
                knowledge_context += "\n## 相关FAQ参考：\n"
                for i, knowledge in enumerate(relevant_knowledge, 1):
                    knowledge_context += f"### FAQ{i}：\n"
                    knowledge_context += f"问题：{knowledge['question']}\n"
                    knowledge_context += f"答案：{knowledge['answer']}\n\n"
                logger.info(f"📚 为用户 {user_id} 检索到 {len(relevant_knowledge)} 条相关FAQ")

            # 添加Dify文档知识
            if relevant_dify_docs:
                if knowledge_context:
                    knowledge_context += "\n## 相关文档参考：\n"
                else:
                    knowledge_context = "\n## 相关文档参考：\n"

                for i, doc in enumerate(relevant_dify_docs, 1):
                    knowledge_context += f"### 文档{i}：\n"
                    knowledge_context += f"内容：{doc.get('segment', {}).get('content', '')[:500]}...\n"
                    knowledge_context += f"相关度：{doc.get('score', 0):.3f}\n\n"

            if not relevant_knowledge and not relevant_dify_docs:
                logger.info(f"📭 用户 {user_id} 未检索到相关知识")

            # 调用DeepSeek服务进行流式对话
            ai_response_content = ""
            # 确保conversation_id被传递，用于在响应中返回给前端
            for event in self.deepseek_service.stream_response(
                user_id=user_id,
                user_message=message,
                conversation_history=conversation_history,
                prompt_type=prompt_type,
                conversation_id=conversation_id,  # 确保传递conversation_id，即使前端未提供也会自动生成
                knowledge_context=knowledge_context  # 传入知识上下文
            ):
                # 累积AI回复内容用于标签提取
                # 注意：deepseek_service.stream_response返回的是字典对象
                if isinstance(event, dict) and event.get('event') == 'conversation.message.delta':
                    content = event.get('data', {}).get('content', '')
                    ai_response_content += content
                    logger.debug(f"累积内容: '{content}', 总长度: {len(ai_response_content)}")

                # 直接转发所有DeepSeek事件（已经是Coze兼容格式）
                yield event

            # for循环结束后
            logger.info(f"🔚 DeepSeek流式响应处理完成，准备保存AI回复")
            # 保存AI回复
            logger.info(f"💬 AI回复内容长度: {len(ai_response_content)}, conversation_id: {conversation_id}, 内容预览: '{ai_response_content[:50]}...'")
            # 强制执行保存，不管内容是否为空（用于调试）
            if conversation_id:
                logger.info(f"💾 保存AI回复，长度: {len(ai_response_content)}")
                self.save_message(user_id, conversation_id, 'assistant', ai_response_content or "AI回复内容为空")
            else:
                logger.warning(f"⚠️ 跳过保存AI回复: conversation_id={conversation_id}, ai_response_content='{ai_response_content[:50]}...'")

                # 异步提取标签并更新用户状态（不阻塞对话响应）
                logger.info(f"🏷️ 对话完成，开始准备标签提取，用户 {user_id}，会话 {conversation_id}")
                try:
                    logger.info(f"🏷️ 开始准备标签提取，用户 {user_id}，会话 {conversation_id}")
                    # 获取完整的对话历史用于标签提取
                    history_result = self.get_chat_history(user_id, conversation_id, limit=50)
                    full_history = history_result.get('messages', []) if isinstance(history_result, dict) else []
                    logger.info(f"📚 获取到对话历史: {len(full_history)} 条消息")

                    if full_history and len(full_history) >= 2:  # 至少有用户和AI各一条消息
                        # 构建对话文本用于标签提取
                        conversation_text = ""
                        for msg in full_history[-10:]:  # 只用最近10条消息
                            role = "用户" if msg.get('role') == 'user' else "AI助手"
                            content = msg.get('content', '')[:200]  # 限制内容长度
                            conversation_text += f"{role}: {content}\n"

                        logger.info(f"📝 构建对话文本完成，长度: {len(conversation_text.strip())}")

                        if conversation_text.strip():
                            logger.info(f"🏷️ 开始同步标签提取测试")
                            try:
                                logger.info(f"🤖 开始调用DeepSeek提取标签")
                                # 同步执行标签提取进行测试
                                tags = self.deepseek_service.tag_user_from_conversation(user_id, conversation_text)
                                logger.info(f"🔍 标签提取完成，获得 {len(tags) if tags else 0} 个标签: {tags}")

                                if tags:
                                    updated_count = self._update_user_tags_safe(user_id, tags)
                                    logger.info(f"✅ 为用户 {user_id} 更新了 {updated_count} 个标签")

                                    # 再次检查是否完成了信息收集
                                    if is_initial and not self._is_initial_conversation(user_id):
                                        logger.info(f"🎉 用户 {user_id} 信息收集已完成，下次对话将使用normal提示词")
                                else:
                                    logger.info(f"📭 用户 {user_id} 未提取到新标签")
                            except Exception as e:
                                logger.error(f"❌ 标签提取失败: {str(e)}")
                                import traceback
                                logger.error(f"❌ 详细错误信息: {traceback.format_exc()}")
                        else:
                            logger.info(f"📭 对话文本为空，跳过标签提取")
                    else:
                        logger.info(f"📭 对话历史不足，跳过标签提取")
                except Exception as e:
                    logger.error(f"❌ 准备标签提取失败: {str(e)}")

                except Exception as e:
                    logger.error(f"❌ 启动标签提取失败: {str(e)}")

                # 如果是初次对话模式，检查信息是否收集完整
                if is_initial:
                    self._check_and_mark_onboarding_completed(user_id)
                    # 重新检查状态，如果已完成，记录日志
                    if not self._is_initial_conversation(user_id):
                        logger.info(f"🎉 用户 {user_id} 信息收集已完成，下次对话将使用normal提示词")

        except Exception as e:
            logger.error(f"❌ 流式对话失败: {str(e)}")
            yield {'event': 'error', 'data': {'message': str(e)}}
    
    def stream_chat_with_tts(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        enable_tts: bool = False
    ) -> Generator[Dict, None, None]:
        """
        流式对话（兼容TTS接口，已移除TTS功能）
        
        Args:
            user_id: 用户ID
            message: 消息内容
            conversation_id: 对话ID
            enable_tts: 已废弃，不再使用
            
        Yields:
            Dict: 流式事件
        """
        try:
            # 如果没有提供conversation_id，自动生成一个
            if not conversation_id:
                import time
                conversation_id = f"chat_{user_id}_{int(time.time() * 1000)}"
                logger.info(f"🆕 自动生成conversation_id: {conversation_id}")
            
            # 自动判断使用initial还是normal提示词
            is_initial = self._is_initial_conversation(user_id)
            prompt_type = "initial" if is_initial else "normal"
            
            if is_initial:
                logger.info(f"🆕 用户 {user_id} 使用初次对话模式（信息收集）")
            else:
                logger.info(f"💬 用户 {user_id} 使用正常对话模式")

            # 获取用户标签用于个性化对话
            logger.info(f"🏷️ 获取用户 {user_id} 的标签信息")
            try:
                user_tags, _ = TagValue.get_user_tags(user_id)
                logger.info(f"✅ 用户 {user_id} 共有 {len(user_tags)} 个标签")
            except Exception as e:
                logger.warning(f"⚠️ 获取用户 {user_id} 标签失败: {e}")
                user_tags = []

            # 确保会话存在，然后保存用户消息（先保存，再获取历史）
            self.ensure_session_exists(user_id, conversation_id)
            self.save_message(user_id, conversation_id, 'user', message)
            
            # 获取对话历史（用于上下文）- 直接从数据库查询原始消息
            conversation_history = []
            try:
                from utils.database import execute_query
                # 直接查询数据库获取原始消息（不使用配对逻辑）
                history_sql = """
                    SELECT role, content, created_at
                    FROM chat_messages
                    WHERE user_id = %s AND conversation_id = %s
                    ORDER BY created_at ASC
                    LIMIT 40
                """
                raw_messages = execute_query(history_sql, (user_id, conversation_id))
                
                # 转换为DeepSeek需要的格式，排除刚保存的当前用户消息
                for msg in raw_messages:
                    # 排除当前刚保存的用户消息（通过内容匹配）
                    if msg.get('role') == 'user' and msg.get('content') == message:
                        continue
                    conversation_history.append({
                        'role': msg.get('role'),
                        'content': msg.get('content')
                    })
                logger.info(f"📚 用户 {user_id} 对话历史: {len(conversation_history)} 条消息")
            except Exception as e:
                logger.warning(f"⚠️ 获取对话历史失败: {str(e)}")
                conversation_history = []

            # 知识召回：检索相关FAQ + Dify知识库
            logger.info(f"🔍 开始检索FAQ知识，查询: '{message}'")
            relevant_knowledge = self.knowledge_qa_service.search_knowledge(
                query=message,
                top_k=2,
                min_similarity=0.1
            )
            logger.info(f"📚 FAQ检索完成，找到 {len(relevant_knowledge)} 条相关FAQ")

            # Dify知识库召回
            dify_knowledge_result = self.dify_knowledge_service.retrieve_knowledge(
                user_id=user_id,
                query=message,
                top_k=3,
                score_threshold=0.5
            )

            relevant_dify_docs = []
            if dify_knowledge_result.get('success'):
                relevant_dify_docs = dify_knowledge_result.get('data', {}).get('records', [])
                logger.info(f"📚 为用户 {user_id} 从Dify知识库检索到 {len(relevant_dify_docs)} 条文档片段")

            # 构建增强提示词
            knowledge_context = ""

            # 添加用户标签信息（个性化上下文）
            if user_tags:
                user_info = self._format_user_tags_for_context(user_tags)
                if user_info:
                    knowledge_context += f"\n## 用户个人信息：\n{user_info}\n"
                    logger.info(f"👤 为用户 {user_id} 添加了个性化标签信息到上下文")

            # 添加FAQ知识
            if relevant_knowledge:
                knowledge_context += "\n## 相关FAQ参考：\n"
                for i, knowledge in enumerate(relevant_knowledge, 1):
                    knowledge_context += f"### FAQ{i}：\n"
                    knowledge_context += f"问题：{knowledge['question']}\n"
                    knowledge_context += f"答案：{knowledge['answer']}\n\n"
                logger.info(f"📚 为用户 {user_id} 检索到 {len(relevant_knowledge)} 条相关FAQ")

            # 添加Dify文档知识
            if relevant_dify_docs:
                if knowledge_context:
                    knowledge_context += "\n## 相关文档参考：\n"
                else:
                    knowledge_context = "\n## 相关文档参考：\n"

                for i, doc in enumerate(relevant_dify_docs, 1):
                    knowledge_context += f"### 文档{i}：\n"
                    knowledge_context += f"内容：{doc.get('segment', {}).get('content', '')[:500]}...\n"
                    knowledge_context += f"相关度：{doc.get('score', 0):.3f}\n\n"

            if not relevant_knowledge and not relevant_dify_docs:
                logger.info(f"📭 用户 {user_id} 未检索到相关知识")

            # 调用DeepSeek服务进行流式对话
            ai_response_content = ""
            # 确保conversation_id被传递，用于在响应中返回给前端
            for event in self.deepseek_service.stream_response(
                user_id=user_id,
                user_message=message,
                conversation_history=conversation_history,
                prompt_type=prompt_type,
                conversation_id=conversation_id,  # 确保传递conversation_id，即使前端未提供也会自动生成
                knowledge_context=knowledge_context
            ):
                # 累积AI回复内容用于标签提取
                # 注意：deepseek_service.stream_response返回的是字典对象
                if isinstance(event, dict) and event.get('event') == 'conversation.message.delta':
                    content = event.get('data', {}).get('content', '')
                    ai_response_content += content

                # 直接转发所有DeepSeek事件（已经是Coze兼容格式）
                yield event

            # 保存AI回复
            if conversation_id and ai_response_content.strip():
                self.save_message(user_id, conversation_id, 'assistant', ai_response_content)

                # 异步提取标签并更新用户状态（不阻塞对话响应）
                try:
                    logger.info(f"🏷️ 对话完成，开始准备标签提取，用户 {user_id}，会话 {conversation_id}")
                    # 获取原始对话消息用于标签提取
                    sql = """
                        SELECT role, content, created_at
                        FROM chat_messages
                        WHERE user_id = %s AND conversation_id = %s
                        ORDER BY created_at ASC
                        LIMIT 50
                    """
                    messages = execute_query(sql, (user_id, conversation_id))
                    full_history = messages if messages else []
                    logger.info(f"📚 获取到对话历史: {len(full_history)} 条消息")

                    if full_history and len(full_history) >= 2:  # 至少有用户和AI各一条消息
                        # 构建对话文本用于标签提取
                        conversation_text = ""
                        for msg in full_history[-10:]:  # 只用最近10条消息
                            role = "用户" if msg.get('role') == 'user' else "AI助手"
                            content = msg.get('content', '')[:200]  # 限制内容长度
                            conversation_text += f"{role}: {content}\n"

                        logger.info(f"📝 构建对话文本完成，长度: {len(conversation_text.strip())}")

                        if conversation_text.strip():
                            logger.info(f"🏷️ 开始同步标签提取测试")
                            try:
                                logger.info(f"🤖 开始调用DeepSeek提取标签")
                                # 同步执行标签提取进行测试
                                tags = self.deepseek_service.tag_user_from_conversation(user_id, conversation_text)
                                logger.info(f"🔍 标签提取完成，获得 {len(tags) if tags else 0} 个标签: {tags}")

                                if tags:
                                    updated_count = self._update_user_tags_safe(user_id, tags)
                                    logger.info(f"✅ 为用户 {user_id} 更新了 {updated_count} 个标签")

                                    # 再次检查是否完成了信息收集
                                    if is_initial and not self._is_initial_conversation(user_id):
                                        logger.info(f"🎉 用户 {user_id} 信息收集已完成，下次对话将使用normal提示词")
                                else:
                                    logger.info(f"📭 用户 {user_id} 未提取到新标签")
                            except Exception as e:
                                logger.error(f"❌ 标签提取失败: {str(e)}")
                                import traceback
                                logger.error(f"❌ 详细错误信息: {traceback.format_exc()}")
                        else:
                            logger.info(f"📭 对话文本为空，跳过标签提取")
                    else:
                        logger.info(f"📭 对话历史不足，跳过标签提取")
                except Exception as e:
                    logger.error(f"❌ 准备标签提取失败: {str(e)}")

                # 如果是初次对话模式，检查信息是否收集完整
                if is_initial:
                    self._check_and_mark_onboarding_completed(user_id)
                    # 重新检查状态，如果已完成，记录日志
                    if not self._is_initial_conversation(user_id):
                        logger.info(f"🎉 用户 {user_id} 信息收集已完成，下次对话将使用normal提示词")

        except Exception as e:
            logger.error(f"❌ 流式对话失败: {str(e)}")
            yield {'event': 'error', 'data': {'message': str(e)}}
    
    def speech_to_text(
        self,
        user_id: int,
        audio_data: bytes = None,
        audio_file_path: str = None,
        audio_format: str = 'wav',
        mime_type: str = 'audio/wav'
    ) -> Dict[str, Any]:
        """
        语音转文本 (ASR) - 暂时不可用
        
        Args:
            user_id: 用户ID
            audio_data: 音频数据（bytes）
            audio_file_path: 音频文件路径
            
        Returns:
            Dict: 识别结果 {'success': False, 'message': '功能暂时不可用'}
        """
        logger.warning("⚠️ 语音转文本功能暂时不可用（DeepSeek不支持ASR）")

        return {
            'success': False,
            'message': '语音转文本功能暂时不可用，请直接输入文字'
        }
    
    def ensure_session_exists(self, user_id: int, conversation_id: str) -> bool:
        """
        确保会话存在，如果不存在则创建

        Args:
            user_id: 用户ID
            conversation_id: 对话ID

        Returns:
            bool: 是否成功
        """
        try:
            # 检查会话是否已存在
            check_sql = "SELECT session_id FROM chat_sessions WHERE conversation_id = %s"
            result = execute_query(check_sql, (conversation_id,), fetch_one=True)
            
            if not result:
                # 创建新会话
                insert_sql = """
                    INSERT INTO chat_sessions
                    (user_id, conversation_id, status, created_at)
                    VALUES (%s, %s, 'created', NOW())
                """
                execute_update(insert_sql, (user_id, conversation_id))
                logger.info(f"✅ 创建新会话: {conversation_id} (用户: {user_id})")

            return True
                
        except Exception as e:
            logger.error(f"❌ 确保会话存在失败: {str(e)}")
            return False
    
    def save_message(
        self,
        user_id: int,
        conversation_id: str,
        role: str,
        content: str,
        message_type: str = 'text'
    ) -> bool:
        """
        保存消息
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID
            role: 角色（user/assistant）
            content: 消息内容
            message_type: 消息类型
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                INSERT INTO chat_messages 
                (user_id, conversation_id, role, content, message_type, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            result = execute_update(sql, (user_id, conversation_id, role, content, message_type))
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ 保存消息失败: {str(e)}")
            return False

    def _format_user_tags_for_context(self, user_tags: List[Dict[str, Any]]) -> str:
        """
        将用户标签格式化为AI上下文字符串

        Args:
            user_tags: 用户标签列表

        Returns:
            str: 格式化的用户信息字符串
        """
        try:
            # 按分类整理标签
            tag_dict = {}
            for tag in user_tags:
                tag_key = tag.get('tag_key')
                tag_value = tag.get('tag_value')
                tag_name = tag.get('tag_name', tag_key)
                category = tag.get('tag_category', 'basic')

                # 只包含有值的标签
                if tag_value is not None and tag_value != '' and tag_value != 'null':
                    if category not in tag_dict:
                        tag_dict[category] = []
                    tag_dict[category].append({
                        'name': tag_name,
                        'value': tag_value
                    })

            # 格式化为字符串
            context_parts = []

            # 基本信息
            if 'basic' in tag_dict:
                basic_info = []
                for tag in tag_dict['basic']:
                    basic_info.append(f"- {tag['name']}: {tag['value']}")
                if basic_info:
                    context_parts.append("### 基本信息：\n" + "\n".join(basic_info))

            # 健康信息
            if 'health' in tag_dict:
                health_info = []
                for tag in tag_dict['health']:
                    health_info.append(f"- {tag['name']}: {tag['value']}")
                if health_info:
                    context_parts.append("### 健康信息：\n" + "\n".join(health_info))

            # 行为偏好
            if 'behavior' in tag_dict:
                behavior_info = []
                for tag in tag_dict['behavior']:
                    behavior_info.append(f"- {tag['name']}: {tag['value']}")
                if behavior_info:
                    context_parts.append("### 行为偏好：\n" + "\n".join(behavior_info))

            # 统计信息
            if 'stats' in tag_dict:
                stats_info = []
                for tag in tag_dict['stats']:
                    stats_info.append(f"- {tag['name']}: {tag['value']}")
                if stats_info:
                    context_parts.append("### 统计信息：\n" + "\n".join(stats_info))

            return "\n".join(context_parts) if context_parts else ""

        except Exception as e:
            logger.error(f"❌ 格式化用户标签失败: {str(e)}")
            return ""


# 全局单例
_chat_service_instance = None

def get_chat_service() -> ChatService:
    """获取对话服务单例"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance

