"""
智糖小助手 - 路由层
~~~~~~~~~~~~~~~~~~~

提供RESTful API路由定义，包括：
- 认证路由
- 用户管理路由
- 对话路由
- TTS路由
- 新手引导路由
- 标签管理路由
- 打卡路由
- 积分路由
- 知识库路由
- 前端页面路由

作者: 智糖团队
日期: 2025-01-15
"""

from flask import Blueprint

# 创建所有Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api')
user_bp = Blueprint('user', __name__, url_prefix='/api')
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
tts_bp = Blueprint('tts', __name__, url_prefix='/api')
tag_bp = Blueprint('tag', __name__, url_prefix='/api/tags')

# 导入路由处理函数（这样会自动注册路由）
from .auth import auth_bp
from .user import user_bp
from .chat import chat_bp
from .tts import tts_bp
from .tag import tag_bp
from .checkin import checkin_bp
from .points import points_bp
from .knowledge import knowledge_bp
from .prompt import prompt_bp
from .knowledge_qa import knowledge_qa_bp
from .faq_management import faq_bp
from .tag_scheduler import tag_scheduler_bp
from .admin_checkin import admin_checkin_bp
from .upload import upload_bp

# 从独立文件导入额外的Blueprint
from .frontend import frontend_bp


def register_blueprints(app):
    """
    注册所有Blueprint到Flask应用
    
    Args:
        app: Flask应用实例
    """
    # 处理CORS OPTIONS请求
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_cors_options(path):
        from flask import request
        origin = request.headers.get('Origin')
        # 允许所有域名
        if origin:
            response = app.response_class('', status=200)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Accept-Language'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response

        return app.response_class('Origin not allowed', status=403)

    # 注册前端页面路由（无前缀，直接访问）
    app.register_blueprint(frontend_bp)
    
    # 注册上传和静态文件路由（无前缀，直接访问）
    app.register_blueprint(upload_bp)
    
    # 注册API路由
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(tts_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(points_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(prompt_bp)
    app.register_blueprint(knowledge_qa_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(tag_scheduler_bp)
    app.register_blueprint(admin_checkin_bp)



__all__ = [
    'frontend_bp',
    'auth_bp',
    'user_bp',
    'chat_bp',
    'tts_bp',
    'tag_bp',
    'checkin_bp',
    'points_bp',
    'knowledge_bp',
    'prompt_bp',
    'knowledge_qa_bp',
    'faq_bp',
    'tag_scheduler_bp',
    'admin_checkin_bp',
    'upload_bp',
    'register_blueprints',
]

