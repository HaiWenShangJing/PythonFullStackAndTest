import uuid
import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, HTTPStatusError, Response


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai(mock_post, client: AsyncClient):
    """Test the AI chat endpoint with mocked AI service - 成功用例1"""
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
async def test_chat_with_ai_different_model(mock_post, client: AsyncClient):
    """Test the AI chat endpoint with a specific model - 成功用例2"""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Response from specific model"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    # Test data with a specific model
    chat_request = {
        "message": "Hello AI with specific model",
        "session_id": str(uuid.uuid4()),
        "model": "anthropic/claude-3-haiku"
    }
    
    # Make API request
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Response from specific model"
    
    # 验证mock被调用并且使用了正确的模型
    mock_post.assert_called_once()
    assert "model" in mock_post.call_args[1]["json"]
    assert mock_post.call_args[1]["json"]["model"] == "anthropic/claude-3-haiku"


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_empty_context(mock_post, client: AsyncClient):
    """Test the AI chat endpoint with empty context - 成功用例3"""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Response to new conversation"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    # Test data with empty context
    chat_request = {
        "message": "Start a new conversation",
        "session_id": str(uuid.uuid4())
    }
    
    # Make API request
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Response to new conversation"
    
    # 验证消息只包含系统提示和用户消息
    mock_post.assert_called_once()
    sent_messages = mock_post.call_args[1]["json"]["messages"]
    assert len(sent_messages) >= 1  # 至少有用户消息
    # 最后的消息应该是用户消息
    assert sent_messages[-1]["role"] == "user"
    assert sent_messages[-1]["content"] == "Start a new conversation"


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai_http_error(mock_post, client: AsyncClient):
    """Test error handling in the AI chat endpoint - 失败用例1"""
    # Setup mock to raise Exception
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
async def test_chat_with_ai_invalid_response(mock_post, client: AsyncClient):
    """Test handling of invalid API response - 失败用例2"""
    # Setup mock response with invalid format
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "invalid_format": True,
        "no_choices_field": "Missing choices field"
    }
    mock_post.return_value = mock_response
    
    # Test data
    chat_request = {
        "message": "Hello AI",
        "session_id": str(uuid.uuid4())
    }
    
    # Make API request
    response = await client.post("/api/v1/chat", json=chat_request)
    
    # Expect fallback response due to invalid format
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "session_id" in data
    # 应该有错误消息中的一部分
    error_msg = os.environ.get("AI_SERVICE_ERROR_MSG", "AI服务暂时无法使用")
    assert error_msg in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
@patch("backend.app.routers.ai.httpx.AsyncClient.post")
async def test_chat_with_ai_credits_error(mock_post, client: AsyncClient):
    """Test handling of 402 payment required error (credits error) - 失败用例3"""
    # 创建模拟响应对象，返回402错误
    mock_response = AsyncMock()
    mock_response.status_code = 402
    mock_response.raise_for_status = AsyncMock(side_effect=HTTPStatusError("Payment required", request=None, response=mock_response))
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