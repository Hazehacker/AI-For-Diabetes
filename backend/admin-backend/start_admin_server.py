#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智糖小助手 - 独立后台管理服务
独立运行，不与前端混淆
"""

import os
import sys
import json
import time
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
from functools import wraps
import traceback

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入主应用的配置和工具函数
try:
    from main.app import get_db_connection, init_database, load_config
except ImportError:
    # 如果无法导入主应用，使用独立的配置
    import yaml
    
    def load_config():
        """加载配置文件"""
        try:
            config_path = os.path.join(project_root, 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def get_db_connection():
        """获取数据库连接"""
        try:
            config = load_config()
            
            # 使用配置文件中的数据库信息
            # 检查是否是旧格式还是新格式
            if 'DATABASE' in config:
                db_config = config['DATABASE']
                host = db_config.get('HOST', 'localhost')
                port = db_config.get('PORT', 3306)
                user = db_config.get('USER', 'root')
                password = db_config.get('PASSWORD', '')
                database = db_config.get('NAME', 'ai')
            else:
                # 旧格式兼容
                host = config.get('DB_HOST', 'localhost')
                port = config.get('DB_PORT', 3306)
                user = config.get('DB_USER', 'root')
                password = config.get('DB_PASSWORD', '')
                database = config.get('DB_NAME', 'ai')

            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                connect_timeout=10
            )
            return conn
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def init_database():
        """初始化数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 创建必要的表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nickname VARCHAR(100),
                    phone_number VARCHAR(20),
                    date_of_birth DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            ''')
            
            # 检查并添加 is_admin 字段
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
                logger.info("已添加 is_admin 字段")
            except:
                # 字段已存在，忽略错误
                pass
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points (
                    user_id INT PRIMARY KEY,
                    points_balance INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coze_datasets (
                    dataset_id VARCHAR(50) PRIMARY KEY,
                    dataset_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建默认管理员账户
            admin_username = 'admin'
            admin_password = 'admin123'
            
            # 检查管理员是否已存在
            cursor.execute('SELECT user_id FROM users WHERE username = %s', (admin_username,))
            existing_admin = cursor.fetchone()
            
            if not existing_admin:
                # 创建默认管理员
                import bcrypt
                password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute('''
                    INSERT INTO users (username, password_hash, nickname, is_admin)
                    VALUES (%s, %s, %s, %s)
                ''', (admin_username, password_hash, '系统管理员', True))
                
                admin_user_id = cursor.lastrowid
                
                # 初始化管理员积分
                cursor.execute('INSERT INTO points (user_id, points_balance) VALUES (%s, 0)', (admin_user_id,))
                
                logger.info(f"默认管理员账户已创建: {admin_username} / {admin_password}")
            else:
                # 更新现有admin用户的密码和管理员权限
                import bcrypt
                password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = %s, is_admin = TRUE, nickname = %s
                    WHERE username = %s
                ''', (password_hash, '系统管理员', admin_username))
                
                logger.info(f"管理员账户密码已更新: {admin_username} / {admin_password}")
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 加载配置
config = load_config()

# JWT密钥
JWT_SECRET = config.get('JWT_SECRET', 'your-secret-key')

