# Design Document

## Overview

本设计文档描述了智糖小助手管理后台的三个核心增强功能的技术实现方案：

1. **打卡明细管理** - 提供管理员视角的打卡记录查询和Excel导出功能
2. **FAQ批量管理** - 实现FAQ数据的Excel导入导出功能
3. **FAQ图片上传** - 支持在FAQ中嵌入图片，并提供静态文件服务

这些功能将复用现有的数据库连接池、认证机制和路由注册系统，确保与现有系统的无缝集成。

## Architecture

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin Frontend                          │
│  (Vue.js - admin-backend/zhitang-admin)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Route Layer                              │  │
│  │  - /api/admin/checkin/records (GET)                  │  │
│  │  - /api/admin/checkin/export (GET)                   │  │
│  │  - /api/faq/import (POST)                            │  │
│  │  - /api/faq/export (GET)                             │  │
│  │  - /api/faq/upload-image (POST)                      │  │
│  │  - /uploads/<path:filename> (GET)                    │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Service Layer                              │  │
│  │  - AdminCheckinService                               │  │
│  │  - FAQImportExportService                            │  │
│  │  - ImageUploadService                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Database Connection Pool                     │  │
│  │  (utils.database.get_db_connection)                  │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    MySQL Database                            │
│  - checkin_records                                          │
│  - faq_list                                                 │
│  - faq_list_keys                                            │
│  - users                                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  File System Storage                         │
│  - uploads/faq_images/                                      │
│  - logo.png (root)                                          │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

- **后端框架**: Flask 2.x/3.x
- **数据库**: MySQL (通过连接池访问)
- **Excel处理**: openpyxl (读写.xlsx文件)
- **文件上传**: Flask request.files + werkzeug
- **认证**: JWT (复用现有的@token_required装饰器)
- **日志**: 复用现有的utils.logger系统

## Components and Interfaces

### 1. Admin Checkin Routes (main/routes/admin_checkin.py)

新建路由文件，提供管理员视角的打卡记录管理接口。

```python
# Blueprint定义
admin_checkin_bp = Blueprint('admin_checkin', __name__, url_prefix='/api/admin/checkin')

# 接口列表
GET  /api/admin/checkin/records  # 查询打卡记录（支持筛选）
GET  /api/admin/checkin/export   # 导出打卡记录为Excel
```

**接口详情**:

#### GET /api/admin/checkin/records

查询所有用户的打卡记录，支持多维度筛选。

**Query Parameters**:
- `start_date` (optional): 开始日期，格式YYYY-MM-DD
- `end_date` (optional): 结束日期，格式YYYY-MM-DD
- `user_id` (optional): 用户ID筛选
- `page` (optional): 页码，默认1
- `page_size` (optional): 每页数量，默认20

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "records": [
      {
        "record_id": 1,
        "user_id": 123,
        "username": "user1",
        "checkin_type": "blood_glucose",
        "checkin_value": "5.6",
        "glucose_status": "良好",
        "feeling_text": "今天感觉不错",
        "timestamp": "2025-01-15 08:30:00",
        "is_completed": true
      }
    ]
  }
}
```

#### GET /api/admin/checkin/export

导出打卡记录为Excel文件，支持与查询接口相同的筛选条件。

**Query Parameters**: 同上

**Response**: Excel文件下载 (Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

### 2. FAQ Import/Export Routes (扩展main/routes/faq_management.py)

在现有FAQ管理路由中添加导入导出接口。

```python
# 新增接口
POST /api/faq/import   # 导入FAQ（Excel文件）
GET  /api/faq/export   # 导出FAQ为Excel
```

**接口详情**:

#### POST /api/faq/import

从Excel文件批量导入FAQ数据。

**Request**: multipart/form-data
- `file`: Excel文件 (.xlsx)

**Excel格式要求**:
- 第一行为表头: question, answer, category, source, keywords, status, sort_order
- keywords列格式: 逗号分隔的关键词字符串，如"胰岛素,血糖,饮食"

**Response**:
```json
{
  "success": true,
  "message": "导入完成",
  "data": {
    "total": 50,
    "success_count": 48,
    "failed_count": 2,
    "errors": [
      {"row": 3, "reason": "问题内容为空"},
      {"row": 15, "reason": "问题已存在"}
    ]
  }
}
```

#### GET /api/faq/export

导出FAQ数据为Excel文件。

**Query Parameters**:
- `category` (optional): 分类筛选
- `status` (optional): 状态筛选
- `source` (optional): 来源筛选

**Response**: Excel文件下载

### 3. Image Upload Routes (新建main/routes/upload.py)

提供图片上传和静态文件服务。

```python
upload_bp = Blueprint('upload', __name__)

