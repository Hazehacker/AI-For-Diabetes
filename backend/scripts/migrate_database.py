#!/usr/bin/env python3
"""
数据库迁移脚本
~~~~~~~~~~~~~

执行数据库表结构迁移

作者: 智糖团队
日期: 2025-01-15
"""

import pymysql
import yaml
import sys
import re

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 数据库连接参数
DB_CONFIG = {
    'host': config['DATABASE']['HOST'],
    'port': int(config['DATABASE']['PORT']),
    'user': config['DATABASE']['USER'],
    'password': config['DATABASE']['PASSWORD'],
    'database': config['DATABASE']['NAME'],
    'charset': config['DATABASE']['CHARSET']
}


def parse_sql_file(filepath):
    """解析SQL文件，智能分割语句"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除注释
    content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
    
    # 分割SQL语句（处理多行语句）
    statements = []
    current_statement = []
    in_statement = False
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        current_statement.append(line)
        
        # 如果行以分号结尾，表示语句结束
        if line.endswith(';'):
            stmt = ' '.join(current_statement)
            if stmt.strip():
                statements.append(stmt)
            current_statement = []
    
    return statements

def execute_statement(conn, statement, verbose=True):
    """执行单个SQL语句"""
    try:
        cursor = conn.cursor()
        cursor.execute(statement)
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return True, affected_rows
    except Exception as e:
        error_msg = str(e)
        # 忽略某些预期的错误
        if any(x in error_msg.lower() for x in ['already exists', 'duplicate key', 'duplicate entry']):
            return True, 0  # 视为成功但跳过
        return False, error_msg

def check_column_exists(conn, table, column):
    """检查列是否存在"""
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
    result = cursor.fetchone()
    cursor.close()
    return result is not None

def check_table_exists(conn, table):
    """检查表是否存在"""
    cursor = conn.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table}'")
    result = cursor.fetchone()
    cursor.close()
    return result is not None

try:
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)

    
    # ==================== 第一步：修复users表 ====================

    
    # 检查users表是否存在
    if not check_table_exists(conn, 'users'):
        sys.exit(1)
    
    modifications = [
        ('created_at', "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'"),
        ('updated_at', "ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"),
        ('is_active', "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活'"),
        ('last_login', "ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL COMMENT '最后登录时间'"),
    ]
    
    for column, sql in modifications:
        if not check_column_exists(conn, 'users', column):
            success, result = execute_statement(conn, sql)

    
    # ==================== 第二步：执行标签表迁移 ====================

    try:
        statements = parse_sql_file('migrations/001_create_tag_tables.sql')
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for i, statement in enumerate(statements, 1):
            # 显示语句类型
            stmt_type = ""
            if 'CREATE TABLE' in statement.upper():
                # 提取表名
                match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?', statement, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    stmt_type = f"创建表 {table_name}"
            elif 'INSERT INTO' in statement.upper():
                stmt_type = "插入初始数据"
            elif 'CREATE OR REPLACE VIEW' in statement.upper() or 'CREATE VIEW' in statement.upper():
                stmt_type = "创建视图"
            elif 'ALTER TABLE' in statement.upper():
                stmt_type = "修改表"
            else:
                stmt_type = "执行SQL"
            
            success, result = execute_statement(conn, statement)
            if success:
                if result == 0:
                    skip_count += 1
                else:
                    success_count += 1
            else:
                fail_count += 1
        

    except FileNotFoundError:
        pass
    except Exception as e:
        pass
    
    # ==================== 第三步：执行新手引导表迁移 ====================

    try:
        statements = parse_sql_file('migrations/002_create_onboarding_tables.sql')
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for i, statement in enumerate(statements, 1):
            stmt_type = ""
            if 'CREATE TABLE' in statement.upper():
                match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?', statement, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    stmt_type = f"创建表 {table_name}"
            elif 'INSERT INTO' in statement.upper():
                stmt_type = "插入初始数据"
            else:
                stmt_type = "执行SQL"
            
            success, result = execute_statement(conn, statement)
            if success:
                if result == 0:
                    skip_count += 1
                else:
                    success_count += 1
            else:
                fail_count += 1
        

    except FileNotFoundError:
        pass
    except Exception as e:
        pass
    
    # ==================== 验证迁移结果 ====================
    
    required_tables = [
        ('user_tag_definitions', '标签定义表'),
        ('user_tag_values', '标签值表'),
        ('user_tag_history', '标签历史表'),
        ('user_onboarding_status', '新手引导状态表'),
        ('user_onboarding_answers', '新手引导回答表'),
        ('onboarding_questions', '新手引导问题表')
    ]
    
    all_exist = True
    for table, desc in required_tables:
        if check_table_exists(conn, table):
            # 统计记录数
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            cursor.close()
        else:
            all_exist = False
    

    
    # 验证users表字段

    required_columns = ['created_at', 'updated_at', 'is_active', 'last_login']
    for column in required_columns:
        if check_column_exists(conn, 'users', column):
            pass
        else:
            all_exist = False
    

    if all_exist:
        pass
    else:
        pass

    conn.close()

except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