# 管理员认证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]

            # 优先尝试验证Keycloak管理员token
            from utils.jwt_helper import verify_admin_token
            data = verify_admin_token(token)

            if data:
                # Keycloak token验证成功
                user_id = data.get('preferred_username')  # 对于管理员，使用用户名作为标识
                if not user_id:
                    return jsonify({'message': 'Token格式错误'}), 401
            else:
                # 回退到本地JWT验证
                data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = data.get('user_id')
            
                if not user_id:
                    return jsonify({'message': 'Token格式错误'}), 401

            # 检查是否为管理员
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT is_admin FROM users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result or not result[0]:
                return jsonify({'message': '需要管理员权限'}), 403
                
        except Exception as e:
            logger.error(f"认证失败: {e}")
            return jsonify({'message': '无效的认证令牌'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# 外部登录接口对接（手机号登录）
@app.route('/api/login/phone', methods=['POST'])
def phone_login():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if not phone_number or not password:
            return jsonify({'message': '手机号和密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户信息
        cursor.execute('''
            SELECT user_id, username, password_hash, nickname, is_admin 
            FROM users 
            WHERE phone_number = %s
        ''', (phone_number,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'message': '手机号或密码错误'}), 401
        
        user_id, username, password_hash, nickname, is_admin = user
        
        # 验证密码
        if not verify_password(password, password_hash):
            return jsonify({'message': '手机号或密码错误'}), 401
        
        # 生成JWT令牌
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'phone_number': phone_number,
            'is_admin': is_admin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'user_id': user_id,
                'username': username,
                'nickname': nickname,
                'phone_number': phone_number,
                'is_admin': is_admin
            }
        }), 200
        
    except Exception as e:
        logger.error(f"手机号登录失败: {e}")
        return jsonify({'message': '登录失败'}), 500

# 管理员登录
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户信息
        cursor.execute('''
            SELECT user_id, username, password_hash, is_admin 
            FROM users 
            WHERE username = %s AND is_admin = TRUE
        ''', (username,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'message': '用户名或密码错误'}), 401
        
        user_id, db_username, password_hash, is_admin = user
        
        # 验证密码
        if not verify_password(password, password_hash):
            return jsonify({'message': '用户名或密码错误'}), 401
        
        # 生成JWT token（优先尝试Keycloak，失败则使用本地JWT）
        token = None
        try:
            # 尝试导入Keycloak相关函数
            from main.utils.jwt_helper import generate_admin_token
            token = generate_admin_token(db_username, password)
            if token:
                logger.info("使用Keycloak生成管理员token成功")
        except ImportError:
            logger.debug("Keycloak模块未找到，使用本地JWT")
        except Exception as e:
            logger.warning(f"Keycloak管理员token生成失败: {e}，使用本地JWT")
        
        if not token:
            # Keycloak失败或未启用，使用本地JWT
            token = jwt.encode({
                'user_id': user_id,
                'username': db_username,
                'is_admin': is_admin,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            logger.info("使用本地JWT生成管理员token")
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'user_id': user_id,
                'username': db_username,
                'is_admin': is_admin
            }
        }), 200
        
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        return jsonify({'message': '登录失败'}), 500

# 密码验证函数
def verify_password(password, password_hash):
    """验证密码"""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

