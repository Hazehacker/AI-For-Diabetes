"""
TTS语音服务
~~~~~~~~~~~

文本转语音服务，包括：
- 文本转语音
- 语音缓存管理
- 批量转语音
- 预生成常用语音

作者: 智糖团队
日期: 2025-01-15
"""

import os
import hashlib
import base64
from typing import Optional, List, Dict

# Windows 兼容性处理
try:
    import fcntl
except ImportError:
    # Windows 不支持 fcntl，使用 portalocker 替代
    try:
        import portalocker as fcntl
    except ImportError:
        # 如果 portalocker 也没有，使用空实现
        fcntl = None
from utils.logger import get_logger
from utils.config_loader import get_config
from utils.decorators import cache_result

logger = get_logger(__name__)

# 尝试导入TTS客户端
try:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from tencent_tts_simple import TencentTTSSimple
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("⚠️ TencentTTSSimple 未安装，将使用模拟模式")


class TTSService:
    """
    TTS服务类
    
    提供统一的TTS接口，支持缓存和批量处理
    """
    
    def __init__(self):
        """初始化TTS服务"""
        self.config = get_config()
        self.cache_dir = get_config('CACHE.TTS_CACHE_DIR', '../tts_cache')
        self.tts_client = None
        
        # 创建缓存目录
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.debug(f"✅ 创建TTS缓存目录: {self.cache_dir}")
        
        # 初始化TTS客户端
        if TTS_AVAILABLE:
            try:
                self.tts_client = TencentTTSSimple()
                logger.info("✅ 腾讯云TTS客户端初始化成功")
            except Exception as e:
                logger.error(f"❌ TTS客户端初始化失败: {str(e)}")
                self.tts_client = None
    
    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """
        将PCM音频数据转换为WAV格式
        
        Args:
            pcm_data: PCM音频数据
            sample_rate: 采样率（默认16000）
            channels: 声道数（默认1，单声道）
            bits_per_sample: 采样位数（默认16）
            
        Returns:
            bytes: WAV格式的音频数据
        """
        import struct
        
        # WAV文件格式：
        # RIFF头（12字节）："RIFF" + 文件大小(4字节) + "WAVE"
        # fmt子块（24字节）："fmt " + 子块大小(4字节) + 格式数据(16字节)
        # data子块（8字节 + PCM数据）："data" + 数据大小(4字节) + PCM数据
        
        data_size = len(pcm_data)
        # 🔥 修复：RIFF头中的文件大小 = 整个文件大小 - 8（不包括"RIFF"标识和大小字段本身）
        # 文件内容 = fmt子块(24) + data子块头(8) + PCM数据 + WAVE标识(4)
        # 所以：file_size_in_header = 4 + 24 + 8 + data_size = 36 + data_size
        file_size_in_header = 36 + data_size
        
        # 计算字节率和块对齐
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        
        # 构建RIFF头（RIFF标识 + 文件大小 + WAVE标识）
        wav_header = struct.pack('<4sI4s', b'RIFF', file_size_in_header, b'WAVE')
        
        # 构建fmt子块
        fmt_chunk = struct.pack('<4sIHHIIHH',
            b'fmt ',  # 子块ID (4字节)
            16,  # fmt子块大小 (4字节，不包括ID和大小本身)
            1,  # 音频格式 (2字节，1=PCM)
            channels,  # 声道数 (2字节)
            sample_rate,  # 采样率 (4字节)
            byte_rate,  # 字节率 (4字节)
            block_align,  # 块对齐 (2字节)
            bits_per_sample  # 采样位数 (2字节)
        )
        
        # 构建data子块头
        data_chunk_header = struct.pack('<4sI', b'data', data_size)
        
        # 组合WAV文件
        wav_data = wav_header + fmt_chunk + data_chunk_header + pcm_data
        
        return wav_data
    
    def _get_cache_path(self, text: str, voice_id: str = None, speed: float = 1.0) -> str:
        """
        生成缓存文件路径

        Args:
            text: 文本内容
            voice_id: 语音ID（会转换为实际的TTS voice_type）
            speed: 语速

        Returns:
            str: 缓存文件路径
        """
        # 使用实际的TTS参数生成缓存key，确保相同音色能正确复用
        from utils.config_loader import get_config as _get_config

        # 获取默认TTS语音类型
        default_voice_type = _get_config('TENCENT_TTS.VOICE_TYPE')
        if not default_voice_type:
            default_voice_type = "7426720361753903141"  # 默认值

        # 转换voice_id为实际的TTS voice_type
        if voice_id and voice_id.isdigit() and len(voice_id) == 6:
            actual_voice_type = voice_id
        else:
            actual_voice_type = default_voice_type

        # 将speed转换为TTS实际使用的speed值
        if speed <= 0.5:
            tts_speed = -2
        elif speed >= 2.0:
            tts_speed = 6
        else:
            tts_speed = int((speed - 0.5) / 1.5 * 8 - 2)
            tts_speed = max(-2, min(6, tts_speed))

        # 生成唯一的缓存key（使用实际的TTS参数）
        cache_key = f"{text}_{actual_voice_type}_{tts_speed}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{file_hash}.wav")
    
    def text_to_speech(
        self,
        text: str,
        voice_id: str = "7426720361753903141",
        speed: float = 1.0,
        sample_rate: int = 16000,
        use_cache: bool = True
    ) -> Optional[bytes]:
        """
        文本转语音
        
        Args:
            text: 要转换的文本
            voice_id: 语音ID
            speed: 语速 (0.5-2.0)
            sample_rate: 采样率
            use_cache: 是否使用缓存
            
        Returns:
            bytes: 音频数据（WAV格式）
        """
        try:
            # 检查缓存
            if use_cache:
                cache_path = self._get_cache_path(text, voice_id, speed)
                if os.path.exists(cache_path):
                    with open(cache_path, 'rb') as f:
                        # 获取共享锁，确保读取时文件不被修改（仅在 Unix/Linux 上）
                        if fcntl:
                            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        try:
                            cached_data = f.read()
                        finally:
                            if fcntl:
                                fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # 释放锁

                        # 验证缓存文件格式（支持WAV和MP3）
                        is_valid_cache = False
                        cache_format = None

                        # 🔥 改进：添加详细的格式检测日志
                        file_size = len(cached_data)
                        header_hex = cached_data[:16].hex() if len(cached_data) >= 16 else cached_data.hex()

                        # 检查是否是WAV格式
                        if len(cached_data) >= 12 and cached_data[:4] == b'RIFF' and cached_data[8:12] == b'WAVE':
                            is_valid_cache = True
                            cache_format = 'wav'
                            logger.debug(f"✅ WAV格式验证通过: size={file_size}, header={header_hex[:32]}...")
                        # 检查是否是MP3格式（ID3标签或直接MP3帧）
                        elif (len(cached_data) >= 3 and cached_data[:3] == b'ID3') or \
                             (len(cached_data) >= 2 and cached_data[:2] in [b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2']):
                            is_valid_cache = True
                            cache_format = 'mp3'
                            logger.debug(f"✅ MP3格式验证通过: size={file_size}, header={header_hex[:32]}...")

                        if is_valid_cache:
                            logger.info(f"✅ 使用缓存音频 ({cache_format}, {file_size} bytes): {text[:30]}...")

                            # 🔍 额外验证：检查Base64编码后的长度是否合理
                            expected_base64_length = (file_size + 2) * 4 // 3  # 近似Base64长度
                            logger.debug(f"🔍 缓存文件验证: 文件大小={file_size}, 预期Base64长度≈{expected_base64_length}")

                            # 记录数据库访问
                            try:
                                from models.tts_cache import TTSCache
                                cache_record = TTSCache.find_cache(text, voice_id, speed, sample_rate, cache_format)
                                if cache_record:
                                    TTSCache.update_access(cache_record.cache_id)
                            except Exception as db_e:
                                logger.debug(f"⚠️ 更新缓存访问记录失败: {str(db_e)}")

                            return cached_data
                        else:
                            # 🔥 改进：输出详细的错误信息
                            logger.warning(f"⚠️ 缓存文件格式不正确，删除旧缓存: {text[:30]}...")
                            logger.warning(f"   文件大小: {file_size} bytes")
                            logger.warning(f"   文件头: {header_hex}")
                            logger.warning(f"   缓存路径: {cache_path}")
                            os.remove(cache_path)

                            # 同时标记数据库记录为无效
                            try:
                                from models.tts_cache import TTSCache
                                cache_record = TTSCache.find_cache(text, voice_id, speed, sample_rate, codec or 'mp3')
                                if cache_record:
                                    TTSCache.deactivate_cache(cache_record.cache_id)
                            except Exception as db_e:
                                logger.debug(f"⚠️ 标记缓存记录无效失败: {str(db_e)}")
            
            # 调用TTS服务
            if self.tts_client:
                # 从统一配置文件获取默认voice_type
                from utils.config_loader import get_config as _get_config

                # 获取默认TTS语音类型
                default_voice_type = _get_config('TENCENT_TTS.VOICE_TYPE')
                if not default_voice_type:
                    default_voice_type = "7426720361753903141"  # 默认值

                # 尝试将voice_id转换为voice_type
                # 如果voice_id是6位数字（腾讯云格式），则使用它；否则使用默认值
                if voice_id and voice_id.isdigit() and len(voice_id) == 6:
                    tts_voice_type = voice_id
                else:
                    tts_voice_type = default_voice_type
                
                # 将speed从0.5-2.0范围映射到腾讯云的-2到6范围
                # 1.0 -> 0 (正常语速), 0.5 -> -2 (最慢), 2.0 -> 6 (最快)
                if speed <= 0.5:
                    tts_speed = -2
                elif speed >= 2.0:
                    tts_speed = 6
                else:
                    # 线性映射: 0.5-2.0 -> -2-6
                    tts_speed = int((speed - 0.5) / 1.5 * 8 - 2)
                    tts_speed = max(-2, min(6, tts_speed))  # 限制在[-2, 6]范围内
                
                # 获取音量配置，默认值为0
                tts_volume = get_config('TENCENT_TTS.VOLUME', 0)

                logger.debug(f"🎤 TTS转换: text={text[:30]}..., voice_type={tts_voice_type}, speed={speed}->{tts_speed}, volume={tts_volume}")

                pcm_data = self.tts_client.synthesize(
                    text=text,
                    voice_type=tts_voice_type,
                    sample_rate=sample_rate,
                    speed=tts_speed,
                    volume=tts_volume
                )
                
                # 根据配置的codec处理音频数据
                if pcm_data:
                    codec = get_config('TENCENT_TTS.CODEC', 'mp3').lower()
                    logger.debug(f"🎵 TTS合成完成: 格式={codec}, 大小={len(pcm_data)} bytes, 采样率={sample_rate}")

                    if codec == 'pcm':
                        # PCM格式：转换为WAV
                        logger.info("🔄 开始PCM转WAV...")
                        audio_data = self._pcm_to_wav(pcm_data, sample_rate=sample_rate)
                        logger.info(f"✅ PCM转WAV成功: {len(pcm_data)} bytes -> {len(audio_data)} bytes")
                        # 验证WAV文件头
                        if len(audio_data) >= 12 and audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                            logger.info(f"✅ WAV文件头验证通过: RIFF={audio_data[:4]}, WAVE={audio_data[8:12]}")
                        else:
                            logger.warning("⚠️ WAV文件头验证失败")
                    elif codec == 'mp3':
                        # MP3格式：直接使用原始PCM数据（腾讯云会返回MP3格式）
                        audio_data = pcm_data
                    else:
                        audio_data = self._pcm_to_wav(pcm_data, sample_rate=sample_rate)

                    # 保存到缓存（使用文件锁确保原子性）
                    if use_cache:
                        cache_path = self._get_cache_path(text, voice_id, speed)

                        # 确保缓存目录存在
                        cache_dir = os.path.dirname(cache_path)
                        os.makedirs(cache_dir, exist_ok=True)

                        # 使用文件锁确保原子性写入（仅在 Unix/Linux 上）
                        with open(cache_path, 'wb') as f:
                            # 获取独占锁
                            if fcntl:
                                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                            try:
                                f.write(audio_data)
                                f.flush()  # 确保数据写入磁盘
                                os.fsync(f.fileno())  # 强制同步到磁盘
                                logger.debug(f"✅ 缓存文件写入完成: {cache_path}, 大小: {len(audio_data)} bytes")
                            finally:
                                if fcntl:
                                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # 释放锁

                        # 同时写入数据库记录
                        try:
                            from models.tts_cache import TTSCache
                            TTSCache.add_cache(
                                text=text,
                                voice_id=voice_id,
                                speed=speed,
                                cache_path=cache_path,
                                file_size=len(audio_data),
                                sample_rate=sample_rate,
                                codec=codec
                            )
                        except Exception as db_e:
                            logger.warning(f"⚠️ 写入缓存数据库记录失败: {str(db_e)}")
                    
                    return audio_data
                else:
                    return None
            else:
                logger.warning("⚠️ TTS客户端未初始化，返回None")
                return None
                
        except Exception as e:
            logger.error(f"❌ TTS转换失败: {str(e)}")
            return None
    
    def text_to_speech_base64(
        self,
        text: str,
        voice_id: str = "7426720361753903141",
        speed: float = 1.0,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        文本转语音（返回Base64编码）
        
        Args:
            text: 要转换的文本
            voice_id: 语音ID
            speed: 语速
            
        Returns:
            str: Base64编码的音频数据
        """
        audio_data = self.text_to_speech(text, voice_id, speed, use_cache=use_cache)
        if audio_data:
            return base64.b64encode(audio_data).decode('utf-8')
        return None
    
    def batch_text_to_speech(
        self,
        texts: List[str],
        voice_id: str = "7426720361753903141",
        speed: float = 1.0
    ) -> List[Dict[str, any]]:
        """
        批量文本转语音
        
        Args:
            texts: 文本列表
            voice_id: 语音ID
            
        Returns:
            List[Dict]: 结果列表，每项包含 text, audio_base64, cache_path
        """
        results = []
        
        for text in texts:
            try:
                audio_data = self.text_to_speech(text, voice_id, speed)
                cache_path = self._get_cache_path(text, voice_id, speed)
                
                results.append({
                    'text': text,
                    'audio_base64': base64.b64encode(audio_data).decode('utf-8') if audio_data else None,
                    'cache_path': cache_path,
                    'success': audio_data is not None
                })
                
                logger.debug(f"✅ 批量TTS: {text[:20]}... 完成")
                
            except Exception as e:
                logger.error(f"❌ 批量TTS失败: {text[:20]}... - {str(e)}")
                results.append({
                    'text': text,
                    'audio_base64': None,
                    'cache_path': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def pregenerate_onboarding_audios(self) -> Dict[int, str]:
        """
        预生成新手引导的所有语音
        
        Returns:
            Dict[int, str]: {step_number: audio_base64}
        """
        # 从数据库获取引导问题
        from models.onboarding import OnboardingQuestion
        
        questions = OnboardingQuestion.get_all()
        results = {}
        
        for q in questions:
            try:
                audio_data = self.text_to_speech(q.question_text, use_cache=True)
                if audio_data:
                    results[q.step_number] = base64.b64encode(audio_data).decode('utf-8')
                    logger.info(f"✅ 预生成引导语音 Step {q.step_number}")
            except Exception as e:
                logger.error(f"❌ 预生成引导语音失败 Step {q.step_number}: {str(e)}")
        
        return results
    
    def clear_cache(self, older_than_days: int = 30) -> int:
        """
        清理过期缓存
        
        Args:
            older_than_days: 清理多少天前的缓存
            
        Returns:
            int: 清理的文件数量
        """
        import time
        
        count = 0
        current_time = time.time()
        cutoff_time = current_time - (older_than_days * 24 * 3600)
        
        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                
                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    
                    if file_mtime < cutoff_time:
                        os.remove(filepath)
                        count += 1
            
            logger.info(f"✅ 清理TTS缓存: {count}个文件")
            return count
            
        except Exception as e:
            logger.error(f"❌ 清理缓存失败: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计
        """
        try:
            files = os.listdir(self.cache_dir)
            total_files = len(files)
            
            total_size = 0
            for filename in files:
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            logger.error(f"❌ 获取缓存统计失败: {str(e)}")
            return {'error': str(e)}


# 全局单例
_tts_service_instance = None

def get_tts_service() -> TTSService:
    """获取TTS服务单例"""
    global _tts_service_instance
    if _tts_service_instance is None:
        _tts_service_instance = TTSService()
    return _tts_service_instance

