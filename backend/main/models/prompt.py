"""
提示词模型
~~~~~~~

提示词管理相关的数据模型

作者: 智糖团队
日期: 2025-01-17
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.database import execute_query
from utils.logger import get_logger

logger = get_logger(__name__)


class PromptTemplate:
    """
    提示词模板模型

    对应表: prompt_templates
    """

    def __init__(self, prompt_id: int = None, prompt_type: str = None,
                 prompt_name: str = None, prompt_content: str = None,
                 version: int = 1, is_active: bool = True, **kwargs):
        self.prompt_id = prompt_id
        self.prompt_type = prompt_type  # 'initial', 'normal', 'tagging'
        self.prompt_name = prompt_name
        self.prompt_content = prompt_content
        self.version = version
        self.is_active = is_active

    @staticmethod
    def get_all(prompt_type: str = None, active_only: bool = True) -> List['PromptTemplate']:
        """
        获取所有提示词模板

        Args:
            prompt_type: 提示词类型过滤
            active_only: 只获取启用的模板

        Returns:
            List[PromptTemplate]: 提示词模板列表
        """
        sql = "SELECT * FROM prompt_templates WHERE 1=1"
        params = []

        if prompt_type:
            sql += " AND prompt_type = %s"
            params.append(prompt_type)

        if active_only:
            sql += " AND is_active = TRUE"

        sql += " ORDER BY prompt_type, version DESC, prompt_id"

        rows = execute_query(sql, tuple(params) if params else None)
        return [PromptTemplate(**row) for row in rows]

    @staticmethod
    def get_by_id(prompt_id: int) -> Optional['PromptTemplate']:
        """
        根据ID获取提示词模板

        Args:
            prompt_id: 提示词ID

        Returns:
            PromptTemplate: 提示词模板对象
        """
        sql = "SELECT * FROM prompt_templates WHERE prompt_id = %s AND is_active = TRUE"
        row = execute_query(sql, (prompt_id,), fetch_one=True)
        return PromptTemplate(**row) if row else None

    @staticmethod
    def get_by_type(prompt_type: str) -> Optional['PromptTemplate']:
        """
        根据类型获取最新的提示词模板

        Args:
            prompt_type: 提示词类型

        Returns:
            PromptTemplate: 最新的提示词模板
        """
        sql = """
            SELECT * FROM prompt_templates
            WHERE prompt_type = %s AND is_active = TRUE
            ORDER BY version DESC, prompt_id DESC
            LIMIT 1
        """
        row = execute_query(sql, (prompt_type,), fetch_one=True)
        return PromptTemplate(**row) if row else None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'prompt_id': self.prompt_id,
            'prompt_type': self.prompt_type,
            'prompt_name': self.prompt_name,
            'prompt_content': self.prompt_content,
            'version': self.version,
            'is_active': self.is_active
        }


class UserPromptSetting:
    """
    用户提示词设置模型

    对应表: user_prompt_settings
    """

    def __init__(self, setting_id: int = None, user_id: int = None,
                 prompt_type: str = None, prompt_id: int = None,
                 is_custom: bool = False, custom_content: str = None, **kwargs):
        self.setting_id = setting_id
        self.user_id = user_id
        self.prompt_type = prompt_type
        self.prompt_id = prompt_id
        self.is_custom = is_custom
        self.custom_content = custom_content

    @staticmethod
    def get_user_settings(user_id: int) -> Dict[str, Dict[str, Any]]:
        """
        获取用户的提示词设置

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户的提示词设置，key为prompt_type
        """
        sql = """
            SELECT
                ups.prompt_type,
                CASE
                    WHEN ups.is_custom = TRUE THEN ups.custom_content
                    ELSE pt.prompt_content
                END as prompt_content,
                ups.is_custom,
                pt.prompt_name,
                pt.version,
                ups.prompt_id,
                ups.custom_content as raw_custom_content
            FROM user_prompt_settings ups
            JOIN prompt_templates pt ON ups.prompt_id = pt.prompt_id
            WHERE ups.user_id = %s AND pt.is_active = TRUE
        """

        rows = execute_query(sql, (user_id,))
        settings = {}

        for row in rows:
            settings[row['prompt_type']] = {
                'prompt_content': row['prompt_content'],
                'is_custom': row['is_custom'],
                'prompt_name': row['prompt_name'],
                'version': row['version'],
                'prompt_id': row['prompt_id'],
                'custom_content': row['raw_custom_content']
            }

        return settings

    @staticmethod
    def set_user_prompt(user_id: int, prompt_type: str, prompt_id: int = None,
                       custom_content: str = None) -> bool:
        """
        设置用户的提示词

        Args:
            user_id: 用户ID
            prompt_type: 提示词类型
            prompt_id: 模板ID（当不使用自定义时）
            custom_content: 自定义内容（当使用自定义时）

        Returns:
            bool: 是否成功
        """
        try:
            from utils.database import execute_update, get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            if custom_content:
                # 使用自定义提示词
                sql = """
                    INSERT INTO user_prompt_settings
                    (user_id, prompt_type, prompt_id, is_custom, custom_content)
                    VALUES (%s, %s, NULL, TRUE, %s)
                    ON DUPLICATE KEY UPDATE
                        prompt_id = NULL,
                        is_custom = TRUE,
                        custom_content = VALUES(custom_content),
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (user_id, prompt_type, custom_content))
            else:
                # 使用模板提示词
                if prompt_id is None:
                    raise ValueError("使用模板提示词时必须提供prompt_id")
                sql = """
                    INSERT INTO user_prompt_settings
                    (user_id, prompt_type, prompt_id, is_custom, custom_content)
                    VALUES (%s, %s, %s, FALSE, NULL)
                    ON DUPLICATE KEY UPDATE
                        prompt_id = VALUES(prompt_id),
                        is_custom = FALSE,
                        custom_content = NULL,
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (user_id, prompt_type, prompt_id))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ 用户 {user_id} 提示词设置更新成功: {prompt_type}")
            return True

        except Exception as e:
            logger.error(f"❌ 设置用户提示词失败: {str(e)}")
            return False

    @staticmethod
    def get_user_prompt_content(user_id: int, prompt_type: str) -> Optional[str]:
        """
        获取用户指定类型的提示词内容

        Args:
            user_id: 用户ID
            prompt_type: 提示词类型

        Returns:
            str: 提示词内容
        """
        settings = UserPromptSetting.get_user_settings(user_id)
        if prompt_type in settings:
            return settings[prompt_type]['prompt_content']

        # 如果用户没有设置，使用默认模板
        template = PromptTemplate.get_by_type(prompt_type)
        return template.prompt_content if template else None
