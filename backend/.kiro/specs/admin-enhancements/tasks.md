# Implementation Plan

- [x] 1. 创建管理员打卡记录查询和导出功能
  - 创建新的路由文件 main/routes/admin_checkin.py
  - 实现GET /api/admin/checkin/records接口，支持日期范围、用户ID筛选和分页
  - 实现GET /api/admin/checkin/export接口，导出Excel文件
  - 在main/routes/__init__.py中注册admin_checkin_bp
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ]* 1.1 编写属性测试：打卡记录查询筛选正确性
  - **Property 1: Checkin records query filter correctness**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.6**

- [ ]* 1.2 编写属性测试：打卡记录Excel导出完整性
  - **Property 2: Checkin Excel export completeness**
  - **Validates: Requirements 1.4, 1.5**

- [x] 2. 创建FAQ Excel导入导出功能
  - 在main/routes/faq_management.py中添加POST /api/faq/import接口
  - 实现Excel文件解析，支持question、answer、category、source、keywords等字段
  - 实现关键词字符串解析（逗号分隔转数组）
  - 实现批量插入FAQ和关键词记录
  - 实现重复问题检测和跳过逻辑
  - 在main/routes/faq_management.py中添加GET /api/faq/export接口
  - 实现FAQ数据导出为Excel，包含所有字段
  - 实现关键词数组转逗号分隔字符串
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ]* 2.1 编写属性测试：FAQ Excel导出完整性
  - **Property 3: FAQ Excel export completeness**
  - **Validates: Requirements 2.1, 2.2**

- [ ]* 2.2 编写属性测试：FAQ关键词序列化往返
  - **Property 4: FAQ keyword serialization round-trip**
  - **Validates: Requirements 2.3, 2.6**

- [ ]* 2.3 编写属性测试：FAQ导入验证和持久化
  - **Property 5: FAQ import validation and persistence**
  - **Validates: Requirements 2.4, 2.5, 2.8**

- [ ]* 2.4 编写属性测试：FAQ导入幂等性
  - **Property 6: FAQ import idempotency**
  - **Validates: Requirements 2.7**

- [x] 3. 创建图片上传和静态文件服务
  - 创建新的路由文件 main/routes/upload.py
  - 实现POST /api/faq/upload-image接口
  - 实现文件类型验证（jpg, jpeg, png, gif）
  - 实现文件大小验证
  - 实现唯一文件名生成（UUID + 时间戳）
  - 实现文件存储到uploads/faq_images/目录
  - 实现URL生成（https://chat.cmkjai.com/uploads/faq_images/{filename}）
  - 实现GET /uploads/<path:filename>静态文件服务
  - 实现GET /<filename>根目录静态文件服务（支持logo.png）
  - 设置正确的Content-Type响应头
  - 在main/routes/__init__.py中注册upload_bp
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.4, 4.5_

- [ ]* 3.1 编写属性测试：图片上传和URL生成
  - **Property 7: Image upload and URL generation**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [ ]* 3.2 编写属性测试：FAQ图片Markdown支持
  - **Property 8: FAQ image markdown support**
  - **Validates: Requirements 3.6**

- [ ]* 3.3 编写属性测试：静态文件服务正确性
  - **Property 9: Static file service correctness**
  - **Validates: Requirements 4.2, 4.4**

- [x] 4. 创建uploads目录结构
  - 创建uploads/faq_images/目录（如果不存在）
  - 设置正确的目录权限
  - 添加.gitkeep文件保持目录结构
  - _Requirements: 3.2_

- [ ]* 4.1 编写单元测试：打卡记录查询接口
  - 测试无筛选条件查询
  - 测试日期范围筛选
  - 测试用户ID筛选
  - 测试分页功能
  - 测试空结果集
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 4.2 编写单元测试：打卡记录导出接口
  - 测试Excel文件生成
  - 测试Excel列结构
  - 测试导出数据完整性
  - _Requirements: 1.4, 1.5_

- [ ]* 4.3 编写单元测试：FAQ导入接口
  - 测试有效Excel文件导入
  - 测试无效文件格式拒绝
  - 测试重复问题跳过
  - 测试导入响应格式
  - _Requirements: 2.4, 2.5, 2.7, 2.8_

- [ ]* 4.4 编写单元测试：FAQ导出接口
  - 测试Excel文件生成
  - 测试Excel列结构
  - 测试关键词格式化
  - _Requirements: 2.1, 2.2, 2.3_

- [ ]* 4.5 编写单元测试：图片上传接口
  - 测试支持的图片格式上传
  - 测试不支持的文件类型拒绝
  - 测试文件大小限制
  - 测试URL生成格式
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 4.6 编写单元测试：静态文件服务
  - 测试图片文件访问
  - 测试根目录文件访问（logo.png）
  - 测试404错误处理
  - 测试Content-Type响应头
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [ ] 5. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户
