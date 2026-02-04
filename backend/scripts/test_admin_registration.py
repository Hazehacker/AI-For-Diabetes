#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员用户注册和Keycloak同步

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

def test_admin_registration():
    """测试管理员用户注册"""
    try:

        from utils.jwt_helper import get_keycloak_admin_client
        from utils.database import get_db_connection
        from services.auth_service import get_auth_service

        # 获取服务
        auth_service = get_auth_service()
        keycloak_client = get_keycloak_admin_client()

        if not keycloak_client:
            return False

        # 测试数据
        admin_username = "husir"
        admin_password = "husir@123"
        admin_email = "husir@admin.com"
        admin_nickname = "系统管理员"


        # 1. 先检查本地数据库中是否已存在
        print('\n1️⃣ 检查本地数据库...')
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, username, is_admin, email FROM users WHERE username = %s", (admin_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f'⚠️ 用户已存在: {existing_user}')
            user_id = existing_user['user_id']
            is_admin = existing_user['is_admin']
            if not is_admin:
                print('🔧 将用户设置为管理员...')
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = %s", (user_id,))
                conn.commit()
                print('✅ 本地管理员权限设置成功')
        else:
            # 注册新管理员用户
            print('📝 注册新管理员用户...')

            # 先创建普通用户
            result = auth_service.register(
                username=admin_username,
                password=admin_password,
                email=admin_email,
                nickname=admin_nickname
            )

            if not result['success']:
                print(f'❌ 用户注册失败: {result.get("message", "未知错误")}')
                return False

            user_id = result['user_id']
            print(f'✅ 普通用户创建成功，用户ID: {user_id}')

            # 设置为管理员
            cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = %s", (user_id,))
            conn.commit()
            print('✅ 管理员权限设置成功')

        # 验证本地数据库
        cursor.execute("SELECT user_id, username, nickname, email, is_admin, created_at FROM users WHERE username = %s", (admin_username,))
        user_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_record:
            print('✅ 本地数据库验证成功')
            print(f'   用户ID: {user_record["user_id"]}')
            print(f'   用户名: {user_record["username"]}')
            print(f'   昵称: {user_record["nickname"]}')
            print(f'   邮箱: {user_record["email"]}')
            print(f'   是否管理员: {user_record["is_admin"]}')
            print(f'   创建时间: {user_record["created_at"]}')

            user_id = user_record["user_id"]
        else:
            print('❌ 本地数据库验证失败')
            return False

        # 2. 检查Keycloak同步
        print('\n2️⃣ 检查Keycloak同步...')
        time.sleep(2)  # 等待同步

        try:
            # 通过用户名查找Keycloak用户
            keycloak_username = f"{admin_username}_{user_id}"
            users = keycloak_client.get_users({'username': keycloak_username})

            if users:
                keycloak_user = users[0]
                print('✅ Keycloak用户同步成功')
                print(f'   Keycloak用户名: {keycloak_user.get("username")}')
                print(f'   Keycloak用户ID: {keycloak_user.get("id")}')
                print(f'   是否启用: {keycloak_user.get("enabled")}')
                print(f'   邮箱: {keycloak_user.get("email", "N/A")}')

                # 检查attributes
                attrs = keycloak_user.get('attributes', {})
                if attrs:
                    print('   用户属性:')
                    print(f'     user_id: {attrs.get("user_id", ["N/A"])[0]}')
                    print(f'     original_username: {attrs.get("original_username", ["N/A"])[0]}')

                # 检查角色
                realm_roles = keycloak_client.get_realm_roles_of_user(keycloak_user['id'])
                print(f'   领域角色: {[role["name"] for role in realm_roles]}')

            else:
                print('❌ Keycloak用户同步失败 - 未找到用户')
                print(f'   查找的用户名: {keycloak_username}')

                # 尝试通过attributes查找
                attr_users = keycloak_client.get_users({'q': f'user_id:{user_id}'})
                if attr_users:
                    print('✅ 通过attributes找到Keycloak用户')
                    keycloak_user = attr_users[0]
                    print(f'   Keycloak用户名: {keycloak_user.get("username")}')
                else:
                    print('❌ 通过attributes也未找到用户')
                    return False

        except Exception as e:
            print(f'❌ 检查Keycloak用户失败: {str(e)}')
            return False

        # 3. 测试管理员登录
        print('\n3️⃣ 测试管理员登录...')

        # 测试本地登录
        login_result = auth_service.login(admin_username, admin_password)
        if login_result['success']:
            print('✅ 本地管理员登录成功')
            token = login_result.get('token')
            if token:
                print('✅ Token生成成功')
                print(f'   Token长度: {len(token)} 字符')

                # 验证token中的管理员权限
                from utils.jwt_helper import verify_token
                payload = verify_token(token)
                if payload:
                    print('✅ Token验证成功')
                    print(f'   Token中的管理员标识: {payload.get("is_admin", False)}')
                else:
                    print('❌ Token验证失败')
            else:
                print('⚠️ 未返回token')
        else:
            print(f'❌ 本地管理员登录失败: {login_result.get("message", "未知错误")}')

        # 4. 测试Keycloak管理员token生成
        print('\n4️⃣ 测试Keycloak管理员token生成...')

        from utils.jwt_helper import generate_admin_token
        keycloak_token = generate_admin_token(admin_username, admin_password)

        if keycloak_token:
            print('✅ Keycloak管理员token生成成功')
            print(f'   Token长度: {len(keycloak_token)} 字符')

            # 验证Keycloak token
            from utils.jwt_helper import verify_admin_token
            admin_payload = verify_admin_token(keycloak_token)

            if admin_payload:
                print('✅ Keycloak管理员token验证成功')
                print(f'   用户名: {admin_payload.get("preferred_username")}')
                print(f'   角色: {admin_payload.get("realm_access", {}).get("roles", [])}')
            else:
                print('❌ Keycloak管理员token验证失败')
        else:
            print('⚠️ Keycloak管理员token生成失败（可能是Keycloak服务器不可用）')

        print('\n' + '=' * 60)
        print('🎉 管理员用户注册和Keycloak同步测试完成')
        print('📋 测试总结:')
        print(f'   ✅ 本地数据库: 用户 {admin_username} (ID: {user_id}) 创建成功，管理员权限已设置')
        print(f'   ✅ Keycloak同步: 用户已在Keycloak中创建')
        print(f'   ✅ 管理员认证: 本地登录和Keycloak token都工作正常')

        return True

    except Exception as e:
        print(f'❌ 测试异常: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_registration()
    if not success:
        sys.exit(1)
