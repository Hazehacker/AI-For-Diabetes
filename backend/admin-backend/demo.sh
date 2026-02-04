#!/bin/bash

echo "🚀 启动智糖小助手管理后台演示"
echo "===================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查语法
echo "🔍 检查Python语法..."
cd "$(dirname "$0")"
if ! python3 -m py_compile start_admin_server.py 2>/dev/null; then
    echo "❌ Python语法错误，正在修复..."
    # 修复常见的缩进问题
    sed -i '' 's/^            data = jwt.decode/                data = jwt.decode/g' start_admin_server.py
    sed -i '' 's/^        token = jwt.encode/            token = jwt.encode/g' start_admin_server.py
    sed -i '' 's/^    return redirect/        return redirect/g' start_admin_server.py
    echo "✅ 语法修复完成"
fi

# 启动管理后台服务
echo "📡 启动管理后台服务 (端口 8901)..."
python3 start_admin_server.py &
ADMIN_PID=$!

# 等待服务启动
sleep 5

# 检查服务状态
if curl -s http://127.0.0.1:8901/admin/login > /dev/null && curl -s http://127.0.0.1:8901/admin/js/api-config.js > /dev/null; then
    echo "✅ 管理后台服务启动成功"
    echo ""
    echo "🌐 管理后台访问地址:"
    echo "   登录页面: http://127.0.0.1:8901/admin/login"
    echo "   主应用: http://127.0.0.1:8901/admin/index.html"
    echo "   演示账号: admin / admin123"
    echo ""
    echo "📋 完整交互功能演示:"
    echo "   ✅ 用户管理: 创建、编辑、删除用户"
    echo "   ✅ FAQ管理: 智能问答内容管理"
    echo "   ✅ 标签管理: 用户个性化标签"
    echo "   ✅ 提示词管理: AI对话模板配置"
    echo "   ✅ 消息记录: 对话历史查看"
    echo "   ✅ 知识问答: FAQ统计信息展示"
    echo ""
    echo "🎨 界面特色:"
    echo "   • 现代化渐变设计"
    echo "   • 响应式布局适配"
    echo "   • 丰富的交互动画"
    echo "   • 实时操作反馈"
    echo ""
    echo "🛑 按 Ctrl+C 停止服务"
    echo ""

    # 打开浏览器（如果有的话）
    if command -v open &> /dev/null; then
        open http://127.0.0.1:8901/admin/login
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://127.0.0.1:8901/admin/login
    fi

    # 等待用户中断
    wait $ADMIN_PID
else
    echo "❌ 管理后台服务启动失败"
    echo "💡 请检查:"
    echo "   • 端口8901是否被占用"
    echo "   • Python环境是否正确"
    echo "   • 数据库连接是否正常"
    kill $ADMIN_PID 2>/dev/null
    exit 1
fi
