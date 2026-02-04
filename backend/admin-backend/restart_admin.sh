#!/bin/bash

# 重启管理后台服务

echo "🛑 停止现有服务..."
pkill -f "start_admin_server.py"
sleep 2

echo "🚀 启动管理后台服务..."
cd "$(dirname "$0")"
./start_admin.sh

