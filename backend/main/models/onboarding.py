"""
新手引导模型
~~~~~~~~~~~

新手引导流程的数据模型，包括：
- OnboardingStatus: 引导状态
- OnboardingAnswer: 用户回答
- OnboardingQuestion: 问题配置

作者: 智糖团队
日期: 2025-01-15
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from utils.database import execute_query, execute_update, get_db_connection, DatabaseTransaction
from utils.logger import get_logger

logger = get_logger(__name__)


class OnboardingStatus:
    """
    新手引导状态模型
    
    对应表: user_onboarding_status
    """
    
    def __init__(self, status_id: int = None, user_id: int = None,
                 is_completed: bool = False, current_step: int = 1,
                 total_steps: int = 6, skip_count: int = 0,
                 collected_tags: Dict = None, **kwargs):
        self.status_id = status_id
        self.user_id = user_id
        self.is_completed = is_completed
        self.current_step = current_step
        self.total_steps = total_steps
        self.skip_count = skip_count
        self.collected_tags = collected_tags or {}
    
    @staticmethod
    def get_by_user(user_id: int) -> Optional['OnboardingStatus']:
        """
        获取用户的引导状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            OnboardingStatus: 引导状态对象，不存在返回None
        """
        sql = "SELECT * FROM user_onboarding_status WHERE user_id = %s"
        row = execute_query(sql, (user_id,), fetch_one=True)
        
        if row:
            # 解析JSON字段
            if row.get('collected_tags'):
                row['collected_tags'] = json.loads(row['collected_tags'])
            return OnboardingStatus(**row)
        return None
    
    @staticmethod
    def create(user_id: int) -> 'OnboardingStatus':
        """
        创建新的引导状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            OnboardingStatus: 创建的状态对象
        """
        try:
            sql = """
                INSERT INTO user_onboarding_status (user_id, current_step, total_steps)
                VALUES (%s, 1, 6)
            """
            execute_update(sql, (user_id,))
            
            logger.info(f"✅ 用户 {user_id} 创建引导状态成功")
            return OnboardingStatus.get_by_user(user_id)
            
        except Exception as e:
            logger.error(f"❌ 创建引导状态失败: {str(e)}")
            return None
    
    @staticmethod
    def update_step(user_id: int, step: int) -> bool:
        """
        更新用户当前步骤
        
        Args:
            user_id: 用户ID
            step: 新步骤号
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                UPDATE user_onboarding_status
                SET current_step = %s,
                    progress_percentage = (%s / total_steps) * 100
                WHERE user_id = %s
            """
            execute_update(sql, (step, step, user_id))
            return True
        except Exception as e:
            logger.error(f"❌ 更新引导步骤失败: {str(e)}")
            return False
    
    @staticmethod
    def mark_completed(user_id: int) -> bool:
        """
        标记引导完成
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                UPDATE user_onboarding_status
                SET is_completed = TRUE,
                    completed_at = CURRENT_TIMESTAMP,
                    progress_percentage = 100
                WHERE user_id = %s
            """
            execute_update(sql, (user_id,))
            
            logger.info(f"✅ 用户 {user_id} 完成新手引导")
            return True
        except Exception as e:
            logger.error(f"❌ 标记引导完成失败: {str(e)}")
            return False
    
    @staticmethod
    def increment_skip_count(user_id: int) -> bool:
        """
        增加跳过次数
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE user_onboarding_status SET skip_count = skip_count + 1 WHERE user_id = %s"
            execute_update(sql, (user_id,))
            return True
        except Exception as e:
            logger.error(f"❌ 更新跳过次数失败: {str(e)}")
            return False


