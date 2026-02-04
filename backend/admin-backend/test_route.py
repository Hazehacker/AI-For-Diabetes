#!/usr/bin/env python3
# 测试路由是否正常工作

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from start_admin_server import app

# 测试路由匹配
with app.test_client() as client:
    # 测试 /admin/js/api-config.js
    response = client.get('/admin/js/api-config.js')
