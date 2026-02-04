import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from flask import Flask, request, jsonify, Blueprint, render_template
from flask_cors import CORS
import pymysql
import uuid  # 添加uuid模块
import logging  # 添加日志模块

zhishiku_bp = Blueprint('zhishikuguanli', __name__,url_prefix='/zhishiku/')

# 配置日志，输出到文件
logging.basicConfig(filename='zhishikuguanli.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库配置
DB_CONFIG = {
    'host': '120.92.216.191',
    'port': 3306,
    'user': 'dwetl',
    'password': '4*vBlG&$w6GPKkLu',
    'database': 'coach',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
# 设置固定的API Key
knowledge_api_key = "xY9Ls0jYgSr3r5UgGOQYeKUvxkNd43D1"


@zhishiku_bp.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': '服务器运行正常'
    })

@zhishiku_bp.route('/api/wiki_nodes/<space_id>', methods=['GET'])
def get_all_wiki_nodes(space_id):
    try:
        all_nodes = asyncio.run(async_get_all_wiki_nodes(space_id))
        return jsonify({
            'status': 'success',
            'data': all_nodes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

async def async_get_all_wiki_nodes(space_id):
    async with aiohttp.ClientSession() as session:
        return await get_wiki_nodes(space_id, session)

async def get_tenant_access_token(session: aiohttp.ClientSession) -> str:
    """异步获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": "cli_a7b45d900837d00c",
        "app_secret": "W9vEUngUtWYYdO4ejp2qeblbHq7L1wo3"
    }
    
    async with session.post(url, headers=headers, json=data) as response:
        data = await response.json()
        return data.get("tenant_access_token")

async def get_wiki_nodes(space_id: str, session: aiohttp.ClientSession, parent_node_token: str = None, access_token: str = None) -> List[Dict[str, Any]]:
    """异步递归获取知识库所有节点"""
    if access_token is None:
        access_token = await get_tenant_access_token(session)
    
    all_node_tokens = []
    
    base_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes?page_size=50"
    url = f"{base_url}&parent_node_token={parent_node_token}" if parent_node_token else base_url
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            
            if data.get("code") == 0 and "data" in data:
                items = data["data"]["items"]
                
                tasks = []
                
                for item in items:
                    node_token = item["node_token"]
                    has_child = item["has_child"]
                    title = item["title"]
                    
                    # 只有当节点没有子节点时才添加到结果中
                    if (not has_child) and (item["obj_type"] == "docx"):
                        all_node_tokens.append({
                            "node_token": node_token,
                            "title": title,
                            "has_child": has_child
                        })
                    
                    if has_child:
                        # 创建异步任务
                        task = get_wiki_nodes(space_id, session, node_token, access_token)
                        tasks.append(task)
                
                # 并发执行所有子节点的获取任务
                if tasks:
                    child_results = await asyncio.gather(*tasks)
                    # 展平结果并添加到总列表中
                    for child_tokens in child_results:
                        all_node_tokens.extend(child_tokens)
            
            return all_node_tokens
            
    except Exception as e:

        return []

import logging
import pymysql

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def query_mysql_knowledge(query: str, dataset_id: str, top_k: int = 2, score_threshold: float = 0.5):
    """
    从MySQL数据库查询知识库内容，同时搜索title和content字段
    """
    if not query:
        logging.error("查询参数为空")
        return {"records": []}

    query_terms = [term.strip() for term in query.split(',') if term.strip()]
    if not query_terms:
        logging.error("拆分后的查询参数为空")
        return {"records": []}

    logging.info(f"拆分后的查询词: {query_terms}")

    try:
        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor(pymysql.cursors.DictCursor)
        
        # 构建SQL语句
        like_conditions = " OR ".join(["title LIKE %s OR content LIKE %s"] * len(query_terms))
        
        # 构建CASE WHEN语句
        case_title_conditions = ' '.join([f'WHEN title LIKE %s THEN 2' for _ in query_terms])
        case_content_conditions = ' '.join([f'WHEN content LIKE %s THEN 1' for _ in query_terms])
        
        sql = f"""
            SELECT *,
                    (CASE {case_title_conditions} ELSE 0 END) + 
                    (CASE {case_content_conditions} ELSE 0 END) as match_score
            FROM knowledge_base 
            WHERE ({like_conditions})
                AND  dataset_id = %s
            ORDER BY match_score DESC
            LIMIT %s
        """
        
        # 构建参数列表
        params = []
        # CASE WHEN title的占位符参数
        params.extend([f"%{term}%" for term in query_terms])
        # CASE WHEN content的占位符参数
        params.extend([f"%{term}%" for term in query_terms])
        # WHERE中的LIKE参数
        for term in query_terms:
            like_term = f"%{term}%"
            params.extend([like_term, like_term])
        # 添加dataset_id和top_k
        params.extend([dataset_id, top_k])
        
        # 验证参数数量
        expected_params = 2 * len(query_terms) * 2 + 2  # CASE(2n) + WHERE(2n) + 2
        if len(params) != expected_params:
            logging.error(f"参数数量错误，预期{expected_params}，实际{len(params)}")
            return {"records": []}

        # 在执行 SQL 查询之前，打印 SQL 语句和参数
        logging.info(f"执行SQL: {sql} 参数: {params}")
        cursor.execute(sql, params)
        logging.debug(f"SQL执行完成，结果数量: {cursor.rowcount}")
        results = cursor.fetchall()

        # 过滤结果并格式化
        records = []
        for row in results:
            if row.get('match_score', 0) >= score_threshold:
                records.append({
                    "metadata": {
                        "path": row.get("document_path", ""),
                        "description": row.get("description", "")
                    },
                    "score": row.get("match_score", 0.0),
                    "title": row.get("title", ""),
                    "content": row.get("content", "")
                })
        
        logging.info(f"查询到的记录数量: {len(records)}")
        
        cursor.close()
        db.close()
        return {"records": records}
    
    except pymysql.Error as err:
        logging.error(f"MySQL错误: {err}")
        return {"records": []}
    except Exception as e:
        logging.error(f"异常错误: {str(e)}")
        return {"records": []}

@zhishiku_bp.route('/api/retrieval', methods=['POST'])
def query_knowledge():
    """
    知识库查询接口
    """
    try:
        # 添加请求日志
        logging.info(f"收到请求: {request.get_json()}")
        
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            logging.warning('无效的 Authorization 头格式')
            return jsonify({
                'error_code': 1001,
                'error_msg': '无效的 Authorization 头格式'
            }), 401
            
        api_key = auth_header.replace('Bearer ', '')
      
        if api_key != knowledge_api_key:
            logging.warning('授权失败')
            return jsonify({
                'error_code': 1002,
                'error_msg': '授权失败'
            })

            
        # 获取查询参数
        data = request.get_json()
        if not data or 'query' not in data or 'knowledge_id' not in data:
            logging.warning('知识库不存在')
            return jsonify({
                'error_code': 2001,
                'error_msg': '知识库不存在'
            })

        # 获取检索设置
        retrieval_setting = data.get('retrieval_setting', {})
        top_k = retrieval_setting.get('top_k', 2)
        score_threshold = retrieval_setting.get('score_threshold', 0.5)

        # 调用MySQL知识库查询
        results = query_mysql_knowledge(
            query=data['query'],
            dataset_id=data['knowledge_id'],
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        # 添加响应日志
        logging.info(f"查询结果: {results}")
        return jsonify(results), 200
        
    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        return jsonify({
            'error_code': 500,
            'error_msg': f'内部服务器错误: {str(e)}'
        }), 500

async def main(space_id: str):
    async with aiohttp.ClientSession() as session:
        all_nodes = await get_wiki_nodes(space_id, session)
        

@zhishiku_bp.route('/api/documents', methods=['POST'])
def create_document():
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '无效的 Authorization 头格式'
            }), 403
            
        api_key = auth_header.replace('Bearer ', '')
        if api_key != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        # 获取请求数据
        data = request.get_json()
        
        # 验证知识库是否存在
        try:
            db = pymysql.connect(**DB_CONFIG)
            cursor = db.cursor()
            
            check_dataset_sql = """
                SELECT id FROM knowledge_datasets 
                WHERE id = %s
            """
            cursor.execute(check_dataset_sql, (data.get('dataset_id'),))
            dataset = cursor.fetchone()
            
            if not dataset:
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '知识库不存在'
                }), 404
                
            # 只验证必需字段
            required_fields = ['dataset_id', 'title', 'content']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'code': 500,
                        'data': None,
                        'msg': f'缺少必填字段: {field}'
                    }), 500

            # 生成随机UUID作为knowledge_id
            knowledge_id = str(uuid.uuid4())
            
            # 获取是否覆盖的参数，默认为1
            is_override = data.get('is_override', 1)
            
            if is_override == 1:
                # 检查是否存在相同标题的文档
                check_sql = """
                    SELECT id FROM knowledge_base 
                    WHERE dataset_id = %s AND title = %s
                """
                cursor.execute(check_sql, (data['dataset_id'], data['title']))
                existing_doc = cursor.fetchone()
                
                if existing_doc:
                    # 更新现有文档
                    update_sql = """
                        UPDATE knowledge_base 
                        SET content = %s,
                            document_path = %s,
                            description = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE dataset_id = %s AND title = %s
                    """
                    cursor.execute(update_sql, (
                        data['content'],
                        data.get('document_path', ''),
                        data.get('description', ''),
                        data['dataset_id'],
                        data['title']
                    ))
                    doc_id = existing_doc['id']
                else:
                    # 插入新文档
                    insert_sql = """
                        INSERT INTO knowledge_base (
                            knowledge_id, dataset_id, title, content, 
                            document_path, description, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, 
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """
                    cursor.execute(insert_sql, (
                        knowledge_id,
                        data['dataset_id'],
                        data['title'],
                        data['content'],
                        data.get('document_path', ''),
                        data.get('description', '')
                    ))
                    doc_id = cursor.lastrowid
            
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': {'knowledge_id': knowledge_id},
                'msg': '文档创建成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

# 知识库管理相关接口

@zhishiku_bp.route('/api/datasets', methods=['POST'])
def create_dataset():
    """创建知识库"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        data = request.get_json()
        required_fields = ['name', 'org_id']
        
        # 验证必填字段
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'code': 500,
                    'data': None,
                    'msg': f'缺少必填字段: {field}'
                }), 500

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            insert_sql = """
                INSERT INTO knowledge_datasets (
                    id, name, description, org_id, created_at
                ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            dataset_id = str(uuid.uuid4())  # 生成随机UUID
            cursor.execute(insert_sql, (
                dataset_id,  # 添加UUID作为主键
                data['name'],
                data.get('description', ''),
                data['org_id']
            ))
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': {'id': dataset_id},  # 返回生成的UUID
                'msg': '知识库创建成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除知识库"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 检查知识库是否存在
            check_sql = "SELECT id FROM knowledge_datasets WHERE id = %s"
            cursor.execute(check_sql, (dataset_id,))
            if not cursor.fetchone():
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '知识库不存在'
                }), 404

            # 删除知识库
            delete_sql = "DELETE FROM knowledge_datasets WHERE id = %s"
            cursor.execute(delete_sql, (dataset_id,))
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': None,
                'msg': '知识库删除成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/datasets/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """更新知识库信息"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': '请求数据为空'
            }), 500

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 检查知识库是否存在
            check_sql = "SELECT id FROM knowledge_datasets WHERE id = %s"
            cursor.execute(check_sql, (dataset_id,))
            if not cursor.fetchone():
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '知识库不存在'
                }), 404

            # 更新知识库信息
            update_sql = """
                UPDATE knowledge_datasets 
                SET name = %s,
                    description = %s
                WHERE id = %s
            """
            cursor.execute(update_sql, (
                data.get('name'),
                data.get('description', ''),
                dataset_id
            ))
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': None,
                'msg': '知识库更新成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/datasets', methods=['GET'])
