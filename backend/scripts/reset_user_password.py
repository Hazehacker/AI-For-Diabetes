#!/usr/bin/env python3
"""
重置用户密码脚本
~~~~~~~~~~~~~~~~

用于管理员重置指定用户的密码

使用方法:
    python reset_user_password.py <username> <new_password>
    
示例:
    python reset_user_password.py 13270860672 admin123

作者: 智糖团队
日期: 2025-01-14
"""

import sys
import os
import hashlib

# 添加父目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main'))

from utils.config_loader import load_config
from utils.database import get_db_connection
from utils.logger import setup_logger

logger = setup_logger('reset_password', log_level='INFO')


def hash_password(password: str) -> str:
    """
    对密码进行SHA-256哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def reset_user_password(username: str, new_password: str) -> bool:
    """
    重置用户密码
    
    Args:
        username: 用户名或手机号
        new_password: 新密码（明文）
        
    Returns:
        bool: 是否成功
    """
    try:
        # 加载配置
        load_config()
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查找用户
        logger.info(f"🔍 查找用户: {username}")
        cursor.execute("""
            SELECT user_id, username, phone_number 
            FROM users 
            WHERE username = %s OR phone_number = %s
        """, (username, username))
        
        user = cursor.fetchone()
        
        if not user:
            logger.error(f"❌ 用户不存在: {username}")
            return False
        
        user_id = user['user_id']
        username_display = user['username']
        phone_display = user['phone_number'] or 'N/A'
        
        logger.info(f"✅ 找到用户:")
        logger.info(f"   - ID: {user_id}")
        logger.info(f"   - 用户名: {username_display}")
        logger.info(f"   - 手机号: {phone_display}")
        
        # 加密新密码
        hashed_password = hash_password(new_password)
        logger.info(f"🔐 新密码已加密")
        
        # 更新密码
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """, (hashed_password, user_id))
        
        conn.commit()
        
        logger.info(f"✅ 密码重置成功!")
        logger.info(f"   - 用户: {username_display}")
        logger.info(f"   - 新密码: {new_password}")
        logger.info(f"   - 可以使用用户名或手机号登录")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 重置密码失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """主函数"""
    if len(sys.argv) < 3:
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    

    # 确认操作

    
    confirm = input("确认继续? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        sys.exit(0)

    
    # 执行重置
    success = reset_user_password(username, new_password)
    

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