POST /api/faq/upload-image   # 上传FAQ图片
GET  /uploads/<path:filename>  # 访问上传的文件
GET  /<filename>              # 访问根目录静态文件（如logo.png）
```

**接口详情**:

#### POST /api/faq/upload-image

上传图片文件，返回可访问的URL。

**Request**: multipart/form-data
- `file`: 图片文件 (jpg, jpeg, png, gif)

**Response**:
```json
{
  "success": true,
  "data": {
    "url": "https://chat.cmkjai.com/uploads/faq_images/abc123.jpg",
    "filename": "abc123.jpg"
  }
}
```

#### GET /uploads/<path:filename>

访问上传的文件。

**Response**: 文件内容 (设置正确的Content-Type)

#### GET /<filename>

访问根目录的静态文件（如logo.png）。

**Response**: 文件内容

## Data Models

### Database Tables

本功能使用现有的数据库表，无需创建新表。

#### checkin_records (已存在)

```sql
CREATE TABLE checkin_records (
    record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_type VARCHAR(50) DEFAULT 'blood_glucose',
    checkin_value TEXT,
    glucose_status ENUM('一般', '良好', '好'),
    feeling_text TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_completed BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_timestamp (timestamp)
);
```

#### faq_list (已存在)

```sql
CREATE TABLE faq_list (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    source VARCHAR(100),
    status TINYINT DEFAULT 1,
    sort_order INT DEFAULT 0,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    is_manual BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### faq_list_keys (已存在)

```sql
CREATE TABLE faq_list_keys (
    faq_id INT NOT NULL,
    keyword VARCHAR(50) NOT NULL,
    keyword_type ENUM('manual', 'auto') DEFAULT 'manual',
    weight FLOAT DEFAULT 1.0,
    PRIMARY KEY (faq_id, keyword),
    FOREIGN KEY (faq_id) REFERENCES faq_list(id) ON DELETE CASCADE
);
```

### File Storage Structure

```
project_root/
├── logo.png                          # 根目录静态文件
├── uploads/
│   └── faq_images/                   # FAQ图片存储目录
│       ├── {uuid}_{timestamp}.jpg
│       ├── {uuid}_{timestamp}.png
│       └── ...
└── main/
    └── ...
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Checkin records query filter correctness

*For any* combination of filter parameters (start_date, end_date, user_id), the returned checkin records should only include records that match ALL provided filters (AND logic), and the total count should accurately reflect the filtered result set.

**Validates: Requirements 1.1, 1.2, 1.3, 1.6**

### Property 2: Checkin Excel export completeness

*For any* set of checkin records, exporting to Excel should produce a file that contains all required columns (record_id, user_id, username, checkin_type, checkin_value, glucose_status, feeling_text, timestamp) and all records matching the filter criteria.

**Validates: Requirements 1.4, 1.5**

### Property 3: FAQ Excel export completeness

*For any* set of FAQ records, exporting to Excel should produce a file that contains all required columns (id, question, answer, category, source, keywords, status, sort_order) and all records matching the filter criteria.

**Validates: Requirements 2.1, 2.2**

### Property 4: FAQ keyword serialization round-trip

*For any* FAQ record with keywords, exporting to Excel (converting keywords array to comma-separated string) and then importing (parsing comma-separated string back to array) should preserve all keywords without loss or duplication.

**Validates: Requirements 2.3, 2.6**

### Property 5: FAQ import validation and persistence

*For any* valid FAQ Excel file, the system should parse all rows, validate data format, insert valid records into the database, and return accurate counts of successful and failed imports with error details.

**Validates: Requirements 2.4, 2.5, 2.8**

### Property 6: FAQ import idempotency

*For any* valid FAQ Excel file, importing it twice should result in the same database state as importing it once, with duplicate questions being skipped on the second import and reported in the response.

**Validates: Requirements 2.7**

### Property 7: Image upload and URL generation

*For any* valid image file (jpg, jpeg, png, gif), uploading it should generate a unique filename, store the file in the correct directory, and return a URL in the format https://chat.cmkjai.com/uploads/faq_images/{filename} that is immediately accessible.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 8: FAQ image markdown support

*For any* FAQ answer containing Markdown image syntax ![](URL), the system should accept and store the answer without modification, preserving the Markdown formatting.

**Validates: Requirements 3.6**

### Property 9: Static file service correctness

*For any* existing file in the uploads directory or root directory, requesting it via the static file route should return the exact file contents with the correct Content-Type header matching the file extension.

**Validates: Requirements 4.2, 4.4**

## Error Handling

### Error Categories

1. **Validation Errors (400)**
   - 缺少必需参数
   - 无效的日期格式
   - 不支持的文件类型
   - 文件大小超限
   - Excel格式错误

2. **Authentication Errors (401)**
   - 缺少JWT token
   - Token过期或无效

3. **Authorization Errors (403)**
   - 非管理员用户访问管理接口

4. **Not Found Errors (404)**
   - 请求的文件不存在
   - 用户不存在

5. **Server Errors (500)**
   - 数据库连接失败
   - 文件系统操作失败
   - Excel处理异常

### Error Response Format

所有错误响应遵循统一格式：

```json
{
  "success": false,
  "code": 400,
  "message": "错误描述",
  "data": {}
}
```

### Error Handling Strategy

1. **输入验证**: 在服务层进行参数验证，提前返回明确的错误信息
2. **异常捕获**: 使用try-except包裹所有数据库和文件操作
3. **日志记录**: 所有错误都通过logger记录，包含完整的堆栈信息
4. **事务回滚**: 批量导入操作使用数据库事务，失败时自动回滚
5. **资源清理**: 文件上传失败时清理临时文件

## Testing Strategy

### Unit Testing

使用pytest框架进行单元测试，测试库为pytest和pytest-flask。

**测试文件结构**:
```
tests/
├── test_admin_checkin.py      # 打卡管理接口测试
├── test_faq_import_export.py  # FAQ导入导出测试
├── test_image_upload.py       # 图片上传测试
└── conftest.py                # 测试配置和fixtures
```

**测试覆盖**:

1. **Admin Checkin Tests**
   - 测试无筛选条件的记录查询
   - 测试日期范围筛选
   - 测试用户ID筛选
   - 测试分页功能
   - 测试Excel导出文件格式
   - 测试空结果集处理

2. **FAQ Import/Export Tests**
   - 测试有效Excel文件导入
   - 测试重复问题跳过
   - 测试关键词解析
   - 测试Excel导出格式
   - 测试导入错误报告
   - 测试空文件处理

3. **Image Upload Tests**
   - 测试支持的图片格式上传
   - 测试不支持的文件类型拒绝
   - 测试文件大小限制
   - 测试URL生成正确性
   - 测试文件访问
   - 测试不存在文件的404响应

### Property-Based Testing

使用Hypothesis库进行属性测试，验证系统在各种输入下的正确性。

**配置**: 每个属性测试运行100次迭代

**测试标记格式**: 
```python
# Feature: admin-enhancements, Property 1: Checkin records query completeness
```

**属性测试用例**:

1. **Property 1: Checkin records query completeness**
   - 生成随机的打卡记录数据集
   - 生成随机的筛选条件
   - 验证返回结果只包含匹配的记录

2. **Property 2: Excel export data consistency**
   - 生成随机的数据库记录
   - 导出为Excel
   - 读取Excel并比较数据

3. **Property 3: FAQ import idempotency**
   - 生成随机的FAQ Excel文件
   - 导入两次
   - 验证数据库状态一致

4. **Property 4: Keyword serialization round-trip**
   - 生成随机的关键词数组
   - 转换为逗号分隔字符串
   - 解析回数组
   - 验证内容一致

5. **Property 5: Image upload URL accessibility**
   - 生成随机的图片文件
   - 上传并获取URL
   - 访问URL并验证内容

6. **Property 6: File type validation**
   - 生成各种文件扩展名
   - 验证只有允许的类型通过验证

7. **Property 7: Static file service correctness**
   - 创建随机的测试文件
   - 通过静态文件路由访问
   - 验证内容和Content-Type

### Integration Testing

测试完整的请求-响应流程，包括认证、数据库操作和文件系统操作。

**测试场景**:
1. 管理员查询打卡记录并导出Excel
2. 管理员导入FAQ Excel文件
3. 管理员上传图片并在FAQ中使用
4. 前端访问上传的图片

### Test Data Management

- 使用pytest fixtures创建测试数据
- 每个测试使用独立的数据库事务，测试后自动回滚
- 测试文件上传使用临时目录，测试后自动清理

## Implementation Notes

### 1. Excel处理最佳实践

- 使用openpyxl库处理.xlsx文件
- 导出时设置合适的列宽和样式
- 处理大文件时使用流式读取
- 正确处理中文编码

### 2. 文件上传安全

- 验证文件扩展名和MIME类型
- 使用UUID生成唯一文件名，防止覆盖
- 限制文件大小（配置在config.yaml中）
- 存储在uploads目录外，防止直接执行
- 设置正确的文件权限

### 3. 静态文件服务

- 使用Flask的send_from_directory函数
- 设置正确的Content-Type响应头
- 支持浏览器缓存（Cache-Control）
- 处理中文文件名

### 4. 性能优化

- 打卡记录查询使用索引（已有idx_user, idx_timestamp）
- 分页查询避免一次性加载大量数据
- Excel导出使用流式写入，避免内存溢出
- 图片上传使用异步处理（可选）

### 5. 兼容性考虑

- 复用现有的JWT认证机制
- 遵循现有的API响应格式
- 使用现有的数据库连接池
- 日志格式与现有系统一致
