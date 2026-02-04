"""
知识库路由
~~~~~~~~~

知识库管理的API端点：
- 文件上传
- 数据集查询
- 文件删除

作者: 智糖团队
日期: 2025-01-15
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from services.knowledge_service import get_knowledge_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建Blueprint
knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

# 获取服务实例
knowledge_service = get_knowledge_service()


@knowledge_bp.route('/upload', methods=['POST'], endpoint='upload_file')
@token_required
def upload_file(user_id):
    """
    上传文件到知识库
    
    Headers:
        Authorization: Bearer <token>
    
    Form Data:
        file: 文件内容（必需）
        file_name: 文件名（可选，不传则使用上传文件的原始文件名）
        dataset_id: 数据集ID（可选，不传则使用默认数据集）

    注意: 如果不传dataset_id，将使用默认数据集ID: 110b7e73-3050-49f4-b424-910951a016d9
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '必须上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '文件名不能为空'
            }), 400
        
        # 获取表单数据
        file_name = request.form.get('file_name')
        dataset_id = request.form.get('dataset_id')

        # 如果没有指定file_name，使用上传文件的原始文件名
        if not file_name:
            file_name = file.filename

        # 读取文件内容
        file_data = file.read()

        result = knowledge_service.upload_file_data(
            user_id, file_data, file_name, dataset_id
        )
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 上传文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/files/view/<path:file_path>', methods=['GET'], endpoint='view_file')
def view_file(file_path):
    """
    通过文件链接查看/下载文件

    Path:
        file_path: 文件路径（从文件链接中提取）
    """
    try:
        from flask import send_file
        from werkzeug.utils import safe_join
        from utils.config_loader import get_config
        import os

        # 获取文件存储目录 - 使用与上传时相同的逻辑
        upload_dir = get_config('UPLOAD.DIR', 'uploads/knowledge')

        # 如果是相对路径，相对于项目根目录
        if not os.path.isabs(upload_dir):
            # 获取项目根目录的绝对路径
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            parent_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(parent_dir)
            upload_dir = os.path.join(project_root, upload_dir)

        file_full_path = safe_join(upload_dir, file_path)
        
        if not file_full_path or not os.path.exists(file_full_path):
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '文件不存在'
            }), 404
        
        return send_file(
            file_full_path,
            as_attachment=False,  # 预览模式，不强制下载
            download_name=os.path.basename(file_path)
        )
        
    except Exception as e:
        logger.error(f"❌ 查看文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/files/download/<path:file_path>', methods=['GET'], endpoint='download_file_by_path')
def download_file_by_path(file_path):
    """
    通过文件链接下载文件

    Path:
        file_path: 文件路径（从文件链接中提取）
    """
    try:
        from flask import send_file
        from werkzeug.utils import safe_join
        from utils.config_loader import get_config
        import os

        # 获取文件存储目录 - 使用与上传时相同的逻辑
        upload_dir = get_config('UPLOAD.DIR', 'uploads/knowledge')

        # 如果是相对路径，相对于项目根目录
        if not os.path.isabs(upload_dir):
            # 获取项目根目录的绝对路径
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            parent_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(parent_dir)
            upload_dir = os.path.join(project_root, upload_dir)

        file_full_path = safe_join(upload_dir, file_path)
        
        if not file_full_path or not os.path.exists(file_full_path):
            return jsonify({
                'code': 404,
                'data': {},
                'success': False,
                'message': '文件不存在'
            }), 404
        
        return send_file(
            file_full_path,
            as_attachment=True,  # 下载模式
            download_name=os.path.basename(file_path)
        )
        
    except Exception as e:
        logger.error(f"❌ 下载文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/datasets', methods=['GET'], endpoint='list_datasets')
@token_required
def list_datasets(user_id):
    """
    列出数据集（知识库文件列表）
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        dataset_id: 数据集ID（可选）
        file_name: 文档名称（可选，支持模糊查询）
        file_type: 文档类型（可选，如：pdf, txt, docx等）
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        dataset_id = request.args.get('dataset_id')
        file_name = request.args.get('file_name')
        file_type = request.args.get('file_type')
        
        result = knowledge_service.list_datasets(
            user_id, page, page_size, dataset_id, file_name, file_type
        )
        return jsonify({
            'code': 200,
            'data': result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取数据集列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/datasets', methods=['POST'], endpoint='create_dataset')
@token_required
def create_dataset(user_id):
    """
    创建数据集
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "name": "数据集名称",
            "description": "描述"
        }
    """
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '数据集名称不能为空'
            }), 400
        
        result = knowledge_service.create_dataset(user_id, name, description)
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 创建数据集失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/files/<file_id>', methods=['DELETE'], endpoint='delete_file')
@token_required
def delete_file(user_id, file_id):
    """
    删除知识库文件
    
    Headers:
        Authorization: Bearer <token>
    
    Query:
        dataset_id: 数据集ID
    """
    try:
        dataset_id = request.args.get('dataset_id')
        
        result = knowledge_service.delete_file(user_id, file_id, dataset_id)
        return jsonify({
            'code': 200 if result.get('success') else 400,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ 删除文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_bp.route('/files/<file_id>/status', methods=['PATCH'], endpoint='update_document_status')
@token_required
def update_document_status(user_id, file_id):
    """
    更新文档启用/禁用状态

    注意: 此功能暂未实现，Dify API当前不支持更新文档状态

    Headers:
        Authorization: Bearer <token>

    Query:
        dataset_id: 数据集ID

    Body:
        {
            "enabled": true/false
        }
    """
    try:
        data = request.get_json()

        if not data or 'enabled' not in data:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '缺少enabled字段'
            }), 400

        enabled = data['enabled']
        if not isinstance(enabled, bool):
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': 'enabled必须是布尔值'
            }), 400

        dataset_id = request.args.get('dataset_id')

        result = knowledge_service.update_document_status(user_id, file_id, enabled, dataset_id)
        return jsonify({
            'code': 200 if result.get('success') else 501,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 501  # 501 Not Implemented

    except Exception as e:
        logger.error(f"❌ 更新文档状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

