#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户创建时是否在Keycloak同步

作者: 智糖团队
日期: 2025-01-15
"""

import sys
import os
import time

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'main'))

def test_user_creation_sync():
    """测试用户创建时是否在Keycloak同步"""
    try:


        from utils.jwt_helper import get_keycloak_admin_client
        from services.auth_service import get_auth_service

        # 获取服务
        auth_service = get_auth_service()
        keycloak_client = get_keycloak_admin_client()

        if not keycloak_client:
            print('❌ Keycloak客户端不可用')
            return False

        # 获取创建用户前的数量
        try:
            users_before = keycloak_client.get_users()
            count_before = len(users_before) if users_before else 0
            print(f'✅ 创建前Keycloak用户数量: {count_before}')
        except Exception as e:
            print(f'⚠️ 无法获取用户数量: {str(e)}')
            count_before = 0

        # 创建一个测试用户
        timestamp = int(time.time())
        test_username = f'test_kc_{timestamp % 10000}'  # 缩短用户名
        print(f'📝 正在创建测试用户: {test_username}')

        result = auth_service.register(
            username=test_username,
            password='Test123456',
            email=f'{test_username}@test.com',
            nickname='Keycloak测试用户'
        )

        if result['success']:
            user_id = result['user_id']

            # 等待一下让异步任务完成
            time.sleep(3)

            # 检查Keycloak中是否创建了用户
            try:
                # 方式1：通过attributes查找用户
                users_by_attr = keycloak_client.get_users({'q': f'user_id:{user_id}'})
                if users_by_attr:
                    keycloak_user = users_by_attr[0]


                    # 检查attributes
                    attrs = keycloak_user.get('attributes', {})
                    return True

                # 方式2：通过用户名查找用户
                users_by_name = keycloak_client.get_users({'username': f'{test_username}_{user_id}'})
                if users_by_name:
                    keycloak_user = users_by_name[0]
                    return True

                # 方式3：获取所有用户并查找
                all_users = keycloak_client.get_users()
                matching_users = [u for u in (all_users or []) if u.get('username', '').startswith(f'{test_username}_')]
                if matching_users:
                    keycloak_user = matching_users[0]
                    return True

                return False

            except Exception as e:
                return False

        else:
            return False

    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_creation_sync()
    print('=' * 50)
    if success:
        print('🎉 测试成功：用户创建时会在Keycloak同步')
    else:
        print('❌ 测试失败：用户创建未在Keycloak同步')
    sys.exit(0 if success else 1)
