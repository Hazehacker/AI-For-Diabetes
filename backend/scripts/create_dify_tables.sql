-- Dify知识库管理数据库表结构

-- 知识库数据集表
CREATE TABLE IF NOT EXISTS knowledge_datasets (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(50) DEFAULT 'dify',
    permission VARCHAR(20) DEFAULT 'all_team_members',
    data_source_type VARCHAR(20) DEFAULT 'upload_file',
    indexing_technique VARCHAR(20) DEFAULT 'high_quality',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_provider (provider),
    INDEX idx_created_at (created_at)
);

-- 知识库文档表
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    title VARCHAR(500),
    content LONGTEXT,
    word_count INT DEFAULT 0,
    tokens INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    indexing_status VARCHAR(20) DEFAULT 'completed',
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_document_dataset (document_id, dataset_id),
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_status (status),
    INDEX idx_indexing_status (indexing_status)
);

-- 文档片段表（用于召回）
CREATE TABLE IF NOT EXISTS knowledge_document_segments (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    title VARCHAR(500),
    content TEXT,
    position INT DEFAULT 0,
    score DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_document_id (document_id),
    INDEX idx_dataset_id (dataset_id)
);

-- 上传文件表
CREATE TABLE IF NOT EXISTS knowledge_uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id VARCHAR(36) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    file_size BIGINT DEFAULT 0,
    mime_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 文件批次表
CREATE TABLE IF NOT EXISTS knowledge_file_batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id VARCHAR(36) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 批次文件关联表
CREATE TABLE IF NOT EXISTS knowledge_batch_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id VARCHAR(36) NOT NULL,
    file_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_batch_id (batch_id),
    INDEX idx_file_id (file_id),
    UNIQUE KEY uk_batch_file (batch_id, file_id)
);

-- 处理任务表
CREATE TABLE IF NOT EXISTS knowledge_processing_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL UNIQUE,
    dataset_id VARCHAR(36) NOT NULL,
    batch_id VARCHAR(36),
    process_rule JSON,
    status VARCHAR(20) DEFAULT 'pending',
    progress INT DEFAULT 0,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_batch_id (batch_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 初始化默认知识库
INSERT IGNORE INTO knowledge_datasets (id, name, description) VALUES
('110b7e73-3050-49f4-b424-910951a016d9', '智糖小助手知识库', '儿童青少年糖尿病管理相关知识库');
