#!/bin/bash
# 智糖小助手阿里云部署脚本
# 使用阿里云镜像源安装所有依赖

echo "🚀 开始部署智糖小助手到阿里云服务器..."

# 设置阿里云pip镜像源
echo "📦 配置阿里云pip镜像源..."
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3 -m venv myenv

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source myenv/bin/activate

# 进入main目录
cd main

# 安装项目依赖
echo "📥 安装项目依赖包..."
pip install -r requirements.txt

# 检查安装是否成功
echo "🔍 检查关键依赖..."
python -c "import yaml; print('✅ PyYAML安装成功')"
python -c "import flask; print('✅ Flask安装成功')"
python -c "import pymysql; print('✅ PyMySQL安装成功')"

# 启动服务
echo "🌟 启动智糖小助手服务..."
python app.py

echo "✅ 服务启动完成！"
echo "🌐 API地址: http://$(hostname -I | awk '{print $1}'):8900"
echo "🏥 健康检查: http://$(hostname -I | awk '{print $1}'):8900/api/health"
