"""
智糖小助手主应用 - 【核心文件】
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask主应用入口，提供RESTful API服务

功能：
- 应用初始化和配置管理
- Blueprint路由注册和中间件设置
- 数据库连接池初始化
- CORS跨域支持
- 请求日志记录和错误处理

核心组件：
- 用户认证和授权
- 对话服务（流式对话、TTS集成）
- 知识问答（FAQ检索、AI回答）
- 用户标签管理
- 提示词管理
- 打卡积分系统

作者: 智糖团队
日期: 2025-01-15
版本: 2.0.0
"""

from flask import Flask, request
from flask_cors import CORS
import os

# Monkey patch Flask to handle decorated functions properly
import functools

def _patched_endpoint_from_view_func(view_func):
    """修复后的endpoint提取函数，处理装饰器返回None的情况"""
    if view_func is None:
        return "auto_generated_endpoint"
    # 如果函数有__wrapped__属性，说明它是装饰器返回的函数，使用原始函数名
    if hasattr(view_func, '__wrapped__'):
        return view_func.__wrapped__.__name__
    return view_func.__name__

try:
    # Flask 2.x
    import flask.scaffold
    flask.scaffold._endpoint_from_view_func = _patched_endpoint_from_view_func
except ImportError:
    # Flask 3.x
    try:
        import flask.app as flask_app
        flask_app.Flask._endpoint_from_view_func = _patched_endpoint_from_view_func
    except AttributeError:
        # 如果都找不到，创建一个兼容的函数
        pass

# 导入工具模块
from utils.config_loader import load_config, get_config
from utils.logger import setup_logger, get_logger
from utils.database import init_db_pool

# 导入路由
from routes import register_blueprints

# 初始化日志
logger = setup_logger('zhitang', log_level='INFO')

# 加载配置
try:
    config = load_config()
    logger.info("✅ 配置加载成功")
except Exception as e:
    logger.error(f"❌ 配置加载失败: {str(e)}")
    raise


def create_app():
    """
    创建Flask应用实例
    
    Returns:
        Flask: 配置好的Flask应用
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(project_root, '前端页面')
    
    # 创建Flask应用，配置静态文件目录
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path='')
    
    # 加载配置
    app.config['SECRET_KEY'] = get_config('JWT.SECRET_KEY', 'default-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = get_config('UPLOAD.MAX_FILE_SIZE', 100 * 1024 * 1024)  # 默认100MB
    
    # CORS将在before_request钩子中处理
    logger.info("✅ CORS将在before_request钩子中处理")
    
    # 初始化数据库连接池
    try:
        init_db_pool()
        logger.info("✅ 数据库连接池初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {str(e)}")
        # 不抛出异常，允许应用继续运行（用于调试）
    
    # 注册所有Blueprint
    register_blueprints(app)
    
    # 初始化WebSocket ASR服务
    try:
        from services.websocket_asr_service import init_websocket_asr
        init_websocket_asr(app)
        logger.info("✅ WebSocket ASR服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠️ WebSocket ASR服务初始化失败: {str(e)}")
        # 继续运行，不影响其他功能

    # 初始化标签提取调度服务（默认不启动，需要时手动启动）
    try:
        from services.tag_extraction_scheduler import get_tag_extraction_scheduler
        tag_scheduler = get_tag_extraction_scheduler()
        # tag_scheduler.start()  # 注释掉自动启动，需要时通过API手动启动
        logger.info("✅ 标签提取调度服务初始化完成（未自动启动）")
    except Exception as e:
        logger.warning(f"⚠️ 标签提取调度服务初始化失败: {str(e)}")
        # 继续运行，不影响其他功能
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册钩子函数
    register_hooks(app)
    
    logger.info("🚀 智糖小助手应用初始化完成")
    
    return app


def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    from flask import jsonify
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '接口不存在',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"❌ 服务器内部错误: {str(error)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': 'Internal Server Error'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': '请求参数错误',
            'error': 'Bad Request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': '未授权，请先登录',
            'error': 'Unauthorized'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': '权限不足',
            'error': 'Forbidden'
        }), 403
    
    logger.info("✅ 错误处理器已注册")


def register_hooks(app):
    """
    注册Flask钩子函数
    
    Args:
        app: Flask应用实例
    """
    @app.before_request
    def before_request():
        """请求前处理"""
        pass
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 添加安全头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # 添加CORS头 - 允许所有域名
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            # 强制设置凭证头，不管是什么请求方法
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Accept-Language'
            response.headers['Access-Control-Max-Age'] = '3600'

        return response
    
    logger.info("✅ 请求钩子已注册")


# 创建应用实例
app = create_app()


# 主程序入口
if __name__ == '__main__':
    port = int(get_config('API_PORT', 8900))
    debug = get_config('DEBUG', False)
    
    logger.info(f"🌟 智糖小助手启动中...")
    logger.info(f"📍 监听端口: {port}")
    logger.info(f"🐛 调试模式: {'开启' if debug else '关闭'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

