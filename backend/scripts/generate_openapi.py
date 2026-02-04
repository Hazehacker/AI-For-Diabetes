#!/usr/bin/env python3
"""
生成 OpenAPI 3.0 规范文档
用于导入到 Apifox 等 API 管理工具

使用方法:
    python scripts/generate_openapi.py

输出:
    openapi.json - OpenAPI 3.0 规范文档（JSON格式）
    openapi.yaml - OpenAPI 3.0 规范文档（YAML格式）
"""

import json
import yaml
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "main"))

# OpenAPI 3.0 基础结构
openapi_spec = {
    "openapi": "3.0.3",
    "info": {
        "title": "智糖小助手 API",
        "description": "智糖小助手 RESTful API 文档\n\n提供完整的用户管理、对话、标签、知识问答等功能。",
        "version": "2.0.0",
        "contact": {
            "name": "智糖团队"
        }
    },
    "servers": [
        {
            "url": "http://localhost:8900",
            "description": "本地开发环境"
        },
        {
            "url": "https://api.zhitang.com",
            "description": "生产环境"
        }
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Token认证，格式: Bearer <token>"
            }
        },
        "schemas": {
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "message": {
                        "type": "string",
                        "example": "错误信息"
                    }
                }
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "message": {
                        "type": "string",
                        "example": "操作成功"
                    }
                }
            }
        }
    },
    "paths": {}
}

