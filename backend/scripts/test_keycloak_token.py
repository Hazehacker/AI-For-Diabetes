#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keycloak Token测试脚本
~~~~~~~~~~~~~~~~~~~~~

测试Keycloak token生成和验证功能

作者: 智糖团队
日期: 2025-01-15
"""

import sys
import os
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'main'))

def test_keycloak_token():
    """测试Keycloak token功能"""
    try:
        from utils.jwt_helper import generate_token, verify_token, get_keycloak_client, get_keycloak_admin_client
        from utils.config_loader import load_config

        print("🔍 测试Keycloak Token功能")
        print("=" * 50)

        # 加载配置
        config = load_config()
        print("✅ 配置加载成功")

        # 测试Keycloak客户端初始化
        print("\n1. 测试Keycloak客户端初始化...")
        client = get_keycloak_client()
        admin_client = get_keycloak_admin_client()

        if client:
            print("✅ Keycloak普通客户端初始化成功")
        else:
            print("⚠️  Keycloak普通客户端初始化失败")

        if admin_client:
            print("✅ Keycloak管理员客户端初始化成功")
        else:
            print("⚠️  Keycloak管理员客户端初始化失败")

        # 测试token生成
        print("\n2. 测试token生成...")
        user_id = 1
        username = "test_admin"

        token = generate_token(user_id, username, {"is_admin": True})
        print(f"✅ Token生成成功: {token[:50]}...")

        # 测试token验证
        print("\n3. 测试token验证...")
        payload = verify_token(token)
        if payload:
            print("✅ Token验证成功")
            print(f"   用户ID: {payload.get('user_id')}")
            print(f"   用户名: {payload.get('username')}")
            print(f"   是否管理员: {payload.get('is_admin')}")
        else:
            print("❌ Token验证失败")

        # 测试token刷新
        print("\n4. 测试token刷新...")
        from utils.jwt_helper import refresh_token
        new_token = refresh_token(token)
        if new_token and new_token != token:
            print("✅ Token刷新成功")
            print(f"   新Token: {new_token[:50]}...")
        else:
            print("❌ Token刷新失败")

        # 验证新token
        print("\n5. 验证刷新后的token...")
        new_payload = verify_token(new_token)
        if new_payload:
            print("✅ 新Token验证成功")
        else:
            print("❌ 新Token验证失败")

        # 测试管理员token
        print("\n6. 测试管理员Keycloak token...")
        from utils.jwt_helper import generate_admin_token, verify_admin_token

        admin_token = generate_admin_token('admin', 'admin123')
        if admin_token:
            print("✅ 管理员Keycloak token生成成功")
            print(f"   Token: {admin_token[:50]}...")

            # 验证管理员token
            admin_payload = verify_admin_token(admin_token)
            if admin_payload:
                print("✅ 管理员token验证成功")
                print(f"   用户名: {admin_payload.get('preferred_username')}")
                print(f"   角色: {admin_payload.get('realm_access', {}).get('roles', [])}")
            else:
                print("❌ 管理员token验证失败")
        else:
            print("⚠️  管理员Keycloak token生成失败（可能是Keycloak服务器不可用）")

        print("\n" + "=" * 50)
        print("🎉 Keycloak Token测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keycloak_token()
