#!/bin/bash

# 智糖小助手 - 基于用户认证的知识库API测试脚本

echo "=============================================="
echo "智糖小助手 - 基于用户认证的知识库API测试"
echo "=============================================="
echo

# 配置
BASE_URL="http://localhost:8900"
DATASET_ID="110b7e73-3050-49f4-b424-910951a016d9"

echo "第一步：用户登录获取token"
echo "请先通过前端或API登录获取用户token"
echo "管理员用户会自动分配Dify API Key权限"
echo

# 这里需要手动设置用户token
USER_TOKEN="your_user_token_here"

if [ "$USER_TOKEN" = "your_user_token_here" ]; then
    echo "请先设置 USER_TOKEN 变量为实际的用户登录token"
    echo "可以通过以下方式获取token："
    echo "1. 前端登录获取token"
    echo "2. 调用登录API获取token"
    echo "3. 从浏览器开发者工具中复制token"
    exit 1
fi

echo "第二步：测试知识库数据集列表"
echo "获取用户可访问的知识库文档列表"
echo

curl -X GET "$BASE_URL/api/knowledge/datasets?page=1&page_size=5" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -s | jq .

echo
echo "=============================================="
echo "第三步：测试知识库文件上传"
echo "上传一个测试文件到知识库"
echo

# 创建一个测试文件
echo "这是一个测试文件，用于验证知识库上传功能。" > test_knowledge_file.txt

# 注意：实际使用时需要提供真实的文件路径
echo "注意：文件上传需要真实的本地文件路径"
echo "示例请求体："
echo '{
  "file_path": "/path/to/your/test_knowledge_file.txt",
  "file_name": "test_knowledge_file.txt"
}'

# 清理测试文件
rm -f test_knowledge_file.txt

echo
echo "=============================================="
echo "第四步：测试聊天集成知识库"
echo "（这个会自动调用知识库进行检索和回答）"
echo

curl -X POST "$BASE_URL/api/chat/stream" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "儿童糖尿病患者早餐后2小时血糖应该控制在什么范围内？",
    "conversation_id": "knowledge_test_'$(date +%s)'"
  }' -N -s | head -20

echo
echo "=============================================="
echo "测试完成！"
echo
echo "安全特性说明："
echo "✅ 不再使用硬编码的Dify API Key"
echo "✅ 基于用户JWT token进行身份验证"
echo "✅ 每个用户只能访问自己的知识库权限"
echo "✅ 管理员用户自动分配完整权限"
echo "=============================================="
