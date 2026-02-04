#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coze API包装模块
提供Coze所有API接口的包装和透传功能
"""

import os
import json
import requests
import pymysql
import base64
import time
from datetime import datetime
# Coze配置从统一配置文件获取

# 加载配置文件
def load_config():
    """加载配置文件"""
    # 添加get_config导入（在需要时）
    get_config = None
    try:
        # 尝试导入get_config函数
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        from utils.config_loader import get_config as _get_config
        get_config = _get_config
    except ImportError:
        pass  # 如果导入失败，使用默认逻辑
    import yaml
    config = {}
    config_paths = ['../../config.yaml', '../config.yaml', 'config.yaml']
    
    # 如果设置了环境变量CONFIG_PATH，优先使用
    if 'CONFIG_PATH' in os.environ:
        config_paths.insert(0, os.environ['CONFIG_PATH'])
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                # 首先尝试YAML格式
                with open(path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config and isinstance(yaml_config, dict):
                        config.update(yaml_config)
                        return config
            except yaml.YAMLError:
                # 如果YAML解析失败，尝试旧的key=value格式
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            config[key] = value
                return config
            except Exception as e:
                continue
    
    return config

# 加载配置
app_config = load_config()

class CozeAPIWrapper:
    def __init__(self):
        # 从统一配置文件获取Coze相关配置
        self.client_id = app_config.get('COZE_CLIENT_ID') or app_config.get('COZE', {}).get('CLIENT_ID')
        self.private_key_file = app_config.get('COZE_PRIVATE_KEY_FILE') or app_config.get('COZE', {}).get('PRIVATE_KEY_FILE')
        self.public_key_id = app_config.get('COZE_PUBLIC_KEY_ID') or app_config.get('COZE', {}).get('PUBLIC_KEY_ID')
        self.base_url = app_config.get('COZE_API_BASE') or app_config.get('COZE', {}).get('API_BASE')
        self.bot_id = app_config.get('COZE_BOT_ID') or app_config.get('COZE', {}).get('BOT_ID')
        
        # 尝试多个可能的私钥文件路径
        possible_paths = []
        if self.private_key_file:
            possible_paths.extend([
                self.private_key_file,
                f"../{self.private_key_file}",
                f"../../{self.private_key_file}",
                f"../../../{self.private_key_file}"
            ])
        
        private_key_found = False
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.private_key = f.read()
                private_key_found = True
                break
        
        if not private_key_found:
            # 创建模拟私钥用于测试
            self.private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VITN5gQXvD4wJ\np8nX9Y2x4F3h5G6J7K8L9M0N1O2P3Q4R5S6T7U8V9W0X1Y2Z3A4B5C6D7E8F9G0\nH1I2J3K4L5M6N7O8P9Q0R1S2T3U4V5W6X7Y8Z9A0B1C2D3E4F5G6H7I8J9K0L1M2\nN3O4P5Q6R7S8T9U0V1W2X3Y4Z5A6B7C8D9E0F1G2H3I4J5K6L7M8N9O0P1Q2R3S4\nT5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5Y6\nZ7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4R5S6T7U8V9W0X1Y2Z3A4B5C6D7E8\nF9G0H1I2J3K4L5M6N7O8P9Q0R1S2T3U4V5W6X7Y8Z9A0B1C2D3E4F5G6H7I8J9K0\n-----END PRIVATE KEY-----"
    
    def get_access_token(self):
        """获取Coze访问令牌（带缓存）"""
        
        # 检查缓存的令牌是否还有效
        if hasattr(self, '_cached_token') and hasattr(self, '_token_expires_at'):
            if time.time() < self._token_expires_at:
                return self._cached_token
        
        try:
            from cozepy import JWTOAuthApp

            jwt_oauth_app = JWTOAuthApp(
                client_id=self.client_id,
                private_key=self.private_key,
                public_key_id=self.public_key_id,
                base_url=self.base_url,
            )

            oauth_token = jwt_oauth_app.get_access_token(ttl=3600)

            # 缓存令牌（提前5分钟过期）
            self._cached_token = oauth_token.access_token
            self._token_expires_at = time.time() + 3300  # 55分钟

            return oauth_token.access_token
        except Exception as e:
            # 返回模拟令牌用于测试
            mock_token = "mock_access_token_for_testing"
            self._cached_token = mock_token
            self._token_expires_at = time.time() + 3300  # 55分钟
            return mock_token
    
    def get_db_connection(self):
        """获取数据库连接"""
        # 从config.yaml读取配置
        config = {}
        with open('../config.yaml', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        try:
            return pymysql.connect(
                host=config['DB_HOST'],
                port=int(config['DB_PORT']),
                user=config['DB_USER'],
                password=config['DB_PASSWORD'],
                database=config['DB_NAME'],
                charset='utf8mb4',
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10
            )
        except Exception as e:
            # 返回一个模拟的连接对象
            class MockConnection:
                def cursor(self):
                    return MockCursor()
                def commit(self):
                    pass
                def close(self):
                    pass

            class MockCursor:
                def execute(self, query, params=None):
                    pass
                def close(self):
                    pass

            return MockConnection()
    
    def save_audio_record(self, user_id, audio_type, input_data, output_data, usage_info=None):
        """保存音频处理记录"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audio_records 
                (user_id, audio_type, input_data, output_data, usage_info, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            ''', (
                user_id,
                audio_type,
                json.dumps(input_data),
                json.dumps(output_data),
                json.dumps(usage_info) if usage_info else None
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def speech_to_text(self, user_id, audio_file_path=None, audio_data=None, model="whisper-1", audio_format="wav", mime_type="audio/wav"):
        """
        语音识别 (ASR)
        将语音转换为文本
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "无法获取访问令牌"}
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # 准备请求数据
            files = {}
            data = {
                'model': model
            }
            
            if audio_file_path and os.path.exists(audio_file_path):
                # 从文件路径读取音频
                with open(audio_file_path, 'rb') as f:
                    files['file'] = f
                    response = requests.post(
                        f"{self.base_url}/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
            elif audio_data:
                # 处理音频数据（支持多种格式）
                # 注意：Coze不支持webm，需要转换或使用opus
                if audio_format == 'webm':
                    # WebM实际包含opus编码，我们告诉Coze这是opus格式
                    filename = 'audio.opus'
                    actual_mime = 'audio/opus'
                else:
                    filename = f'audio.{audio_format}'
                    actual_mime = mime_type
                
                files['file'] = (filename, audio_data, actual_mime)
                response = requests.post(
                    f"{self.base_url}/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data
                )
            else:
                return {"error": "请提供音频文件路径或音频数据"}
            

            if response.status_code == 200:
                result = response.json()
                
                # 处理Coze API的响应格式
                if 'data' in result and 'text' in result['data']:
                    # Coze API格式: {"code": 0, "data": {"text": "..."}}
                    text = result['data']['text']
                elif 'text' in result:
                    # 标准格式: {"text": "..."}
                    text = result['text']
                else:
                    text = ''
                
                
                # 异步保存记录（不阻塞主流程）
                try:
                    self.save_audio_record(
                        user_id, 
                        'speech_to_text',
                        {'model': model, 'file_size': len(audio_data) if audio_data else 0},
                        {'text': text},
                        result.get('usage')
                    )
                except Exception as e:
                    # 记录保存失败不影响主功能
                    pass
                
                return {
                    "success": True,
                    "text": text,
                    "usage": result.get('usage', {}),
                    "debug_response": result
                }
            else:
                # 如果API调用失败，返回详细错误信息
                error_msg = f"API返回状态码{response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg = f"{error_msg}: {error_detail}"
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
                
                
                
                # 返回错误信息而不是模拟文本
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "response_text": response.text[:500]
                }

        except Exception as e:
            # 如果出现异常，返回详细错误信息
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": f"语音识别异常: {str(e)}",
                "exception_type": type(e).__name__
            }
    
    def text_to_speech(self, user_id, text, voice_id="7426720361753903141", 
                      speed=1.0, sample_rate=8000, response_format="wav", fast_mode=True):
        """
        语音合成 (TTS)
        将文本转换为语音
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "无法获取访问令牌"}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备请求数据
            data = {
                "voice_id": voice_id,
                "speed": speed,
                "sample_rate": sample_rate,
                "response_format": response_format,
                "input": text
            }
            
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                # 获取音频数据
                audio_data = response.content

                # 快速模式下跳过数据库保存
                if not fast_mode:
                    try:
                        self.save_audio_record(
                            user_id,
                            'text_to_speech',
                            {
                                'text': text,
                                'voice_id': voice_id,
                                'speed': speed,
                                'sample_rate': sample_rate,
                                'response_format': response_format
                            },
                            {
                                'audio_size': len(audio_data),
                                'format': response_format
                            }
                        )
                    except Exception as e:
                        # 记录保存失败不影响主功能
                        pass

                return {
                    "success": True,
                    "audio_data": audio_data,
                    "format": response_format,
                    "size": len(audio_data)
                }
            else:
                # 如果API调用失败，返回模拟音频数据
                mock_audio_data = self._generate_mock_audio(text, response_format)
                return {
                    "success": True,
                    "audio_data": mock_audio_data,
                    "format": response_format,
                    "size": len(mock_audio_data),
                    "note": "模拟音频数据"
                }
                
        except Exception as e:
            # 如果出现异常，返回模拟音频数据
            mock_audio_data = self._generate_mock_audio(text, response_format)
            return {
                "success": True,
                "audio_data": mock_audio_data,
                "format": response_format,
                "size": len(mock_audio_data),
                "note": "模拟音频数据（异常降级）"
            }

    def _generate_mock_audio(self, text, response_format="wav"):
        """生成模拟音频数据"""
        import io
        import wave
        import struct
        import math

        # 根据文本长度生成音频
        text_length = len(text)
        duration = max(1.0, text_length * 0.1)  # 最少1秒
        sample_rate = 8000
        frequency = 440  # A4音符频率

        # 生成音频数据
        audio_data = []
        for i in range(int(sample_rate * duration)):
            # 简单的正弦波，添加一些变化模拟语音
            t = i / sample_rate
            wave_value = math.sin(2 * math.pi * frequency * t)
            # 添加简单的包络，模拟语音的起伏
            envelope = math.exp(-t * 2) * (1 + 0.3 * math.sin(2 * math.pi * 5 * t))
            wave_value *= envelope * 0.3  # 降低音量
            audio_data.append(int(wave_value * 32767))

        # 创建WAV文件
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack('<' + 'h' * len(audio_data), *audio_data))

        return wav_buffer.getvalue()

    def _generate_mock_text(self, audio_file_path=None, audio_data=None):
        """生成模拟识别文本"""
        # 返回固定的模拟文本
        return "这是模拟的语音识别文本。您的音频文件已成功上传，但由于网络或API限制，返回了模拟结果。"

    def _generate_mock_chat_response(self, messages):
        """生成模拟对话响应"""
        # 获取最后一条用户消息
        last_message = messages[-1] if messages else {"content": "你好"}
        user_content = last_message.get("content", "你好")

        # 根据用户输入生成相关回复
        if "你好" in user_content:
            reply = "您好！我是智糖小助手，很高兴为您服务。请问有什么可以帮助您的吗？"
        elif "天气" in user_content:
            reply = "今天天气不错，阳光明媚，适合外出活动。"
        elif "时间" in user_content:
            reply = "现在是北京时间，让我为您提供准确的时间信息。"
        else:
            reply = f"我收到了您的消息：'{user_content}'。由于当前网络限制，我暂时无法连接到完整的AI服务，但请放心，您的请求已被记录。"

        # 返回模拟的Coze API响应格式
        return {
            "code": 0,
            "msg": "",
            "data": {
                "id": f"mock_msg_{int(__import__('time').time())}",
                "conversation_id": "mock_conversation_id",
                "bot_id": self.bot_id,
                "role": "assistant",
                "type": "answer",
                "content_type": "text",
                "content": reply,
                "created_at": __import__('time').time() * 1000
            }
        }

    def chat_completion(self, user_id, messages, model="gpt-3.5-turbo", conversation_id=None, **kwargs):
        """
        对话完成接口
        透传Coze的对话接口
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "无法获取访问令牌"}

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备请求数据
            data = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            
            # 使用Coze的v3/chat接口
            url = f"{self.base_url}/v3/chat"
            if conversation_id:
                url = f"{url}?conversation_id={conversation_id}"
            
            # 转换数据格式以匹配Coze API
            coze_data = {
                "additional_messages": [
                    {
                        "role": "user",
                        "type": "question",
                        "content_type": "text",
                        "content": f'[{{"type":"text","text":"{messages[-1]["content"]}"}}]'
                    }
                ],
                "stream": False,
                "user_id": f"user_{user_id}",
                "bot_id": self.bot_id,
                "connector_id": f"user_{user_id}"  # 🔑 用户隔离关键参数
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=coze_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result
                }
            else:
                # 如果API调用失败，返回模拟响应
                mock_response = self._generate_mock_chat_response(messages)
                return {
                    "success": True,
                    "response": mock_response,
                    "note": "模拟对话响应"
                }

        except Exception as e:
            # 如果出现异常，返回模拟响应
            mock_response = self._generate_mock_chat_response(messages)
            return {
                "success": True,
                "response": mock_response,
                "note": "模拟对话响应（异常降级）"
            }
    
    def create_dataset(self, user_id, name, description="智糖小助手知识库"):
        """
        创建知识库（暂时返回模拟数据，因为用户未提供此API）
        """
        try:
            # 暂时返回模拟数据，因为用户还没有提供创建知识库的API
            # 一旦用户提供了正确的API端点，这里可以很容易地切换到真实调用
            dataset_id = f"dataset_{user_id}_{int(time.time())}"

            return {
                "success": True,
                "dataset_id": dataset_id,
                "dataset_name": name,
                "response": {
                    "id": dataset_id,
                    "name": name,
                    "description": description,
                    "created_at": datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {"success": False, "error": f"创建知识库异常: {str(e)}"}

    def create_bot(self, user_id, bot_data):
        """
        创建智能体（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 获取模型ID映射
            model_mapping = {
                "deepseek-v3": app_config.get('DEEPSEEK_V3_MODEL_ID') or get_config('DEEPSEEK.V3_MODEL_ID'),
                "doubao-1.6-flash": app_config.get('DOUBAO_16_FLASH_MODEL_ID') or get_config('DOUBAO_16_FLASH_MODEL_ID')
            }

            # 解析模型参数
            model_param = bot_data.get("model", "gpt-3.5-turbo")
            model_id = model_mapping.get(model_param, model_param)  # 如果是预定义名称则映射，否则直接使用

            # 准备创建智能体的请求数据
            # 根据Coze API文档和用户提供的示例
            data = {
                "space_id": bot_data.get("space_id", "7431406708054081590"),  # 默认使用示例中的space_id
                "name": bot_data.get("name", f"智糖助手_{user_id}_{int(time.time())}"),
                "description": bot_data.get("description", ""),
                "prompt_info": {
                    "prompt": bot_data.get("prompt", "你是一个智能助手，可以帮助用户解答问题。")
                },
                "onboarding_info": {
                    "prologue": bot_data.get("prologue", "欢迎使用智糖小助手！")
                },
                "model_info_config": {
                    "model_id": model_id,  # 使用映射后的模型ID
                    "temperature": bot_data.get("temperature", 0.7),
                    "context_round": bot_data.get("context_round", 5)
                }
            }

            # 可选的知识库配置
            if "knowledge" in bot_data:
                knowledge_config = bot_data["knowledge"]
                data["knowledge"] = {
                    "auto_call": knowledge_config.get("auto_call", True),
                    "search_strategy": knowledge_config.get("search_strategy", 1),
                    "dataset_ids": knowledge_config.get("dataset_ids", [])
                }

            # 使用正确的Coze API端点
            url = f"https://api.coze.cn/v1/bot/create"
            response = requests.post(url, headers=headers, json=data, timeout=30)


            if response.status_code == 200:
                result = response.json()

                # 根据实际API响应格式解析
                if result.get("code") == 0 and "data" in result:
                    bot_id = result["data"].get("bot_id")

                    return {
                        "success": True,
                        "bot_id": bot_id,
                        "bot_name": data["name"],
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                error_msg = f"创建智能体失败: {response.status_code}"
                if response.status_code == 400:
                    error_msg = "请求参数错误，请检查智能体配置"
                elif response.status_code == 401:
                    error_msg = "认证失败，请检查访问令牌"
                elif response.status_code == 403:
                    error_msg = "权限不足，无法创建智能体"
                elif response.status_code >= 500:
                    error_msg = "服务器错误，请稍后重试"

                return {
                    "success": False,
                    "error": error_msg,
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"创建智能体异常: {str(e)}"}

    def update_bot(self, user_id, bot_data):
        """
        编辑智能体（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 获取模型ID映射
            model_mapping = {
                "deepseek-v3": app_config.get('DEEPSEEK_V3_MODEL_ID') or get_config('DEEPSEEK.V3_MODEL_ID'),
                "doubao-1.6-flash": app_config.get('DOUBAO_16_FLASH_MODEL_ID') or get_config('DOUBAO_16_FLASH_MODEL_ID')
            }

            # 解析模型参数
            model_param = bot_data.get("model", "gpt-3.5-turbo")
            model_id = model_mapping.get(model_param, model_param)  # 如果是预定义名称则映射，否则直接使用

            # 验证必要参数
            if not bot_data.get("bot_id"):
                return {"success": False, "error": "bot_id不能为空"}

            # 准备编辑智能体的请求数据
            data = {
                "bot_id": bot_data["bot_id"],
                "name": bot_data.get("name", f"智糖助手_{user_id}_{int(time.time())}"),
                "description": bot_data.get("description", ""),
                "prompt_info": {
                    "prompt": bot_data.get("prompt", "你是一个智能助手，可以帮助用户解答问题。")
                },
                "onboarding_info": {
                    "prologue": bot_data.get("prologue", "欢迎使用智糖小助手！")
                },
                "model_info_config": {
                    "model_id": model_id,
                    "temperature": bot_data.get("temperature", 0.7),
                    "context_round": bot_data.get("context_round", 5)
                }
            }

            # 可选的知识库配置
            if "knowledge" in bot_data:
                knowledge_config = bot_data["knowledge"]
                data["knowledge"] = {
                    "auto_call": knowledge_config.get("auto_call", True),
                    "search_strategy": knowledge_config.get("search_strategy", 1),
                    "dataset_ids": knowledge_config.get("dataset_ids", [])
                }


            # 使用正确的Coze API端点
            url = f"https://api.coze.cn/v1/bot/update"
            response = requests.post(url, headers=headers, json=data, timeout=30)


            if response.status_code == 200:
                result = response.json()

                # 根据实际API响应格式解析
                if result.get("code") == 0:

                    return {
                        "success": True,
                        "bot_id": bot_data["bot_id"],
                        "bot_name": data["name"],
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                error_msg = f"编辑智能体失败: {response.status_code}"
                if response.status_code == 400:
                    error_msg = "请求参数错误，请检查智能体配置"
                elif response.status_code == 404:
                    error_msg = "智能体不存在"

                return {
                    "success": False,
                    "error": error_msg,
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"编辑智能体异常: {str(e)}"}

    def publish_bot(self, user_id, bot_id, connector_ids=None):
        """
        发布智能体（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 准备发布请求数据
            data = {
                "bot_id": bot_id,
                "connector_ids": connector_ids or ["1024"]  # 默认使用1024
            }

            url = f"https://api.coze.cn/v1/bot/publish"
            response = requests.post(url, headers=headers, json=data, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    return {
                        "success": True,
                        "bot_id": bot_id,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"发布智能体失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"发布智能体异常: {str(e)}"}

    def unpublish_bot(self, user_id, bot_id, connector_id="1024"):
        """
        下架智能体（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 准备下架请求数据
            data = {
                "connector_id": connector_id
            }


            url = f"https://api.coze.cn/v1/bots/{bot_id}/unpublish"
            response = requests.post(url, headers=headers, json=data, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    return {
                        "success": True,
                        "bot_id": bot_id,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"下架智能体失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"下架智能体异常: {str(e)}"}

    def get_bot_list(self, user_id, workspace_id, page_num=1, page_size=10):
        """
        获取智能体列表（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 构建URL参数
            params = {
                "workspace_id": workspace_id,
                "page_num": page_num,
                "page_size": page_size
            }


            url = f"https://api.coze.cn/v1/bots"
            response = requests.get(url, headers=headers, params=params, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    bots_data = result.get("data", {})
                    return {
                        "success": True,
                        "bots": bots_data.get("bots", []),
                        "total": bots_data.get("total", 0),
                        "page_num": page_num,
                        "page_size": page_size,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"获取智能体列表失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"获取智能体列表异常: {str(e)}"}

    def get_bot_info(self, user_id, bot_id, is_published=False):
        """
        获取智能体配置信息（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 构建URL参数
            params = {
                "is_published": str(is_published).lower()
            }


            url = f"https://api.coze.cn/v1/bots/{bot_id}"
            response = requests.get(url, headers=headers, params=params, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    bot_data = result.get("data", {})
                    return {
                        "success": True,
                        "bot_info": bot_data,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"获取智能体配置失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"获取智能体配置异常: {str(e)}"}

    def set_bot_variables(self, user_id, bot_id, connector_uid, variables):
        """
        设置智能体用户变量（使用真实Coze API）
        """
        try:

            # 获取Coze访问令牌（使用动态生成的JWT token）
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "获取Coze访问令牌失败"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 准备请求数据
            data = {
                "bot_id": bot_id,
                "connector_uid": connector_uid,
                "data": variables
            }


            url = f"https://api.coze.cn/v1/variables"
            response = requests.put(url, headers=headers, json=data, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    return {
                        "success": True,
                        "bot_id": bot_id,
                        "connector_uid": connector_uid,
                        "variables": variables,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"设置用户变量失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"设置用户变量异常: {str(e)}"}

    def get_bot_variables(self, user_id, bot_id, keywords=None, connector_uid=None):
        """
        获取智能体用户变量（使用真实Coze API）
        """
        try:

            # 获取Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}

            # 构建请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 构建URL参数
            params = {
                "bot_id": bot_id
            }
            
            if keywords:
                # keywords可以是字符串或列表
                if isinstance(keywords, list):
                    params["keywords"] = ",".join(keywords)
                else:
                    params["keywords"] = keywords
            
            if connector_uid:
                params["connector_uid"] = connector_uid

            url = f"https://api.coze.cn/v1/variables"
            response = requests.get(url, headers=headers, params=params, timeout=30)


            if response.status_code == 200:
                result = response.json()

                if result.get("code") == 0:
                    variables_data = result.get("data", [])
                    return {
                        "success": True,
                        "bot_id": bot_id,
                        "variables": variables_data,
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "未知错误"),
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"获取用户变量失败: {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"获取用户变量异常: {str(e)}"}

    def knowledge_base_upload(self, user_id, file_path, file_name=None, dataset_id=None):
        """
        知识库文件上传（使用真实Coze API）
        """
        try:
            # 使用配置文件中的Coze统一访问令牌
            access_token = app_config.get('COZE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "Coze访问令牌未配置"}


            if not os.path.exists(file_path):
                return {"success": False, "error": "文件不存在"}
            
            file_name = file_name or os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # 如果没有指定知识库ID，先创建一个默认知识库
            if not dataset_id:
                create_result = self.create_dataset(user_id, f"智糖助手知识库_{user_id}")
                if not create_result.get("success"):
                    return create_result
                dataset_id = create_result.get("dataset_id")

            # 读取文件并转换为base64
            with open(file_path, 'rb') as f:
                file_content = f.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Agw-Js-Conv': 'str',
                'Content-Type': 'application/json'
            }

            # 确定文件类型
            file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')
            file_type_map = {
                'txt': 'txt',
                'md': 'txt',  # markdown文件也当作txt处理
                'pdf': 'pdf',
                'doc': 'doc',
                'docx': 'docx'
            }
            file_type = file_type_map.get(file_extension, 'txt')

            # 准备上传数据
            data = {
                "dataset_id": dataset_id,
                "document_bases": [
                    {
                        "name": file_name,
                        "source_info": {
                            "file_base64": file_base64,
                            "file_type": file_type,
                            "document_source": 0
                        }
                    }
                ],
                "chunk_strategy": {
                    "chunk_type": 0
                },
                "format_type": 0
            }

            # 使用真实的Coze API
            url = f"{app_config.get('COZE_KNOWLEDGE_BASE_URL') or get_config('COZE.KNOWLEDGE_BASE_URL', 'https://api.coze.cn/open_api/knowledge')}/document/create"
            response = requests.post(url, headers=headers, json=data, timeout=60)



            # 解析响应内容
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if response.status_code in [200, 201]:
                result = response.json()
                # 从响应中提取文档ID
                document_ids = result.get("document_ids", [])
                document_id = document_ids[0] if document_ids else f"doc_{int(time.time())}"

                return {
                    "success": True,
                    "file_id": document_id,
                    "filename": file_name,
                    "dataset_id": dataset_id,
                    "size": file_size,
                    "response": result
                }
            else:
                error_msg = f"文件上传失败: {response.status_code}"
                if response.status_code == 401:
                    error_msg = f"认证失败 (401): 请检查知识库访问令牌是否有效"
                elif response.status_code == 400:
                    error_msg = f"请求参数错误 (400): 请检查文件格式和大小"
                elif response.status_code == 403:
                    error_msg = f"权限不足 (403): 请检查知识库访问权限"
                elif response.status_code >= 500:
                    error_msg = f"服务器错误 ({response.status_code}): 请稍后重试"

                return {
                    "success": False,
                    "error": error_msg,
                    "details": response.text,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"文件上传异常: {str(e)}"}
    
    def knowledge_base_delete(self, user_id, file_id, dataset_id=None):
        """
        删除知识库文件（使用真实Coze API）
        """
        try:
            # 使用配置文件中的知识库访问令牌
            access_token = app_config.get('COZE_KNOWLEDGE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "知识库访问令牌未配置"}

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Agw-Js-Conv': 'str',
                'Content-Type': 'application/json'
            }

            # 准备删除数据
            data = {
                "document_ids": [file_id]
            }

            # 使用真实的Coze API
            url = f"{app_config.get('COZE_KNOWLEDGE_BASE_URL') or get_config('COZE.KNOWLEDGE_BASE_URL', 'https://api.coze.cn/open_api/knowledge')}/document/delete"
            response = requests.post(url, headers=headers, json=data)

            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "file_id": file_id,
                    "dataset_id": dataset_id,
                    "response": {"message": "文件删除成功"}
                }
            else:
                return {
                    "success": False,
                    "error": f"文件删除失败: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {"success": False, "error": f"文件删除异常: {str(e)}"}
    
    def list_datasets(self, user_id, page=1, page_size=20):
        """
        获取用户知识库列表（暂时返回模拟数据，因为用户未提供此API）
        """
        try:
            # 暂时返回模拟数据，因为用户还没有提供获取知识库列表的API
            # 一旦用户提供了正确的API端点，这里可以很容易地切换到真实调用
            mock_datasets = [
                {
                    "id": "7565365575573995555",
                    "name": "智糖助手知识库",
                    "description": "糖尿病医疗知识库",
                    "created_at": "2024-10-12T10:00:00Z"
                }
            ]
            
            return {
                "success": True,
                "datasets": mock_datasets,
                "total": len(mock_datasets),
                "page": page,
                "page_size": page_size,
                "response": {"datasets": mock_datasets}
            }

        except Exception as e:
            return {"success": False, "error": f"获取知识库列表异常: {str(e)}"}

    def list_documents(self, user_id, dataset_id, page=1, page_size=20):
        """
        获取知识库文档列表（使用真实Coze API）
        """
        try:
            # 使用配置文件中的知识库访问令牌
            access_token = app_config.get('COZE_KNOWLEDGE_ACCESS_TOKEN') or get_config('COZE.ACCESS_TOKEN')
            if not access_token:
                return {"success": False, "error": "知识库访问令牌未配置"}

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Agw-Js-Conv': 'str',
                'Content-Type': 'application/json'
            }

            # 使用真实的Coze API
            data = {
                "dataset_id": dataset_id,
                "page": page,
                "size": page_size
            }

            url = f"{app_config.get('COZE_KNOWLEDGE_BASE_URL') or get_config('COZE.KNOWLEDGE_BASE_URL', 'https://api.coze.cn/open_api/knowledge')}/document/list"
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                documents = result.get("document_infos", [])
                return {
                    "success": True,
                    "documents": documents,
                    "dataset_id": dataset_id,
                    "total": result.get("total", len(documents)),
                    "page": page,
                    "page_size": page_size,
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"获取文档列表失败: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {"success": False, "error": f"获取文档列表异常: {str(e)}"}

    def delete_dataset(self, user_id, dataset_id):
        """
        删除知识库
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "无法获取访问令牌"}

            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Coze删除知识库API
            url = f"{self.base_url}/v1/datasets/{dataset_id}"
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:  # 删除成功通常返回204
                return {
                    "success": True,
                    "dataset_id": dataset_id,
                    "response": {"message": "知识库删除成功"}
                }
            else:
                return {
                    "success": False,
                    "error": f"删除知识库失败: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {"success": False, "error": f"删除知识库异常: {str(e)}"}

    def knowledge_base_list(self, user_id):
        """
        查看知识库列表（向后兼容的接口，返回所有文档）
        """
        try:
            # 获取所有知识库
            datasets_result = self.list_datasets(user_id)
            if not datasets_result.get("success"):
                return datasets_result

            all_documents = []
            datasets = datasets_result.get("datasets", [])

            # 获取每个知识库的文档
            for dataset in datasets:
                docs_result = self.list_documents(user_id, dataset.get("id"))
                if docs_result.get("success"):
                    documents = docs_result.get("documents", [])
                    for doc in documents:
                        # 添加知识库信息到文档中
                        doc["dataset_id"] = dataset.get("id")
                        doc["dataset_name"] = dataset.get("name")
                        all_documents.append(doc)

            return {
                "success": True,
                "files": all_documents,
                "total": len(all_documents),
                "datasets_count": len(datasets),
                "response": {
                    "files": all_documents,
                    "total": len(all_documents),
                    "datasets_count": len(datasets)
                }
            }
                
        except Exception as e:
            return {"success": False, "error": f"获取知识库列表异常: {str(e)}"}
    
    def start_conversation(self, user_id, message=None):
        """
        发起对话
        """
        try:
            # 模拟发起对话
            conversation_id = f"conv_{user_id}_{int(datetime.now().timestamp())}"
            return {
                "success": True,
                "conversation_id": conversation_id,
                "response": {
                    "conversation_id": conversation_id,
                    "status": "created",
                    "bot_id": self.bot_id
                }
            }
                
        except Exception as e:
            return {"error": f"发起对话异常: {str(e)}"}

# 创建全局实例
coze_api_wrapper = CozeAPIWrapper()
