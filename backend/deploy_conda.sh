#!/bin/bash
# 智糖小助手Conda环境阿里云部署脚本

echo "🚀 开始使用Conda部署智糖小助手到阿里云服务器..."

# 配置阿里云pip镜像源
echo "📦 配置阿里云pip镜像源..."
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

echo "🐍 配置阿里云conda镜像源..."
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/main/
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/free/
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/bioconda/

# 检查是否已有myenv环境，如果有则删除重建
if conda env list | grep -q "myenv"; then
    echo "🔄 删除已存在的myenv环境..."
    conda env remove -n myenv -y
fi

# 创建conda环境
echo "🔧 创建conda环境..."
conda create -n myenv python=3.9 -y

# 激活环境
echo "✅ 激活conda环境..."
# 尝试多种激活方式
if [ -f ~/miniconda3/bin/activate ]; then
    source ~/miniconda3/bin/activate myenv
elif [ -f ~/anaconda3/bin/activate ]; then
    source ~/anaconda3/bin/activate myenv
else
    echo "⚠️ 尝试通用激活方式..."
    eval "$(conda shell.bash hook)"
    conda activate myenv
fi

# 检查环境是否激活成功
if [ "$CONDA_DEFAULT_ENV" != "myenv" ]; then
    echo "❌ Conda环境激活失败，请手动执行: conda activate myenv"
    exit 1
fi

echo "📍 当前环境: $CONDA_DEFAULT_ENV"
echo "🐍 Python路径: $(which python)"

# 进入main目录
cd main

# 安装项目依赖
echo "📥 安装项目依赖包..."
pip install -r requirements.txt

# 检查安装是否成功
echo "🔍 检查关键依赖..."
python -c "import yaml; print('✅ PyYAML安装成功')" || echo "❌ PyYAML安装失败"
python -c "import flask; print('✅ Flask安装成功')" || echo "❌ Flask安装失败"
python -c "import pymysql; print('✅ PyMySQL安装成功')" || echo "❌ PyMySQL安装失败"

# 显示环境信息
echo "📊 环境信息:"
echo "- Conda环境: $CONDA_DEFAULT_ENV"
echo "- Python版本: $(python --version)"
echo "- Pip版本: $(pip --version)"

# 启动服务
echo "🌟 启动智糖小助手服务..."
python app.py

echo "✅ 服务启动完成！"
echo "🌐 API地址: http://$(hostname -I | awk '{print $1}'):8900"
echo "🏥 健康检查: http://$(hostname -I | awk '{print $1}'):8900/api/health"