# 通用响应定义
def get_error_responses():
    return {
        "400": {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "401": {
            "description": "未授权，需要登录",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "500": {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    }

# 定义所有API接口
api_paths = {
    # ========== 认证系统 ==========
    "/api/health": {
        "get": {
            "tags": ["认证系统"],
            "summary": "健康检查",
            "description": "检查API服务是否正常运行",
            "operationId": "healthCheck",
            "responses": {
                "200": {
                    "description": "服务正常",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "message": {"type": "string"},
                                    "version": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "/api/register": {
        "post": {
            "tags": ["认证系统"],
            "summary": "用户注册",
            "description": "新用户注册",
            "operationId": "register",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["username", "password"],
                            "properties": {
                                "username": {"type": "string", "description": "用户名"},
                                "password": {"type": "string", "description": "密码"},
                                "email": {"type": "string", "format": "email", "description": "邮箱"},
                                "nickname": {"type": "string", "description": "昵称"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "注册成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/login": {
        "post": {
            "tags": ["认证系统"],
            "summary": "用户登录",
            "description": "用户登录获取Token",
            "operationId": "login",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["username", "password"],
                            "properties": {
                                "username": {"type": "string", "description": "用户名"},
                                "password": {"type": "string", "description": "密码"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "登录成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "token": {"type": "string", "description": "JWT Token"},
                                    "user": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/refresh": {
        "post": {
            "tags": ["认证系统"],
            "summary": "刷新Token",
            "description": "刷新JWT Token",
            "operationId": "refreshToken",
            "security": [{"BearerAuth": []}],
            "responses": {
                "200": {
                    "description": "刷新成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "token": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 用户管理 ==========
    "/api/user/profile": {
        "get": {
            "tags": ["用户管理"],
            "summary": "获取用户资料",
            "description": "获取当前登录用户的资料信息",
            "operationId": "getUserProfile",
            "security": [{"BearerAuth": []}],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "user": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        },
        "put": {
            "tags": ["用户管理"],
            "summary": "更新用户资料",
            "description": "更新当前登录用户的资料信息",
            "operationId": "updateUserProfile",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "nickname": {"type": "string"},
                                "email": {"type": "string"},
                                "avatar": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "更新成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 对话系统 ==========
    "/api/chat/history": {
        "get": {
            "tags": ["对话系统"],
            "summary": "获取对话历史",
            "description": "获取用户的对话历史记录",
            "operationId": "getChatHistory",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {
                    "name": "conversation_id",
                    "in": "query",
                    "description": "对话ID（可选）",
                    "required": False,
                    "schema": {"type": "string"}
                },
                {
                    "name": "limit",
                    "in": "query",
                    "description": "返回消息数量",
                    "required": False,
                    "schema": {"type": "integer", "default": 50}
                }
            ],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "messages": {"type": "array"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/chat/stream": {
        "post": {
            "tags": ["对话系统"],
            "summary": "流式对话",
            "description": "普通流式对话接口",
            "operationId": "streamChat",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["message"],
                            "properties": {
                                "message": {"type": "string", "description": "用户消息"},
                                "conversation_id": {"type": "string", "description": "对话ID（可选）"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "流式响应",
                    "content": {
                        "text/event-stream": {
                            "schema": {"type": "string"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/chat/stream_with_tts": {
        "post": {
            "tags": ["对话系统"],
            "summary": "带TTS的流式对话",
            "description": "流式对话并返回语音合成结果",
            "operationId": "streamChatWithTTS",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["message"],
                            "properties": {
                                "message": {"type": "string", "description": "用户消息"},
                                "conversation_id": {"type": "string", "description": "对话ID（可选）"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "流式响应（包含文本和音频）",
                    "content": {
                        "text/event-stream": {
                            "schema": {"type": "string"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 标签管理 ==========
    "/api/tags": {
        "get": {
            "tags": ["标签管理"],
            "summary": "获取用户标签",
            "description": "获取当前用户的所有标签",
            "operationId": "getUserTags",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {
                    "name": "category",
                    "in": "query",
                    "description": "标签分类",
                    "required": False,
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "tags": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        },
        "post": {
            "tags": ["标签管理"],
            "summary": "设置用户标签",
            "description": "设置或更新用户标签（支持管理员为其他用户设置）",
            "operationId": "setUserTag",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["tag_key", "tag_value"],
                            "properties": {
                                "user_id": {"type": "integer", "description": "用户ID（可选，管理员可为其他用户设置）"},
                                "tag_key": {"type": "string", "description": "标签键"},
                                "tag_value": {"type": "string", "description": "标签值"},
                                "source": {"type": "string", "description": "数据来源", "default": "manual"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "设置成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 知识问答 ==========
    "/api/knowledge-qa/search": {
        "post": {
            "tags": ["知识问答"],
            "summary": "知识检索",
            "description": "从Markdown文档和FAQ数据库中检索相关知识",
            "operationId": "searchKnowledge",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["query"],
                            "properties": {
                                "query": {"type": "string", "description": "查询文本"},
                                "top_k": {"type": "integer", "description": "返回最相关的top_k条", "default": 3},
                                "min_similarity": {"type": "number", "description": "最小相似度阈值", "default": 0.1}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "检索成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "query": {"type": "string"},
                                    "count": {"type": "integer"},
                                    "results": {"type": "array"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/knowledge-qa/answer": {
        "post": {
            "tags": ["知识问答"],
            "summary": "回答问题",
            "description": "基于知识库回答问题",
            "operationId": "answerQuestion",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["question"],
                            "properties": {
                                "question": {"type": "string", "description": "用户问题"},
                                "top_k": {"type": "integer", "default": 3},
                                "use_ai": {"type": "boolean", "default": False}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "回答成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "answer": {"type": "string"},
                                    "confidence": {"type": "number"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== FAQ管理 ==========
    "/api/faq/list": {
        "get": {
            "tags": ["FAQ管理"],
            "summary": "获取FAQ列表",
            "description": "分页、筛选、搜索FAQ列表",
            "operationId": "getFaqList",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                {"name": "page_size", "in": "query", "schema": {"type": "integer", "default": 20}},
                {"name": "category", "in": "query", "schema": {"type": "string"}},
                {"name": "status", "in": "query", "schema": {"type": "integer"}},
                {"name": "search", "in": "query", "schema": {"type": "string"}},
                {"name": "source", "in": "query", "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "total": {"type": "integer"},
                                            "page": {"type": "integer"},
                                            "page_size": {"type": "integer"},
                                            "items": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    "/api/faq/{id}": {
        "get": {
            "tags": ["FAQ管理"],
            "summary": "获取FAQ详情",
            "description": "根据ID获取FAQ详情",
            "operationId": "getFaqDetail",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        },
        "post": {
            "tags": ["FAQ管理"],
            "summary": "创建FAQ",
            "description": "创建新的FAQ（自动生成AI关键词）",
            "operationId": "createFaq",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["question", "answer"],
                            "properties": {
                                "question": {"type": "string"},
                                "answer": {"type": "string"},
                                "category": {"type": "string"},
                                "keywords": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "创建成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        },
        "put": {
            "tags": ["FAQ管理"],
            "summary": "更新FAQ",
            "description": "更新FAQ信息",
            "operationId": "updateFaq",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "answer": {"type": "string"},
                                "category": {"type": "string"},
                                "status": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "更新成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        },
        "delete": {
            "tags": ["FAQ管理"],
            "summary": "删除FAQ",
            "description": "删除指定的FAQ",
            "operationId": "deleteFaq",
            "security": [{"BearerAuth": []}],
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "responses": {
                "200": {
                    "description": "删除成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== TTS服务 ==========
    "/api/tts": {
        "post": {
            "tags": ["TTS服务"],
            "summary": "文字转语音",
            "description": "将文本转换为语音（腾讯云TTS）",
            "operationId": "textToSpeech",
            "security": [{"BearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["text"],
                            "properties": {
                                "text": {"type": "string", "description": "要转换的文本"},
                                "voice_type": {"type": "string", "description": "语音类型"},
                                "speed": {"type": "number", "description": "语速"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "转换成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "audio_url": {"type": "string"},
                                    "audio_base64": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 打卡系统 ==========
    "/api/checkin": {
        "post": {
            "tags": ["打卡系统"],
            "summary": "用户打卡",
            "description": "用户每日打卡",
            "operationId": "checkin",
            "security": [{"BearerAuth": []}],
            "responses": {
                "200": {
                    "description": "打卡成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                **get_error_responses()
            }
        }
    },
    
    # ========== 积分系统 ==========
    "/api/points/balance": {
        "get": {
            "tags": ["积分系统"],
            "summary": "获取积分余额",
            "description": "获取当前用户的积分余额",
            "operationId": "getPointsBalance",
            "security": [{"BearerAuth": []}],
            "responses": {
                "200": {
                    "description": "获取成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "balance": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                **get_error_responses()
            }
        }
    }
}

# 合并到主规范
openapi_spec["paths"] = api_paths

def main():
    """生成OpenAPI文档"""
    output_dir = project_root
    
    # 生成JSON格式
    json_file = output_dir / "openapi.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
    
    # 生成YAML格式
    try:
        import yaml
        yaml_file = output_dir / "openapi.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_spec, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except ImportError:
        pass
    
if __name__ == "__main__":
    main()