def list_datasets():
    """获取知识库列表"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        org_id = request.args.get('org_id')

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 构建查询条件
            where_clause = "WHERE 1=1"
            params = []
            if org_id:
                where_clause += " AND org_id = %s"
                params.append(org_id)

            # 获取总记录数
            count_sql = f"SELECT COUNT(*) as total FROM knowledge_datasets {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            query_sql = f"""
                SELECT id, name, description, created_at, org_id
                FROM knowledge_datasets
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query_sql, params)
            datasets = cursor.fetchall()
            
            return jsonify({
                'code': 200,
                'data': {
                    'total': total,
                    'items': datasets,
                    'page': page,
                    'page_size': page_size
                },
                'msg': '获取成功'
            })
            
        except pymysql.Error as e:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """获取知识库详情"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            query_sql = """
                SELECT id, name, description, created_at, org_id
                FROM knowledge_datasets
                WHERE id = %s
            """
            cursor.execute(query_sql, (dataset_id,))
            dataset = cursor.fetchone()
            
            if not dataset:
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '知识库不存在'
                }), 404
            
            return jsonify({
                'code': 200,
                'data': dataset,
                'msg': '获取成功'
            })
            
        except pymysql.Error as e:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/documents', methods=['GET'])
def list_documents():
    """获取文档列表，支持分页查询"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        dataset_id = request.args.get('dataset_id')
        title = request.args.get('title')

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 构建查询条件
            where_clause = "WHERE 1=1"
            params = []
            
            if dataset_id:
                where_clause += " AND dataset_id = %s"
                params.append(dataset_id)
            if title:
                where_clause += " AND title LIKE %s"
                params.append(f"%{title}%")

            # 获取总记录数
            count_sql = f"SELECT COUNT(*) as total FROM knowledge_base {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            query_sql = f"""
                SELECT id, knowledge_id, dataset_id, title, content, document_path, 
                       description, created_at, updated_at, original_platform, 
                       original_doc_id
                FROM knowledge_base
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query_sql, params)
            documents = cursor.fetchall()
            
            return jsonify({
                'code': 200,
                'data': {
                    'total': total,
                    'items': documents,
                    'page': page,
                    'page_size': page_size
                },
                'msg': '获取成功'
            })
            
        except pymysql.Error as e:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/documents/<knowledge_id>', methods=['GET'])
