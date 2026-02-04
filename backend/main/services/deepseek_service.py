"""
DeepSeek AI服务 - 【核心文件】
~~~~~~~~~~~~~~~

基于DeepSeek API的AI对话服务

功能：
- 流式对话生成（SSE支持）
- 用户变量获取和提示词占位符替换
- 知识上下文集成（FAQ检索结果）
- AI标签提取（从对话内容提取用户标签）
- 对话历史处理和上下文管理
- 错误处理和重试机制

核心方法：
- stream_response(): 流式对话生成主入口
- _get_user_variables(): 获取用户标签变量
- _prepare_messages(): 构建API消息和提示词替换
- tag_user_from_conversation(): 从对话提取标签
- _get_default_prompt(): 获取内置提示词模板

作者: 智糖团队
日期: 2025-01-17
"""

import json
import time
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime, timezone, timedelta
import requests
from utils.logger import get_logger
from models.prompt import UserPromptSetting
from models.tag import TagValue
from utils.config_loader import get_config

logger = get_logger(__name__)


class DeepSeekService:
    """
    DeepSeek AI服务类
    """

    def __init__(self):
        self.config = get_config()
        self.api_key = "sk-2465e5bebc94464bbae8361aa1396380"  # DeepSeek API Key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # 使用DeepSeek的对话模型

        # 设置默认参数
        self.max_tokens = 4096  # 增加输出token限制
        self.temperature = 0.7
        self.timeout = 60
        self.max_context_messages = 30  # 最多保留30轮对话（约60条消息）

        logger.info("✅ DeepSeek服务初始化完成")

    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _prepare_messages(self, user_message: str, conversation_history: List[Dict] = None,
                         system_prompt: str = None, user_variables: Dict[str, Any] = None,
                         knowledge_context: str = "") -> List[Dict]:
        """
        准备发送给DeepSeek的messages

        Args:
            user_message: 用户消息
            conversation_history: 对话历史
            system_prompt: 系统提示词
            user_variables: 用户变量信息

        Returns:
            List[Dict]: 消息列表
        """
        messages = []

        # 添加系统提示词
        if system_prompt:
            # 如果有用户变量，进行替换
            if user_variables:
                try:
                    processed_prompt = system_prompt
                    logger.info(f"📊 用户变量: {user_variables}")

                    for key, value in user_variables.items():
                        placeholder = f"{{{key}}}"
                        if placeholder in processed_prompt:
                            processed_prompt = processed_prompt.replace(placeholder, str(value))

                    system_prompt = processed_prompt


                    # 同时记录到日志（可能被截断）
                    logger.info(f"📝 最终系统提示词 (长度: {len(system_prompt)}): {system_prompt[:5000]}{'...' if len(system_prompt) > 5000 else ''}")
                except Exception as e:
                    logger.warning(f"处理用户变量失败: {str(e)}")

            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # 添加对话历史
        if conversation_history:
            # 限制历史消息数量，避免超出token限制
            # DeepSeek Chat支持32K上下文，我们保留更多历史
            max_history = self.max_context_messages  # 最多保留30轮对话（约60条消息）
            recent_history = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history

            logger.debug(f"📚 对话历史: 总共{len(conversation_history)}条，保留最近{len(recent_history)}条")

            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')

                # 只保留user和assistant的消息
                if role in ['user', 'assistant']:
                    messages.append({
                        "role": role,
                        "content": content
                    })

        # 添加当前用户消息（包含知识上下文）
        final_user_message = user_message
        if knowledge_context:
            final_user_message = f"{user_message}\n\n{knowledge_context}"

        messages.append({
            "role": "user",
            "content": final_user_message
        })

        return messages

    def chat_completion(self, messages: List[Dict], stream: bool = False,
                       temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """
        调用DeepSeek API进行对话

        Args:
            messages: 消息列表
            stream: 是否流式输出
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            Dict: API响应
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }

        try:
            logger.info(f"🚀 调用DeepSeek API: {len(messages)} 条消息")

            # SSL配置 - 如果SSL验证失败，可以临时禁用
            verify_ssl = get_config('DEEPSEEK.SSL_VERIFY', True)

            # 创建会话以支持重试
            session = requests.Session()

            # 配置重试策略
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=3,  # 总重试次数
                status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码重试
                backoff_factor=1  # 重试间隔
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            response = session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout,
                stream=stream,
                verify=verify_ssl  # SSL验证控制
            )

            response.raise_for_status()

            if stream:
                return response  # 返回流式响应对象
            else:
                return response.json()

        except requests.exceptions.SSLError as ssl_error:
            logger.info("💡 尝试禁用SSL验证重试...")

            # 如果SSL验证失败，尝试禁用SSL验证
            try:
                session = requests.Session()
                retry_strategy = Retry(
                    total=2,
                    status_forcelist=[429, 500, 502, 503, 504],
                    backoff_factor=1
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                response = session.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=self.timeout,
                    stream=stream,
                    verify=False  # 禁用SSL验证
                )

                response.raise_for_status()

                logger.warning("⚠️ 已禁用SSL验证完成请求，请检查网络环境")

                if stream:
                    return response
                else:
                    return response.json()

            except Exception as retry_error:
                raise Exception(f"AI服务SSL连接失败: {str(ssl_error)}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"AI服务请求失败: {str(e)}")

    def generate_response(self, user_id: int, user_message: str,
                         conversation_history: List[Dict] = None,
                         prompt_type: str = "normal") -> str:
        """
        生成AI回复（非流式）

        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史
            prompt_type: 提示词类型

        Returns:
            str: AI回复内容
        """
        try:
            # 获取用户提示词
            system_prompt = UserPromptSetting.get_user_prompt_content(user_id, prompt_type)
            if not system_prompt:
                system_prompt = self._get_default_prompt(prompt_type)

            # 获取用户变量信息
            user_variables = self._get_user_variables(user_id)

            # 添加当前时间变量（使用中国时区 UTC+8）
            china_tz = timezone(timedelta(hours=8))
            current_datetime = datetime.now(china_tz).strftime("%Y年%m月%d日 %H:%M:%S")
            user_variables['current_datetime'] = current_datetime

            # 准备消息
            messages = self._prepare_messages(
                user_message=user_message,
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                user_variables=user_variables
            )

            # 调用API
            response = self.chat_completion(messages, stream=False)

            # 提取回复内容
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0].get('message', {}).get('content', '')
                return content
            else:
                logger.error(f"❌ DeepSeek API响应格式错误: {response}")
                return "抱歉，我现在无法回复，请稍后再试。"

        except Exception as e:
            logger.error(f"❌ 生成AI回复失败: {str(e)}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"

    def stream_response(self, user_id: int, user_message: str,
                       conversation_history: List[Dict] = None,
                       prompt_type: str = "normal",
                       conversation_id: str = None,
                       knowledge_context: str = "") -> Iterator[Dict[str, Any]]:
        """
        生成流式AI回复

        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史
            prompt_type: 提示词类型

        Yields:
            Dict: 流式事件数据
        """
        try:
            # 如果没有提供conversation_id，自动生成一个
            if not conversation_id:
                import time
                conversation_id = f"chat_{user_id}_{int(time.time() * 1000)}"
            
            # 初始化会话状态
            self._conversation_sent = False

            # 获取用户提示词
            system_prompt = UserPromptSetting.get_user_prompt_content(user_id, prompt_type)
            if not system_prompt:
                logger.warning(f"未找到用户 {user_id} 的 {prompt_type} 提示词，使用默认提示词")
                system_prompt = self._get_default_prompt(prompt_type)
            else:
                logger.info(f"从数据库获取用户 {user_id} 的 {prompt_type} 提示词，长度: {len(system_prompt)}")

                # 如果是从数据库获取的initial提示词，添加时间上下文信息
                if prompt_type == "initial":
                    # 使用中国时区 UTC+8
                    china_tz = timezone(timedelta(hours=8))
                    current_time = datetime.now(china_tz)
                    time_context = f"""## 当前时间信息
- 当前日期时间：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}
- 当前日期：{current_time.strftime('%Y年%m月%d日')}
- 当前时间：{current_time.strftime('%H:%M:%S')}
- 今天是星期{current_time.strftime('%w')}（0=星期日，1-6=星期一到六）
- 当前年份：{current_time.year}年
- 当前月份：{current_time.month}月
- 当前日期：{current_time.day}日

