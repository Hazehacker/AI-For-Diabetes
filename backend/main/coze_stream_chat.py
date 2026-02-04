#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coze流式对话模块 (已禁用)
~~~~~~~~~~~~~~~~~~~~~~~~~

⚠️ 此模块已禁用，仅保留基础结构以防依赖问题

处理Coze AI的流式对话接口，包括消息收集和存储
（所有对话功能已禁用，仅保留类结构）
"""

import os
import json
import time
import requests
import pymysql
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径（用于导入config_loader）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 从统一配置文件获取Coze配置
try:
    from utils.config_loader import get_config as _get_config
    def get_config(key):
        try:
            return _get_config(key)
        except:
            return None
except ImportError:
    # 如果导入失败，使用简单的配置加载
    def load_config():
        config = {}
        config_paths = ['../../config.yaml', '../config.yaml', 'config.yaml']
        for path in config_paths:
            if os.path.exists(path):
                try:
                    import yaml
                    with open(path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config and isinstance(yaml_config, dict):
                            config.update(yaml_config)
                            break
                except:
                    pass
        return config

    app_config = load_config()
    def get_config(key):
        keys = key.split('.')
        value = app_config
        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value[k]
                else:
                    return None
            return value
        except:
            return None

class CozeStreamChat:
    def __init__(self):
        # 从统一配置文件获取Coze相关配置
        self.client_id = get_config('COZE.CLIENT_ID')
        self.private_key_file = get_config('COZE.PRIVATE_KEY_FILE')
        self.public_key_id = get_config('COZE.PUBLIC_KEY_ID')
        self.base_url = get_config('COZE.API_BASE')
        self.bot_id = get_config('COZE.BOT_ID')
        self.chat_url = f"{self.base_url}/v3/chat"
        
        # 检查必要的Coze配置 - 改为警告而不是崩溃
        missing_configs = []
        if not self.client_id:
            missing_configs.append("COZE.CLIENT_ID")
        if not self.private_key_file:
            missing_configs.append("COZE.PRIVATE_KEY_FILE")
        if not self.public_key_id:
            missing_configs.append("COZE.PUBLIC_KEY_ID")
        if not self.base_url:
            missing_configs.append("COZE.API_BASE")
        if not self.bot_id:
            missing_configs.append("COZE.BOT_ID")

        if missing_configs:
            print(f"⚠️ 警告: Coze配置缺失: {', '.join(missing_configs)}")
            print("ℹ️ Coze功能将被禁用，但应用可以正常启动")
            self.private_key = None
            return

        # 尝试多个可能的私钥文件路径
        possible_paths = [
            self.private_key_file,
            f"../{self.private_key_file}",
            f"../../{self.private_key_file}"
        ]

        private_key_found = False
        for path in possible_paths:
            if path and os.path.exists(path):  # 确保path不为None且文件存在
                with open(path, "r") as f:
                    self.private_key = f.read()
                private_key_found = True
                break

        if not private_key_found:
            error_msg = f"Coze私钥文件不存在，尝试的路径: {possible_paths}\n"
            error_msg += "请确保以下步骤：\n"
            error_msg += "1. 从Coze控制台下载私钥文件\n"
            error_msg += "2. 将私钥文件放置在项目根目录，并命名为 private_key.pem\n"
            error_msg += "3. 或者在config.yaml中修改 COZE.PRIVATE_KEY_FILE 配置项\n"
            error_msg += "4. 当前配置的私钥文件路径: {self.private_key_file}"
            raise FileNotFoundError(error_msg)
    
    def get_access_token(self):
        """获取Coze访问令牌"""
        if not self.private_key:
            raise ValueError("Coze私钥未配置，无法获取访问令牌。请配置COZE.PRIVATE_KEY_FILE")

        try:
            from cozepy import JWTOAuthApp

            jwt_oauth_app = JWTOAuthApp(
                client_id=self.client_id,
                private_key=self.private_key,
                public_key_id=self.public_key_id,
                base_url=self.base_url,
            )

            oauth_token = jwt_oauth_app.get_access_token(ttl=3600)
            return oauth_token.access_token
        except Exception as e:
            return None
    
    def get_db_connection(self):

        """获取数据库连接"""
        import pymysql
        import yaml
        
        # 加载配置文件
        config = {}
        possible_paths = ['../config.yaml', '../../config.yaml', 'config.yaml']
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config and isinstance(yaml_config, dict):
                            config.update(yaml_config)
                            break
                except:
                    # 尝试旧格式
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                config[key] = value
                    break
        
        if not config:
            raise FileNotFoundError(f"配置文件不存在，尝试的路径: {possible_paths}")
        
        return pymysql.connect(
            host=config['DB_HOST'],
            port=int(config.get('DB_PORT', 3306)),
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            database=config['DB_NAME'],
            charset='utf8mb4',
            autocommit=False
        )
    
    def save_chat_session(self, user_id, conversation_id, chat_id, bot_id, status='created'):
        """保存对话会话信息"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 检查会话是否已存在
            cursor.execute('''
                SELECT session_id FROM coze_chat_sessions 
                WHERE conversation_id = %s
            ''', (conversation_id,))
            
            if cursor.fetchone():
                # 更新现有会话
                cursor.execute('''
                    UPDATE coze_chat_sessions 
                    SET chat_id = %s, status = %s
                    WHERE conversation_id = %s
                ''', (chat_id, status, conversation_id))
            else:
                # 创建新会话
                cursor.execute('''
                    INSERT INTO coze_chat_sessions 
                    (user_id, conversation_id, chat_id, bot_id, status)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, conversation_id, chat_id, bot_id, status))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            # print(f"保存对话会话失败: {e}")
            return False
    
    def _merge_message_buffer(self, message_buffer):
        """
        合并消息缓冲区中相同ID的消息内容
        
        Args:
            message_buffer: 消息缓冲区列表
            
        Returns:
            list: 合并后的消息列表
        """
        merged_messages = {}
        
        for msg in message_buffer:
            msg_id = msg.get('id')
            msg_type = msg.get('type')
            msg_role = msg.get('role')
            
            # 对于answer类型的AI消息，需要合并内容
            if msg_id and msg_type == 'answer' and msg_role == 'assistant':
                if msg_id in merged_messages:
                    # 累积内容
                    existing_content = merged_messages[msg_id].get('content', '')
                    new_content = msg.get('content', '')
                    merged_messages[msg_id]['content'] = existing_content + new_content
                else:
                    # 创建新消息
                    merged_messages[msg_id] = msg.copy()
            else:
                # 其他类型消息直接保存（不合并）
                if msg_id:
                    merged_messages[msg_id] = msg.copy()
                else:
                    # 没有ID的消息也保存
                    merged_messages[f"no_id_{len(merged_messages)}"] = msg.copy()
        
        return list(merged_messages.values())
    
    def save_chat_message(self, user_id, conversation_id, chat_id, message_data):
        """保存对话消息"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # 检查消息是否已存在
            cursor.execute('''
                SELECT message_id FROM coze_chat_messages
                WHERE coze_message_id = %s
            ''', (message_data.get('id'),))

            existing_message = cursor.fetchone()

            if existing_message:
                # 更新现有消息
                # 如果是answer类型的增量消息，需要累积内容
                if message_data.get('type') == 'answer' and message_data.get('role') == 'assistant':
                    # 获取现有内容并追加新内容
                    cursor.execute('''
                        SELECT message_content FROM coze_chat_messages
                        WHERE coze_message_id = %s
                    ''', (message_data.get('id'),))
                    existing_content = cursor.fetchone()
                    existing_text = existing_content['message_content'] if existing_content else ''
                    new_content = existing_text + message_data.get('content', '')
                    
                    cursor.execute('''
                        UPDATE coze_chat_messages
                        SET conversation_id = %s, chat_id = %s, section_id = %s,
                            message_content = %s, updated_at = NOW()
                        WHERE coze_message_id = %s
                    ''', (
                        conversation_id,
                        chat_id,
                        conversation_id,  # section_id 应该与 conversation_id 一致
                        new_content,
                        message_data.get('id')
                    ))
                    # print(f"🔄 更新了AI回答内容: {message_data.get('id')}, 累积长度: {len(new_content)}")
                else:
                    # 其他类型消息只更新元数据
                    cursor.execute('''
                        UPDATE coze_chat_messages
                        SET conversation_id = %s, chat_id = %s, section_id = %s, updated_at = NOW()
                        WHERE coze_message_id = %s
                    ''', (
                        conversation_id,
                        chat_id,
                        conversation_id,
                        message_data.get('id')
                    ))
                    # print(f"🔄 更新了消息元数据: {message_data.get('id')}")
            else:
                # 插入新消息
                cursor.execute('''
                    INSERT INTO coze_chat_messages
                    (user_id, conversation_id, chat_id, message_role, message_type,
                     message_content, content_type, coze_message_id, section_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    user_id,
                    conversation_id,
                    chat_id,
                    message_data.get('role'),
                    message_data.get('type'),
                    message_data.get('content'),
                    message_data.get('content_type'),
                    message_data.get('id'),
                    message_data.get('section_id')
                ))
                # print(f"💾 插入了新消息: {message_data.get('id')}")

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            # print(f"保存对话消息失败: {e}")
            return False
    
    def update_session_usage(self, conversation_id, usage_data):
        """更新会话使用统计"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE coze_chat_sessions 
                SET token_count = %s, input_count = %s, output_count = %s,
                    completed_at = NOW(), status = 'completed'
                WHERE conversation_id = %s
            ''', (
                usage_data.get('token_count', 0),
                usage_data.get('input_count', 0),
                usage_data.get('output_count', 0),
                conversation_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            # print(f"更新会话统计失败: {e}")
            return False
    
    def chat_with_stream(self, user_id, user_message, conversation_id=None):
        """进行流式对话并逐条yield事件"""
        try:
            # 获取访问令牌
            access_token = self.get_access_token()
            if not access_token:
                yield {'event': 'error', 'data': {'message': '无法获取访问令牌'}}
                return
            
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备请求数据
            chat_data = {
                "additional_messages": [
                    {
                        "role": "user",
                        "type": "question",
                        "content_type": "text",
                        "content": f'[{{"type":"text","text":"{user_message}"}}]'
                    }
                ],
                "stream": True,
                "user_id": f"user_{user_id}",
                "bot_id": self.bot_id,
                "connector_id": f"user_{user_id}"  # 🔑 用户隔离关键参数
            }
            
            # 如果有conversation_id，添加到URL参数中
            chat_url = self.chat_url
            if conversation_id:
                chat_url = f"{self.chat_url}?conversation_id={conversation_id}"
            
            # 发送请求
            response = requests.post(
                chat_url, 
                headers=headers, 
                json=chat_data, 
                stream=True
            )
            
            if response.status_code != 200:
                yield {'event': 'error', 'data': {'message': f'请求失败: {response.status_code}'}}
                return
            
            # 处理流式响应，逐条yield事件
            current_conversation_id = None
            current_chat_id = None
            message_buffer = []  # 缓存消息，减少数据库写入频率
            last_complete_message = None  # 记录最后一条完整消息
            has_yielded_chat_created = False  # 标记是否已yield过chat.created事件
            accumulated_answer_content = {}  # 累积每个answer消息的完整内容，用于检测完整消息
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data:'):
                        try:
                            data = json.loads(line_str[5:])  # 去掉 'data:' 前缀
                            
                            # 处理会话创建事件
                            if 'conversation_id' in data and 'chat_id' in data:
                                # 只在首次获取到会话信息时处理
                                if not current_conversation_id:
                                    current_conversation_id = data["conversation_id"]
                                    current_chat_id = data["chat_id"]
                                    
                                    # 保存会话信息
                                    self.save_chat_session(
                                        user_id, 
                                        data["conversation_id"], 
                                        data["chat_id"], 
                                        self.bot_id,
                                        data.get("status", "created")
                                    )
                                    
                                    # 保存用户消息（因为Coze API可能不会在流式响应中返回用户消息）
                                    # 检查是否已经有用户消息（Coze API可能已经返回了）
                                    has_user_message = any(
                                        msg.get('role') == 'user' and msg.get('type') == 'question' 
                                        for msg in message_buffer
                                    )
                                    if not has_user_message:
                                        user_msg_data = {
                                            "id": f"user_msg_{user_id}_{int(time.time() * 1000)}",
                                            "role": "user",
                                            "type": "question",
                                            "content": user_message,
                                            "content_type": "text",
                                            "section_id": current_conversation_id,
                                            "conversation_id": current_conversation_id
                                        }
                                        message_buffer.append(user_msg_data)
                                    
                                    # Yield会话创建事件（只yield一次）
                                    if not has_yielded_chat_created:
                                        has_yielded_chat_created = True
                                        yield {
                                            'event': 'conversation.chat.created',
                                            'data': {
                                                'conversation_id': current_conversation_id,
                                                'chat_id': current_chat_id
                                            }
                                        }
                            
                            # 处理消息增量事件
                            if 'role' in data and 'content' in data:
                                message_data = {
                                    "id": data.get("id"),
                                    "role": data.get("role"),
                                    "type": data.get("type"),
                                    "content": data.get("content"),
                                    "content_type": data.get("content_type"),
                                    "section_id": data.get("section_id"),
                                    "conversation_id": current_conversation_id
                                }
                                
                                # 缓存消息，不立即写入数据库
                                message_buffer.append(message_data)
                                
                                # Yield消息增量事件（只yield增量消息，不yield完整消息）
                                if (data.get("role") == "assistant" and 
                                    data.get("type") == "answer"):
                                    msg_id = data.get("id")
                                    content = data.get("content", "")
                                    
                                    # 累积内容（用于检测完整消息）
                                    if msg_id not in accumulated_answer_content:
                                        accumulated_answer_content[msg_id] = ""
                                    accumulated_answer_content[msg_id] += content
                                    accumulated_content = accumulated_answer_content[msg_id]
                                    
                                    # 检测是否为完整消息（基于累积内容和当前片段）
                                    # 完整消息特征：
                                    # 1. 累积内容长度超过30且包含句号、问号或感叹号
                                    # 2. 或者当前片段内容长度接近累积内容长度（说明这是完整消息的重复）
                                    is_accumulated_complete = (len(accumulated_content) > 30 and 
                                                              any(c in accumulated_content for c in '。！？'))
                                    is_duplicate_complete = (len(content) > 20 and 
                                                            len(content) >= len(accumulated_content) * 0.8)
                                    
                                    if is_duplicate_complete:
                                        # 这是完整消息的重复，不yield（避免重复）
                                        # print(f"⚠️ 检测到完整消息重复，跳过yield: {content[:50]}...")
                                        continue
                                    elif is_accumulated_complete and len(content) > 10:
                                        # 累积内容已经是完整消息，且当前片段较长，可能是完整消息的重复
                                        # 检查当前片段是否包含完整内容
                                        if content in accumulated_content or accumulated_content in content:
                                            # print(f"⚠️ 检测到完整消息重复，跳过yield")
                                            continue
                                    
                                    # 只yield增量消息（短片段）
                                    yield {
                                        'event': 'conversation.message.delta',
                                        'data': message_data
                                    }
                                
                                # Yield后续问题事件
                                if (data.get("role") == "assistant" and 
                                    data.get("type") == "follow_up"):
                                    # 收到follow_up时，立即保存所有缓存的消息（因为前端可能会提前结束）
                                    if current_conversation_id and message_buffer:
                                        # 先合并相同ID的消息内容
                                        merged_messages = self._merge_message_buffer(message_buffer)
                                        for msg in merged_messages:
                                            self.save_chat_message(
                                                user_id,
                                                current_conversation_id,
                                                current_chat_id,
                                                msg
                                            )
                                        message_buffer.clear()
                                    
                                    yield {
                                        'event': 'conversation.message.follow_up',
                                        'data': message_data
                                    }
                            
                            # 处理使用统计
                            if 'usage' in data:
                                # 对话完成，批量保存所有消息
                                if current_conversation_id and message_buffer:
                                    # 先合并相同ID的消息内容
                                    merged_messages = self._merge_message_buffer(message_buffer)
                                    # 批量保存消息，一次性写入
                                    for msg in merged_messages:
                                        self.save_chat_message(
                                            user_id,
                                            current_conversation_id,
                                            current_chat_id,
                                            msg
                                        )
                                    message_buffer.clear()
                                
                                if current_conversation_id:
                                    self.update_session_usage(
                                        current_conversation_id, 
                                        data["usage"]
                                    )
                                
                                # Yield完成事件
                                yield {
                                    'event': 'conversation.chat.completed',
                                    'data': {
                                        'conversation_id': current_conversation_id,
                                        'usage': data["usage"]
                                    }
                                }
                        
                        except json.JSONDecodeError as e:
                            continue
            
        except Exception as e:
            yield {'event': 'error', 'data': {'message': f'对话失败: {str(e)}'}}

# 创建全局实例（延迟初始化）
coze_stream_chat = None

def get_coze_stream_chat():
    """获取CozeStreamChat实例，延迟初始化"""
    global coze_stream_chat
    if coze_stream_chat is None:
        try:
            coze_stream_chat = CozeStreamChat()
        except Exception as e:

            # 创建一个占位对象，避免导入错误
            coze_stream_chat = object()
    return coze_stream_chat
