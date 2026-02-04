# Gunicorn 配置文件
# 智糖小助手生产环境配置

import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8900"
backlog = 2048

# Worker 进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志
accesslog = "../logs/access.log"
errorlog = "../logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "zhitang-assistant"

# 用户和组
# user = "www-data"
# group = "www-data"

# 临时目录
tmp_upload_dir = None

# SSL (如果需要)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# 环境变量
raw_env = [
    'FLASK_ENV=production',
]

def when_ready(server):
    """服务器启动完成时的回调"""
    server.log.info("智糖小助手服务已启动，监听端口 8900")

def worker_int(worker):
    """Worker进程中断时的回调"""
    worker.log.info("Worker进程被中断")

def pre_fork(server, worker):
    """Worker进程fork前的回调"""
    server.log.info("Worker进程即将启动")

def post_fork(server, worker):
    """Worker进程fork后的回调"""
    server.log.info("Worker进程已启动 (PID: %s)", worker.pid)
