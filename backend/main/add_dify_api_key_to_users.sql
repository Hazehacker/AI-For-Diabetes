-- 为用户表添加Dify API Key字段
-- 用于支持基于用户权限的Dify知识库访问控制

USE ai;

-- 添加Dify API Key字段
ALTER TABLE users 
ADD COLUMN dify_api_key VARCHAR(255) DEFAULT NULL COMMENT '用户对应的Dify API Key',
ADD COLUMN dify_dataset_id VARCHAR(100) DEFAULT '110b7e73-3050-49f4-b424-910951a016d9' COMMENT '用户可访问的数据集ID',
ADD COLUMN knowledge_permissions JSON DEFAULT NULL COMMENT '知识库权限配置';

-- 为管理员用户设置默认的Dify API Key
UPDATE users 
SET 
  dify_api_key = 'dataset-51mRkWzs9zAD9yR5eAOsLrpL',
  dify_dataset_id = '28f90de6-f698-4b20-a7fe-02cadfadc6a6'
WHERE is_admin = 1;

-- 创建索引以提高查询性能
CREATE INDEX idx_users_dify_api_key ON users(dify_api_key);
CREATE INDEX idx_users_is_admin ON users(is_admin);

-- 验证修改结果
SELECT user_id, username, is_admin, dify_api_key, dify_dataset_id 
FROM users 
WHERE is_admin = 1 OR dify_api_key IS NOT NULL;
