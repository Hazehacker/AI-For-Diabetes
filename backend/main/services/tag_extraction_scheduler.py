"""
对话标签提取调度服务 - 【核心文件】
~~~~~~~~~~~~~~~

定时处理用户对话，自动提取标签并更新用户画像

功能：
- 定时扫描用户对话（默认5分钟间隔）
- 智能筛选待处理的对话（最近24小时，至少3条消息）
- 使用DeepSeek AI提取用户标签
- 自动更新用户标签数据库
- 同步标签到Coze平台
- 防重复处理机制（60分钟内已处理的跳过）

核心组件：
- TagExtractionScheduler: 主调度服务类
- _process_tag_extractions(): 标签提取处理逻辑
- _process_conversation_tags(): 单对话标签提取
- _get_pending_conversations(): 智能对话筛选

使用方式：
- API控制: /api/tag-scheduler/start|stop|status
- 独立脚本: scripts/tag_extraction_worker.py
- 后台运行: ./scripts/start_tag_scheduler.sh

作者: 智糖团队
日期: 2025-01-21
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.logger import get_logger
from utils.database import execute_query, execute_update
from services.tag_service import get_tag_service
from services.deepseek_service import get_deepseek_service

logger = get_logger(__name__)


class TagExtractionScheduler:
    """
    对话标签提取调度服务

    定期处理用户对话，自动提取标签信息
    """

    def __init__(self, check_interval: int = 300):
        """
        初始化调度服务

        Args:
            check_interval: 检查间隔（秒），默认5分钟
        """
        self.check_interval = check_interval
        self.is_running = False
        self.thread = None

        # 获取依赖服务
        self.tag_service = get_tag_service()
        self.deepseek_service = get_deepseek_service()

        logger.info("✅ 标签提取调度服务初始化完成")

    def start(self):
        """启动调度服务"""
        if self.is_running:
            logger.warning("⚠️ 标签提取调度服务已在运行中")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

        logger.info(f"🚀 标签提取调度服务已启动，检查间隔: {self.check_interval}秒")

    def stop(self):
        """停止调度服务"""
        if not self.is_running:
            logger.warning("⚠️ 标签提取调度服务未运行")
            return

        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)

        logger.info("🛑 标签提取调度服务已停止")

    def _run_scheduler(self):
        """运行调度循环"""
        logger.info("🔄 开始标签提取调度循环")

        while self.is_running:
            try:
                # 执行标签提取任务
                self._process_tag_extractions()

                # 等待下次检查
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"❌ 标签提取调度循环错误: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再试

    def _process_tag_extractions(self):
        """处理标签提取任务"""
        try:
            logger.info("🔍 开始检查需要处理的对话...")

            # 获取需要处理的对话
            conversations = self._get_pending_conversations()

            if not conversations:
                logger.info("📭 暂无需要处理的对话")
                return

            logger.info(f"📋 找到 {len(conversations)} 个对话需要处理标签")

            processed_count = 0
            tag_count = 0

            for conversation in conversations:
                try:
                    # 处理单个对话
                    result = self._process_conversation_tags(conversation)

                    if result['success']:
                        processed_count += 1
                        tag_count += result.get('tag_count', 0)

                        logger.info(f"✅ 处理对话 {conversation['conversation_id']}: 提取了 {result.get('tag_count', 0)} 个标签")

                    else:
                        logger.warning(f"⚠️ 处理对话 {conversation['conversation_id']} 失败: {result.get('message')}")

                except Exception as e:
                    logger.error(f"❌ 处理对话 {conversation['conversation_id']} 时出错: {str(e)}")

            logger.info(f"📊 本次处理完成: {processed_count}/{len(conversations)} 个对话成功，提取了 {tag_count} 个标签")

        except Exception as e:
            logger.error(f"❌ 处理标签提取任务失败: {str(e)}")

    def _get_pending_conversations(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        获取需要处理的对话

        Args:
            hours_back: 检查最近多少小时的对话，默认24小时

        Returns:
            List[Dict]: 待处理的对话列表
        """
        try:
            # 计算时间范围
            time_threshold = datetime.now() - timedelta(hours=hours_back)

            # 查询最近的对话，按用户分组获取最新的对话
            sql = """
                SELECT
                    cm.user_id,
                    cm.conversation_id,
                    MAX(cm.created_at) as last_message_time,
                    COUNT(*) as message_count,
                    GROUP_CONCAT(cm.content ORDER BY cm.created_at SEPARATOR '\\n') as conversation_content
                FROM chat_messages cm
                WHERE cm.created_at >= %s
                  AND cm.role = 'user'
                  AND LENGTH(cm.content) > 10  -- 只处理有意义的对话
                GROUP BY cm.user_id, cm.conversation_id
                HAVING message_count >= 3  -- 至少有3条消息的对话
                ORDER BY last_message_time DESC
                LIMIT 50  -- 每次最多处理50个对话
            """

            conversations = execute_query(sql, (time_threshold,))

            # 过滤掉最近已经处理过的对话
            filtered_conversations = []
            for conv in conversations:
                if not self._is_conversation_processed_recently(conv['conversation_id']):
                    # 截取对话内容（最近的1000个字符）
                    conv['conversation_content'] = conv['conversation_content'][-1000:]
                    filtered_conversations.append(conv)

            return filtered_conversations

        except Exception as e:
            logger.error(f"❌ 获取待处理对话失败: {str(e)}")
            return []

    def _is_conversation_processed_recently(self, conversation_id: str, minutes_back: int = 60) -> bool:
        """
        检查对话是否在最近一段时间内已经处理过

        Args:
            conversation_id: 对话ID
            minutes_back: 检查最近多少分钟，默认60分钟

        Returns:
            bool: 是否最近处理过
        """
        try:
            time_threshold = datetime.now() - timedelta(minutes=minutes_back)

            sql = """
                SELECT COUNT(*) as count
                FROM user_tag_history
                WHERE conversation_id = %s
                  AND updated_at >= %s
                  AND source = 'ai_extract'
            """

            result = execute_query(sql, (conversation_id, time_threshold), fetch_one=True)
            return result['count'] > 0

        except Exception as e:
            logger.error(f"❌ 检查对话处理状态失败: {str(e)}")
            return False

    def _process_conversation_tags(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个对话的标签提取

        Args:
            conversation: 对话信息

        Returns:
            Dict: 处理结果
        """
        try:
            user_id = conversation['user_id']
            conversation_id = conversation['conversation_id']
            content = conversation['conversation_content']

            logger.info(f"🤖 开始为用户 {user_id} 的对话 {conversation_id} 提取标签")

            # 使用DeepSeek AI提取标签
            extracted_tags = self.deepseek_service.tag_user_from_conversation(user_id, content)

            if not extracted_tags:
                return {
                    'success': True,
                    'tag_count': 0,
                    'message': '未提取到标签'
                }

            # 批量设置标签
            tag_results = []
            for tag_info in extracted_tags:
                try:
                    result = self.tag_service.set_user_tag(
                        user_id=user_id,
                        tag_key=tag_info.get('tag_key', ''),
                        tag_value=tag_info.get('tag_value', ''),
                        source='ai_extract',
                        conversation_id=conversation_id,  # 传递对话ID
                        auto_sync_coze=True
                    )

                    if result.get('success'):
                        tag_results.append({
                            'tag_key': tag_info.get('tag_key'),
                            'tag_value': tag_info.get('tag_value'),
                            'confidence': tag_info.get('confidence', 0.5)
                        })

                except Exception as e:
                    logger.warning(f"⚠️ 设置标签 {tag_info.get('tag_key')} 失败: {str(e)}")

            # 同步标签到Coze
            try:
                sync_result = self.tag_service.sync_user_tags_to_coze(user_id)
                if sync_result:
                    logger.info(f"✅ 用户 {user_id} 的标签已同步到Coze")
                else:
                    logger.warning(f"⚠️ 用户 {user_id} 的标签同步到Coze失败")
            except Exception as e:
                logger.error(f"❌ 同步标签到Coze失败: {str(e)}")

            return {
                'success': True,
                'tag_count': len(tag_results),
                'tags': tag_results
            }

        except Exception as e:
            logger.error(f"❌ 处理对话标签提取失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }

    def process_single_conversation(self, user_id: int, conversation_id: str) -> Dict[str, Any]:
        """
        处理单个对话的标签提取（手动调用）

        Args:
            user_id: 用户ID
            conversation_id: 对话ID

        Returns:
            Dict: 处理结果
        """
        try:
            # 获取对话内容
            sql = """
                SELECT
                    cm.user_id,
                    cm.conversation_id,
                    GROUP_CONCAT(cm.content ORDER BY cm.created_at SEPARATOR '\\n') as conversation_content
                FROM chat_messages cm
                WHERE cm.conversation_id = %s AND cm.user_id = %s
                GROUP BY cm.conversation_id
            """

            conversation = execute_query(sql, (conversation_id, user_id), fetch_one=True)

            if not conversation:
                return {
                    'success': False,
                    'message': '对话不存在或无权限访问'
                }

            # 处理标签提取
            return self._process_conversation_tags(conversation)

        except Exception as e:
            logger.error(f"❌ 处理单个对话失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }

    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        获取调度服务状态

        Returns:
            Dict: 服务状态信息
        """
        return {
            'is_running': self.is_running,
            'check_interval': self.check_interval,
            'thread_alive': self.thread.is_alive() if self.thread else False,
            'next_check_in': self.check_interval if self.is_running else None
        }


# 全局单例实例
_scheduler_instance: Optional[TagExtractionScheduler] = None


def get_tag_extraction_scheduler() -> TagExtractionScheduler:
    """获取标签提取调度服务单例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TagExtractionScheduler()
    return _scheduler_instance


def start_tag_extraction_scheduler():
    """启动标签提取调度服务"""
    scheduler = get_tag_extraction_scheduler()
    scheduler.start()
    return scheduler


def stop_tag_extraction_scheduler():
    """停止标签提取调度服务"""
    scheduler = get_tag_extraction_scheduler()
    scheduler.stop()
    return scheduler
