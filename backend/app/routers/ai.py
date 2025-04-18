import os
import uuid
import logging
import json
import traceback
import sys
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv, find_dotenv

from backend.app.schemas import ChatRequest, ChatResponse

# 配置日志
logger = logging.getLogger(__name__)

# Setup console logging - ensure messages appear in the console too
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# Debug function to log directly to console - guaranteed visible
def console_log(message):
    """Log directly to console with visible markers"""
    print(f"\n{'='*50}")
    print(f"AI MODULE: {message}")
    print(f"{'='*50}\n")
    # Also log through regular logger
    logger.info(message)
    
console_log("AI Module initialized - Console logging enabled")

# Print current working directory to help debug path issues
cwd = os.getcwd()
logger.info(f"Current working directory: {cwd}")

# Debug function to print all environment variables
def print_env_variables():
    """Print all environment variables (with sensitive values masked)"""
    logger.info("=== Environment Variables ===")
    for key, value in os.environ.items():
        # Skip outputting some standard environment variables to reduce clutter
        if key.startswith("PATH") or key.startswith("PYTHON") or key in ["USERNAME", "USER", "HOME"]:
            continue
            
        # Mask API keys and tokens
        if "KEY" in key or "TOKEN" in key or "SECRET" in key:
            if value and len(value) > 8:
                masked_value = f"{value[:5]}...{value[-4:]}"
            else:
                masked_value = "[SET]" if value else "[NOT SET]"
            logger.info(f"{key}={masked_value}")
        else:
            logger.info(f"{key}={value}")
    logger.info("===========================")

# Call the debug function
print_env_variables()

# 获取项目根目录 - Multiple approaches to find .env
paths_to_try = [
    Path(__file__).resolve().parent.parent.parent.parent / ".env",  # Standard path
    Path(cwd) / ".env",  # Current working directory
    Path(cwd).parent / ".env",  # Parent of current working directory
]

env_loaded = False
# Try each path
for env_path in paths_to_try:
    logger.info(f"Trying to load .env from: {env_path}")
    if env_path.exists():
        logger.info(f"Found .env file at {env_path}")
        load_dotenv(dotenv_path=env_path)
        env_loaded = True
        break

