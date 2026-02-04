"""
TTS路由
~~~~~~

文本转语音的API端点：
- 文本转语音
- 批量转语音
- 预生成引导语音
- 缓存管理

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify, Response, stream_with_context
from . import tts_bp
from utils.jwt_helper import no_auth_required as token_required
from services.tts_service import get_tts_service
from utils.logger import get_logger
import json
import re
from typing import List

logger = get_logger(__name__)

# 获取服务实例
tts_service = get_tts_service()


@tts_bp.route('/tts/stream', methods=['POST'], endpoint='stream_text_to_speech')
@token_required
def stream_text_to_speech(user_id):
    """
    流式文本转语音（分句处理）

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "text": "要转换的文本，可以很长。会自动按句子分割。",
            "voice_id": "7426720361753903141",
            "speed": 1.0,
            "use_cache": true
        }

    Returns:
        SSE流: 逐句返回音频数据
    """
    try:
        data = request.get_json()

        text = data.get('text')
        if not text:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '文本不能为空'
            }), 400

        voice_id = data.get('voice_id', '7426720361753903141')
        speed = float(data.get('speed', 1.0))
        use_cache = data.get('use_cache', True)
        
        def generate():
            try:
                logger.info(f"🎤 开始流式TTS转换，文本长度: {len(text)}")
                
                # 按句子分割文本（改进的分割逻辑）
                # 首先尝试按标准句子结束符分割
                sentences_list = []
                pattern = r'([。！？；]+|[\n]{2,})'  # 句号、问号、感叹号、分号，或连续换行
                parts = re.split(pattern, text)
                
                # 重新组合：文本片段 + 标点符号
                current_sentence = ""
                for i, part in enumerate(parts):
                    part = part.strip() if part else ""
                    if not part:
                        continue
                    
                    # 如果是标点符号（句号、问号、感叹号、分号）或连续换行
                    if re.match(r'^[。！？；]+$', part) or re.match(r'^[\n]{2,}$', part):
                        current_sentence += part
                        if current_sentence.strip():
                            sentences_list.append(current_sentence.strip())
                            current_sentence = ""
                    else:
                        # 是文本内容
                        current_sentence += part
                
                # 添加最后一段
                if current_sentence.strip():
                    sentences_list.append(current_sentence.strip())

                # 如果没有分割出句子（没有标准句子结束符），尝试更智能的分割
                if len(sentences_list) <= 1:
                    logger.info("🔄 没有找到标准句子结束符，尝试智能分割...")

                    # 方法1：按列表项分割（- 开头的行）
                    if '\n- ' in text or text.startswith('- '):
                        logger.info("📝 检测到列表格式，按列表项分割")
                        # 按列表项分割
                        list_items = []
                        lines = text.split('\n')
                        current_item = ""

                        for line in lines:
                            line = line.strip()
                            if line.startswith('- ') or line.startswith('✅ ') or line.startswith('❌ ') or line.startswith('⚠️ ') or line.startswith('🍋 '):
                                # 保存之前的项
                                if current_item.strip():
                                    list_items.append(current_item.strip())
                                # 开始新项
                                current_item = line
                            elif line.strip():
                                # 继续当前项
                                if current_item:
                                    current_item += '\n' + line
                                else:
                                    current_item = line

                        # 添加最后一个项
                        if current_item.strip():
                            list_items.append(current_item.strip())

                        if len(list_items) > 1:
                            sentences_list = list_items
                            logger.info(f"✅ 按列表项分割成功，得到 {len(sentences_list)} 项")
                
                    # 方法2：按段落分隔符（**）分割
                    if len(sentences_list) <= 1 and '**' in text:
                        logger.info("📝 检测到段落格式，按**分割")
                        # 查找所有 **text** 模式
                        bold_pattern = r'\*\*.*?\*\*'
                        bold_parts = re.findall(bold_pattern, text)

                        if bold_parts:
                            para_sentences = []
                            remaining = text

                            for bold in bold_parts:
                                if bold in remaining:
                                    parts = remaining.split(bold, 1)
                                    if parts[0].strip():
                                        para_sentences.append(parts[0].strip())
                                    para_sentences.append(bold)
                                    remaining = parts[1] if len(parts) > 1 else ''

                            if remaining.strip():
                                para_sentences.append(remaining.strip())

                            # 合并短句子
                            merged = []
                            current = ""
                            for part in para_sentences:
                                if len(current + part) <= 300:  # 稍微放宽限制
                                    current += (" " if current else "") + part
                                else:
                                    if current:
                                        merged.append(current)
                                    current = part
                            if current:
                                merged.append(current)

                            if len(merged) > 1:
                                sentences_list = merged
                                logger.info(f"✅ 按段落分割成功，得到 {len(sentences_list)} 段")

                    # 方法3：按单个换行符分割（最后的fallback）
                    if len(sentences_list) <= 1:
                        logger.info("📝 使用换行符分割作为最后手段")
                        alt_sentences = [s.strip() for s in re.split(r'\n+', text) if s.strip()]
                        if len(alt_sentences) > len(sentences_list):
                            sentences_list = alt_sentences
                            logger.info(f"✅ 按换行符分割成功，得到 {len(alt_sentences)} 句")

                print(f"DEBUG: 句子分割完成，sentences_list长度: {len(sentences_list)}")
                # 对过长的句子进行强制分割
                print(f"DEBUG: 开始强制分割，sentences_list长度: {len(sentences_list)}")
                MAX_CHUNK_LENGTH = 200  # 单个句子最大长度
                processed_sentences = []
                logger.info(f"🔍 开始检查句子长度，共 {len(sentences_list)} 句，最大长度限制: {MAX_CHUNK_LENGTH}")
                logger.info(f"🔍 sentences_list内容: {[len(s) for s in sentences_list]}")
                print(f"DEBUG: MAX_CHUNK_LENGTH = {MAX_CHUNK_LENGTH}")

                for i, sent in enumerate(sentences_list):
                    logger.info(f"   句子 {i+1} 长度: {len(sent)} 字符, MAX_CHUNK_LENGTH: {MAX_CHUNK_LENGTH}")
                    if len(sent) <= MAX_CHUNK_LENGTH:
                        processed_sentences.append(sent)
                        logger.info(f"   句子 {i+1} 长度正常，保持不变")
                    else:
                        logger.info(f"   句子 {i+1} 超过长度限制，开始强制分割")
                        logger.warning(f"⚠️ 句子 {i+1} 过长 ({len(sent)} 字符)，强制分割: {sent[:50]}...")
                        long_text = sent
                        sub_sentences = []

                        # 方法1：按列表项分割（- 开头的行）
                        has_list_markers = any(marker in long_text for marker in ['\n- ', '- ', '\n✅ ', '✅ ', '\n❌ ', '❌ ', '\n⚠️ ', '⚠️ ', '\n🍋 ', '🍋 '])
                        logger.info(f"   检查列表标记: {has_list_markers}")

                        if has_list_markers:
                            logger.info("🔄 强制按列表项分割长句子")
                            lines = long_text.split('\n')
                            current_item = ""

                            for line in lines:
                                line = line.strip()
                                if any(line.startswith(marker.strip()) for marker in ['- ', '✅ ', '❌ ', '⚠️ ', '🍋 ']):
                                    # 保存之前的项
                                    if current_item.strip():
                                        sub_sentences.append(current_item.strip())
                                    # 开始新项
                                    current_item = line
                                elif line.strip():
                                    # 继续当前项
                                    if current_item:
                                        current_item += '\n' + line
                                    else:
                                        current_item = line

                            # 添加最后一个项
                            if current_item.strip():
                                sub_sentences.append(current_item.strip())

                            if len(sub_sentences) > 1:
                                logger.info(f"✅ 强制按列表项分割成功，得到 {len(sub_sentences)} 项")
                            else:
                                logger.warning(f"❌ 列表项分割失败，只得到 {len(sub_sentences)} 项")

                        # 方法2：按换行符分割
                        if not sub_sentences:
                            lines = [line.strip() for line in long_text.split('\n') if line.strip()]
                            logger.info(f"   按换行符分割检查: {len(lines)} 行")
                            if len(lines) > 1:
                                sub_sentences = lines
                                logger.info(f"✅ 强制按换行符分割成功，得到 {len(sub_sentences)} 句")

                        # 方法3：按标点符号分割
                        if not sub_sentences:
                            split_chars = ['。', '！', '？', '；']
                            for char in split_chars:
                                if char in long_text:
                                    parts = long_text.split(char)
                                    candidates = []
                                    for j, part in enumerate(parts):
                                        part = part.strip()
                                        if part:
                                            if j < len(parts) - 1:  # 不是最后一部分
                                                candidates.append(part + char)
                                            else:  # 最后一部分
                                                candidates.append(part)

                                    if len(candidates) > 1:
                                        sub_sentences = candidates
                                        logger.info(f"✅ 强制按'{char}'分割成功，得到 {len(sub_sentences)} 句")
                                        break

                        # 方法4：硬分割
                        if not sub_sentences:
                            logger.warning("⚠️ 所有分割方法都失败了，使用硬分割")
                            chunk_size = 150  # 稍微小一点
                            start = 0
                            while start < len(long_text):
                                end = start + chunk_size
                                if end >= len(long_text):
                                    chunk = long_text[start:].strip()
                                    if chunk:
                                        sub_sentences.append(chunk)
                                    break

                                # 尽量在合适位置断开
                                best_end = end
                                for k in range(min(30, len(long_text) - start)):
                                    pos = end - k
                                    if pos > start and long_text[pos] in '。！？；\n ':
                                        best_end = pos + 1
                                        break

                                chunk = long_text[start:best_end].strip()
                                if chunk:
                                    sub_sentences.append(chunk)
                                start = best_end

                            logger.info(f"✅ 硬分割完成，得到 {len(sub_sentences)} 句")

                        logger.info(f"   句子 {i+1} 被分割为 {len(sub_sentences)} 个子句")
                        processed_sentences.extend(sub_sentences)

                # 修复：将processed_sentences赋值给sentences_list
                sentences_list = processed_sentences
                logger.info(f"📊 最终句子数: {len(sentences_list)} 句（包含强制分割后的子句）")
                
                logger.info(f"📊 文本分割完成，共 {len(sentences_list)} 句")
                # 打印所有句子用于调试
                for idx, sent in enumerate(sentences_list, 1):
                    logger.info(f"   句子 {idx}: {sent[:80]}{'...' if len(sent) > 80 else ''}")
                
                # 定义函数：检查文本是否包含有效的中文字符或英文字母
                def has_valid_text(text: str) -> bool:
                    """检查文本是否包含有效字符（中文、英文、数字）"""
                    if not text or not text.strip():
                        return False
                    # 匹配中文字符、英文字母、数字
                    pattern = r'[\u4e00-\u9fa5a-zA-Z0-9]'
                    return bool(re.search(pattern, text))

                # 定义函数：智能拆分长句子
                def split_long_sentence(text: str, max_length: int) -> List[str]:
                    """智能拆分过长的句子，避免破坏语义"""
                    if len(text) <= max_length:
                        return [text]

                    logger.info(f"📝 开始拆分长句子 ({len(text)} 字符)...")

                    # 方法1：按markdown列表项（- ）和段落（**）优先拆分
                    if '\n- ' in text:
                        # 按列表项拆分
                        parts = text.split('\n- ')
                        result = []
                        for i, part in enumerate(parts):
                            if i == 0:
                                result.append(part.strip())
                            else:
                                result.append(('- ' + part).strip())
                        # 过滤空内容
                        result = [r for r in result if r.strip()]
                        if len(result) > 1:
                            logger.info(f"✅ 按列表项拆分为 {len(result)} 部分")
                            return result

                    # 方法2：按段落分隔符（**）拆分
                    if '**' in text:
                        # 查找所有 **text** 模式
                        bold_parts = re.findall(r'\*\*.*?\*\*', text)
                        if bold_parts:
                            result = []
                            remaining = text
                            for bold in bold_parts:
                                if bold in remaining:
                                    parts = remaining.split(bold, 1)
                                    if parts[0].strip():
                                        result.append(parts[0].strip())
                                    result.append(bold)
                                    remaining = parts[1] if len(parts) > 1 else ''
                            if remaining.strip():
                                result.append(remaining.strip())

                            # 合并短句子
                            merged = []
                            current = ""
                            for part in result:
                                if len(current + part) <= max_length:
                                    current += (" " if current else "") + part
                                else:
                                    if current:
                                        merged.append(current)
                                    current = part
                            if current:
                                merged.append(current)

                            if len(merged) > 1:
                                logger.info(f"✅ 按段落拆分为 {len(merged)} 部分")
                                return merged

                    # 方法3：按换行符和标点符号拆分
                    split_chars = ['\n\n', '。\n', '！\n', '？\n', '；\n', '\n', '。', '！', '？', '；']
                    for char in split_chars:
                        if char in text:
                            parts = text.split(char)
                            result = []
                            current = ""
                            for part in parts:
                                candidate = current + (char if current else "") + part
                                if len(candidate) <= max_length:
                                    current = candidate
                                else:
                                    if current:
                                        result.append(current)
                                    current = part
                            if current:
                                result.append(current)

                            result = [r.strip() for r in result if r.strip()]
                            if len(result) > 1:
                                logger.info(f"✅ 按'{char}'拆分为 {len(result)} 部分")
                                return result

                    # 方法4：按长度硬拆分（最后手段）
                    logger.warning(f"⚠️ 所有智能拆分失败，按长度硬拆分: {len(text)} 字符")
                    result = []
                    start = 0
                    while start < len(text):
                        end = min(start + max_length, len(text))
                        # 尽量在标点处断开
                        if end < len(text):
                            for i in range(min(20, end - start)):
                                pos = end - i
                                if text[pos] in '。！？；.!?\n ':
                                    end = pos + 1
                                    break

                        chunk = text[start:end].strip()
                        if chunk:
                            result.append(chunk)
                        start = end

                    logger.info(f"✅ 硬拆分为 {len(result)} 部分")
                    return result if result else [text]
                
                # 过滤掉无效的句子（只包含标点符号、表情符号等）
                valid_sentences = []
                for sent in sentences_list:
                    if has_valid_text(sent):
                        valid_sentences.append(sent)
                    else:
                        logger.debug(f"⚠️ 跳过无效句子（只包含标点/表情）: {sent[:50]}...")
                
                logger.info(f"📊 过滤后有效句子: {len(valid_sentences)}/{len(sentences_list)} 句")

                # 对过长的句子进行进一步拆分（腾讯云TTS有长度限制）
                MAX_SENTENCE_LENGTH = 200  # 腾讯云TTS实际限制大约200字符以内
                final_sentences = []

                for sent in valid_sentences:
                    if len(sent) <= MAX_SENTENCE_LENGTH:
                        final_sentences.append(sent)
                        logger.debug(f"✅ 句子长度正常: {len(sent)} 字符")
                    else:
                        logger.warning(f"⚠️ 句子过长 ({len(sent)} 字符)，进行进一步拆分: {sent[:80]}...")
                        # 对长句子进行智能拆分
                        sub_sentences = split_long_sentence(sent, MAX_SENTENCE_LENGTH)
                        final_sentences.extend(sub_sentences)
                        logger.info(f"📝 长句子拆分为 {len(sub_sentences)} 个子句")

                logger.info(f"📊 最终句子数: {len(final_sentences)} 句（包含拆分后的子句）")

                # 打印最终句子列表
                for idx, sent in enumerate(final_sentences, 1):
                    logger.info(f"   最终句子 {idx}: {sent[:60]}{'...' if len(sent) > 60 else ''}")

                sentence_count = 0
                success_count = 0
                
                # 逐句处理
                for idx, sentence_text in enumerate(final_sentences):
                    if not sentence_text.strip():
                        logger.warning(f"⚠️ 跳过空句子 {idx + 1}")
                        continue
                    
                    # 再次检查文本有效性
                    if not has_valid_text(sentence_text):
                        logger.warning(f"⚠️ 跳过无效文本（无有效字符）: {sentence_text[:50]}...")
                        continue
                    
                    sentence_count += 1
                    total_sentences = len(final_sentences)
                    logger.debug(f"📝 开始处理第 {sentence_count}/{total_sentences} 句 (长度: {len(sentence_text)}): {sentence_text[:80]}...")
                        
                    try:
                        # 调用TTS服务进行转换
                        logger.info(f"🎬 开始处理句子 {sentence_count}/{len(final_sentences)}: {sentence_text[:50]}...")
                        audio_base64 = tts_service.text_to_speech_base64(
                            text=sentence_text,
                            voice_id=voice_id,
                            speed=speed,
                            use_cache=use_cache
                        )
                        
                        if audio_base64:
                            success_count += 1
                            logger.info(f"✅ 句子 {sentence_count} 转换成功，准备发送音频数据（{len(audio_base64)} bytes base64）")
                            # 发送音频数据
                            yield f"event: audio\n"
                            yield f"data: {json.dumps({'audio': audio_base64, 'sentence': sentence_text, 'index': sentence_count, 'total': total_sentences}, ensure_ascii=False)}\n\n"
                            logger.info(f"📤 句子 {sentence_count} 音频数据已发送")
                        else:
                            logger.warning(f"⚠️ 句子 {sentence_count} 转换失败（返回None）")
                            # 即使转换失败，也发送一个错误事件，让前端知道这一句处理了
                            yield f"event: audio_error\n"
                            yield f"data: {json.dumps({'sentence': sentence_text, 'index': sentence_count, 'total': total_sentences, 'message': 'TTS转换失败'}, ensure_ascii=False)}\n\n"
                    except Exception as e:
                        logger.error(f"❌ 句子 {sentence_count} 处理异常: {str(e)}", exc_info=True)
                        # 发送错误事件，但继续处理下一句
                        yield f"event: audio_error\n"
                        yield f"data: {json.dumps({'sentence': sentence_text, 'index': sentence_count, 'total': total_sentences, 'message': str(e)}, ensure_ascii=False)}\n\n"
                        logger.info(f"🔄 继续处理下一句...")
                                    
                
                # 完成事件
                yield f"event: completed\n"
                yield f"data: {json.dumps({'message': f'TTS转换完成，共处理 {sentence_count} 句，成功 {success_count} 句', 'total': sentence_count, 'success': success_count}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"❌ 流式TTS失败: {str(e)}", exc_info=True)
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
        logger.error(f"❌ 流式TTS初始化失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/synthesize', methods=['POST'], endpoint='text_to_speech')
@token_required
def text_to_speech(user_id):
    """
    文本转语音（一次性返回）
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "text": "要转换的文本",
            "voice_id": "7426720361753903141",
            "speed": 1.0,
            "use_cache": true
        }
    
    Returns:
        JSON: {
            "success": true,
            "audio_base64": "base64编码的音频数据"
        }
    """
    try:
        data = request.get_json()
        
        text = data.get('text')
        if not text:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '文本不能为空'
            }), 400
        
        voice_id = data.get('voice_id', '7426720361753903141')
        speed = float(data.get('speed', 1.0))
        use_cache = data.get('use_cache', True)
        
        # 调用TTS服务
        audio_base64 = tts_service.text_to_speech_base64(
            text=text,
            voice_id=voice_id,
            speed=speed,
            use_cache=use_cache
        )
        
        if audio_base64:
            return jsonify({
                'code': 200,
                'data': {
                    'audio_base64': audio_base64,
                    'text': text
                },
                'success': True
            }), 200
        else:
            return jsonify({
                'code': 500,
                'data': {},
                'success': False,
                'message': 'TTS转换失败'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ TTS转换失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/batch', methods=['POST'], endpoint='batch_text_to_speech')
@token_required
def batch_text_to_speech(user_id):
    """
    批量文本转语音
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "texts": ["文本1", "文本2", ...],
            "voice_id": "7426720361753903141"
        }
    
    Returns:
        JSON: {
            "success": true,
            "results": [
                {"text": "...", "audio_base64": "...", "success": true},
                ...
            ]
        }
    """
    try:
        data = request.get_json()
        
        texts = data.get('texts', [])
        if not texts or not isinstance(texts, list):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '文本列表无效'
            }), 400
        
        voice_id = data.get('voice_id', '7426720361753903141')
        speed = float(data.get('speed', 1.0))

        # 批量转换
        results = tts_service.batch_text_to_speech(texts, voice_id, speed)
        
        return jsonify({
            'code': 200,
            'data': {
                'total': len(results),
                'results': results
            },
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 批量TTS失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/pregenerate-onboarding', methods=['POST'], endpoint='pregenerate_onboarding_audios')
@token_required
def pregenerate_onboarding_audios(user_id):
    """
    预生成新手引导的所有语音
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: {
            "success": true,
            "audios": {
                "1": "base64音频1",
                "2": "base64音频2",
                ...
            }
        }
    """
    try:
        results = tts_service.pregenerate_onboarding_audios()
        
        return jsonify({
            'code': 200,
            'data': {
                'total_steps': len(results),
                'audios': results
            },
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 预生成引导语音失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/cache/stats', methods=['GET'], endpoint='get_cache_stats')
@token_required
def get_cache_stats(user_id):
    """
    获取TTS缓存统计
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: 缓存统计信息
    """
    try:
        stats = tts_service.get_cache_stats()
        return jsonify({
            'code': 200,
            'data': {'stats': stats},
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取缓存统计失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/cache/clear', methods=['POST'], endpoint='clear_cache')
@token_required
def clear_cache(user_id):
    """
    清理TTS缓存

    Headers:
        Authorization: Bearer <token>

    Body:
        {
            "older_than_days": 30
        }

    Returns:
        JSON: 清理结果
    """
    try:
        data = request.get_json() or {}
        older_than_days = data.get('older_than_days', 30)

        # 清理文件系统缓存
        file_count = tts_service.clear_cache(older_than_days)

        # 清理数据库记录
        try:
            from models.tts_cache import TTSCache
            db_count = TTSCache.cleanup_expired(older_than_days)
        except Exception as db_e:
            logger.warning(f"⚠️ 清理数据库缓存记录失败: {str(db_e)}")
            db_count = 0

        return jsonify({
            'code': 200,
            'data': {
                'cleared_files': file_count,
                'cleared_db_records': db_count,
                'message': f'已清理 {file_count} 个缓存文件和 {db_count} 条数据库记录'
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 清理缓存失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/cache/search', methods=['GET'], endpoint='search_cache')
@token_required
def search_cache(user_id):
    """
    搜索TTS缓存记录

    Headers:
        Authorization: Bearer <token>

    Query Parameters:
        text: 搜索文本（可选）
        voice_id: 语音ID（可选）
        speed: 语速（可选）
        limit: 返回结果数量限制（默认10）

    Returns:
        JSON: 缓存记录列表
    """
    try:
        from models.tts_cache import TTSCache

        text = request.args.get('text')
        voice_id = request.args.get('voice_id')
        speed_str = request.args.get('speed')
        limit = int(request.args.get('limit', 10))

        speed = float(speed_str) if speed_str else None

        results = []

        if text:
            # 搜索相似文本
            cache_records = TTSCache.search_similar_text(text, limit)
            results = [record.to_dict() for record in cache_records]
        else:
            # 构建查询条件
            conditions = []
            params = []

            if voice_id:
                conditions.append("voice_id = %s")
                params.append(voice_id)

            if speed is not None:
                conditions.append("speed = %s")
                params.append(speed)

            if conditions:
                sql = f"""
                    SELECT * FROM tts_cache
                    WHERE {' AND '.join(conditions)} AND is_active = TRUE
                    ORDER BY last_accessed DESC
                    LIMIT %s
                """
                params.append(limit)

                from utils.database import execute_query
                rows = execute_query(sql, tuple(params))
                results = [TTSCache(**row).to_dict() for row in rows]
            else:
                # 获取最近的缓存记录
                sql = """
                    SELECT * FROM tts_cache
                    WHERE is_active = TRUE
                    ORDER BY last_accessed DESC
                    LIMIT %s
                """
                from utils.database import execute_query
                rows = execute_query(sql, (limit,))
                results = [TTSCache(**row).to_dict() for row in rows]

        return jsonify({
            'code': 200,
            'data': {
                'total': len(results),
                'results': results
            },
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 搜索缓存失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@tts_bp.route('/tts/cache/db-stats', methods=['GET'], endpoint='get_db_cache_stats')
@token_required
def get_db_cache_stats(user_id):
    """
    获取数据库缓存统计

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON: 数据库缓存统计信息
    """
    try:
        from models.tts_cache import TTSCache

        db_stats = TTSCache.get_cache_stats()

        return jsonify({
            'code': 200,
            'data': {'db_stats': db_stats},
            'success': True
        }), 200

    except Exception as e:
        logger.error(f"❌ 获取数据库缓存统计失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

