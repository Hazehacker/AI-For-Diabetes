#!/usr/bin/env python3
"""
执行TTS缓存表迁移
~~~~~~~~~~~~~~~~~

执行数据库迁移，创建TTS缓存相关的表。

使用方法:
python scripts/migrate_tts_cache_tables.py

作者: 智糖团队
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.database import execute_update, get_db_connection
from utils.logger import get_logger

logger = get_logger(__name__)


def migrate_tts_cache_tables():
    """执行TTS缓存表迁移"""
    print("🎵 开始执行TTS缓存表迁移...")

    try:
        # 读取迁移文件
        migration_file = os.path.join(os.path.dirname(__file__), '..', 'migrations', '008_create_tts_cache_tables.sql')

        if not os.path.exists(migration_file):
            print(f"❌ 迁移文件不存在: {migration_file}")
            return False

        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割SQL语句（按分号分割）
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

        # 执行每个SQL语句
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"📝 执行SQL语句 {i}/{len(statements)}...")
                execute_update(statement)
                print(f"✅ SQL语句 {i} 执行成功")

        print("🎉 TTS缓存表迁移完成！")
        print("\n📋 创建的表:")
        print("  - tts_cache: TTS缓存元数据表")
        print("  - tts_cache_stats: TTS缓存统计表")

        return True

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        logger.error(f"迁移失败: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = migrate_tts_cache_tables()
    sys.exit(0 if success else 1)