# 获取用户统计信息
@app.route('/admin/stats/users', methods=['GET'])
@admin_required
def get_user_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 总用户数
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # 今日新增用户（如果created_at字段存在）
        try:
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()')
            today_users = cursor.fetchone()[0]
        except:
            # 如果没有created_at字段，返回0
            today_users = 0
        
        # 活跃用户（7天内登录的用户）
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''')
            active_users = cursor.fetchone()[0]
        except:
            # 如果没有last_login字段，返回总用户数
            active_users = total_users
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'today_users': today_users,
            'active_users': active_users
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {e}")
        return jsonify({'message': '获取统计信息失败'}), 500

# 获取打卡统计信息
@app.route('/admin/stats/checkin', methods=['GET'])
@admin_required
def get_checkin_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查checkin_records表是否存在
        cursor.execute("SHOW TABLES LIKE 'checkin_records'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # 总打卡数
            cursor.execute('SELECT COUNT(*) FROM checkin_records')
            total_checkins = cursor.fetchone()[0]
            
            # 今日打卡数
            cursor.execute('SELECT COUNT(*) FROM checkin_records WHERE DATE(timestamp) = CURDATE()')
            today_checkins = cursor.fetchone()[0]
            
            # 本周打卡数
            cursor.execute('''
                SELECT COUNT(*) FROM checkin_records 
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''')
            week_checkins = cursor.fetchone()[0]
        else:
            # 表不存在，返回0
            total_checkins = 0
            today_checkins = 0
            week_checkins = 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_checkins': total_checkins,
            'today_checkins': today_checkins,
            'week_checkins': week_checkins
        }), 200
        
    except Exception as e:
        logger.error(f"获取打卡统计失败: {e}")
        return jsonify({'message': '获取统计信息失败'}), 500

# 获取聊天统计信息
@app.route('/admin/stats/chat', methods=['GET'])
@admin_required
def get_chat_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查chat_sessions表是否存在
        cursor.execute("SHOW TABLES LIKE 'chat_sessions'")
        sessions_table_exists = cursor.fetchone()
        
        # 检查chat_messages表是否存在
        cursor.execute("SHOW TABLES LIKE 'chat_messages'")
        messages_table_exists = cursor.fetchone()
        
        if sessions_table_exists:
            # 总会话数
            cursor.execute('SELECT COUNT(*) FROM chat_sessions')
            total_sessions = cursor.fetchone()[0]
            
            # 今日会话数
            cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE DATE(created_at) = CURDATE()')
            today_sessions = cursor.fetchone()[0]
        else:
            total_sessions = 0
            today_sessions = 0
        
        if messages_table_exists:
            # 总消息数
            cursor.execute('SELECT COUNT(*) FROM chat_messages')
            total_messages = cursor.fetchone()[0]
        else:
            total_messages = 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_sessions': total_sessions,
            'today_sessions': today_sessions,
            'total_messages': total_messages
        }), 200
        
    except Exception as e:
        logger.error(f"获取聊天统计失败: {e}")
        return jsonify({'message': '获取统计信息失败'}), 500

# 获取用户列表
@app.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户列表（适应现有数据库结构）
        try:
            cursor.execute('''
                SELECT user_id, username, nickname, phone_number, date_of_birth, 
                       is_admin, created_at, last_login
                FROM users 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            ''', (page_size, offset))
        except:
            # 如果没有created_at字段，使用user_id排序
            cursor.execute('''
                SELECT user_id, username, nickname, phone_number, date_of_birth, 
                       is_admin
                FROM users 
                ORDER BY user_id DESC 
                LIMIT %s OFFSET %s
            ''', (page_size, offset))
        
        users = cursor.fetchall()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM users')
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        user_list = []
        for user in users:
            # 根据字段数量处理不同的数据库结构
            if len(user) >= 8:  # 包含created_at和last_login
                user_list.append({
                    'user_id': user[0],
                    'username': user[1],
                    'nickname': user[2],
                    'phone_number': user[3],
                    'date_of_birth': user[4].isoformat() if user[4] else None,
                    'is_admin': bool(user[5]),
                    'created_at': user[6].isoformat() if user[6] else None,
                    'last_login': user[7].isoformat() if user[7] else None
                })
            else:  # 只有基本字段
                user_list.append({
                    'user_id': user[0],
                    'username': user[1],
                    'nickname': user[2],
                    'phone_number': user[3],
                    'date_of_birth': user[4].isoformat() if user[4] else None,
                    'is_admin': bool(user[5]),
                    'created_at': None,
                    'last_login': None
                })
        
        return jsonify({
            'users': user_list,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({'message': '获取用户列表失败'}), 500

# 获取打卡记录
@app.route('/admin/checkin/records', methods=['GET'])
@admin_required
def get_checkin_records():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取打卡记录
        cursor.execute('''
            SELECT cr.record_id, cr.user_id, u.username, u.nickname, 
                   cr.checkin_type, cr.checkin_value, cr.timestamp
            FROM checkin_records cr
            JOIN users u ON cr.user_id = u.user_id
            ORDER BY cr.timestamp DESC 
            LIMIT %s OFFSET %s
        ''', (page_size, offset))
        
        records = cursor.fetchall()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM checkin_records')
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        record_list = []
        for record in records:
            record_list.append({
                'record_id': record[0],
                'user_id': record[1],
                'username': record[2],
                'nickname': record[3],
                'checkin_type': record[4],
                'checkin_value': record[5],
                'timestamp': record[6].isoformat() if record[6] else None
            })
        
        return jsonify({
            'records': record_list,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        logger.error(f"获取打卡记录失败: {e}")
        return jsonify({'message': '获取打卡记录失败'}), 500

# 知识库管理接口

# 获取知识库文件列表（前端实际需要的是文件列表，不是知识库列表）
@app.route('/admin/knowledge/datasets', methods=['GET'])
@admin_required
def get_knowledge_datasets():
    try:
        # 获取请求参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 使用固定的知识库ID
        dataset_id = "7565365575573995555"
        
        # 直接使用配置文件中的Coze访问令牌
        coze_token = config.get('COZE_ACCESS_TOKEN')
        if not coze_token:
            return jsonify({'message': 'Coze访问令牌未配置'}), 500
        
        # 导入requests模块
        import requests
        
        # 调用Coze API获取知识库文档列表
        headers = {
            'Authorization': f'Bearer {coze_token}',
            'Content-Type': 'application/json',
            'Agw-Js-Conv': 'str'
        }
        
        data = {
            'dataset_id': dataset_id,
            'page': page,
            'size': page_size
        }
        
        response = requests.post(
            "https://api.coze.cn/open_api/knowledge/document/list",
            headers=headers,
            json=data
        )
        
        logger.info(f"知识库文档查询响应: {response.status_code}, {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:  # Coze API成功响应
                # 转换数据格式以适配前端
                documents = result.get('document_infos', [])
                formatted_datasets = []
                
                for doc in documents:
                    formatted_datasets.append({
                        'dataset_id': dataset_id,
                        'dataset_name': doc.get('name', ''),  # 显示文件名而不是知识库名
                        'file_name': doc.get('name', ''),
                        'file_id': doc.get('document_id', ''),
                        'id': doc.get('document_id', ''),  # 添加前端期望的id字段
                        'name': doc.get('name', ''),  # 添加前端期望的name字段
                        'created_at': doc.get('create_time', ''),
                        'file_size': doc.get('size', 0)
                    })
                
                return jsonify({
                    'datasets': formatted_datasets,
                    'total': result.get('total', len(formatted_datasets)),
                    'page': page,
                    'page_size': page_size
                }), 200
            else:
                logger.error(f"Coze API返回错误: {result}")
                return jsonify({'message': f'获取知识库文件列表失败: {result.get("msg", "未知错误")}'}), 500
        else:
            logger.error(f"Coze API调用失败: {response.status_code}, {response.text}")
            return jsonify({'message': '调用Coze API失败'}), 500
        
    except Exception as e:
        logger.error(f"获取知识库文件列表失败: {e}")
        logger.error(f"异常详情: {traceback.format_exc()}")
        return jsonify({'message': f'获取知识库文件列表失败: {str(e)}'}), 500

# 上传知识库文件
@app.route('/admin/knowledge/upload', methods=['POST'])
@admin_required
def upload_knowledge_file():
    try:
        if 'file' not in request.files:
            return jsonify({'message': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': '没有选择文件'}), 400
        
        # 获取数据集ID
        dataset_id = request.form.get('dataset_id', '7565365575573995555')
        
        # 直接使用配置文件中的Coze访问令牌
        coze_token = config.get('COZE_ACCESS_TOKEN')
        if not coze_token:
            return jsonify({'message': 'Coze访问令牌未配置'}), 500
        
        # 导入必要的模块
        import requests
        import base64
        
        # 保存临时文件
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        try:
            # 读取文件并转换为base64
            with open(temp_path, 'rb') as f:
                file_content = f.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # 确定文件类型
            file_extension = file.filename.split('.')[-1].lower()
            file_type_map = {
                'txt': 'txt',
                'md': 'txt',  # markdown文件也当作txt处理
                'pdf': 'pdf',
                'doc': 'doc',
                'docx': 'docx'
            }
            file_type = file_type_map.get(file_extension, 'txt')
            
            # 调用Coze API上传文件
            upload_data = {
                "dataset_id": dataset_id,
                "document_bases": [
                    {
                        "name": file.filename,
                        "source_info": {
                            "file_type": file_type,
                            "file_base64": file_base64,
                            "document_source": 0
                        }
                    }
                ],
                "chunk_strategy": {
                    "chunk_type": 0
                },
                "format_type": 0
            }
            
            headers = {
                'Authorization': f'Bearer {coze_token}',
                'Content-Type': 'application/json',
                'Agw-Js-Conv': 'str'
            }
            
            response = requests.post(
                "https://api.coze.cn/open_api/knowledge/document/create",
                headers=headers,
                json=upload_data
            )
            
            logger.info(f"文件上传响应: {response.status_code}, {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:  # Coze API成功响应
                    document_ids = result.get('document_ids', [])
                    document_id = document_ids[0] if document_ids else f"doc_{int(time.time())}"
                    
                    return jsonify({
                        'message': '文件上传成功',
                        'file_name': file.filename,
                        'dataset_id': dataset_id,
                        'file_id': document_id,
                        'size': len(file_content)
                    }), 200
                else:
                    logger.error(f"Coze API返回错误: {result}")
                    return jsonify({'message': f'上传失败: {result.get("msg", "未知错误")}'}), 500
            else:
                logger.error(f"Coze API调用失败: {response.status_code}, {response.text}")
                return jsonify({'message': '调用Coze API失败'}), 500
                
        finally:
            # 清理临时文件
            try:
                os.remove(temp_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"上传知识库文件失败: {e}")
        return jsonify({'message': '上传文件失败'}), 500

# 删除知识库文件
@app.route('/admin/knowledge/delete', methods=['POST'])
@admin_required
def delete_knowledge_file():
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        dataset_id = data.get('dataset_id')
        
        if not file_id or not dataset_id:
            return jsonify({'message': '缺少必要参数'}), 400
        
        # 导入coze_api_wrapper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))
        from coze_api_wrapper import coze_api_wrapper
        
        # 调用coze_api_wrapper的删除方法
        result = coze_api_wrapper.knowledge_base_delete(1, file_id, dataset_id)
        
        if result.get('success'):
            return jsonify({
                'message': '文件删除成功',
                'file_id': file_id,
                'dataset_id': dataset_id
            }), 200
        else:
            return jsonify({'message': result.get('error', '删除失败')}), 500
        
    except Exception as e:
        logger.error(f"删除知识库文件失败: {e}")
        return jsonify({'message': '删除文件失败'}), 500

# 创建知识库
@app.route('/admin/knowledge/dataset', methods=['POST'])
@admin_required
def create_knowledge_dataset():
    try:
        data = request.get_json()
        name = data.get('name', f'智糖助手知识库_{int(time.time())}')
        description = data.get('description', '智糖小助手知识库')
        
        # 导入coze_api_wrapper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))
        from coze_api_wrapper import coze_api_wrapper
        
        # 调用coze_api_wrapper的创建方法
        result = coze_api_wrapper.create_dataset(1, name, description)
        
        if result.get('success'):
            return jsonify({
                'message': '知识库创建成功',
                'dataset_id': result.get('dataset_id'),
                'dataset_name': result.get('dataset_name')
            }), 200
        else:
            return jsonify({'message': result.get('error', '创建失败')}), 500
        
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        return jsonify({'message': '创建知识库失败'}), 500

# 获取知识库文档列表
@app.route('/admin/knowledge/datasets/<dataset_id>/documents', methods=['GET'])
@admin_required
def get_knowledge_documents(dataset_id):
    try:
        # 获取请求参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 导入coze_api_wrapper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))
        from coze_api_wrapper import coze_api_wrapper
        
        # 调用coze_api_wrapper的方法
        result = coze_api_wrapper.list_documents(1, dataset_id, page, page_size)
        
        if result.get('success'):
            documents = result.get('documents', [])
            return jsonify({
                'documents': documents,
                'dataset_id': dataset_id,
                'total': result.get('total', len(documents)),
                'page': page,
                'page_size': page_size
            }), 200
        else:
            logger.error(f"获取文档列表失败: {result.get('error')}")
            return jsonify({'message': result.get('error', '获取文档列表失败')}), 500
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return jsonify({'message': '获取文档列表失败'}), 500

# 获取所有知识库文件（兼容接口）
@app.route('/admin/knowledge/files', methods=['GET'])
@admin_required
def get_knowledge_files():
    try:
        # 导入coze_api_wrapper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))
        from coze_api_wrapper import coze_api_wrapper
        
        # 调用coze_api_wrapper的方法
        result = coze_api_wrapper.knowledge_base_list(1)
        
        if result.get('success'):
            files = result.get('files', [])
            return jsonify({
                'files': files,
                'total': result.get('total', len(files)),
                'datasets_count': result.get('datasets_count', 0)
            }), 200
        else:
            logger.error(f"获取知识库文件列表失败: {result.get('error')}")
            return jsonify({'message': result.get('error', '获取知识库文件列表失败')}), 500
        
    except Exception as e:
        logger.error(f"获取知识库文件列表失败: {e}")
        return jsonify({'message': '获取知识库文件列表失败'}), 500

# 用户管理接口

# 创建用户
@app.route('/admin/users', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname', '')
        phone_number = data.get('phone_number', '')
        is_admin = data.get('is_admin', False)

        logger.info(f"尝试创建用户: {username}")

        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'message': '用户名已存在'}), 400

        # 检查points表是否存在
        cursor.execute("SHOW TABLES LIKE 'points'")
        if not cursor.fetchone():
            logger.warning("points表不存在，创建points表")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points (
                    user_id INT PRIMARY KEY,
                    points_balance INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')

        # 对密码进行哈希加密
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        logger.info(f"为用户 {username} 创建密码哈希")

        # 创建用户
        cursor.execute('''
            INSERT INTO users (username, password_hash, nickname, phone_number, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        ''', (username, password_hash, nickname, phone_number, is_admin))

        user_id = cursor.lastrowid
        logger.info(f"用户 {username} 创建成功，ID: {user_id}")

        try:
            # 初始化用户积分
            cursor.execute('''
                INSERT INTO points (user_id, points_balance, created_at)
                VALUES (%s, 0, NOW())
            ''', (user_id,))
            logger.info(f"为用户 {username} 初始化积分成功")
        except Exception as points_error:
            logger.warning(f"为用户 {username} 初始化积分失败: {points_error}")
            # 积分初始化失败不影响用户创建，继续

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'message': '用户创建成功',
            'user_id': user_id
        }), 200

    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500

# 更新用户信息
@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        if 'nickname' in data:
            update_fields.append('nickname = %s')
            update_values.append(data['nickname'])
        
        if 'phone_number' in data:
            update_fields.append('phone_number = %s')
            update_values.append(data['phone_number'])
        
        if 'is_admin' in data:
            update_fields.append('is_admin = %s')
            update_values.append(data['is_admin'])
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({'message': '没有需要更新的字段'}), 400
        
        update_values.append(user_id)
        
        cursor.execute(f'''
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE user_id = %s
        ''', update_values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': '用户信息更新成功'}), 200
        
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        return jsonify({'message': '更新用户信息失败'}), 500

# 删除用户
@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute('SELECT username FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'message': '用户不存在'}), 404
        
        # 删除用户相关数据（级联删除）
        cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return jsonify({'message': '删除用户失败'}), 500

# 重置用户密码
@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({'message': '新密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute('SELECT username FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'message': '用户不存在'}), 404
        
        # 对新密码进行哈希加密
        import bcrypt
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 更新密码
        cursor.execute('''
            UPDATE users
            SET password_hash = %s, updated_at = NOW()
            WHERE user_id = %s
        ''', (password_hash, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': '密码重置成功'}), 200
        
    except Exception as e:
        logger.error(f"重置用户密码失败: {e}")
        return jsonify({'message': '重置密码失败'}), 500

# 健康检查
@app.route('/admin/health', methods=['GET'])
def health_check():
    try:
        # 检查数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'admin-backend'
        }), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'service': 'admin-backend'
        }), 500

# 静态资源服务（libs目录）
@app.route('/libs/<path:filename>')
def libs_static(filename):
    # 从项目根目录的libs目录提供静态文件
    libs_path = os.path.join(project_root, '前端页面', 'libs')
    return send_from_directory(libs_path, filename)

# JS文件服务（admin-backend/js目录）- 必须在 /admin/<path:filename> 之前注册
@app.route('/admin/js/<path:filename>')
def admin_js_static(filename):
    js_path = os.path.join(os.path.dirname(__file__), 'js')
    logger.debug(f"请求JS文件: {filename}, 路径: {js_path}")
    if not os.path.exists(js_path):
        logger.error(f"JS目录不存在: {js_path}")
        return jsonify({'error': 'JS目录不存在'}), 404
    file_path = os.path.join(js_path, filename)
    if not os.path.exists(file_path):
        logger.error(f"JS文件不存在: {file_path}")
        return jsonify({'error': f'文件不存在: {filename}'}), 404
    logger.info(f"返回JS文件: {file_path}")
    return send_from_directory(js_path, filename)

# 根路径重定向到管理页面
@app.route('/')
def root_redirect():
    return redirect('/admin')

# 管理页面路由（旧版本，保留兼容性）

@app.route('/admin/user-management')
def user_management_page():
    user_path = os.path.join(os.path.dirname(__file__), 'user-management.html')
    if os.path.exists(user_path):
        with open(user_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>用户管理页面未找到</h1>'

# 登录页面
@app.route('/admin/login')
def admin_login_page():
    login_path = os.path.join(os.path.dirname(__file__), 'login.html')
    if os.path.exists(login_path):
        with open(login_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>登录页面未找到</h1>'

# 管理后台首页（重定向到登录）
@app.route('/admin')
def admin_index():
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return redirect('/admin/login')

# 管理后台仪表盘
@app.route('/admin/dashboard')
def admin_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>仪表盘页面未找到</h1>'

# 其他管理页面路由
@app.route('/admin/tag-management')
def tag_management_page():
    tag_path = os.path.join(os.path.dirname(__file__), 'tag-management.html')
    if os.path.exists(tag_path):
        with open(tag_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>标签管理页面未找到</h1>'

@app.route('/admin/faq-management')
def faq_management_page():
    faq_path = os.path.join(os.path.dirname(__file__), 'faq-management.html')
    if os.path.exists(faq_path):
        with open(faq_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>FAQ管理页面未找到</h1>'

@app.route('/admin/prompt-management')
def prompt_management_page():
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt-management.html')
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>提示词管理页面未找到</h1>'

@app.route('/admin/chat-history')
def chat_history_page():
    chat_path = os.path.join(os.path.dirname(__file__), 'chat-history.html')
    if os.path.exists(chat_path):
        with open(chat_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>消息记录页面未找到</h1>'

@app.route('/admin/knowledge-management')
def knowledge_management_page_new():
    knowledge_path = os.path.join(os.path.dirname(__file__), 'knowledge-management.html')
    if os.path.exists(knowledge_path):
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '<h1>知识文档管理页面未找到</h1>'

# 静态文件服务（用于管理页面）- 放在最后，作为兜底路由
# 注意：这个路由必须在所有具体的 /admin/xxx 路由之后注册
@app.route('/admin/<path:filename>')
def admin_static(filename):
    # 优先检查自定义HTML文件
    if filename.endswith('.html') and not filename.startswith('js/'):
        custom_html_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(custom_html_path):
            with open(custom_html_path, 'r', encoding='utf-8') as f:
                return f.read()

    # 检查Vue应用目录
    admin_dist_path = os.path.join(os.path.dirname(__file__), 'zhitang-admin', 'dist')
    if os.path.exists(admin_dist_path):
        file_path = os.path.join(admin_dist_path, filename)
        if os.path.exists(file_path):
            return send_from_directory(admin_dist_path, filename)

    return jsonify({'error': f'文件未找到: {filename}'}), 404

if __name__ == '__main__':
    try:
        # 尝试初始化数据库
        try:
            init_database()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.warning(f"数据库初始化失败，服务将以演示模式启动: {e}")
            logger.warning("部分功能可能不可用，请确保MySQL服务正在运行")
        
        # 启动服务
        port = int(os.environ.get('ADMIN_PORT', 8901))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"启动管理后台服务，端口: {port}")
        logger.info(f"管理界面: http://localhost:{port}/admin")
        logger.info(f"知识库管理: http://localhost:{port}/admin/knowledge-management")
        logger.info(f"用户管理: http://localhost:{port}/admin/user-management")
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"启动管理后台服务失败: {e}")
        traceback.print_exc()
        sys.exit(1)
