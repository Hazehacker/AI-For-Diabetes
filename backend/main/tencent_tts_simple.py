"""
腾讯云TTS - 简化版本
使用HTTP API实现实时合成（边生成边播报）
"""

import requests
import json
import time
import base64
from utils.config_loader import get_config


class TencentTTSSimple:
    """腾讯云TTS客户端（HTTP API版本）"""
    
    def __init__(self, app_id=None, secret_id=None, secret_key=None):
        # 从配置获取参数
        self.app_id = app_id or get_config('TENCENT_TTS.APP_ID')
        self.secret_id = secret_id or get_config('TENCENT_TTS.SECRET_ID')
        self.secret_key = secret_key or get_config('TENCENT_TTS.SECRET_KEY')
        self.api_url = "https://tts.cloud.tencent.com/stream"
    
    def synthesize(self, text, voice_type=None, codec=None, sample_rate=None, speed=None, volume=None):
        """
        合成文本为语音
        返回：音频二进制数据
        
        Args:
            text: 要合成的文本
            voice_type: 语音类型（默认使用配置）
            codec: 音频编码格式（默认使用配置）
            sample_rate: 采样率（默认使用配置）
            speed: 语速 [-2, 6]，0表示正常语速（默认使用配置）
            volume: 音量 [-10, 10]，0表示正常音量（默认使用配置）
        """
        try:
            # 从配置获取默认值
            voice_type = voice_type or get_config('TENCENT_TTS.VOICE_TYPE', '502001')
            codec = codec or get_config('TENCENT_TTS.CODEC', 'mp3')
            sample_rate = sample_rate or get_config('TENCENT_TTS.SAMPLE_RATE', 16000)

            # 使用传入的speed或配置中的默认值
            tts_speed = speed if speed is not None else get_config('TENCENT_TTS.SPEED', 0)

            # 获取音量配置，默认值为0
            tts_volume = volume if volume is not None else get_config('TENCENT_TTS.VOLUME', 0)

            # 构建请求参数
            timestamp = int(time.time())
            params = {
                "Action": "TextToStreamAudio",
                "AppId": self.app_id,
                "SecretId": self.secret_id,
                "Timestamp": str(timestamp),
                "Expired": str(timestamp + 3600),
                "Text": text,
                "SessionId": f"session_{timestamp}",
                "ModelType": 1,  # 1-高级音色
                "VoiceType": int(voice_type),
                "Codec": codec,
                "SampleRate": sample_rate,
                "Volume": tts_volume,
                "Speed": tts_speed,
            }
            
            # 生成签名
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.tts.v20190823 import tts_client, models
            
            # 使用SDK
            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tts.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            client = tts_client.TtsClient(cred, "", clientProfile)
            req = models.TextToVoiceRequest()
            
            params_json = {
                "Text": text,
                "SessionId": f"session_{timestamp}",
                "ModelType": 1,
                "VoiceType": int(voice_type),
                "Codec": codec,
                "SampleRate": sample_rate,
                "Volume": tts_volume,
                "Speed": tts_speed,
            }
            req.from_json_string(json.dumps(params_json))
            
            resp = client.TextToVoice(req)
            
            # 获取音频数据
            if resp.Audio:
                audio_data = base64.b64decode(resp.Audio)
                return audio_data
            else:
                return None
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

