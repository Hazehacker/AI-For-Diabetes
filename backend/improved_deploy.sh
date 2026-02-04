#!/bin/bash
# 智糖小助手 - 改进的阿里云部署脚本
# 包含完整的修复和验证步骤

echo "🚀 开始智糖小助手改进版部署..."

# 检查当前目录
if [ ! -f "config.yaml" ]; then
    echo "❌ 错误: 请在项目根目录 (/ai/zhitang/smart-sugar-assistant) 运行此脚本"
    exit 1
fi

# 1. 拉取最新代码
echo "📥 步骤1: 拉取最新代码..."
git pull origin main

# 2. 停止旧服务
echo "🛑 步骤2: 停止旧服务..."
lsof -t -i:8900 | xargs -r kill -9

# 3. 配置阿里云镜像源
echo "📦 步骤3: 配置阿里云镜像源..."
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/main/
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/conda-forge/

# 4. 激活Conda环境
echo "🐍 步骤4: 激活Conda环境..."
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

# 5. 进入main目录并重新安装依赖
echo "📥 步骤5: 重新安装依赖..."
cd main
pip install -r requirements.txt

# 6. 验证代码修复
echo "🔍 步骤6: 验证代码修复..."

# 检查PyYAML
if python -c "import yaml; print('PyYAML OK')" 2>/dev/null; then
    echo "✅ PyYAML安装成功"
else
    echo "❌ PyYAML安装失败"
    exit 1
fi

# 检查Flask
if python -c "import flask; print('Flask OK')" 2>/dev/null; then
    echo "✅ Flask安装成功"
else
    echo "❌ Flask安装失败"
    exit 1
fi

# 检查TTS服务语法
if python -m py_compile services/tts_service.py 2>/dev/null; then
    echo "✅ TTS服务语法检查通过"
else
    echo "❌ TTS服务语法错误"
    exit 1
fi

# 运行综合测试
echo "🧪 运行综合验证测试..."
if python ../test_fix.py; then
    echo "✅ 所有验证测试通过"
else
    echo "❌ 部分验证测试失败"
    exit 1
fi

# 7. 检查私钥文件
echo "🔐 步骤7: 检查Coze私钥..."
if [ -f "../private_key.pem" ]; then
    echo "✅ Coze私钥文件存在"
else
    echo "⚠️ 警告: 私钥文件不存在 (../private_key.pem)"
    echo "ℹ️ 应用仍可启动，Coze功能将被禁用"
fi

# 8. 显示系统信息
echo ""
echo "📊 系统信息:"
echo "- Python版本: $(python --version)"
echo "- 当前目录: $(pwd)"
echo "- Conda环境: ${CONDA_DEFAULT_ENV:-'系统Python'}"
echo "- 私钥文件: $([ -f "../private_key.pem" ] && echo "存在" || echo "不存在")"

# 9. 启动新服务
echo ""
echo "🌟 步骤8: 启动新服务..."
gunicorn -w 4 -b 0.0.0.0:8900 \
         --timeout 300 \
         --worker-class gevent \
         --worker-connections 1000 \
         wsgi:application &

# 等待几秒让服务启动
sleep 3

# 检查服务是否启动成功
if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
    echo "✅ 服务启动成功！"
    echo "🌐 API地址: http://115.120.251.86:8900"
    echo "🏥 健康检查: http://115.120.251.86:8900/api/health"
    echo ""
    echo "📝 常用管理命令:"
    echo "- 查看进程: ps aux | grep gunicorn"
    echo "- 停止服务: pkill -f gunicorn"
    echo "- 查看日志: tail -f ../logs/zhitang.log"
else
    echo "❌ 服务启动失败，请检查上面的错误信息"
    exit 1
fi

echo ""
echo "🎉 部署完成！服务正在运行中。"
