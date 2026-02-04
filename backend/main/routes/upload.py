"""
图片上传和静态文件服务路由
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

提供FAQ图片上传和静态文件访问功能：
- POST /api/faq/upload-image: 上传FAQ图片
- GET /uploads/<path:filename>: 访问上传的文件
- GET /<filename>: 访问根目录静态文件（如logo.png）

作者: 智糖团队
日期: 2025-01-21
"""

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from utils.jwt_helper import no_auth_required as token_required
from utils.logger import get_logger
from utils.config_loader import get_config
import os
import uuid
from datetime import datetime
import mimetypes

logger = get_logger(__name__)

# 创建Blueprint
upload_bp = Blueprint('upload', __name__)

# 允许的图片扩展名
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# 前端页面目录（用于静态文件访问）
# __file__ 是 main/routes/upload.py
# 需要往上两层到项目根目录，再进入前端页面目录
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    '前端页面'
)
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

logger.info(f"📁 静态文件目录: {FRONTEND_DIR}")

# 最大文件大小（从配置读取，默认10MB）
MAX_IMAGE_SIZE = get_config('UPLOAD.MAX_FILE_SIZE', 10 * 1024 * 1024)

# 上传目录
FAQ_IMAGES_DIR = 'uploads/faq_images'


def allowed_image_file(filename):
    """
    检查文件是否为允许的图片类型
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def generate_unique_filename(original_filename):
    """
    生成唯一的文件名（UUID + 时间戳 + 原始扩展名）
    
    Args:
        original_filename: 原始文件名
        
    Returns:
        str: 唯一文件名
    """
    # 获取文件扩展名
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # 生成唯一文件名：UUID_时间戳.扩展名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
    
    return f"{unique_id}_{timestamp}.{ext}"


def ensure_upload_directory():
    """
    确保上传目录存在
    """
    if not os.path.exists(FAQ_IMAGES_DIR):
        os.makedirs(FAQ_IMAGES_DIR, exist_ok=True)
        logger.info(f"✅ 创建上传目录: {FAQ_IMAGES_DIR}")


@upload_bp.route('/api/faq/upload-image', methods=['POST'], endpoint='upload_faq_image')
@token_required
def upload_faq_image(user_id):
    """
    上传FAQ图片
    
    Headers:
        Authorization: Bearer <token>
        
    Body:
        multipart/form-data
        file: 图片文件 (jpg, jpeg, png, gif)
        
    Returns:
        JSON: 上传结果，包含图片URL
    """
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '未找到上传文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '文件名为空'
            }), 400
        
        # 验证文件类型
        if not allowed_image_file(file.filename):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': f'不支持的文件类型，仅支持: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if file_size > MAX_IMAGE_SIZE:
            max_size_mb = MAX_IMAGE_SIZE / (1024 * 1024)
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': f'文件大小超过限制（最大{max_size_mb:.1f}MB）'
            }), 400
        
        # 确保上传目录存在
        ensure_upload_directory()
        
        # 生成唯一文件名
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(FAQ_IMAGES_DIR, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 生成访问URL
        base_url = get_config('API_BASE_URL', 'https://chat.cmkjai.com')
        file_url = f"{base_url}/uploads/faq_images/{unique_filename}"
        
        logger.info(f"✅ 图片上传成功: {unique_filename} (大小: {file_size} bytes)")
        
        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'data': {
                'url': file_url,
                'filename': unique_filename,
                'size': file_size
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 图片上传失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': f'图片上传失败: {str(e)}'
        }), 500


@upload_bp.route('/uploads/<path:filename>', methods=['GET'], endpoint='serve_uploaded_file')
def serve_uploaded_file(filename):
    """
    访问上传的文件
    
    Path Parameters:
        filename: 文件路径（相对于uploads目录）
        
    Returns:
        文件内容
    """
    try:
        # 获取完整的文件路径（相对于main目录）
        file_path = os.path.join('uploads', filename)
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ 文件不存在: {file_path}")
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 获取MIME类型
        mimetype = mimetypes.guess_type(file_path)[0]
        if mimetype is None:
            # 默认MIME类型
            ext = basename.rsplit('.', 1)[1].lower() if '.' in basename else ''
            mimetype_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'txt': 'text/plain',
                'pdf': 'application/pdf'
            }
            mimetype = mimetype_map.get(ext, 'application/octet-stream')
        
        # 返回文件
        return send_from_directory(
            directory,
            basename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"❌ 文件访问失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': f'文件访问失败: {str(e)}'
        }), 500


@upload_bp.route('/<filename>', methods=['GET'], endpoint='serve_root_file')
def serve_root_file(filename):
    """
    访问根目录的静态文件（如logo.png, nvsheng.png等）
    从前端页面目录提供文件
    
    Path Parameters:
        filename: 文件名
        
    Returns:
        文件内容
    """
    try:
        # 扩展允许的根目录文件列表
        allowed_root_files = [
            'logo.png', 'favicon.ico', 
            'nvsheng.png', 'nansheng.png',
            'silence_1s.mp3'
        ]
        
        if filename not in allowed_root_files:
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 从前端页面目录查找文件
        file_path = os.path.join(FRONTEND_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ 前端页面文件不存在: {file_path}")
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 获取MIME类型
        mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            mimetype_map = {
                'png': 'image/png',
                'ico': 'image/x-icon',
                'mp3': 'audio/mpeg'
            }
            mimetype = mimetype_map.get(ext, 'application/octet-stream')
        
        # 返回文件
        return send_from_directory(
            FRONTEND_DIR,
            filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"❌ 根目录文件访问失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': f'文件访问失败: {str(e)}'
        }), 500
