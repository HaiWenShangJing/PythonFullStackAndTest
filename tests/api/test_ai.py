import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


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
    response = await client.post("/api/v1/ai/chat", json=chat_request)
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a test AI response"
    assert "session_id" in data
    
    # Verify the mock was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
    assert "messages" in call_args[1]["json"]
    assert len(call_args[1]["json"]["messages"]) == len(chat_request["context"]) + 1


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
    response = await client.post("/api/v1/ai/chat", json=chat_request)
    
    # Validate error response
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Internal server error" in data["detail"]