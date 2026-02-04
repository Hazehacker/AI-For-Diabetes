"""
前端页面路由模块
~~~~~~~~~~~~~~~~

提供前端HTML页面的访问路由

作者: 智糖团队
日期: 2025-01-14
"""

from flask import Blueprint, send_from_directory, abort
from utils.logger import get_logger
import os

logger = get_logger(__name__)

# 创建Blueprint
frontend_bp = Blueprint('frontend', __name__)

# 前端页面目录（相对于main目录）
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '前端页面')
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

logger.info(f"📁 前端页面目录: {FRONTEND_DIR}")


@frontend_bp.route('/')
def index():
    """
    主页 - 重定向到登录页
    """
    try:
        return send_from_directory(FRONTEND_DIR, 'P-LOGIN.html')
    except Exception as e:
        logger.error(f"❌ 加载主页失败: {str(e)}")
        abort(404)


@frontend_bp.route('/login')
@frontend_bp.route('/P-LOGIN.html')
def login_page():
    """
    登录页面
    """
    try:
        return send_from_directory(FRONTEND_DIR, 'P-LOGIN.html')
    except Exception as e:
        logger.error(f"❌ 加载登录页失败: {str(e)}")
        abort(404)


@frontend_bp.route('/chat')
@frontend_bp.route('/P-CHAT.html')
def chat_page():
    """
    对话页面
    """
    try:
        return send_from_directory(FRONTEND_DIR, 'P-CHAT.html')
    except Exception as e:
        logger.error(f"❌ 加载对话页失败: {str(e)}")
        abort(404)


@frontend_bp.route('/home')
@frontend_bp.route('/P-HOME.html')
def home_page():
    """
    首页
    """
    try:
        return send_from_directory(FRONTEND_DIR, 'P-HOME.html')
    except Exception as e:
        logger.error(f"❌ 加载首页失败: {str(e)}")
        abort(404)


@frontend_bp.route('/config.js')
def config_js():
    """
    前端配置文件
    """
    try:
        return send_from_directory(FRONTEND_DIR, 'config.js')
    except Exception as e:
        logger.error(f"❌ 加载配置文件失败: {str(e)}")
        abort(404)


@frontend_bp.route('/libs/<path:filename>')
def libs_files(filename):
    """
    前端库文件 (JS, CSS等)
    """
    try:
        libs_dir = os.path.join(FRONTEND_DIR, 'libs')
        return send_from_directory(libs_dir, filename)
    except Exception as e:
        logger.error(f"❌ 加载库文件失败: {filename}, 错误: {str(e)}")
        abort(404)


@frontend_bp.route('/<path:filename>')
def static_files(filename):
    """
    前端静态资源文件 (MP3, 图片等)
    注意：这个路由应该放在最后，避免覆盖其他路由
    """
    # 排除已定义的路由
    excluded_files = [
        'P-LOGIN.html', 'P-CHAT.html', 'P-HOME.html', 
        'P-CHECKIN.html', 'P-SETTINGS.html', 'P-USER_PROFILE.html',
        'config.js', 'index.html'
    ]
    
    if filename in excluded_files:
        abort(404)
    
    try:
        file_path = os.path.join(FRONTEND_DIR, filename)
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            abort(404)
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception as e:
        logger.error(f"❌ 加载静态文件失败: {filename}, 错误: {str(e)}")
        abort(404)


logger.info("✅ 前端页面路由已加载")

