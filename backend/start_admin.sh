#!/bin/bash

# 智糖小助手管理后台启动脚本
# 作者: AI Assistant
# 日期: $(date +%Y-%m-%d)

echo "🚀 启动智糖小助手管理后台..."

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js 18.0+"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

# 显示环境信息
echo "📋 环境信息:"
echo "   Node.js版本: $(node --version)"
echo "   npm版本: $(npm --version)"

# 进入管理后台目录
ADMIN_DIR="admin-backend/zhitang-admin"
if [ ! -d "$ADMIN_DIR" ]; then
    echo "❌ 管理后台目录不存在: $ADMIN_DIR"
    echo "请先运行 setup_admin_env.sh 脚本"
    exit 1
fi

cd "$ADMIN_DIR"
echo "📁 进入目录: $(pwd)"

# 检查依赖是否已安装
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo "⚙️ 创建环境配置文件..."
    cat > .env << EOF
# 环境配置
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=智糖小助手管理后台
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=智糖小助手管理后台系统
EOF
    echo "✅ 环境配置文件已创建"
fi

# 检查后端服务是否运行
echo "🔍 检查后端服务状态..."
if curl -s http://115.120.251.86:8900/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️ 后端服务未运行，请先启动Flask后端服务"
    echo "   启动命令: cd main && python app.py"
    echo ""
    read -p "是否继续启动前端服务？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消启动"
        exit 1
    fi
fi

# 启动开发服务器
echo "🌟 启动开发服务器..."
echo ""
echo "📱 访问地址: http://localhost:5173"
echo "🔑 默认登录: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
