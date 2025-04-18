import uuid
import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, HTTPStatusError, Response


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai(mock_post, client: AsyncClient):
    """Test the AI chat endpoint with mocked AI service"""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a test AI response"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    # Test data
    chat_request = {
        "message": "Hello AI",
        "session_id": str(uuid.uuid4()),
        "context": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]
    }
    
    # Make API request
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a test AI response"
    assert "session_id" in data
    
    # Verify the mock was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    # 使用环境变量中的API URL
    api_url = os.environ.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
    assert call_args[0][0] in [api_url, "https://api.openrouter.ai/api/v1/chat/completions"]
    # 验证请求包含必要字段
    assert "messages" in call_args[1]["json"]
    assert "max_tokens" in call_args[1]["json"]  # 验证max_tokens字段被添加
    assert len(call_args[1]["json"]["messages"]) == len(chat_request["context"]) + 1


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai_http_error(mock_post, client: AsyncClient):
    """Test error handling in the AI chat endpoint"""
    # Setup mock to raise HTTPStatusError
    mock_post.side_effect = Exception("API Error")
    
    # Test data
    chat_request = {
        "message": "Hello AI",
    }
    
    # Make API request
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # 从环境变量获取错误消息模板
    error_msg_1 = os.environ.get("AI_SERVICE_ERROR_MSG", "AI服务暂时无法使用")
    error_msg_2 = os.environ.get("AI_FALLBACK_MSG", "我是AI助手")
    
    # Validate error response - 我们现在会返回硬编码响应而不是错误
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "session_id" in data
    assert error_msg_1 in data["message"] or error_msg_2 in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai_credits_error(mock_post, client: AsyncClient):
    """Test handling of 402 payment required error (credits error)"""
    # 创建模拟响应对象，返回402错误
    mock_response = AsyncMock()
    mock_response.status_code = 402
    mock_response.json.return_value = {
        "error": {
            "code": 402,
            "message": "This request requires more credits. You requested 1000 tokens, but can only afford 500."
        }
    }
    mock_response.text = '{"error":{"code":402,"message":"Credits error"}}'
    mock_post.return_value = mock_response
    
    # 测试数据
    chat_request = {
        "message": "需要很多token的大请求",
        "session_id": str(uuid.uuid4())
    }
    
    # 发送API请求
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # 从环境变量获取错误消息模板
    credits_error_msg = os.environ.get("AI_CREDITS_ERROR_MSG", "积分不足")
    
    # 验证响应 - 应该得到200状态码和特定的错误消息
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert credits_error_msg in data["message"]
    assert "session_id" in data


@pytest.mark.api
@pytest.mark.asyncio
async def test_test_connection_endpoint(client: AsyncClient):
    """测试连接测试端点"""
    # 发送请求到测试端点
    response = await client.get("/api/v1/test-connection")
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert "env_variables" in data
    assert "api_tests" in data
    
    # 验证环境变量信息存在
    expected_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_API_URL",
        "MODEL_NAME"
    ]
    for var in expected_vars:
        assert var in data["env_variables"]
    
    # 验证API测试结果存在
    assert len(data["api_tests"]) > 0
    for test in data["api_tests"]:
        assert "url" in test
        assert "status" in test
        assert "details" in test