请在回答用户问题时考虑当前时间因素，例如：
- 如果用户询问时间相关的问题，直接使用上述时间信息回答
- 如果涉及日期计算，使用上述时间作为基准
- 如果是医疗建议，考虑季节、时间等因素

"""
                    system_prompt = time_context + system_prompt
                    logger.info(f"✅ 为initial提示词添加了时间上下文信息，新长度: {len(system_prompt)}")

            # 获取用户变量信息
            user_variables = self._get_user_variables(user_id)

            # 添加当前时间变量（使用中国时区 UTC+8）
            china_tz = timezone(timedelta(hours=8))
            current_datetime = datetime.now(china_tz).strftime("%Y年%m月%d日 %H:%M:%S")
            user_variables['current_datetime'] = current_datetime

            # 记录对话历史信息
            if conversation_history:
                # 统计消息类型
                user_count = sum(1 for msg in conversation_history if msg.get('role') == 'user')
                assistant_count = sum(1 for msg in conversation_history if msg.get('role') == 'assistant')
                # 显示历史摘要
                history_summary = []
                for msg in conversation_history[-5:]:  # 显示最近5条
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:80]
                    history_summary.append(f"{role}: {content}...")

            
            # 准备消息
            messages = self._prepare_messages(
                user_message=user_message,
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                user_variables=user_variables,
                knowledge_context=knowledge_context
            )

            logger.info(f"📤 发送给DeepSeek的消息总数: {len(messages)} 条（包含system提示词）")
            if knowledge_context:
                logger.info(f"📚 包含知识上下文: {len(knowledge_context)} 字符")

            # 调用API
            response = self.chat_completion(messages, stream=True)

            # 处理流式响应
            logger.info("开始处理DeepSeek流式响应")
            line_count = 0
            for raw_line in response.iter_lines():
                line_count += 1
                # DeepSeek API发送空行，我们需要处理所有行
                line = raw_line.decode('utf-8') if raw_line else ''

                # 只处理非空行
                if not line.strip():
                    continue

                if line.startswith('data: '):
                    data = line[6:]  # 移除'data: '前缀

                    if data == '[DONE]':
                        logger.info(f"收到[DONE]标记，结束处理，共处理 {line_count} 行")
                        break

                    try:
                        chunk = json.loads(data)

                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')

                        if content:
                            # 使用Coze兼容的事件格式
                            event_data = {
                                'content': content
                            }

                            # 确保conversation_id始终包含在事件中（贯穿整个流式输出）
                            if conversation_id:
                                event_data['conversation_id'] = conversation_id
                                # 只在第一个事件时记录日志
                                if not hasattr(self, '_conversation_sent') or not self._conversation_sent:
                                    self._conversation_sent = True
                                    logger.info(f"📤 发送第一个事件，包含conversation_id: {conversation_id}")

                            logger.debug(f"yield事件: conversation.message.delta")
                            yield {
                                'event': 'conversation.message.delta',
                                'data': event_data
                            }
                    except json.JSONDecodeError:
                            continue

            # 发送follow_up事件表示AI回复完成
            yield {
                'event': 'conversation.message.follow_up',
                'data': {
                    'content': 'AI回复完成',
                    'conversation_id': conversation_id if conversation_id else None
                }
            }

            # 发送对话完成事件
            yield {
                'event': 'conversation.chat.completed',
                'data': {
                    'conversation_id': conversation_id if conversation_id else None
                }
            }

        except Exception as e:
            logger.error(f"❌ 流式AI回复失败: {str(e)}")
            # 发送错误事件（使用兼容格式）
            yield {
                'event': 'conversation.message.follow_up',
                'data': {
                    'content': f'AI服务错误: {str(e)}',
                    'conversation_id': conversation_id if 'conversation_id' in locals() and conversation_id else None
                }
            }

    def chat_with_stream(self, user_id: int, user_message: str,
                        conversation_history: List[Dict] = None,
                        prompt_type: str = "normal",
                        conversation_id: str = None,
                        knowledge_context: str = "") -> Iterator[Dict[str, Any]]:
        """
        生成流式AI回复（chat_with_stream别名）

        这是一个别名方法，调用stream_response方法以保持接口一致性。

        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史
            prompt_type: 提示词类型
            conversation_id: 对话ID
            knowledge_context: 知识上下文

        Yields:
            Dict: 流式事件数据
        """
        return self.stream_response(
            user_id=user_id,
            user_message=user_message,
            conversation_history=conversation_history,
            prompt_type=prompt_type,
            conversation_id=conversation_id,
            knowledge_context=knowledge_context
        )

    def _get_user_variables(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户变量信息，用于注入到提示词中

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户变量字典，格式为 {变量名: 变量值}
        """
        try:
            # 获取用户基本信息
            from utils.database import execute_query
            user_sql = """
                SELECT username, nickname, phone_number, email
                FROM users
                WHERE user_id = %s
            """
            user_data = execute_query(user_sql, (user_id,), fetch_one=True)

            variables = {}

            # 添加用户基本信息
            if user_data:
                if user_data.get('username'):
                    variables['username'] = user_data['username']
                if user_data.get('nickname'):
                    variables['nickname'] = user_data['nickname']
                if user_data.get('phone_number'):
                    variables['phone_number'] = user_data['phone_number']
                if user_data.get('email'):
                    variables['email'] = user_data['email']

            # 获取用户标签信息作为变量
            user_tags, _ = TagValue.get_user_tags(user_id)
            tag_dict = {tag.get('tag_key'): tag.get('tag_value') for tag in user_tags}

            for tag in user_tags:
                tag_key = tag.get('tag_key')
                tag_value = tag.get('tag_value')
                if tag_key and tag_value:
                    # 将标签值转换为合适的格式
                    if isinstance(tag_value, str):
                        tag_value = tag_value.strip()
                        if tag_value:  # 只添加非空值
                            variables[tag_key] = tag_value
                    else:
                        variables[tag_key] = tag_value

            # 添加是否应该询问蜜月期的判断
            disease_duration_years = tag_dict.get('disease_duration_years')
            if disease_duration_years:
                try:
                    years = float(disease_duration_years)
                    # 只有病程小于等于2年时才应该询问蜜月期
                    variables['should_ask_honeymoon'] = '是' if years <= 2 else '否'
                except (ValueError, TypeError):
                    variables['should_ask_honeymoon'] = '未知'
            else:
                variables['should_ask_honeymoon'] = '未知'

            logger.info(f"📊 获取用户 {user_id} 变量信息: {len(variables)} 个变量")
            return variables

        except Exception as e:
            logger.error(f"❌ 获取用户变量失败: {str(e)}")
            return {}

    def _get_default_prompt(self, prompt_type: str) -> str:
        """
        获取默认提示词

        Args:
            prompt_type: 提示词类型

        Returns:
            str: 默认提示词
        """
        # 获取当前时间信息（使用中国时区 UTC+8）
        china_tz = timezone(timedelta(hours=8))
        current_time = datetime.now(china_tz)
        time_context = f"""## 当前时间信息
- 当前日期时间：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}
- 当前日期：{current_time.strftime('%Y年%m月%d日')}
- 当前时间：{current_time.strftime('%H:%M:%S')}
- 今天是星期{current_time.strftime('%w')}（0=星期日，1-6=星期一到六）
- 当前年份：{current_time.year}年
- 当前月份：{current_time.month}月
- 当前日期：{current_time.day}日

请在回答用户问题时考虑当前时间因素，例如：
- 如果用户询问时间相关的问题，直接使用上述时间信息回答
- 如果涉及日期计算，使用上述时间作为基准
- 如果是医疗建议，考虑季节、时间等因素

"""

        default_prompts = {
            "initial": """你是一个专业的儿童青少年1型糖尿病管理助手。用户可能是1型糖尿病患儿本人，也可能是患儿的家长或其他监护人。

## 当前日期和时间
{current_datetime}

## 用户已知信息
- 用户名: {username}
- 昵称: {nickname}
- 年龄: {age}
- 性别: {gender}
- 糖尿病类型: {diabetes_type}
- 诊断日期: {diagnosis_date}
- 病程年数: {disease_duration_years}
- 胰岛素给药途径: {insulin_route}
- CGM使用情况: {cgm_usage}
- 蜜月期状态: {honeymoon_period}
- 是否应该询问蜜月期: {should_ask_honeymoon}（基于病程判断：病程<=2年时为"是"，否则为"否"）
- 信息收集完成: {onboarding_completed}

## 你的任务
通过多轮对话，逐步、友好地收集用户的以下信息：
1. **用户身份确认**：确认用户是患儿本人还是家长/监护人
2. **基本信息**：年龄、性别
3. **与患儿的关系**（如果是家长）：本人/父亲/母亲/祖父母、外祖父母/其他
4. **病程信息**：1型糖尿病诊断日期至今的时间（年、月）
5. **蜜月期状态**（仅病程2年以下询问）：是否处于蜜月期或部分缓解期
6. **治疗方案**：胰岛素给药途径（胰岛素笔注射/胰岛素泵）
7. **监测设备**：是否使用CGM（动态血糖监测仪）

## 对话策略（非常重要）
1. **友好开场**：先自我介绍，说明你的作用，让用户感到安心
2. **严格按轮次提问**：每次回复只问1个问题！不要一次性问多个问题
3. **等待用户回答**：问完一个问题后，等待用户回答，然后再问下一个
4. **根据身份调整**：
   - 如果是患儿本人：使用鼓励性、支持性的语言，考虑年龄特点
   - 如果是家长：使用专业但易懂的语言，体现理解和支持
5. **自然对话**：让对话像朋友聊天一样自然，不要像填表格
6. **信息确认**：收集到信息后，简单确认一下，确保理解正确，然后继续问下一个问题
7. **适时鼓励**：在收集信息过程中，给予适当的鼓励和支持

## 智能提问策略（根据已有信息动态调整）
**重要**：查看上面的"用户已知信息"部分，如果某些信息已经有值，就不要重复询问！

提问顺序（跳过已有信息）：
第一轮：如果用户身份未知，只问"请问您是1型糖尿病的小朋友/青少年本人，还是孩子的家长呢？"
第二轮：如果年龄或性别未知，等待回答后，再问年龄和性别（可以一起问这两个）
第三轮：如果回答是家长且关系未知，再问与患儿的关系
第四轮：如果病程信息未知，问病程信息
第五轮：如果是否应该询问蜜月期为"是"且蜜月期状态未知，问蜜月期状态
第六轮：如果治疗方案未知，问治疗方案（胰岛素给药途径）
第七轮：如果监测设备未知，问监测设备（CGM使用情况）

**如果所有信息都已收集完整，直接进入正常对话模式！**

## 重要注意事项
- **一次只问一个问题**：绝对不要在一次回复中问多个问题！
- **等待回答**：问完一个问题后，必须等待用户回答再问下一个
- **蜜月期问题**：如果用户病程已经超过2年，**绝对不要询问**蜜月期相关问题
- **病程计算**：如果用户说"2024年9月诊断为1型糖尿病"，现在计算病程时需要考虑当前日期
- **信息完整性**：尽量收集完整信息，但如果用户不愿意回答某些问题，不要强迫
- **心理支持**：在收集信息过程中，要体现对用户的理解和支持，特别是对患儿本人

记住：你是AI助手，不是医生，不能替代专业医疗建议。遇到紧急情况要及时提醒就医。

## 输出格式要求

**信息收集阶段**：
在收集信息时，要自然地将信息融入到对话中。当收集到关键信息时，可以在回复中自然地确认，例如：
- "好的，我了解到您是患儿的母亲..."
- "明白了，您确诊1型糖尿病已经1年1个月了..."
- "好的，您使用的是胰岛素泵..."

**个性化对话阶段**：
如果用户信息已收集完整，使用以下格式回复：

你好[用户称呼]！我们又见面啦！😊

我记得你：
[年龄]岁的[性别]
确诊1型糖尿病[病程描述]
使用[治疗方案]治疗
[是否使用CGM监测]

今天有什么想和我聊的吗？比如：
[根据用户情况提供个性化的帮助选项]

随便什么都可以问我，我很乐意帮你解答！

现在，请开始与用户进行友好的初次对话，按照严格的轮次顺序提问。

**重要提醒**：
- **首要原则**：检查对话历史，如果发现用户已经提供了完整的基本信息，请直接进入个性化对话模式！
- **信息识别**：从对话历史中提取用户信息，包括身份、年龄性别、病程、治疗方案、监测设备等
- **个性化回复**：基于提取的用户信息，提供友好的个性化问候和针对性帮助
- **问候格式**：使用"你好[用户称呼]！我们又见面啦！"这样的友好问候
- **信息展示**：简要列出记住的用户信息，让用户感到被重视
- **帮助选项**：根据用户的具体情况（年龄、病程、治疗方式等）提供个性化的帮助选项
- **如果信息不完整**：继续按照轮次顺序收集缺失的信息，每次只问一个问题
- **绝对禁止**：在任何情况下都不要一次性问多个问题！

**识别用户信息的关键标志**：
- 身份：对话中有"本人"、"家长"等明确回答
- 年龄性别：包含年龄数字和性别信息（如"13岁男孩"、"15岁女孩"）
- 病程：包含确诊时间或病程描述（如"前年确诊"、"2年"、"2023年"）
- 治疗方案：包含"胰岛素笔"、"胰岛素泵"等
- 监测设备：包含"CGM"、"动态血糖监测仪"或明确回答"没有"

""",
            "normal": """你是一个专业的儿童青少年1型糖尿病管理助手。基于已收集的用户信息，为用户提供个性化的糖尿病管理建议。

## 当前日期和时间
{current_datetime}

## 用户信息
以下是你已收集到的用户信息，请基于这些信息提供个性化建议：
- 年龄：{age}（如果已知）
- 性别：{gender}（如果已知）
- 糖尿病类型：{diabetes_type}（如果已知）
- 病程：{disease_duration_years}年{disease_duration_months}月（如果已知）
- 胰岛素给药途径：{insulin_route}（如果已知）
- CGM使用情况：{cgm_usage}（如果已知）

## 回答要求
1. **直接回答问题**：不要先介绍自己或技术架构，直接回答用户的问题
2. **简洁明了**：控制在50字以内，直接给答案
3. **个性化建议**：基于用户信息提供针对性建议
4. **专业实用**：用通俗易懂的语言，提供具体可操作的建议
5. **安全提醒**：遇到紧急情况及时提醒就医

记住：你是AI助手，不是医生，不能替代专业医疗建议。""",
            "tagging": """你是一个专业的用户标签分析助手。基于用户的对话内容，分析并为用户打上合适的标签。

请分析对话内容，提取用户的相关信息，并以JSON数组格式返回标签列表。

标签系统包括以下类别：
1. **基本信息**: age（年龄）, gender（性别）, city（城市）
2. **健康信息**: diabetes_type（糖尿病类型）, diagnosis_date（诊断日期）, current_medication（当前用药）, blood_glucose_control（血糖控制情况）, complications（并发症）, family_history（家族史）, bmi（BMI指数）, blood_pressure（血压）, exercise_frequency（运动频率）, diet_habits（饮食习惯）
3. **治疗信息**: insulin_route（胰岛素给药途径）, cgm_usage（CGM使用情况）
4. **行为特征**: conversation_style（对话风格偏好）, active_time（活跃时间段）, checkin_frequency（打卡频率）, concern_topics（关注话题）, learning_preference（学习偏好）, reminder_enabled（提醒开关）, tts_enabled（语音播报偏好）

**输出格式要求**：
返回一个JSON数组，每个元素包含：
- tag_key: 标签键名（必须严格使用上述标签系统中的英文键名，不能使用中文或自定义键名）
- tag_value: 标签值（字符串、数字或布尔值，根据标签类型而定）
- confidence: 置信度（0.0-1.0之间的数字，表示提取的准确性）

**重要提醒**：
- 标签键名必须严格匹配上述英文键名，如：age, gender, diabetes_type, insulin_route, cgm_usage等
- 绝对不能使用中文标签键名或自定义键名
- 如果找不到合适的英文键名，可以不输出该标签

示例输出：
```json
[
  {"tag_key": "age", "tag_value": "13", "confidence": 0.9},
  {"tag_key": "gender", "tag_value": "男", "confidence": 0.95},
  {"tag_key": "diabetes_type", "tag_value": "1型糖尿病", "confidence": 1.0},
  {"tag_key": "insulin_route", "tag_value": "胰岛素笔", "confidence": 0.8}
]
```

**重要规则**：
1. 只提取对话中明确提到的信息，不要推测或编造
2. 标签键名必须严格匹配上述列表
3. 对于布尔值标签，使用字符串 "true" 或 "false"
4. 如果没有提取到任何标签，返回空数组 []
5. 确保输出是有效的JSON格式"""
        }

        # 获取基础提示词
        base_prompt = default_prompts.get(prompt_type, default_prompts["normal"])

        # 为所有提示词添加时间上下文信息
        full_prompt = time_context + base_prompt

        return full_prompt

    def tag_user_from_conversation(self, user_id: int, conversation_text: str) -> List[Dict[str, Any]]:
        """
        从对话内容中提取用户标签

        Args:
            user_id: 用户ID
            conversation_text: 对话内容

        Returns:
            List[Dict]: 标签列表
        """
        try:
            # 获取打标签提示词
            system_prompt = UserPromptSetting.get_user_prompt_content(user_id, "tagging")
            if not system_prompt:
                system_prompt = self._get_default_prompt("tagging")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析以下对话内容，提取用户标签：\n\n{conversation_text}"}
            ]

            response = self.chat_completion(messages, stream=False)

            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0].get('message', {}).get('content', '')
                logger.info(f"🔍 AI原始响应内容: {content[:500]}...")  # 记录前500个字符

                # 预处理内容：移除markdown代码块标记
                import re
                content = re.sub(r'```\w*\n?', '', content)  # 移除```json等标记
                content = content.strip()

                # 尝试解析JSON格式的标签
                try:
                    tags = json.loads(content)
                    if isinstance(tags, list):
                        # 处理中文字段名映射到英文字段名，并映射标签键
                        processed_tags = []
                        for tag in tags:
                            processed_tag = {}
                            # 映射字段名
                            if '标签键' in tag or 'tag_key' in tag:
                                processed_tag['tag_key'] = tag.get('标签键') or tag.get('tag_key')
                            if '标签值' in tag or 'tag_value' in tag:
                                processed_tag['tag_value'] = tag.get('标签值') or tag.get('tag_value')
                            if '置信度' in tag or 'confidence' in tag:
                                processed_tag['confidence'] = tag.get('置信度') or tag.get('confidence', 0.5)

                            if processed_tag.get('tag_key') and processed_tag.get('tag_value'):
                                # 映射中文标签名到英文标签键
                                tag_key_mapping = {
                                    '姓名': 'nickname',
                                    '性别': 'gender',
                                    '年龄': 'age',
                                    '糖尿病类型': 'diabetes_type',
                                    '诊断日期': 'diagnosis_date',
                                    '病程': 'disease_duration_years',
                                    '胰岛素给药途径': 'insulin_route',
                                    '胰岛素泵使用情况': 'cgm_usage',  # 这个实际上是CGM使用情况，不是胰岛素途径
                                    'CGM使用情况': 'cgm_usage',
                                    '动态血糖监测仪': 'cgm_usage',
                                    '血糖控制情况': 'blood_glucose_control',
                                    '并发症': 'complications',
                                    '家族史': 'family_history',
                                    'BMI指数': 'bmi',
                                    '血压': 'blood_pressure',
                                    '运动频率': 'exercise_frequency',
                                    '饮食习惯': 'diet_habits'
                                }

                                # 映射标签键
                                original_key = processed_tag['tag_key']
                                mapped_key = tag_key_mapping.get(original_key, original_key)

                                # 对于某些标签，标准化值
                                if mapped_key == 'cgm_usage':
                                    value_lower = str(processed_tag['tag_value']).lower()
                                    if '没有' in value_lower or '未使用' in value_lower or '不用' in value_lower:
                                        processed_tag['tag_value'] = 'false'
                                    elif '使用' in value_lower or '有' in value_lower:
                                        processed_tag['tag_value'] = 'true'
                                    else:
                                        processed_tag['tag_value'] = 'false'

                                elif mapped_key == 'gender':
                                    if '男' in str(processed_tag['tag_value']):
                                        processed_tag['tag_value'] = '男'
                                    elif '女' in str(processed_tag['tag_value']):
                                        processed_tag['tag_value'] = '女'

                                elif mapped_key == 'insulin_route':
                                    if '泵' in str(processed_tag['tag_value']):
                                        processed_tag['tag_value'] = '胰岛素泵'
                                    elif '笔' in str(processed_tag['tag_value']):
                                        processed_tag['tag_value'] = '胰岛素笔注射'

                                processed_tag['tag_key'] = mapped_key
                                processed_tags.append(processed_tag)

                        logger.info(f"✅ 从对话中提取到 {len(processed_tags)} 个标签")
                        return processed_tags
                except json.JSONDecodeError:
                    logger.warning(f"AI返回的标签格式不是有效的JSON: {content[:200]}")

            return []

        except Exception as e:
            logger.error(f"❌ 标签提取失败: {str(e)}")
            return []


# 全局服务实例
_deepseek_service = None


def get_deepseek_service() -> DeepSeekService:
    """
    获取DeepSeek服务实例（单例模式）
    """
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service