def get_document(knowledge_id):
    """获取文档信息"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403
        
        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            query_sql = """
                SELECT id, knowledge_id, dataset_id, title, content, document_path, 
                       description, created_at, updated_at, original_platform, 
                       original_doc_id
                FROM knowledge_base
                WHERE knowledge_id = %s
            """
            cursor.execute(query_sql, (knowledge_id,))
            document = cursor.fetchone()
            
            if not document:
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '文档不存在'
                }), 404

            return jsonify({
                'code': 200,
                'data': document,
                'msg': '获取成功'
            })
        
        except pymysql.Error as e:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/documents/<knowledge_id>', methods=['PUT'])
def update_document(knowledge_id):
    """更新文档信息"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'code': 500,
                'data': None,
                'msg': '请求数据为空'
            }), 500

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 检查文档是否存在
            check_sql = "SELECT knowledge_id FROM knowledge_base WHERE knowledge_id = %s"
            cursor.execute(check_sql, (knowledge_id,))
            if not cursor.fetchone():
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '文档不存在'
                }), 404

            # 更新文档信息
            update_sql = """
                UPDATE knowledge_base 
                SET title = %s,
                    content = %s,

                    updated_at = CURRENT_TIMESTAMP
                WHERE knowledge_id = %s
            """
            cursor.execute(update_sql, (
                data.get('title'),
                data.get('content'),
            
                knowledge_id
            ))
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': None,
                'msg': '文档更新成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/api/documents/<knowledge_id>', methods=['DELETE'])
