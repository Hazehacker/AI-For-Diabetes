#!/bin/bash

# 更新 Nginx 配置脚本
# 用法: ./update_nginx_config.sh

echo "=== 更新 Nginx 配置 ==="

# 1. 备份当前配置
echo "1. 备份当前配置..."
sudo cp /etc/nginx/sites-available/chat.cmkjai.com /etc/nginx/sites-available/chat.cmkjai.com.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
sudo cp /etc/nginx/conf.d/chat.cmkjai.com.conf /etc/nginx/conf.d/chat.cmkjai.com.conf.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
echo "未找到现有配置文件，将创建新配置"

# 2. 复制新配置到 nginx 目录
echo "2. 复制新配置..."
if [ -d "/etc/nginx/sites-available" ]; then
    sudo cp nginx_chat_config_fixed.conf /etc/nginx/sites-available/chat.cmkjai.com
    sudo ln -sf /etc/nginx/sites-available/chat.cmkjai.com /etc/nginx/sites-enabled/chat.cmkjai.com
    echo "配置已复制到 /etc/nginx/sites-available/chat.cmkjai.com"
elif [ -d "/etc/nginx/conf.d" ]; then
    sudo cp nginx_chat_config_fixed.conf /etc/nginx/conf.d/chat.cmkjai.com.conf
    echo "配置已复制到 /etc/nginx/conf.d/chat.cmkjai.com.conf"
else
    echo "错误: 未找到 nginx 配置目录"
    exit 1
fi

# 3. 测试配置
echo "3. 测试 Nginx 配置..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "错误: Nginx 配置测试失败！"
    echo "请检查配置文件"
    exit 1
fi

# 4. 重新加载 nginx
echo "4. 重新加载 Nginx..."
sudo systemctl reload nginx || sudo nginx -s reload
if [ $? -eq 0 ]; then
    echo "✓ Nginx 配置已成功更新并重新加载"
else
    echo "错误: Nginx 重新加载失败"
    exit 1
fi

# 5. 测试服务
echo ""
echo "5. 测试服务..."
echo "测试后端服务:"
curl -I http://127.0.0.1:8900/nvsheng.png 2>/dev/null | head -n 1

echo ""
echo "测试 HTTPS 访问:"
curl -I https://chat.cmkjai.com/nvsheng.png 2>/dev/null | head -n 1

echo ""
echo "=== 完成 ==="
echo "如果图片还是无法访问，请检查:"
echo "1. 后端服务是否正常: curl http://127.0.0.1:8900/nvsheng.png"
echo "2. 图片文件是否存在"
echo "3. 查看 nginx 错误日志: sudo tail -f /var/log/nginx/chat.error.log"
