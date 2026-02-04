#!/bin/bash
# 智糖小助手阿里云部署问题修复脚本

echo "🔧 开始修复智糖小助手阿里云部署问题..."

# 检查当前目录
if [ ! -f "config.yaml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 配置阿里云镜像源
echo "📦 配置阿里云pip镜像源..."
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

echo "🐍 配置阿里云conda镜像源..."
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/main/
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/conda-forge/

# 激活Conda环境
echo "✅ 激活Conda环境..."
if command -v conda &> /dev/null; then
    # 尝试多种激活方式
    if [ -f ~/miniconda3/bin/activate ]; then
        source ~/miniconda3/bin/activate myenv
    elif [ -f ~/anaconda3/bin/activate ]; then
        source ~/anaconda3/bin/activate myenv
    else
        eval "$(conda shell.bash hook)"
        conda activate myenv
    fi
else
    echo "⚠️ Conda未找到，继续使用系统Python"
fi

# 进入main目录
echo "📁 进入main目录..."
cd main

# 重新安装依赖
echo "📥 重新安装所有依赖..."
pip install -r requirements.txt

# 验证修复
echo "🔍 验证修复结果..."

# 检查PyYAML
python -c "import yaml; print('✅ PyYAML安装成功')" || echo "❌ PyYAML安装失败"

# 检查Flask
python -c "import flask; print('✅ Flask安装成功')" || echo "❌ Flask安装失败"

# 检查PyMySQL
python -c "import pymysql; print('✅ PyMySQL安装成功')" || echo "❌ PyMySQL安装失败"

# 检查语法错误
python -m py_compile services/tts_service.py && echo "✅ TTS服务语法检查通过" || echo "❌ TTS服务语法错误"

# 检查应用导入
python -c "from app import app; print('✅ 应用导入成功')" || echo "❌ 应用导入失败"

# 检查私钥文件
if [ -f "../private_key.pem" ]; then
    echo "✅ Coze私钥文件存在"
else
    echo "⚠️ 警告: Coze私钥文件不存在 (../private_key.pem)"
    echo "请将Coze私钥文件放置在项目根目录"
fi

echo ""
echo "📊 系统信息:"
echo "- Python版本: $(python --version)"
echo "- 当前目录: $(pwd)"
echo "- Conda环境: ${CONDA_DEFAULT_ENV:-'系统Python'}"

echo ""
echo "🎯 下一步操作:"
echo "1. 如果私钥文件不存在，请先配置Coze私钥"
echo "2. 运行以下命令启动服务:"
echo "   gunicorn -w 4 -b 0.0.0.0:8900 --timeout 300 --worker-class gevent --worker-connections 1000 wsgi:application"
echo ""
echo "✨ 修复完成！"
