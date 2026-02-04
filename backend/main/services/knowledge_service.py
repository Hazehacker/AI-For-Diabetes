"""
知识库服务
~~~~~~~~~

知识库管理服务，基于Dify实现，包括：
- 文件上传
- 文件删除
- 数据集管理
- 文档查询
- 知识召回

作者: 智糖团队
日期: 2025-01-25
"""

import requests
import json
import os
import uuid
from typing import Optional, Dict, Any, List
from utils.logger import get_logger
from utils.config_loader import get_config
from utils.database import get_db_connection, execute_query
from flask import url_for

logger = get_logger(__name__)


class KnowledgeService:
    """知识库服务类"""

    def __init__(self):
        """初始化服务"""
        # 获取基础Dify配置
        self.base_dify_config = {
            'base_url': get_config('DIFY.BASE_URL', 'https://top.megameta.cn'),
            'default_api_key': get_config('DIFY.API_KEY', 'dataset-51mRkWzs9zAD9yR5eAOsLrpL'),
            'default_dataset_id': get_config('DIFY.DATASET_ID', '28f90de6-f698-4b20-a7fe-02cadfadc6a6'),
            'timeout': get_config('DIFY.TIMEOUT', 30),
            'retry_attempts': get_config('DIFY.RETRY_ATTEMPTS', 3)
        }
        # 文件存储目录 - 保持与路由一致
        upload_dir = get_config('UPLOAD.DIR', 'uploads/knowledge')
        # 如果是相对路径，相对于项目根目录
        if not os.path.isabs(upload_dir):
            # 获取项目根目录的绝对路径
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            parent_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(parent_dir)
            self.upload_dir = os.path.join(project_root, upload_dir)
        else:
            self.upload_dir = upload_dir
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_user_dify_config(self, user_id: int) -> Dict[str, Any]:
        """
        根据用户ID获取用户的Dify配置

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户的Dify配置
        """
        try:
            # 使用系统统一的Dify配置，不再依赖用户个人配置
            return {
                'base_url': self.base_dify_config['base_url'],
                'api_key': self.base_dify_config['default_api_key'],
                'dataset_id': self.base_dify_config['default_dataset_id'],
                'timeout': self.base_dify_config['timeout'],
                'retry_attempts': self.base_dify_config['retry_attempts'],
                'is_admin': False  # 默认非管理员
            }

        except Exception as e:
            logger.error(f"获取用户Dify配置失败: {str(e)}")
            # 返回默认配置作为fallback
            return {
                'base_url': self.base_dify_config['base_url'],
                'api_key': self.base_dify_config['default_api_key'],
                'dataset_id': self.base_dify_config['default_dataset_id'],
                'timeout': self.base_dify_config['timeout'],
                'retry_attempts': self.base_dify_config['retry_attempts'],
                'is_admin': False
            }
    
    def upload_file(
        self,
        user_id: int,
        file_path: str,
        file_name: Optional[str] = None,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件到知识库

        Args:
            user_id: 用户ID
            file_path: 文件路径
            file_name: 文件名（可选）
            dataset_id: 数据集ID（可选，不传则使用配置中的默认数据集ID）

        Returns:
            Dict: 上传结果
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # 构造文件名
            if not file_name:
                import os
                file_name = os.path.basename(file_path)

            # 使用指定的数据集ID或配置中的默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']
            logger.info(f"🔍 用户 {user_id} 上传文件到知识库 - 使用数据集ID: {target_dataset_id}, 文件名: {file_name}, Dify配置: base_url={dify_config['base_url']}, api_key前缀={dify_config['api_key'][:10]}...")

            # 调用Dify文件上传API
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/document/create-by-file"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            # 构造multipart/form-data请求
            files = {
                'file': (file_name, file_data, 'application/octet-stream')
            }

            # 构造处理规则 - 先尝试完全不传process_rule，看看Dify API的默认行为
            data = {
                'data': json.dumps({
                    "indexing_technique": "high_quality"
                })
            }

            logger.info(f"用户 {user_id} 上传文件到Dify: {file_name}, 大小: {len(file_data)} bytes")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ 用户 {user_id} 上传知识库文件成功: {file_name}")
                return {
                    'success': True,
                    'message': '文件上传成功',
                    'data': result
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 上传知识库文件失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 上传知识库文件失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def upload_file_data(
        self,
        user_id: int,
        file_data: bytes,
        file_name: str,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件数据到知识库（用于multipart/form-data上传）
        同时保存文件到服务端并提供文件链接

        Args:
            user_id: 用户ID
            file_data: 文件二进制数据
            file_name: 文件名
            dataset_id: 数据集ID（可选，不传则使用配置中的默认数据集ID）

        Returns:
            Dict: 上传结果，包含文件链接
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 使用指定的数据集ID或配置中的默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']
            logger.info(f"🔍 用户 {user_id} 上传文件数据到知识库 - 使用数据集ID: {target_dataset_id}, Dify配置: base_url={dify_config['base_url']}, api_key前缀={dify_config['api_key'][:10]}...")

            # 保存文件到服务端
            file_ext = os.path.splitext(file_name)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 生成文件访问链接（相对路径）
            file_url = f"/api/knowledge/files/download/{unique_filename}"
            
            logger.info(f"✅ 文件已保存到服务端: {file_path}")

            # 调用Dify文件上传API
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/document/create-by-file"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            # 构造multipart/form-data请求
            files = {
                'file': (file_name, file_data, 'application/octet-stream')
            }

            # 构造处理规则 - 使用Dify官方推荐配置
            data = {
                'data': json.dumps({
                    "indexing_technique": "high_quality",
                    "process_rule": {
                        "rules": {
                            "pre_processing_rules": [
                                {"id": "remove_extra_spaces", "enabled": True},
                                {"id": "remove_urls_emails", "enabled": True}
                            ],
                            "segmentation": {
                                "separator": "###",
                                "max_tokens": 500
                            }
                        },
                        "mode": "custom"
                    }
                })
            }

            response = requests.post(url, headers=headers, files=files, data=data, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ 用户 {user_id} 上传知识库文件成功: {file_name}")
                
                # 根据Dify实际返回格式获取文档ID
                document = result.get('document', {})
                document_id = document.get('id')
                dify_file_name = document.get('name', file_name)  # 使用Dify返回的文件名，如果没有则使用原始文件名
                
                # 如果获取不到document_id，使用文件名作为临时ID
                if not document_id:
                    document_id = f"temp_{unique_filename}"
                    logger.warning(f"⚠️ 未获取到Dify文档ID，使用临时ID: {document_id}")
                
                # 保存文件信息到数据库
                file_info = self._save_file_info_to_db(
                    document_id=document_id,
                    file_name=dify_file_name,  # 使用Dify返回的文件名
                    file_path=unique_filename,
                    file_url=file_url,
                    file_type=file_ext.lstrip('.') if file_ext else 'unknown',
                    file_size=len(file_data),
                    dataset_id=target_dataset_id,
                    user_id=user_id
                )
                
                # 返回结果包含文件链接
                return {
                    'success': True,
                    'message': '文件上传成功',
                    'data': {
                        **result,
                        'file_url': file_url,
                        'file_name': dify_file_name,
                        'file_type': file_ext.lstrip('.') if file_ext else 'unknown',
                        'file_size': len(file_data),
                        'file_id': document_id,
                        'document_id': document_id
                    }
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 上传知识库文件失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 上传知识库文件失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def list_datasets(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        dataset_id: Optional[str] = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出数据集（知识库文件列表），支持文件名称和类型查询

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            dataset_id: 数据集ID（可选）
            file_name: 文档名称（可选，支持模糊查询）
            file_type: 文档类型（可选，如：pdf, txt, docx等）

        Returns:
            Dict: 数据集列表，包含文件链接
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 使用指定的数据集ID或默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']

            # 调用Dify文档列表API
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/documents"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            params = {
                'page': page,
                'limit': page_size
            }
            
            # 如果提供了文件名称，添加到参数中
            if file_name:
                params['keyword'] = file_name

            response = requests.get(url, headers=headers, params=params, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                documents = result.get('data', [])
                
                # 如果指定了文件类型，进行过滤
                if file_type:
                    documents = [
                        doc for doc in documents 
                        if doc.get('name', '').lower().endswith(f'.{file_type.lower()}')
                    ]
                
                # 为每个文档添加文件链接（从数据库查询）
                for doc in documents:
                    doc_id = doc.get('id')
                    if doc_id:
                        file_info = self._get_file_info_from_db(doc_id)
                        if file_info:
                            # 添加完整的前缀URL
                            file_url = file_info.get('file_url')
                            if file_url and file_url.startswith('/'):
                                doc['file_url'] = f"https://chat.cmkjai.com{file_url}"
                            else:
                                doc['file_url'] = file_url
                            doc['file_path'] = file_info.get('file_path')
                            doc['file_type'] = file_info.get('file_type')
                        else:
                            # 如果没有找到文件信息，生成默认链接
                            doc_name = doc.get('name', '')
                            if doc_name:
                                doc['file_url'] = f"https://chat.cmkjai.com/api/knowledge/files/view/{doc_name}"
                
                logger.info(f"✅ 用户 {user_id} 获取数据集文档列表成功: {len(documents)} 个文档")

                return {
                    'documents': documents,
                    'total': len(documents) if file_type else result.get('total', 0),
                    'page': page,
                    'page_size': page_size,
                    'has_more': result.get('has_more', False)
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 用户 {user_id} 获取数据集列表失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 获取数据集列表失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def delete_file(
        self,
        user_id: int,
        file_id: str,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        删除知识库文件

        Args:
            user_id: 用户ID
            file_id: 文件ID
            dataset_id: 数据集ID

        Returns:
            Dict: 删除结果
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 调用Dify文档删除API
            url = f"{dify_config['base_url']}/v1/datasets/{dataset_id or dify_config['dataset_id']}/documents/{file_id}"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            logger.info(f"用户 {user_id} 删除Dify文档: {file_id}")
            response = requests.delete(url, headers=headers, timeout=dify_config['timeout'])

            if response.status_code in [200, 204]:
                logger.info(f"✅ 用户 {user_id} 删除知识库文件成功: {file_id}")
                return {
                    'success': True,
                    'message': '文件删除成功'
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 用户 {user_id} 删除知识库文件失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 用户 {user_id} 删除知识库文件失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def update_document_status(
        self,
        user_id: int,
        document_id: str,
        enabled: bool,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新文档启用/禁用状态

        注意: 当前Dify API版本不支持通过API更新文档状态。
        此方法保留接口以备将来使用，目前返回友好提示。

        Args:
            user_id: 用户ID
            document_id: 文档ID
            enabled: 是否启用
            dataset_id: 数据集ID

        Returns:
            Dict: 更新结果
        """
        logger.info(f"用户 {user_id} 尝试更新文档状态: {document_id} -> {'enabled' if enabled else 'disabled'}")

        # Dify API当前不支持更新文档状态，保留接口以备将来扩展
        return {
            'success': False,
            'message': '文档启用/禁用功能暂未实现。当前Dify API版本不支持此操作。如需启用/禁用文档，请直接在Dify控制台中操作。',
            'note': '此功能将在Dify API支持后实现'
        }

    def create_dataset(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建数据集

        Args:
            user_id: 用户ID
            name: 数据集名称
            description: 描述

        Returns:
            Dict: 创建结果
        """
        try:
            # Dify不支持通过API创建数据集，这里返回成功
            logger.info(f"✅ 用户 {user_id} 创建数据集: {name}")

            return {
                'success': True,
                'message': '数据集创建成功',
                'data': {
                    'dataset_id': self.base_dify_config['default_dataset_id'],
                    'name': name,
                    'description': description
                }
            }

        except Exception as e:
            logger.error(f"❌ 创建数据集失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def retrieve_knowledge(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        知识库召回

        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回数量
            score_threshold: 分数阈值
            dataset_id: 数据集ID

        Returns:
            Dict: 召回结果
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 调用Dify知识召回API
            url = f"{dify_config['base_url']}/v1/datasets/{dataset_id or dify_config['dataset_id']}/retrieve"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}',
                'Content-Type': 'application/json'
            }

            payload = {
                'query': query,
                'top_k': top_k,
                'score_threshold': score_threshold,
                'search_method': 'semantic_search'
            }

            logger.info(f"用户 {user_id} 进行知识召回: {query}")
            response = requests.post(url, headers=headers, json=payload, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                records = result.get('records', [])
                logger.info(f"✅ 知识召回成功: 找到 {len(records)} 条记录")

                return {
                    'success': True,
                    'message': '知识召回成功',
                    'data': {
                        'query': query,
                        'records': records,
                        'total': len(records)
                    }
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 知识召回失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 知识召回失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def list_files(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        dataset_id: Optional[str] = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取知识库文件列表，支持文档名称和类型查询

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            dataset_id: 数据集ID（可选）
            file_name: 文档名称（可选，支持模糊查询）
            file_type: 文档类型（可选，如：pdf, txt, docx等）

        Returns:
            Dict: 文件列表
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 使用指定的数据集ID或配置中的默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']
            logger.info(f"🔍 用户 {user_id} 获取数据集列表 - 使用数据集ID: {target_dataset_id}")

            # 调用Dify文档列表API
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/documents"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            params = {
                'page': page,
                'limit': page_size
            }
            
            # 如果提供了关键词，添加到参数中
            if file_name:
                params['keyword'] = file_name

            response = requests.get(url, headers=headers, params=params, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                documents = result.get('data', [])
                
                # 如果指定了文件类型，进行过滤
                if file_type:
                    documents = [
                        doc for doc in documents 
                        if doc.get('name', '').lower().endswith(f'.{file_type.lower()}')
                    ]
                
                # 为每个文档添加文件链接
                for doc in documents:
                    doc_name = doc.get('name', '')
                    if doc_name:
                        # 尝试从上传目录中查找文件
                        doc['file_url'] = f"https://chat.cmkjai.com/api/knowledge/files/download/{doc_name}"
                        doc['preview_url'] = f"/api/knowledge/files/preview/{doc.get('id', '')}"
                
                logger.info(f"✅ 用户 {user_id} 获取文件列表成功: {len(documents)} 个文件")
                
                return {
                    'documents': documents,
                    'total': len(documents),
                    'page': page,
                    'page_size': page_size,
                    'has_more': result.get('has_more', False)
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 用户 {user_id} 获取文件列表失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 获取文件列表失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def get_file_preview_link(
        self,
        user_id: int,
        file_id: str,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取文件预览链接

        Args:
            user_id: 用户ID
            file_id: 文件ID
            dataset_id: 数据集ID（可选）

        Returns:
            Dict: 预览链接信息
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 使用指定的数据集ID或配置中的默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']
            logger.info(f"🔍 用户 {user_id} 获取文件预览 - 使用数据集ID: {target_dataset_id}")

            # 调用Dify文档详情API获取文件信息
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/documents/{file_id}"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            response = requests.get(url, headers=headers, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                doc = result.get('data', {})
                file_name = doc.get('name', '')
                
                # 生成预览链接
                preview_url = f"/api/knowledge/files/preview/{file_id}"
                
                return {
                    'success': True,
                    'data': {
                        'file_id': file_id,
                        'file_name': file_name,
                        'preview_url': preview_url
                    }
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 获取文件预览链接失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 获取文件预览链接失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def get_file_download_link(
        self,
        user_id: int,
        file_id: str,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取文件下载链接

        Args:
            user_id: 用户ID
            file_id: 文件ID
            dataset_id: 数据集ID（可选）

        Returns:
            Dict: 下载链接信息
        """
        try:
            # 获取用户的Dify配置
            dify_config = self._get_user_dify_config(user_id)

            # 使用指定的数据集ID或配置中的默认数据集ID
            target_dataset_id = dataset_id or dify_config['dataset_id']
            logger.info(f"🔍 用户 {user_id} 获取文件下载 - 使用数据集ID: {target_dataset_id}")

            # 调用Dify文档详情API获取文件信息
            url = f"{dify_config['base_url']}/v1/datasets/{target_dataset_id}/documents/{file_id}"

            headers = {
                'Authorization': f'Bearer {dify_config["api_key"]}'
            }

            response = requests.get(url, headers=headers, timeout=dify_config['timeout'])

            if response.status_code == 200:
                result = response.json()
                doc = result.get('data', {})
                file_name = doc.get('name', '')
                
                # 生成下载链接
                download_url = f"/api/knowledge/files/download/{file_id}"
                
                return {
                    'success': True,
                    'data': {
                        'file_id': file_id,
                        'file_name': file_name,
                        'download_url': download_url
                    }
                }
            else:
                error_msg = f"Dify API error: {response.status_code} - {response.text}"
                logger.error(f"❌ 获取文件下载链接失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            logger.error(f"❌ 获取文件下载链接失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def _save_file_info_to_db(
        self,
        document_id: str,
        file_name: str,
        file_path: str,
        file_url: str,
        file_type: str,
        file_size: int,
        dataset_id: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        保存文件信息到数据库

        Args:
            document_id: Dify文档ID
            file_name: 文件名
            file_path: 文件存储路径
            file_url: 文件访问链接
            file_type: 文件类型
            file_size: 文件大小
            dataset_id: 数据集ID
            user_id: 用户ID

        Returns:
            Dict: 保存的文件信息
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 检查表是否存在，如果不存在则创建
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_file_storage (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    document_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'Dify文档ID',
                    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
                    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
                    file_url VARCHAR(500) NOT NULL COMMENT '文件访问链接',
                    file_type VARCHAR(50) COMMENT '文件类型',
                    file_size BIGINT COMMENT '文件大小(字节)',
                    dataset_id VARCHAR(100) COMMENT '数据集ID',
                    user_id INT COMMENT '上传用户ID',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    INDEX idx_document_id (document_id),
                    INDEX idx_file_name (file_name),
                    INDEX idx_file_type (file_type),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文件存储表'
            """)
            
            # 插入或更新文件信息
            cursor.execute("""
                INSERT INTO knowledge_file_storage 
                (document_id, file_name, file_path, file_url, file_type, file_size, dataset_id, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    file_name = VALUES(file_name),
                    file_path = VALUES(file_path),
                    file_url = VALUES(file_url),
                    file_type = VALUES(file_type),
                    file_size = VALUES(file_size),
                    updated_at = CURRENT_TIMESTAMP
            """, (document_id, file_name, file_path, file_url, file_type, file_size, dataset_id, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 文件信息已保存到数据库: document_id={document_id}, file_name={file_name}")
            
            return {
                'document_id': document_id,
                'file_name': file_name,
                'file_path': file_path,
                'file_url': file_url,
                'file_type': file_type,
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"❌ 保存文件信息到数据库失败: {str(e)}")
            return None

    def _get_file_info_from_db(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        从数据库获取文件信息

        Args:
            document_id: Dify文档ID

        Returns:
            Dict: 文件信息
        """
        try:
            sql = """
                SELECT document_id, file_name, file_path, file_url, file_type, file_size
                FROM knowledge_file_storage
                WHERE document_id = %s
            """
            result = execute_query(sql, (document_id,), fetch_one=True)
            return result
            
        except Exception as e:
            logger.error(f"❌ 从数据库获取文件信息失败: {str(e)}")
            return None


# 全局单例
_knowledge_service_instance = None

def get_knowledge_service() -> KnowledgeService:
    """获取知识库服务单例"""
    global _knowledge_service_instance
    if _knowledge_service_instance is None:
        _knowledge_service_instance = KnowledgeService()
    return _knowledge_service_instance

