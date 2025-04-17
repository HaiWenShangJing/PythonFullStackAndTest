import os
import uuid
import logging
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv, find_dotenv

from backend.app.schemas import ChatRequest, ChatResponse

# 配置日志
logger = logging.getLogger(__name__)

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# 尝试多种方式加载环境变量
logger.info(f"Trying to load .env from: {ENV_FILE}")
if ENV_FILE.exists():
    logger.info(f".env file exists at {ENV_FILE}")
    load_dotenv(dotenv_path=ENV_FILE)
else:
    logger.warning(f".env file not found at {ENV_FILE}")
    # 尝试自动查找.env文件
    dotenv_path = find_dotenv()
    if dotenv_path:
        logger.info(f"Found .env at {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        logger.warning("No .env file found. Using environment variables or defaults.")

# 获取环境变量
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "testkey")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 打印API密钥前5个字符，用于调试
if OPENROUTER_API_KEY != "testkey":
    logger.info(f"Using API key: {OPENROUTER_API_KEY[:5]}...")
else:
    logger.warning("Using default API key (testkey)")

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message using OpenRouter API"""
    # Generate a session ID if not provided
    session_id = request.session_id or uuid.uuid4()
    
    # Prepare the context for the AI model
    messages = []
    
    # Add context from previous messages if available
    if request.context:
        for msg in request.context:
            messages.append(msg)
    
    # Add the current message
    messages.append({"role": "user", "content": request.message})
    
    try:
        # Call the OpenRouter API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",  # Default model
                    "messages": messages
                },
                timeout=30.0
            )
            
            # Check for successful response
            response.raise_for_status()
            data = response.json()
            
            # Extract the AI's response
            ai_message = data["choices"][0]["message"]["content"]
            
            return {"message": ai_message, "session_id": session_id}
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenRouter API error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with OpenRouter API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )