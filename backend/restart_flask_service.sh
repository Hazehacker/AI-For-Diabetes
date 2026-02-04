#!/bin/bash

# 重启 Flask 服务脚本
# 用法: ./restart_flask_service.sh

echo "=== 重启 Flask 服务 ==="

# 1. 查找并停止现有的 gunicorn 进程
echo "1. 停止现有服务..."
pkill -f "gunicorn.*wsgi:application" && echo "✓ 已停止 gunicorn 进程" || echo "未找到运行中的 gunicorn 进程"

# 等待进程完全停止
sleep 2

# 2. 检查端口是否被占用
echo ""
echo "2. 检查端口 8900..."
if lsof -i:8900 > /dev/null 2>&1; then
    echo "⚠️  端口 8900 仍被占用，尝试强制停止..."
    lsof -ti:8900 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 3. 启动服务
echo ""
echo "3. 启动服务..."
cd /root || exit 1

# 检查是否有 start_admin.sh 脚本
if [ -f "start_admin.sh" ]; then
    echo "使用 start_admin.sh 启动..."
    bash start_admin.sh
elif [ -f "main/wsgi.py" ]; then
    echo "使用 gunicorn 直接启动..."
    cd main
    nohup gunicorn -w 4 -b 0.0.0.0:8900 --timeout 300 wsgi:application > ../logs/gunicorn.log 2>&1 &
    cd ..
else
    echo "❌ 错误: 找不到启动脚本或 wsgi.py"
    exit 1
fi

# 4. 等待服务启动
echo ""
echo "4. 等待服务启动..."
sleep 3

# 5. 检查服务状态
echo ""
echo "5. 检查服务状态..."
if lsof -i:8900 > /dev/null 2>&1; then
    echo "✓ 服务已在端口 8900 上运行"
    
    # 测试静态文件访问
    echo ""
    echo "6. 测试静态文件访问..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8900/nvsheng.png)
    if [ "$response" = "200" ]; then
        echo "✓ 静态文件访问成功 (HTTP $response)"
    else
        echo "⚠️  静态文件访问失败 (HTTP $response)"
        echo "请检查文件是否存在: ls -la 前端页面/nvsheng.png"
    fi
    
    # 测试 API
    echo ""
    echo "7. 测试 API..."
    api_response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8900/api/health 2>/dev/null || echo "000")
    if [ "$api_response" != "000" ]; then
        echo "✓ API 响应正常 (HTTP $api_response)"
    else
        echo "⚠️  API 未响应，但服务可能正在启动中..."
    fi
else
    echo "❌ 服务启动失败"
    echo "查看日志: tail -f logs/gunicorn.log"
    exit 1
fi

echo ""
echo "=== 完成 ==="
echo "查看实时日志: tail -f logs/gunicorn.log"
echo "测试图片访问: curl -I http://127.0.0.1:8900/nvsheng.png"
