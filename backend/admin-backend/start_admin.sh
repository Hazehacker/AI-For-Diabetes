#!/bin/bash

# 智糖小助手 - 独立后台管理服务启动脚本

echo "🚀 启动智糖小助手 - 独立后台管理服务..."

# 设置环境变量
export ADMIN_PORT=8901
export FLASK_DEBUG=False

# 进入admin-backend目录
cd "$(dirname "$0")"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查Python依赖..."
python3 -c "import flask, flask_cors, mysql.connector, jwt" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要的Python依赖包"
    echo "请运行: pip install flask flask-cors mysql-connector-python PyJWT"
    exit 1
fi

# 启动服务
echo "🌟 启动管理后台服务..."
echo "📍 服务地址: http://localhost:8901/admin"
echo "🔧 API地址: http://localhost:8901/admin/api"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 start_admin_server.py
