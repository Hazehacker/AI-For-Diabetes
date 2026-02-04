#!/bin/bash

# 智糖小助手服务重启脚本
# 支持远程服务器和本地环境自动检测
# 功能：停止旧服务 -> 激活环境 -> 启动新服务 -> 验证服务

echo "=========================================="
echo "🚀 智糖小助手服务重启"
echo "=========================================="
echo ""

# 检查是否在远程服务器上
if [ -d "/ai/zhitang/smart-sugar-assistant" ]; then
    # 在远程服务器上
    PROJECT_DIR="/ai/zhitang/smart-sugar-assistant"
    MAIN_DIR="$PROJECT_DIR/main"
    
    echo "📍 检测到远程服务器环境"
    echo "项目目录: $PROJECT_DIR"
    echo ""
    
    # 停止旧服务
    echo "步骤1: 停止旧服务..."
    lsof -t -i:8900 | xargs -r kill -9 2>/dev/null || true
    sleep 2
    echo "✅ 旧服务已停止"
    echo ""
    
    # 激活conda环境
    echo "步骤2: 激活conda环境..."
    source /opt/conda/etc/profile.d/conda.sh
    conda activate myenv
    echo "✅ 环境已激活"
    echo ""
    
    # 进入main目录
    cd $MAIN_DIR

    # 启动服务
    echo "步骤3: 启动新服务..."
    echo "使用wsgi:application模式启动..."
    nohup gunicorn -w 4 -b 0.0.0.0:8900 \
        --timeout 300 \
        --worker-class gevent \
        --worker-connections 1000 \
        --access-logfile $PROJECT_DIR/access.log \
        --error-logfile $PROJECT_DIR/error.log \
        --log-level info \
        --reload \
        wsgi:application > $PROJECT_DIR/gunicorn.log 2>&1 &
    
    GUNICORN_PID=$!
    echo "✅ 服务已启动，进程ID: $GUNICORN_PID"
    echo ""
    
    # 等待服务启动
    echo "步骤4: 等待服务启动（10秒）..."
    sleep 10
    
    # 验证服务
    echo "步骤5: 验证服务..."
    if ps -p $GUNICORN_PID > /dev/null; then
        echo "✅ Gunicorn进程正在运行"
    else
        echo "❌ Gunicorn进程未运行！"
        echo "查看错误日志："
        tail -30 $PROJECT_DIR/error.log
        exit 1
    fi
    
    # 测试健康检查
    HEALTH_CHECK=$(curl -s http://115.120.251.86:8900/api/health)
    if [ $? -eq 0 ]; then
        echo "✅ 健康检查通过"
        echo "响应: $HEALTH_CHECK"
    else
        echo "❌ 健康检查失败"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ 服务重启成功！"
    echo "=========================================="
    
else
    # 本地环境
    echo "📍 检测到本地环境"
    echo ""
    
    # 停止本地服务
    echo "步骤1: 停止本地服务..."
    pkill -f "python.*app.py" 2>/dev/null || true
    lsof -t -i:8900 | xargs kill -9 2>/dev/null || true
    sleep 2
    echo "✅ 本地服务已停止"
    echo ""
    
    # 进入main目录
    cd "$(dirname "$0")/main"
    
    # 启动服务
    echo "步骤2: 启动本地服务..."
    nohup python app.py > ../app.log 2>&1 &
    APP_PID=$!
    echo "✅ 服务已启动，进程ID: $APP_PID"
    echo ""
    
    # 等待服务启动
    echo "步骤3: 等待服务启动（5秒）..."
    sleep 5
    
    # 验证服务
    echo "步骤4: 验证服务..."
    if ps -p $APP_PID > /dev/null; then
        echo "✅ 服务进程正在运行"
    else
        echo "❌ 服务进程未运行！"
        echo "查看错误日志："
        tail -30 ../app.log
        exit 1
    fi
    
    # 测试健康检查
    HEALTH_CHECK=$(curl -s http://localhost:8900/api/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ 健康检查通过"
        echo "响应: $HEALTH_CHECK"
    else
        echo "⚠️  健康检查失败（可能服务还在启动中）"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ 本地服务重启完成！"
    echo "=========================================="
fi

