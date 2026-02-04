# Requirements Document

## Introduction

本文档定义了智糖小助手管理后台的三个核心增强功能：打卡明细管理、FAQ批量导入导出、以及FAQ图片上传功能。这些功能旨在提升管理员的工作效率，使其能够更好地管理用户打卡数据和FAQ知识库内容。

## Glossary

- **Admin System**: 管理后台系统，提供管理员操作界面和API接口
- **Checkin Record**: 打卡记录，用户的健康打卡数据，包括血糖监测、运动、用药等
- **FAQ**: 常见问题解答，存储在faq_list表中的知识库条目
- **Excel Export**: Excel导出功能，将数据库记录转换为Excel文件供下载
- **Excel Import**: Excel导入功能，从Excel文件批量导入数据到数据库
- **Static File Service**: 静态文件服务，用于存储和访问上传的图片等静态资源
- **Image Upload**: 图片上传功能，允许在FAQ中嵌入图片

## Requirements

### Requirement 1

**User Story:** 作为管理员，我想要查询和导出用户打卡记录，以便分析用户健康数据和生成报表。

#### Acceptance Criteria

1. WHEN 管理员访问打卡明细接口 THEN Admin System SHALL 返回所有用户的打卡记录列表
2. WHEN 管理员提供开始日期和结束日期参数 THEN Admin System SHALL 返回该时间范围内的打卡记录
3. WHEN 管理员提供用户ID参数 THEN Admin System SHALL 返回该用户的所有打卡记录
4. WHEN 管理员请求导出打卡记录 THEN Admin System SHALL 生成包含所有筛选条件的Excel文件
5. WHEN 导出的Excel文件生成 THEN Admin System SHALL 包含record_id、user_id、username、checkin_type、checkin_value、glucose_status、feeling_text、timestamp等字段
6. WHEN 管理员同时使用多个筛选条件 THEN Admin System SHALL 返回满足所有条件的记录

### Requirement 2

**User Story:** 作为管理员，我想要批量导入和导出FAQ数据，以便高效管理知识库内容。

#### Acceptance Criteria

1. WHEN 管理员请求导出FAQ列表 THEN Admin System SHALL 生成包含所有FAQ数据的Excel文件
2. WHEN 导出的Excel文件生成 THEN Admin System SHALL 包含id、question、answer、category、source、keywords、status、sort_order等字段
3. WHEN 导出Excel时存在关键词 THEN Admin System SHALL 将关键词数组转换为逗号分隔的字符串
4. WHEN 管理员上传Excel文件进行导入 THEN Admin System SHALL 解析Excel文件并验证数据格式
5. WHEN Excel数据验证通过 THEN Admin System SHALL 批量插入FAQ记录到数据库
6. WHEN Excel中包含关键词列 THEN Admin System SHALL 将逗号分隔的关键词字符串解析为关键词数组并存储
7. WHEN 导入过程中遇到重复问题 THEN Admin System SHALL 跳过该记录并在响应中报告
8. WHEN 导入完成 THEN Admin System SHALL 返回成功导入数量和失败记录详情

### Requirement 3

**User Story:** 作为管理员，我想要在创建或编辑FAQ时上传图片，以便提供更丰富的视觉内容。

#### Acceptance Criteria

1. WHEN 管理员上传图片文件 THEN Admin System SHALL 验证文件类型为jpg、jpeg、png或gif
2. WHEN 图片文件验证通过 THEN Admin System SHALL 生成唯一的文件名并存储到指定目录
3. WHEN 图片存储成功 THEN Admin System SHALL 返回可访问的图片URL
4. WHEN 图片URL生成 THEN Admin System SHALL 使用格式https://chat.cmkjai.com/uploads/faq_images/{filename}
5. WHEN 用户访问图片URL THEN Static File Service SHALL 返回对应的图片文件
6. WHEN 管理员在FAQ答案中插入图片 THEN Admin System SHALL 支持Markdown格式![](图片URL)
7. WHEN 上传的文件超过大小限制 THEN Admin System SHALL 拒绝上传并返回错误信息
8. WHEN 上传的文件类型不支持 THEN Admin System SHALL 拒绝上传并返回错误信息

### Requirement 4

**User Story:** 作为系统，我需要提供静态文件服务，以便前端能够访问上传的图片和其他静态资源。

#### Acceptance Criteria

1. WHEN Flask应用启动 THEN Admin System SHALL 配置静态文件路由
2. WHEN 客户端请求静态文件路径 THEN Static File Service SHALL 返回对应的文件内容
3. WHEN 请求的文件不存在 THEN Static File Service SHALL 返回404错误
4. WHEN 返回图片文件 THEN Static File Service SHALL 设置正确的Content-Type响应头
5. WHEN 访问logo.png THEN Static File Service SHALL 从根目录返回logo.png文件
