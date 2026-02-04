"""
知识问答服务 - 【核心文件】
~~~~~~~~~~~

独立的知识问答服务，支持：
- 从知识库文档和数据库FAQ中检索相关信息
- 基于检索结果进行问答
- 关键词匹配和相似度计算
- 支持手动和自动关键词提取
- 可独立运行或集成到对话服务

核心功能：
- search_knowledge(): 知识检索（支持双数据源）
- answer_question(): 基于检索结果的问答
- _load_from_files(): 从Markdown文件加载知识
- _load_from_database(): 从数据库FAQ表加载知识
- _calculate_similarity(): 相似度计算算法

数据源：
- Markdown文档：doc/knowledge_slices/
- 数据库FAQ：faq_list 和 faq_list_keys 表

作者: 智糖团队
日期: 2025-01-21
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from utils.logger import get_logger
from utils.config_loader import get_config
from utils.database import get_db_connection, execute_query

logger = get_logger(__name__)


class KnowledgeQAService:
    """知识问答服务类"""

    def __init__(self, knowledge_base_path: Optional[str] = None, load_from_db: bool = True):
        """
        初始化知识问答服务

        Args:
            knowledge_base_path: 知识库文档路径，默认为 doc/knowledge_slices/
            load_from_db: 是否从数据库加载FAQ，默认True
        """
        # 获取知识库路径
        if knowledge_base_path:
            self.knowledge_base_path = Path(knowledge_base_path)
        else:
            # 默认路径：项目根目录下的 doc/knowledge_slices/
            current_dir = Path(__file__).parent.parent.parent
            self.knowledge_base_path = current_dir / "doc" / "knowledge_slices"

        # 知识库缓存
        self.knowledge_base: List[Dict[str, Any]] = []
        self.is_loaded = False
        self.load_from_db = load_from_db

        # 加载知识库
        self._load_knowledge_base()

        logger.info(f"✅ 知识问答服务初始化完成，加载了 {len(self.knowledge_base)} 条知识")
    
    def _load_knowledge_base(self):
        """加载知识库（文档 + 数据库）"""
        total_qa = 0

        # 从数据库加载（优先）
        if self.load_from_db:
            db_count = self._load_from_database()
            total_qa += db_count
            logger.info(f"📊 从数据库加载了 {db_count} 条FAQ")

        # 从文档加载
        file_count = self._load_from_files()
        total_qa += file_count
        logger.info(f"📁 从文档加载了 {file_count} 条问答")

        self.is_loaded = True
        logger.info(f"📚 知识库加载完成，总问答数: {total_qa}")

    def _load_from_files(self) -> int:
        """从文档加载知识库"""
        try:
            if not self.knowledge_base_path.exists():
                logger.warning(f"⚠️ 知识库路径不存在: {self.knowledge_base_path}")
                return 0

            # 获取所有markdown文件
            md_files = list(self.knowledge_base_path.glob("*.md"))
            logger.info(f"📚 找到 {len(md_files)} 个知识库文档")

            # 解析每个文档
            file_count = 0
            for md_file in sorted(md_files):
                try:
                    qa_pairs = self._parse_knowledge_file(md_file)
                    self.knowledge_base.extend(qa_pairs)
                    file_count += len(qa_pairs)
                    logger.info(f"✅ 加载文档 {md_file.name}: {len(qa_pairs)} 条问答")
                except Exception as e:
                    logger.error(f"❌ 解析文档 {md_file.name} 失败: {str(e)}")

            return file_count

        except Exception as e:
            logger.error(f"❌ 从文档加载知识库失败: {str(e)}")
            return 0

    def _load_from_database(self) -> int:
        """从数据库加载FAQ"""
        try:
            import pymysql

            # 直接连接数据库（避免连接池问题）
            conn = pymysql.connect(
                host='115.120.251.86',
                port=3306,
                user='root',
                password='MyNewPass!2024',
                database='ai',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

            with conn.cursor() as cursor:
                # 查询启用的FAQ
                sql = """
                    SELECT
                        f.id,
                        f.question,
                        f.answer,
                        f.category,
                        f.source,
                        f.status,
                        f.sort_order,
                        f.view_count,
                        f.like_count,
                        f.is_manual,
                        f.description,
                        GROUP_CONCAT(
                            CONCAT(k.keyword, ':', k.keyword_type, ':', k.weight)
                            ORDER BY k.weight DESC, k.keyword
                        ) as keywords_str
                    FROM faq_list f
                    LEFT JOIN faq_list_keys k ON f.id = k.faq_id
                    WHERE f.status = 1
                    GROUP BY f.id
                    ORDER BY f.sort_order, f.id
                """

                cursor.execute(sql)
                faq_records = cursor.fetchall()

                for record in faq_records:
                    # 解析关键词
                    keywords = []
                    keywords_str = record.get('keywords_str')
                    if keywords_str:
                        for kw_str in keywords_str.split(','):
                            if ':' in kw_str:
                                keyword, kw_type, weight = kw_str.split(':', 2)
                                keywords.append({
                                    'keyword': keyword,
                                    'type': kw_type,
                                    'weight': float(weight)
                                })

                    # 构建问答对
                    qa_pair = {
                        'question': record['question'],
                        'answer': record['answer'],
                        'source': f"db_faq_{record['id']}",
                        'category': record.get('category'),
                        'keywords': [kw['keyword'] for kw in keywords],
                        'manual_keywords': [kw['keyword'] for kw in keywords if kw['type'] == 'manual'],
                        'auto_keywords': [kw['keyword'] for kw in keywords if kw['type'] == 'auto'],
                        'db_id': record['id'],
                        'view_count': record['view_count'],
                        'like_count': record['like_count'],
                        'is_manual': bool(record['is_manual'])
                    }

                    self.knowledge_base.append(qa_pair)

            conn.close()
            return len(faq_records)

        except Exception as e:
            logger.error(f"❌ 从数据库加载FAQ失败: {str(e)}")
            return 0
    
    def _parse_knowledge_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析知识库文档，提取问答对
        
        Args:
            file_path: 文档路径
            
        Returns:
            List[Dict]: 问答对列表
        """
        qa_pairs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式提取问答对（包含可能的关键词）
            # 匹配格式：### 问答 N\n\n**问题：** ...\n\n**答案：** ...\n\n**关键词：** ...（可选）
            pattern = r'###\s*问答\s*\d+\s*\n(.*?)(?=\n---|\n###|$)'
            
            matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
            
            for match in matches:
                qa_block = match.group(1)
                
                # 提取问题
                question_match = re.search(r'\*\*问题[：:]\*\*\s*(.*?)(?=\n\s*\*\*答案|\n\s*\*\*关键词|$)', qa_block, re.DOTALL)
                question = question_match.group(1).strip() if question_match else ""
                
                # 提取答案
                answer_match = re.search(r'\*\*答案[：:]\*\*\s*(.*?)(?=\n\s*\*\*关键词|\n\s*\*\*问题|$)', qa_block, re.DOTALL)
                answer = answer_match.group(1).strip() if answer_match else ""
                
                # 清理格式
                question = re.sub(r'\*\*', '', question).strip()
                answer = re.sub(r'\*\*', '', answer).strip()
                
                if question and answer:
                    # 尝试从文档中提取手动设置的关键词（如果存在）
                    manual_keywords = self._extract_manual_keywords(qa_block)
                    
                    # 自动提取关键词
                    auto_keywords = self._extract_keywords(question + ' ' + answer)
                    
                    # 合并关键词（手动设置的关键词优先级更高）
                    all_keywords = list(set(manual_keywords + auto_keywords))
                    
                    qa_pairs.append({
                        'question': question,
                        'answer': answer,
                        'source': file_path.name,
                        'keywords': all_keywords[:15],  # 最多15个关键词
                        'manual_keywords': manual_keywords,  # 手动设置的关键词
                        'auto_keywords': auto_keywords  # 自动提取的关键词
                    })
            
            # 如果没有匹配到，尝试更宽松的模式
            if not qa_pairs:
                # 尝试匹配：**问题：** ... **答案：** ...
                pattern2 = r'(\*\*问题[：:]\*\*\s*.*?\s*\*\*答案[：:]\*\*\s*.*?)(?=\n---|\n###|$)'
                matches2 = re.finditer(pattern2, content, re.DOTALL | re.MULTILINE)
                
                for match in matches2:
                    qa_block = match.group(1)
                    
                    # 提取问题
                    question_match = re.search(r'\*\*问题[：:]\*\*\s*(.*?)(?=\n\s*\*\*答案|$)', qa_block, re.DOTALL)
                    question = question_match.group(1).strip() if question_match else ""
                    
                    # 提取答案
                    answer_match = re.search(r'\*\*答案[：:]\*\*\s*(.*?)(?=\n\s*\*\*关键词|$)', qa_block, re.DOTALL)
                    answer = answer_match.group(1).strip() if answer_match else ""
                    
                    # 清理格式
                    question = re.sub(r'\*\*', '', question).strip()
                    answer = re.sub(r'\*\*', '', answer).strip()
                    
                    if question and answer:
                        # 尝试从文档中提取手动设置的关键词（如果存在）
                        manual_keywords = self._extract_manual_keywords(qa_block)
                        
                        # 自动提取关键词
                        auto_keywords = self._extract_keywords(question + ' ' + answer)
                        
                        # 合并关键词（手动设置的关键词优先级更高）
                        all_keywords = list(set(manual_keywords + auto_keywords))
                        
                        qa_pairs.append({
                            'question': question,
                            'answer': answer,
                            'source': file_path.name,
                            'keywords': all_keywords[:15],  # 最多15个关键词
                            'manual_keywords': manual_keywords,  # 手动设置的关键词
                            'auto_keywords': auto_keywords  # 自动提取的关键词
                        })
            
        except Exception as e:
            logger.error(f"❌ 解析文件 {file_path} 失败: {str(e)}")
        
        return qa_pairs
    
    def _extract_manual_keywords(self, text: str) -> List[str]:
        """
        从文档中提取手动设置的关键词
        
        支持格式：
        - **关键词：** 胰岛素,剂量,计算
        - **标签：** 胰岛素,剂量,计算
        - keywords: 胰岛素,剂量,计算
        
        Args:
            text: 包含问答对的文本片段
            
        Returns:
            List[str]: 手动设置的关键词列表
        """
        keywords = []
        
        # 匹配格式：**关键词：** 胰岛素,剂量,计算
        pattern1 = r'\*\*关键词[：:]\*\*\s*([^\n]+)'
        match1 = re.search(pattern1, text, re.IGNORECASE)
        if match1:
            keywords_str = match1.group(1).strip()
            keywords.extend([kw.strip() for kw in keywords_str.split(',') if kw.strip()])
        
        # 匹配格式：**标签：** 胰岛素,剂量,计算
        pattern2 = r'\*\*标签[：:]\*\*\s*([^\n]+)'
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            keywords_str = match2.group(1).strip()
            keywords.extend([kw.strip() for kw in keywords_str.split(',') if kw.strip()])
        
        # 匹配格式：keywords: 胰岛素,剂量,计算
        pattern3 = r'keywords[：:]\s*([^\n]+)'
        match3 = re.search(pattern3, text, re.IGNORECASE)
        if match3:
            keywords_str = match3.group(1).strip()
            keywords.extend([kw.strip() for kw in keywords_str.split(',') if kw.strip()])
        
        return list(set(keywords))  # 去重
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本内容
            
        Returns:
            List[str]: 关键词列表
        """
        # 简单的关键词提取：去除停用词，提取重要词汇
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
                     '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
                     '自己', '这', '为', '什么', '能', '可以', '如何', '怎么', '如果', '需要', '应该'}
        
        # 提取中文词汇（2-4个字）
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        
        # 过滤停用词和重复词
        keywords = list(set([w for w in words if w not in stop_words and len(w) >= 2]))
        
        return keywords[:10]  # 最多返回10个关键词
    
    def _calculate_similarity(self, query: str, text: str, manual_keywords: List[str] = None) -> float:
        """
        计算查询和文本的相似度（基于关键词匹配）
        
        Args:
            query: 查询文本
            text: 目标文本
            manual_keywords: 手动设置的关键词列表（可选）
            
        Returns:
            float: 相似度分数 (0-1)
        """
        # 提取查询关键词
        query_keywords = set(self._extract_keywords(query))
        
        # 提取文本关键词
        text_keywords = set(self._extract_keywords(text))
        
        # 如果有手动设置的关键词，也加入匹配
        if manual_keywords:
            text_keywords.update(manual_keywords)
        
        if not query_keywords:
            return 0.0
        
        # 计算交集比例（Jaccard相似度）
        intersection = query_keywords & text_keywords
        union = query_keywords | text_keywords
        
        if not union:
            return 0.0
        
        jaccard_score = len(intersection) / len(union)
        
        # 计算关键词在文本中的出现频率
        query_text = query.lower()
        text_lower = text.lower()
        
        keyword_matches = sum(1 for kw in query_keywords if kw in text_lower)
        frequency_score = keyword_matches / len(query_keywords) if query_keywords else 0
        
        # 手动关键词命中加分（如果查询关键词命中手动设置的关键词，给予额外加分）
        manual_hit_bonus = 0.0
        if manual_keywords:
            manual_keywords_set = set(manual_keywords)
            manual_hits = query_keywords & manual_keywords_set
            if manual_hits:
                # 手动关键词命中给予额外0.2的加分
                manual_hit_bonus = min(0.2, len(manual_hits) / len(query_keywords) * 0.3)
        
        # 综合得分（Jaccard 50% + 频率 30% + 手动关键词命中 20%）
        similarity = jaccard_score * 0.5 + frequency_score * 0.3 + manual_hit_bonus
        
        return min(1.0, similarity)  # 确保不超过1.0
    
    def search_knowledge(self, query: str, top_k: int = 3, min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """
        从知识库中检索相关知识
        
        Args:
            query: 查询文本
            top_k: 返回最相关的top_k条
            min_similarity: 最小相似度阈值
            
        Returns:
            List[Dict]: 检索结果，按相似度排序
        """
        if not self.is_loaded or not self.knowledge_base:
            logger.warning("⚠️ 知识库未加载或为空")
            return []
        
        results = []
        
        # 计算每个问答对的相似度
        for qa in self.knowledge_base:
            # 获取手动设置的关键词（如果有）
            manual_keywords = qa.get('manual_keywords', [])
            
            # 计算问题和答案的相似度（传入手动关键词）
            question_sim = self._calculate_similarity(query, qa['question'], manual_keywords)
            answer_sim = self._calculate_similarity(query, qa['answer'], manual_keywords)
            
            # 检查查询是否直接命中手动关键词（精确匹配）
            keyword_hit = False
            if manual_keywords:
                query_keywords = set(self._extract_keywords(query))
                manual_keywords_set = set(manual_keywords)
                if query_keywords & manual_keywords_set:
                    keyword_hit = True
                    # 如果命中手动关键词，给予额外加分
                    question_sim = min(1.0, question_sim + 0.15)
            
            # 综合相似度（问题权重更高）
            similarity = question_sim * 0.7 + answer_sim * 0.3
            
            if similarity >= min_similarity:
                results.append({
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'similarity': similarity,
                    'source': qa['source'],
                    'keyword_hit': keyword_hit,  # 是否命中手动关键词
                    'matched_keywords': list(set(self._extract_keywords(query)) & set(qa.get('keywords', []))) if keyword_hit else []  # 匹配到的关键词
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 返回top_k条
        return results[:top_k]
    
    def answer_question(self, question: str, top_k: int = 3, use_ai: bool = False) -> Dict[str, Any]:
        """
        回答问题
        
        Args:
            question: 用户问题
            top_k: 检索最相关的top_k条知识
            use_ai: 是否使用AI进行答案生成（需要集成DeepSeek）
            
        Returns:
            Dict: 回答结果
        """
        try:
            # 从知识库检索相关知识
            knowledge_results = self.search_knowledge(question, top_k=top_k)
            
            if not knowledge_results:
                return {
                    'success': False,
                    'answer': '抱歉，我在知识库中没有找到相关信息。',
                    'knowledge_used': [],
                    'confidence': 0.0
                }
            
            # 如果找到相关知识
            best_match = knowledge_results[0]
            
            if use_ai:
                # 使用AI生成答案（需要集成DeepSeek服务）
                # 这里可以调用DeepSeek API，将检索到的知识作为上下文
                answer = self._generate_ai_answer(question, knowledge_results)
            else:
                # 直接返回最相关的答案
                answer = best_match['answer']
            
            return {
                'success': True,
                'answer': answer,
                'knowledge_used': knowledge_results,
                'confidence': best_match['similarity'],
                'source': best_match['source']
            }
            
        except Exception as e:
            logger.error(f"❌ 回答问题失败: {str(e)}")
            return {
                'success': False,
                'answer': f'处理问题时出现错误: {str(e)}',
                'knowledge_used': [],
                'confidence': 0.0
            }
    
    def _generate_ai_answer(self, question: str, knowledge_results: List[Dict]) -> str:
        """
        使用AI生成答案（基于检索到的知识）
        
        Args:
            question: 用户问题
            knowledge_results: 检索到的知识
            
        Returns:
            str: AI生成的答案
        """
        # TODO: 集成DeepSeek服务生成答案
        # 这里可以构建prompt，将检索到的知识作为上下文
        # 暂时返回最相关的答案
        if knowledge_results:
            return knowledge_results[0]['answer']
        return "抱歉，无法生成答案。"
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.is_loaded:
            return {
                'loaded': False,
                'total_qa': 0,
                'sources': []
            }
        
        # 统计来源文件
        sources = {}
        for qa in self.knowledge_base:
            source = qa.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'loaded': True,
            'total_qa': len(self.knowledge_base),
            'sources': sources,
            'knowledge_base_path': str(self.knowledge_base_path)
        }


# 全局单例
_knowledge_qa_service_instance = None

def get_knowledge_qa_service(knowledge_base_path: Optional[str] = None) -> KnowledgeQAService:
    """获取知识问答服务单例"""
    global _knowledge_qa_service_instance
    if _knowledge_qa_service_instance is None:
        _knowledge_qa_service_instance = KnowledgeQAService(knowledge_base_path)
    return _knowledge_qa_service_instance



