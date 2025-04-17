import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
import httpx

from backend.app.schemas import ChatRequest, ChatResponse

router = APIRouter()

# Get OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "testkey")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


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