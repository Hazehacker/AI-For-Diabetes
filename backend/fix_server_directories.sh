#!/bin/bash

# 修复服务器缺失目录的脚本
# 用法: 在服务器上运行 ./fix_server_directories.sh

echo "=== 修复服务器目录结构 ==="

# 获取项目根目录（脚本所在目录）
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "当前目录: $(pwd)"

# 1. 创建必要的目录
echo ""
echo "1. 创建必要的目录..."
mkdir -p logs
mkdir -p uploads
mkdir -p tts_cache
mkdir -p output
mkdir -p static/js

echo "✓ 目录创建完成"

# 2. 设置目录权限
echo ""
echo "2. 设置目录权限..."
chmod 755 logs uploads tts_cache output static
chmod 755 static/js 2>/dev/null || true

echo "✓ 权限设置完成"

# 3. 检查目录结构
echo ""
echo "3. 检查目录结构..."
for dir in logs uploads tts_cache output static; do
    if [ -d "$dir" ]; then
        echo "✓ $dir 存在"
    else
        echo "✗ $dir 不存在"
    fi
done

# 4. 检查配置文件
echo ""
echo "4. 检查配置文件..."
if [ -f "config.yaml" ]; then
    echo "✓ config.yaml 存在"
elif [ -f "config.yaml.example" ]; then
    echo "⚠️  config.yaml 不存在，从 config.yaml.example 复制..."
    cp config.yaml.example config.yaml
    echo "✓ 已创建 config.yaml，请修改其中的配置"
else
    echo "✗ 配置文件不存在"
fi

# 5. 检查前端页面目录
echo ""
echo "5. 检查前端页面目录..."
if [ -d "前端页面" ]; then
    echo "✓ 前端页面目录存在"
    ls -la 前端页面/*.png 2>/dev/null | head -3
else
    echo "✗ 前端页面目录不存在"
fi

echo ""
echo "=== 完成 ==="
echo ""
echo "现在可以启动服务了："
echo "  cd $PROJECT_ROOT/main"
echo "  /root/miniconda3/envs/myenv/bin/gunicorn --bind 0.0.0.0:8900 --workers 4 --worker-class gevent --worker-connections 1000 wsgi:application"
