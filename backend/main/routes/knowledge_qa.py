"""
知识问答路由
~~~~~~~~~~~

知识问答API端点：
- 知识检索
- 问答接口
- 知识库统计

作者: 智糖团队
日期: 2025-01-21
"""

from flask import request, jsonify, Blueprint
from utils.jwt_helper import no_auth_required as token_required
from services.knowledge_qa_service import get_knowledge_qa_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建Blueprint
knowledge_qa_bp = Blueprint('knowledge_qa', __name__, url_prefix='/api/knowledge-qa')

# 获取服务实例
knowledge_qa_service = get_knowledge_qa_service()


@knowledge_qa_bp.route('/search', methods=['POST'], endpoint='search_knowledge')
@token_required
def search_knowledge(user_id):
    """
    检索知识库
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "query": "查询文本",
            "top_k": 3,
            "min_similarity": 0.1
        }
    
    Returns:
        JSON: 检索结果列表
    """
    try:
        data = request.get_json() or {}
        
        query = data.get('query')
        if not query:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '查询文本不能为空'
            }), 400
        
        top_k = int(data.get('top_k', 3))
        min_similarity = float(data.get('min_similarity', 0.1))
        
        # 检索知识
        results = knowledge_qa_service.search_knowledge(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity
        )
        
        return jsonify({
            'code': 200,
            'data': {
                'query': query,
                'count': len(results),
                'results': results
            },
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 知识检索失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_qa_bp.route('/answer', methods=['POST'], endpoint='answer_question')
@token_required
def answer_question(user_id):
    """
    回答问题
    
    Headers:
        Authorization: Bearer <token>
    
    Body:
        {
            "question": "用户问题",
            "top_k": 3,
            "use_ai": false
        }
    
    Returns:
        JSON: 回答结果
    """
    try:
        data = request.get_json() or {}
        
        question = data.get('question')
        if not question:
            return jsonify({
                'code': 400,
                'data': {},
                'success': False,
                'message': '问题不能为空'
            }), 400
        
        top_k = int(data.get('top_k', 3))
        use_ai = data.get('use_ai', False)
        
        # 回答问题
        result = knowledge_qa_service.answer_question(
            question=question,
            top_k=top_k,
            use_ai=use_ai
        )
        
        return jsonify({
            'code': 200 if result.get('success') else 404,
            'data': result.get('data', {}) if result.get('success') else {},
            'success': result.get('success'),
            'message': result.get('message', '')
        }), 200 if result.get('success') else 404
        
    except Exception as e:
        logger.error(f"❌ 回答问题失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500


@knowledge_qa_bp.route('/stats', methods=['GET'], endpoint='get_knowledge_stats')
@token_required
def get_knowledge_stats(user_id):
    """
    获取知识库统计信息
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: 统计信息
    """
    try:
        stats = knowledge_qa_service.get_knowledge_stats()
        return jsonify({
            'code': 200,
            'data': {'stats': stats},
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'data': {},
            'success': False,
            'message': str(e)
        }), 500

