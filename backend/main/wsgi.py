#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智糖小助手 WSGI 应用入口文件
用于生产环境部署（配合gunicorn等WSGI服务器使用）

使用方法：
    gunicorn -w 4 -b 0.0.0.0:8900 wsgi:application
"""

# ⚠️ 重要：必须在导入任何其他模块之前进行 gevent monkey patching
# 这样可以避免 SSL 相关的递归错误
try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    # 如果没有安装 gevent，忽略（使用 sync worker 时）
    pass

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)  # 也添加main目录本身到路径

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 确保配置路径正确设置
# 尝试多种可能的配置文件位置
possible_config_paths = [
    os.environ.get('CONFIG_PATH'),  # 环境变量中指定的路径
    os.path.join(parent_dir, 'config.yaml'),  # 项目根目录
    os.path.join(current_dir, '..', 'config.yaml'),  # 从main目录向上找
    'config.yaml'  # 当前目录
]

config_path = None
for path in possible_config_paths:
    if path and os.path.exists(path):
        config_path = path
        break

if config_path:
    os.environ['CONFIG_PATH'] = config_path
else:
    # 如果找不到配置文件，使用默认的硬编码配置
    os.environ['CONFIG_PATH'] = os.path.join(parent_dir, 'config.yaml')

# 导入Flask应用
try:
    from app import app

    # 重构后的应用已经在create_app()中完成了数据库初始化
    # 不需要额外的init_database()调用

    # 创建应用实例供WSGI服务器使用
    application = app

except ImportError as e:

    raise

# 开发环境下可以直接运行（不推荐生产环境使用）
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8900, debug=False)