# If no path worked, try find_dotenv as a last resort
if not env_loaded:
    logger.warning(f"No .env file found in standard locations. Trying find_dotenv()...")
    dotenv_path = find_dotenv()
    if dotenv_path:
        logger.info(f"Found .env at {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
        env_loaded = True
    else:
        logger.error("No .env file found anywhere! API calls will likely fail.")

# 获取环境变量
# OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "testkey") # Removed default
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
# Ensure we have a default value for the URL
OPENROUTER_API_URL = os.environ.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
# Alternative API URLs to try if the main one fails
ALTERNATE_API_URLS = [
    "https://openrouter.ai/api/v1/chat/completions",  # Standard URL
    "https://api.openrouter.ai/api/v1/chat/completions",  # Alternative with api subdomain
]
MODEL_NAME = os.environ.get("MODEL_NAME") # Also get model name here

# CRITICAL - Last resort fallback if .env not loading properly
if not OPENROUTER_API_KEY:
    logger.warning("HARDCODED FALLBACK: OpenRouter API key not found in environment variables")
    # 使用硬编码的API密钥（仅用于测试）
    hardcoded_key = "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"
    logger.warning(f"Using HARDCODED OpenRouter API key: {hardcoded_key[:8]}... (FOR TESTING ONLY)")
    OPENROUTER_API_KEY = hardcoded_key

if not MODEL_NAME:
    logger.warning("HARDCODED FALLBACK: MODEL_NAME not found in environment variables")
    hardcoded_model = "anthropic/claude-3-haiku" # Guaranteed to work with OpenRouter
    logger.warning(f"Using HARDCODED model: {hardcoded_model} (FOR TESTING ONLY)")
    MODEL_NAME = hardcoded_model

# Check if essential variables are loaded
# 硬编码的fallback已经确保API密钥不为空，所以这里只需记录警告
if not OPENROUTER_API_KEY:
    logger.warning("API key is still missing after fallback attempts!")
    logger.warning("Attempted loading from: " + ", ".join(str(p) for p in paths_to_try))
else:
    # Check OpenRouter API key format (should start with sk-or-)
    if not OPENROUTER_API_KEY.startswith('sk-or-'):
        logger.warning(f"API key may have incorrect format. OpenRouter API keys typically start with 'sk-or-'")
        logger.warning(f"Current key format: {OPENROUTER_API_KEY[:5]}...")
        
# 硬编码的fallback已经确保OPENROUTER_API_URL不为空，此处可省略
# if not OPENROUTER_API_URL:
#      logger.error("CRITICAL: OPENROUTER_API_URL not found.")
     
# 硬编码的fallback已经确保MODEL_NAME不为空，所以这里只需记录模型信息
if MODEL_NAME:
     # Log model name information
     logger.info(f"Using model: '{MODEL_NAME}'")
     
     # Common OpenRouter models include:
     # - anthropic/claude-3-opus
     # - anthropic/claude-3-sonnet
     # - anthropic/claude-3-haiku  
     # - meta-llama/llama-3-70b-instruct
     # - google/gemini-pro
     # - mistralai/mistral-7b-instruct
     
     # Check for Qwen model format (but don't change unless needed)
     if "qwen" in MODEL_NAME.lower():
         logger.info("Using Qwen model")

# 打印API密钥前5个字符，用于调试
# if OPENROUTER_API_KEY != "testkey": # Condition no longer needed
if OPENROUTER_API_KEY:
    logger.info(f"Using API key: {OPENROUTER_API_KEY[:5]}...")
    # Confirm the format has proper Bearer prefix
    auth_header = f"Bearer {OPENROUTER_API_KEY}"
    logger.info(f"Authorization header will be: Bearer sk-****...")
# else: # Removed else block
#     logger.warning("Using default API key (testkey)")

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message using OpenRouter API"""
    # 在函数开头声明global
    global OPENROUTER_API_URL
    
    # Generate a session ID if not provided
    session_id = request.session_id or uuid.uuid4()
    
    # Check if API key is available (and not empty string)
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.strip() == "":
        logger.error("Missing or empty OpenRouter API key")
        raise HTTPException(
            status_code=500,
            detail="API key not configured or empty - check server logs"
        )
    
    # Check if model name is available
    if not MODEL_NAME or MODEL_NAME.strip() == "":
        logger.error("Missing or empty MODEL_NAME environment variable")
        raise HTTPException(
            status_code=500,
            detail="MODEL_NAME not configured or empty - check server logs"
        )
    
    # Apply Qwen-specific checks based on model
    current_model = MODEL_NAME.strip()
    if "qwen" in current_model.lower():
        logger.info(f"Qwen model detected: {current_model}")
        # Check if Qwen model is available on OpenRouter
        if "qwen2.5" in current_model.lower():
            # While we'll try to use it, log a note for troubleshooting
            logger.info("Using Qwen 2.5 model - make sure this model is available via OpenRouter")
    
    # Prepare the context for the AI model
    messages = []
    
    # Add context from previous messages if available
    if request.context:
        for msg in request.context:
            messages.append(msg)
    
    # Add the current message
    messages.append({"role": "user", "content": request.message})
    
    try:
        # Log the API key being used (partially masked)
        masked_key = f"{OPENROUTER_API_KEY[:8]}...{OPENROUTER_API_KEY[-4:]}" if len(OPENROUTER_API_KEY) > 12 else OPENROUTER_API_KEY
        logger.info(f"Attempting OpenRouter request with API Key: {masked_key}")
        logger.info(f"Using model: '{MODEL_NAME}'")
        
        # Call the OpenRouter API
        async with httpx.AsyncClient() as client:
            # OpenRouter requires specific format for models and headers
            # Reference: https://openrouter.ai/docs
            
            # Check if the model is likely a Qwen model
            fallback_model = None
            try_model = MODEL_NAME
            
            # Always define a fallback model for reliability
            fallback_model = "anthropic/claude-3-haiku"
            logger.info(f"Primary model: {try_model}, Fallback model: {fallback_model}")
            
            # Ensure API key is properly formatted
            # OpenRouter keys start with sk-or-
            if not OPENROUTER_API_KEY.startswith("sk-or-"):
                logger.warning(f"API key doesn't start with 'sk-or-', this might cause authentication issues")
                # Try fixing the key if it looks wrong
                if OPENROUTER_API_KEY.startswith("sk-"):
                    logger.warning("API key starts with 'sk-' but not 'sk-or-', this might be an OpenAI key instead of OpenRouter")
            
            # Try using a basic, proven model to test the API connection
            test_connection = True  # Set to True to always try a test first
            
            # Simplest possible payload - bare minimum required fields
            payload = {
                "model": try_model,
                "messages": messages,
                # 限制token数量，避免积分不足问题
                "max_tokens": 500  # 限制回复长度，减少token消耗
            }
            
            # Absolute minimal headers required by OpenRouter
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # First try a test connection with a guaranteed working model if needed
            if test_connection:
                try:
                    # Ensure we have a URL to test
                    test_url = OPENROUTER_API_URL or ALTERNATE_API_URLS[0]
                    console_log(f"TESTING API CONNECTION to {test_url}")
                    console_log(f"Using API Key: {OPENROUTER_API_KEY[:8]}...")
                    
                    test_payload = {
                        "model": "anthropic/claude-3-haiku",
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10  # 严格限制token数，这只是个测试
                    }
                    
                    # Log complete request details
                    console_log(f"TEST REQUEST: {json.dumps(test_payload)}")
                    console_log(f"TEST HEADERS: Authorization: Bearer {OPENROUTER_API_KEY[:8]}..., Content-Type: application/json")
                    
                    # Make the request with more detailed error handling
                    try:
                        test_response = await client.post(
                            test_url,
                            headers=headers,
                            json=test_payload,
                            timeout=10.0
                        )
                        
                        # Log complete response
                        console_log(f"TEST RESPONSE STATUS: {test_response.status_code}")
                        console_log(f"TEST RESPONSE HEADERS: {dict(test_response.headers)}")
                        console_log(f"TEST RESPONSE BODY: {test_response.text[:1000]}")
                        
                        if test_response.status_code == 200:
                            console_log("✅ TEST CONNECTION SUCCESSFUL!")
                            try:
                                resp_data = test_response.json()
                                console_log(f"TEST RESPONSE PARSED JSON: {json.dumps(resp_data)[:500]}...")
                            except Exception as e:
                                console_log(f"Could not parse test response as JSON: {str(e)}")
                        else:
                            console_log(f"❌ TEST CONNECTION FAILED: HTTP {test_response.status_code}")
                            console_log(f"RESPONSE TEXT: {test_response.text}")
                            
                            # Try to check specific error reasons
                            if test_response.status_code == 401:
                                console_log("AUTHENTICATION ERROR: Invalid API key or unauthorized")
                            elif test_response.status_code == 400:
                                console_log("BAD REQUEST: Check model name or request format")
                            elif test_response.status_code == 404:
                                console_log("NOT FOUND: Check API URL or model name")
                            elif test_response.status_code == 422:
                                console_log("VALIDATION ERROR: Check request parameters")
                    
                    except httpx.ConnectError as e:
                        console_log(f"CONNECTION ERROR: Could not connect to {test_url}")
                        console_log(f"Error details: {str(e)}")
                        console_log("Check internet connection and API URL")
                        
                    except httpx.TimeoutException as e:
                        console_log(f"TIMEOUT ERROR: Connection to {test_url} timed out")
                        console_log(f"Error details: {str(e)}")
                        
                    except Exception as e:
                        console_log(f"UNEXPECTED ERROR during request: {type(e).__name__}: {str(e)}")
                        traceback.print_exc()
                
                except Exception as e:
                    console_log(f"CRITICAL ERROR in test connection: {type(e).__name__}: {str(e)}")
                    traceback.print_exc()
            
            # If the test connection isn't successful, try all alternate URLs for the actual request
            all_urls_to_try = []
            if OPENROUTER_API_URL:
                all_urls_to_try.append(OPENROUTER_API_URL)
            # 添加所有不在列表中且不为None的备用URL    
            all_urls_to_try.extend([url for url in ALTERNATE_API_URLS if url and url not in all_urls_to_try])
            
            # 确保我们至少有一个URL可以尝试
            if not all_urls_to_try:
                all_urls_to_try = ["https://openrouter.ai/api/v1/chat/completions"]
                console_log("No valid URLs found, using default URL")
                
            # Try each URL in turn
            for i, current_url in enumerate(all_urls_to_try):
                console_log(f"Attempt {i+1}/{len(all_urls_to_try)}: Trying URL {current_url}")
                
                try:
                    # First attempt with the requested model
                    response = await client.post(
                        current_url,
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    # Log response status
                    console_log(f"Response status: {response.status_code} from {current_url}")
                    
                    # If successful, use this URL and stop trying others
                    if response.status_code == 200:
                        console_log(f"Successful response from {current_url}")
                        if current_url != OPENROUTER_API_URL:
                            console_log(f"Updating primary API URL to {current_url}")
                            OPENROUTER_API_URL = current_url
                        break
                    
                    # Check if model not found and try fallback if available
                    if response.status_code in [404, 400] and fallback_model and try_model != fallback_model:
                        error_text = response.text
                        console_log(f"Primary model error ({response.status_code}): {error_text}")
                        console_log(f"Trying fallback model: {fallback_model} on {current_url}")
                        
                        # Update payload with fallback model
                        payload["model"] = fallback_model
                        
                        # Make second attempt with fallback model
                        response = await client.post(
                            current_url,
                            headers=headers,
                            json=payload,
                            timeout=30.0
                        )
                        console_log(f"Fallback response status: {response.status_code}")
                        
                        # If successful with fallback model, stop trying other URLs
                        if response.status_code == 200:
                            console_log(f"Successful response with fallback model from {current_url}")
                            break
                
                except Exception as e:
                    console_log(f"Error with URL {current_url}: {type(e).__name__}: {str(e)}")
                    # Continue trying other URLs
            
            # For debugging, log the final response content
            if 'response' in locals():
                console_log(f"Final response content: {response.text[:500]}")
                
                # Process the response if we have one
                try:
                    # Check for successful response status
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            console_log(f"Response JSON: {json.dumps(data)[:500]}")
                            
                            # 检查是否返回了错误响应
                            if "error" in data:
                                error_code = data.get("error", {}).get("code")
                                error_msg = data.get("error", {}).get("message", "未知错误")
                                console_log(f"API返回错误: code={error_code}, message={error_msg}")
                                
                                # 特殊处理402积分不足错误
                                if error_code == 402:
                                    return {
                                        "message": f"AI服务暂时无法使用：积分不足。{error_msg}",
                                        "session_id": session_id
                                    }
                                
                                # 处理其他错误
                                return {
                                    "message": f"AI服务返回错误: {error_msg}",
                                    "session_id": session_id
                                }
                            
                            # 验证预期的响应格式
                            if "choices" not in data:
                                console_log(f"API response missing 'choices': {data}")
                                raise ValueError(f"Invalid API response missing 'choices': {data}")
                            
                            if not data["choices"] or not isinstance(data["choices"], list):
                                console_log(f"API response has empty choices: {data}")
                                raise ValueError(f"Invalid API response with empty choices: {data}")
                            
                            if "message" not in data["choices"][0]:
                                console_log(f"API response missing message in first choice: {data['choices'][0]}")
                                raise ValueError("Invalid API response format: missing message in first choice")
                            
                            if "content" not in data["choices"][0]["message"]:
                                console_log(f"API response missing content in message: {data['choices'][0]['message']}")
                                raise ValueError("Invalid API response format: missing content in message")
                            
                            # Extract the AI's response
                            ai_message = data["choices"][0]["message"]["content"]
                            console_log(f"Got AI response: {ai_message[:100]}...")
                            
                            return {"message": ai_message, "session_id": session_id}
                        except json.JSONDecodeError as e:
                            console_log(f"Failed to parse JSON response: {str(e)}")
                    else:
                        console_log(f"Final response status code was not 200: {response.status_code}")
                        
                        # 检查是否为积分不足错误
                        try:
                            error_data = response.json()
                            if "error" in error_data and error_data.get("error", {}).get("code") == 402:
                                error_msg = error_data.get("error", {}).get("message", "")
                                console_log(f"CREDITS ERROR: {error_msg}")
                                # 返回自定义错误信息
                                return {
                                    "message": f"AI服务暂时无法使用：积分不足。{error_msg}",
                                    "session_id": session_id
                                }
                        except Exception as e:
                            console_log(f"Failed to parse error response: {str(e)}")
                except Exception as e:
                    console_log(f"Error processing final response: {type(e).__name__}: {str(e)}")
                    traceback.print_exc()
            
            # If we get here, we couldn't get a valid response from any URL or model
            console_log("All API attempts failed, using hardcoded response")
            hardcoded_resp = "我是AI助手，很高兴为您服务！您好！因为OpenRouter API连接暂时不可用，我目前使用的是后备响应模式。请稍后再试或联系管理员检查API配置。"
            return {"message": hardcoded_resp, "session_id": session_id}
    
    except Exception as e:
        logger.error(f"Outer exception handler caught: {str(e)}", exc_info=True)  # Add exc_info=True to get traceback
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# Add a direct test endpoint for debugging
@router.get("/test-connection", status_code=200)
async def test_api_connection():
    """Test the connection to the OpenRouter API"""
    # 在函数开头声明global
    global OPENROUTER_API_URL
    
    console_log("Direct API test requested")
    results = {}
    
    # Check environment variables
    results["env_variables"] = {
        "OPENROUTER_API_KEY": f"{OPENROUTER_API_KEY[:8]}..." if OPENROUTER_API_KEY else "Not set",
        "OPENROUTER_API_URL": OPENROUTER_API_URL,
        "MODEL_NAME": MODEL_NAME
    }
    
    # Test each API URL
    results["api_tests"] = []
    
    # 确保我们至少有一个有效的URL来测试
    urls_to_test = [url for url in ALTERNATE_API_URLS if url]
    if not urls_to_test:
        urls_to_test = ["https://openrouter.ai/api/v1/chat/completions"]
        console_log("No alternate URLs found, using default URL for testing")
    
    for api_url in urls_to_test:
        test_result = {
            "url": api_url,
            "status": "Not tested",
            "details": {}
        }
        
        try:
            console_log(f"Testing connection to {api_url}")
            
            test_payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10  # 严格限制token数，这只是个测试
            }
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=test_payload,
                    timeout=10.0
                )
                
                test_result["status"] = f"{response.status_code}"
                test_result["details"]["status_code"] = response.status_code
                test_result["details"]["headers"] = dict(response.headers)
                test_result["details"]["body"] = response.text[:200] + "..."
                
                if response.status_code == 200:
                    console_log(f"✅ Connection to {api_url} successful!")
                    # If we find a working URL, update the global URL
                    if OPENROUTER_API_URL != api_url:
                        console_log(f"Updating primary API URL to {api_url}")
                        OPENROUTER_API_URL = api_url
                else:
                    console_log(f"❌ Connection to {api_url} failed: {response.status_code}")
        
        except Exception as e:
            console_log(f"Error testing {api_url}: {str(e)}")
            test_result["status"] = "Error"
            test_result["details"]["error"] = str(e)
            test_result["details"]["error_type"] = type(e).__name__
        
        results["api_tests"].append(test_result)
    
    return results