def delete_document(knowledge_id):
    """删除文档"""
    try:
        # 验证 API Key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.replace('Bearer ', '') != knowledge_api_key:
            return jsonify({
                'code': 403,
                'data': None,
                'msg': '授权失败'
            }), 403

        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        try:
            # 检查文档是否存在
            check_sql = "SELECT knowledge_id FROM knowledge_base WHERE knowledge_id = %s"
            cursor.execute(check_sql, (knowledge_id,))
            if not cursor.fetchone():
                return jsonify({
                    'code': 404,
                    'data': None,
                    'msg': '文档不存在'
                }), 404

            # 删除文档
            delete_sql = "DELETE FROM knowledge_base WHERE knowledge_id = %s"
            cursor.execute(delete_sql, (knowledge_id,))
            db.commit()
            
            return jsonify({
                'code': 200,
                'data': None,
                'msg': '文档删除成功'
            })
            
        except pymysql.Error as e:
            db.rollback()
            return jsonify({
                'code': 500,
                'data': None,
                'msg': f'数据库错误: {str(e)}'
            }), 500
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'msg': f'服务器内部错误: {str(e)}'
        }), 500

@zhishiku_bp.route('/dify_datasets')
def dify_datasets():
    return render_template('dify_datasets.html')
@zhishiku_bp.route('/dify_editor')
def dify_editor():
    return render_template('dify_editor.html')
@zhishiku_bp.route('/dify_documents')
def dify_documents():
    return render_template('dify_documents.html')

@zhishiku_bp.route('/')
def dify_documents_dataset():
    return render_template('dify_documents.html')

# 4. 创建一个工厂函数来创建应用
def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    app.register_blueprint(zhishiku_bp)
    return app

# 5. 只在直接运行此文件时才创建应用并运行
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001, host='0.0.0.0')

        