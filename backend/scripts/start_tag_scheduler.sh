#!/bin/bash
# 标签提取调度服务启动脚本

# 设置脚本所在目录为工作目录
cd "$(dirname "$0")/.."

echo "🚀 启动标签提取调度服务..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请确保已安装Python3"
    exit 1
fi

# 检查日志目录
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "📁 创建日志目录: logs"
fi

# 设置日志文件
LOG_FILE="logs/tag_scheduler_$(date +%Y%m%d_%H%M%S).log"

echo "📝 日志文件: $LOG_FILE"

# 启动服务
echo "🔄 启动标签提取调度服务..."
echo "💡 按 Ctrl+C 停止服务"
echo "📊 查看日志: tail -f $LOG_FILE"
echo ""

# 使用nohup在后台运行，并重定向输出到日志文件
nohup python3 scripts/tag_extraction_worker.py \
    --interval 300 \
    --verbose \
    > "$LOG_FILE" 2>&1 &

# 获取进程ID
PID=$!
echo "✅ 服务已启动 (PID: $PID)"

# 保存PID到文件
echo $PID > tag_scheduler.pid
echo "💾 PID已保存到: tag_scheduler.pid"

# 等待一下确保服务启动
sleep 2

# 检查服务是否还在运行
if kill -0 $PID 2>/dev/null; then
    echo "🎉 服务启动成功！"
    echo ""
    echo "📋 管理命令:"
    echo "  停止服务: kill $PID 或 pkill -f tag_extraction_worker.py"
    echo "  查看状态: ps aux | grep tag_extraction_worker"
    echo "  查看日志: tail -f $LOG_FILE"
else
    echo "❌ 服务启动失败，请查看日志文件: $LOG_FILE"
    exit 1
fi
