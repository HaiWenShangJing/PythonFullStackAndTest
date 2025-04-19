"""
封装与后端API通信的功能
"""
import os
import asyncio
import httpx
import streamlit as st
import json
import html
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend.api")

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


def sanitize_response(content):
    """
    清理API响应内容，防止XSS攻击等
    
    Args:
        content: 原始响应内容
    
    Returns:
        清理后的内容
    """
    # 如果内容为空，返回空字符串
    if not content:
        return ""
    
    # 确保内容是字符串
    if not isinstance(content, str):
        try:
            content = str(content)
        except Exception as e:
            logger.error(f"无法将响应转为字符串: {e}")
            return "[响应格式错误]"
            
    return content


async def send_chat_message(message: str, session_id: str, context: list, model: str = None) -> dict:
    """
    发送普通聊天消息到API
    
    Args:
        message: 用户消息内容
        session_id: 会话ID
        context: 对话上下文
        model: 可选的模型名称
        
    Returns:
        API响应的JSON对象
    """
    async with httpx.AsyncClient() as client:
        try:
            request_data = {
                "message": message,
                "session_id": session_id,
                "context": context
            }
            
            # 添加模型参数如果指定
            if model:
                request_data["model"] = model
            
            logger.info(f"发送请求到 {API_BASE_URL}/chat")
            
            response = await client.post(
                f"{API_BASE_URL}/chat",
                json=request_data,
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                # 清理响应内容
                if "message" in result:
                    result["message"] = sanitize_response(result["message"])
                return result
            else:
                error_text = await response.text()
                logger.error(f"API错误: {response.status_code} - {error_text}")
                return {
                    "message": f"API错误: {response.status_code} - {error_text}",
                    "session_id": session_id
                }
        
        except Exception as e:
            error_message = f"与AI服务通信时发生错误: {str(e)}"
            logger.error(error_message)
            return {
                "message": error_message,
                "session_id": session_id
            }


async def stream_chat_message(message: str, session_id: str, context: list, model: str = None, 
                              on_chunk=None) -> str:
    """
    流式发送聊天消息到API
    
    Args:
        message: 用户消息内容
        session_id: 会话ID
        context: 对话上下文
        model: 可选的模型名称
        on_chunk: 接收每个响应块的回调函数
        
    Returns:
        完整响应文本
    """
    streaming_content = ""
    
    try:
        async with httpx.AsyncClient() as client:
            request_data = {
                "message": message,
                "session_id": session_id,
                "context": context
            }
            
            # 添加模型参数如果指定
            if model:
                request_data["model"] = model
                
            logger.info(f"发送流式请求到 {API_BASE_URL}/chat/stream")
                
            async with client.stream("POST", f"{API_BASE_URL}/chat/stream", 
                                    json=request_data, timeout=60.0) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_text():
                        # 清理每个响应块
                        clean_chunk = sanitize_response(chunk)
                        streaming_content += clean_chunk
                        
                        # 如果提供了回调函数，执行它
                        if on_chunk:
                            on_chunk(streaming_content)
                else:
                    error_text = await response.text()
                    error_message = f"API错误: {response.status_code} - {error_text}"
                    logger.error(error_message)
                    if on_chunk:
                        on_chunk(error_message)
                    return error_message
    
    except Exception as e:
        error_message = f"与AI服务通信时发生错误: {str(e)}"
        logger.error(error_message)
        if on_chunk:
            on_chunk(error_message)
        return error_message
    
    return streaming_content


async def check_api_connection() -> bool:
    """检查API连接状态"""
    try:
        async with httpx.AsyncClient() as client:
            # 使用API_BASE_URL的基础路径部分 + "/"
            base_url = API_BASE_URL.rstrip("/api/v1")
            if not base_url:
                base_url = "http://localhost:8000"
            
            logger.info(f"检查API连接: {API_BASE_URL}/")
            
            # 首先尝试API根路径
            response = await client.get(f"{API_BASE_URL}/", timeout=2.0)
            if response.status_code == 200:
                return True
                
            # 如果失败，尝试服务器根路径
            logger.info(f"尝试备用路径: {base_url}/")
            response = await client.get(f"{base_url}/", timeout=2.0)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"API连接错误: {str(e)}")
        return False


def run_async(func, *args, **kwargs):
    """
    运行异步函数的工具方法
    """
    try:
        return asyncio.run(func(*args, **kwargs))
    except RuntimeError:
        # 处理asyncio运行时错误
        logger.warning("asyncio RuntimeError，创建新的事件循环")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs)) 