class OnboardingAnswer:
    """
    用户引导回答模型
    
    对应表: user_onboarding_answers
    """
    
    def __init__(self, answer_id: int = None, user_id: int = None,
                 step_number: int = None, question_text: str = None,
                 user_answer: str = None, extracted_tags: Dict = None,
                 **kwargs):
        self.answer_id = answer_id
        self.user_id = user_id
        self.step_number = step_number
        self.question_text = question_text
        self.user_answer = user_answer
        self.extracted_tags = extracted_tags or {}
    
    @staticmethod
    def save_answer(user_id: int, step_number: int, question_text: str,
                   user_answer: str, extracted_tags: Dict = None,
                   is_skipped: bool = False, confidence_score: float = None,
                   tts_audio_url: str = None) -> bool:
        """
        保存用户回答
        
        Args:
            user_id: 用户ID
            step_number: 步骤号
            question_text: 问题文本
            user_answer: 用户回答
            extracted_tags: 提取的标签
            is_skipped: 是否跳过
            confidence_score: 置信度
            tts_audio_url: TTS音频URL
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                INSERT INTO user_onboarding_answers 
                (user_id, step_number, question_text, user_answer, extracted_tags, 
                 is_skipped, confidence_score, tts_audio_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            extracted_tags_json = json.dumps(extracted_tags, ensure_ascii=False) if extracted_tags else None
            
            execute_update(sql, (user_id, step_number, question_text, user_answer,
                                extracted_tags_json, is_skipped, confidence_score, tts_audio_url))
            
            logger.info(f"✅ 用户 {user_id} 步骤 {step_number} 回答已保存")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存回答失败: {str(e)}")
            return False
    
    @staticmethod
    def get_user_answers(user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有回答
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 回答列表
        """
        sql = """
            SELECT * FROM user_onboarding_answers
            WHERE user_id = %s
            ORDER BY step_number
        """
        rows = execute_query(sql, (user_id,))
        
        # 解析JSON字段
        for row in rows:
            if row.get('extracted_tags'):
                row['extracted_tags'] = json.loads(row['extracted_tags'])
        
        return rows


class OnboardingQuestion:
    """
    引导问题配置模型
    
    对应表: onboarding_questions
    """
    
    def __init__(self, question_id: int = None, step_number: int = None,
                 question_text: str = None, tag_keys: List[str] = None,
                 is_required: bool = False, skip_allowed: bool = True,
                 tts_audio_url: str = None, **kwargs):
        self.question_id = question_id
        self.step_number = step_number
        self.question_text = question_text
        self.tag_keys = tag_keys or []
        self.is_required = is_required
        self.skip_allowed = skip_allowed
        self.tts_audio_url = tts_audio_url
    
    @staticmethod
    def get_all() -> List['OnboardingQuestion']:
        """
        获取所有引导问题
        
        Returns:
            List[OnboardingQuestion]: 问题列表
        """
        sql = """
            SELECT * FROM onboarding_questions
            WHERE is_active = TRUE
            ORDER BY display_order
        """
        rows = execute_query(sql)
        
        questions = []
        for row in rows:
            # 解析JSON字段
            if row.get('tag_keys'):
                row['tag_keys'] = json.loads(row['tag_keys'])
            questions.append(OnboardingQuestion(**row))
        
        return questions
    
    @staticmethod
    def get_by_step(step_number: int) -> Optional['OnboardingQuestion']:
        """
        根据步骤号获取问题
        
        Args:
            step_number: 步骤号
            
        Returns:
            OnboardingQuestion: 问题对象
        """
        sql = """
            SELECT * FROM onboarding_questions
            WHERE step_number = %s AND is_active = TRUE
        """
        row = execute_query(sql, (step_number,), fetch_one=True)
        
        if row:
            # 解析JSON字段
            if row.get('tag_keys'):
                row['tag_keys'] = json.loads(row['tag_keys'])
            return OnboardingQuestion(**row)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'question_id': self.question_id,
            'step_number': self.step_number,
            'question_text': self.question_text,
            'tag_keys': self.tag_keys,
            'is_required': self.is_required,
            'skip_allowed': self.skip_allowed,
            'tts_audio_url': self.tts_audio_url
        }

