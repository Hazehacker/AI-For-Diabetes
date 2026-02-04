#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签提取定时任务脚本 - 【核心脚本】
~~~~~~~~~~~~~~~

独立运行的后台任务，用于定时处理用户对话并自动提取标签

功能：
- 定时扫描用户对话（默认5分钟间隔）
- 使用DeepSeek AI智能提取用户标签
- 自动更新用户标签数据库
- 同步标签到Coze平台
- 支持手动触发和单次执行

使用方法：
1. 直接运行: python scripts/tag_extraction_worker.py
2. 后台运行: nohup python scripts/tag_extraction_worker.py &
3. 使用screen: screen -S tag_worker python scripts/tag_extraction_worker.py
4. 单次执行: python scripts/tag_extraction_worker.py --once
5. 快速启动: ./scripts/start_tag_scheduler.sh

参数选项：
- --interval: 检查间隔（秒），默认300
- --hours-back: 检查最近多少小时的对话，默认24
- --once: 只执行一次后退出
- --verbose: 详细输出模式

作者: 智糖团队
日期: 2025-01-21
"""

import sys
import os
import time
import signal
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'main'))

from services.tag_extraction_scheduler import get_tag_extraction_scheduler
from utils.logger import setup_logger

# 设置日志
logger = setup_logger('tag_extraction_worker', log_level='INFO')


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，正在停止服务...")
    scheduler = get_tag_extraction_scheduler()
    scheduler.stop()
    logger.info("✅ 服务已停止")
    sys.exit(0)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='标签提取定时任务脚本')
    parser.add_argument('--interval', type=int, default=300,
                       help='检查间隔（秒），默认300秒（5分钟）')
    parser.add_argument('--hours-back', type=int, default=24,
                       help='检查最近多少小时的对话，默认24小时')
    parser.add_argument('--once', action='store_true',
                       help='只执行一次后退出（用于测试）')
    parser.add_argument('--verbose', action='store_true',
                       help='详细输出')

    args = parser.parse_args()

    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 标签提取定时任务脚本启动")
    logger.info(f"配置: 检查间隔={args.interval}秒, 对话时间范围={args.hours_back}小时")

    try:
        # 获取调度服务
        scheduler = get_tag_extraction_scheduler()

        if args.once:
            # 只执行一次
            logger.info("🔄 执行单次标签提取任务...")
            scheduler._process_tag_extractions()
            logger.info("✅ 单次任务执行完成")
            return

        # 启动调度服务
        logger.info("🔄 启动定时调度服务...")
        scheduler.start()

        # 保持运行
        logger.info("✅ 服务已启动，等待定时任务执行...")
        logger.info("💡 按 Ctrl+C 停止服务")

        try:
            while True:
                time.sleep(1)

                # 如果需要详细输出，显示服务状态
                if args.verbose and scheduler.is_running:
                    status = scheduler.get_scheduler_status()
                    if status.get('next_check_in', 0) <= 60:  # 1分钟内
                        logger.info(f"⏰ 距离下次检查还有 {status.get('next_check_in', 0)} 秒")

        except KeyboardInterrupt:
            logger.info("收到键盘中断信号，正在停止...")
            scheduler.stop()

    except Exception as e:
        logger.error(f"❌ 脚本运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
