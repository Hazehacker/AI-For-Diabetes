"""
新手引导服务
~~~~~~~~~~~

新手引导流程管理服务，包括：
- 引导流程控制
- 问答处理
- 标签提取
- TTS集成

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, Dict, List, Any
from models.onboarding import OnboardingStatus, OnboardingAnswer, OnboardingQuestion
from models.tag import TagValue
from utils.logger import get_logger
from utils.decorators import log_execution_time
from .tts_service import get_tts_service
from .tag_service import TagService

logger = get_logger(__name__)


class OnboardingService:
    """
    新手引导服务类
    
    管理用户的新手引导流程
    """
    
    def __init__(self):
        """初始化服务"""
        self.tts_service = get_tts_service()
        self.tag_service = TagService()
    
    def start_onboarding(self, user_id: int) -> Dict[str, Any]:
        """
        开始新手引导
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 第一个问题的信息
        """
        try:
            # 检查是否已存在引导状态
            status = OnboardingStatus.get_by_user(user_id)
            
            if status:
                if status.is_completed:
                    return {
                        'success': False,
                        'message': '您已经完成新手引导了',
                        'is_completed': True
                    }
                else:
                    # 继续未完成的引导
                    return self.get_current_question(user_id)
            
            # 创建新的引导状态
            status = OnboardingStatus.create(user_id)
            if not status:
                return {'success': False, 'message': '创建引导状态失败'}
            
            # 获取第一个问题
            return self.get_current_question(user_id)
            
        except Exception as e:
            logger.error(f"❌ 开始引导失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def get_current_question(self, user_id: int) -> Dict[str, Any]:
        """
        获取当前问题
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 问题信息
        """
        try:
            # 获取引导状态
            status = OnboardingStatus.get_by_user(user_id)
            if not status:
                return {'success': False, 'message': '引导状态不存在'}
            
            if status.is_completed:
                return {
                    'success': True,
                    'is_completed': True,
                    'message': '引导已完成'
                }
            
            # 获取当前步骤的问题
            question = OnboardingQuestion.get_by_step(status.current_step)
            if not question:
                return {'success': False, 'message': '问题不存在'}
            
            # 生成TTS音频
            audio_base64 = None
            if question.question_text:
                audio_base64 = self.tts_service.text_to_speech_base64(
                    question.question_text
                )
            
            return {
                'success': True,
                'step_number': question.step_number,
                'total_steps': status.total_steps,
                'progress': round((question.step_number / status.total_steps) * 100, 1),
                'question_text': question.question_text,
                'is_required': question.is_required,
                'skip_allowed': question.skip_allowed,
                'audio_base64': audio_base64,
                'is_completed': False
            }
            
        except Exception as e:
            logger.error(f"❌ 获取当前问题失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @log_execution_time
    def submit_answer(
        self,
        user_id: int,
        answer_text: str,
        is_skipped: bool = False
    ) -> Dict[str, Any]:
        """
        提交用户回答
        
        Args:
            user_id: 用户ID
            answer_text: 回答内容
            is_skipped: 是否跳过
            
        Returns:
            Dict: 处理结果和下一个问题
        """
        try:
            # 获取当前状态
            status = OnboardingStatus.get_by_user(user_id)
            if not status or status.is_completed:
                return {'success': False, 'message': '引导状态异常'}
            
            # 获取当前问题
            question = OnboardingQuestion.get_by_step(status.current_step)
            if not question:
                return {'success': False, 'message': '问题不存在'}
            
            # 提取标签
            extracted_tags = {}
            if not is_skipped and answer_text:
                extracted_tags = self._extract_tags_from_answer(
                    answer_text,
                    question.tag_keys
                )
                
                # 保存标签到数据库
                for tag_key, tag_value in extracted_tags.items():
                    TagValue.set_value(
                        user_id=user_id,
                        tag_key=tag_key,
                        tag_value=tag_value,
                        source='onboarding',
                        confidence_score=0.8
                    )
            
            # 保存回答记录
            OnboardingAnswer.save_answer(
                user_id=user_id,
                step_number=status.current_step,
                question_text=question.question_text,
                user_answer=answer_text if not is_skipped else None,
                extracted_tags=extracted_tags,
                is_skipped=is_skipped,
                confidence_score=0.8 if extracted_tags else None
            )
            
            # 更新跳过计数
            if is_skipped:
                OnboardingStatus.increment_skip_count(user_id)
            
            # 检查是否完成
            if status.current_step >= status.total_steps:
                # 标记完成
                OnboardingStatus.mark_completed(user_id)
                
                # 同步标签到Coze
                self._sync_tags_to_coze(user_id)
                
                return {
                    'success': True,
                    'is_completed': True,
                    'message': '恭喜您完成新手引导！',
                    'collected_tags': extracted_tags
                }
            else:
                # 进入下一步
                next_step = status.current_step + 1
                OnboardingStatus.update_step(user_id, next_step)
                
                # 获取下一个问题
                next_question_data = self.get_current_question(user_id)
                
                return {
                    'success': True,
                    'is_completed': False,
                    'extracted_tags': extracted_tags,
                    'next_question': next_question_data
                }
                
        except Exception as e:
            logger.error(f"❌ 提交回答失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _extract_tags_from_answer(
        self,
        answer: str,
        tag_keys: List[str]
    ) -> Dict[str, str]:
        """
        从回答中提取标签（简化版，使用规则）
        
        Args:
            answer: 用户回答
            tag_keys: 需要提取的标签键
            
        Returns:
            Dict: {tag_key: tag_value}
        """
        extracted = {}
        answer_lower = answer.lower()
        
        # 糖尿病类型识别
        if 'diabetes_type' in tag_keys:
            if '1型' in answer or '一型' in answer:
                extracted['diabetes_type'] = '1型糖尿病'
            elif '2型' in answer or '二型' in answer:
                extracted['diabetes_type'] = '2型糖尿病'
            elif '妊娠' in answer:
                extracted['diabetes_type'] = '妊娠期糖尿病'
        
        # 用药情况
        if 'current_medication' in tag_keys:
            medications = []
            if '二甲双胍' in answer:
                medications.append('二甲双胍')
            if '胰岛素' in answer:
                medications.append('胰岛素')
            if medications:
                extracted['current_medication'] = '、'.join(medications)
            elif '没有' in answer or '无' in answer:
                extracted['current_medication'] = '无'
        
        # 运动频率
        if 'exercise_frequency' in tag_keys:
            if '每天' in answer or '天天' in answer:
                extracted['exercise_frequency'] = '每天'
            elif '每周' in answer or '一周' in answer:
                # 提取数字
                import re
                numbers = re.findall(r'\d+', answer)
                if numbers:
                    extracted['exercise_frequency'] = f'每周{numbers[0]}次'
            elif '不' in answer or '没' in answer:
                extracted['exercise_frequency'] = '不运动'
        
        # 饮食习惯
        if 'diet_habits' in tag_keys:
            if answer:
                extracted['diet_habits'] = answer[:100]  # 限制长度
        
        # 血糖控制情况
        if 'blood_glucose_control' in tag_keys:
            if '好' in answer or '稳定' in answer:
                extracted['blood_glucose_control'] = '良好'
            elif '一般' in answer or '还行' in answer:
                extracted['blood_glucose_control'] = '一般'
            elif '不' in answer or '差' in answer:
                extracted['blood_glucose_control'] = '较差'
        
        return extracted
    
    def _sync_tags_to_coze(self, user_id: int):
        """
        同步标签到Coze
        
        Args:
            user_id: 用户ID
        """
        try:
            # 使用标签服务同步
            result = self.tag_service.sync_user_tags_to_coze(user_id)
            if result:
                logger.info(f"✅ 用户 {user_id} 标签已同步到Coze")
            else:
                logger.warning(f"⚠️ 用户 {user_id} 标签同步失败")
        except Exception as e:
            logger.error(f"❌ 同步标签到Coze失败: {str(e)}")
    
    def get_onboarding_progress(self, user_id: int) -> Dict[str, Any]:
        """
        获取引导进度
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 进度信息
        """
        try:
            status = OnboardingStatus.get_by_user(user_id)
            if not status:
                return {
                    'has_started': False,
                    'is_completed': False,
                    'message': '尚未开始引导'
                }
            
            answers = OnboardingAnswer.get_user_answers(user_id)
            
            return {
                'has_started': True,
                'is_completed': status.is_completed,
                'current_step': status.current_step,
                'total_steps': status.total_steps,
                'progress_percentage': round((status.current_step / status.total_steps) * 100, 1),
                'skip_count': status.skip_count,
                'answered_questions': len(answers),
                'started_at': str(status.started_at) if hasattr(status, 'started_at') else None,
                'completed_at': str(status.completed_at) if hasattr(status, 'completed_at') and status.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"❌ 获取引导进度失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def skip_question(self, user_id: int) -> Dict[str, Any]:
        """
        跳过当前问题
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 下一个问题信息
        """
        return self.submit_answer(user_id, "", is_skipped=True)
    
    def reset_onboarding(self, user_id: int) -> Dict[str, Any]:
        """
        重置引导（重新开始）
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 操作结果
        """
        try:
            # 删除现有状态（需要在数据库层实现）
            # 这里简化处理：直接更新为第一步
            OnboardingStatus.update_step(user_id, 1)
            
            logger.info(f"✅ 用户 {user_id} 引导已重置")
            return self.get_current_question(user_id)
            
        except Exception as e:
            logger.error(f"❌ 重置引导失败: {str(e)}")
            return {'success': False, 'message': str(e)}


# 全局单例
_onboarding_service_instance = None

def get_onboarding_service() -> OnboardingService:
    """获取新手引导服务单例"""
    global _onboarding_service_instance
    if _onboarding_service_instance is None:
        _onboarding_service_instance = OnboardingService()
    return _onboarding_service_instance

