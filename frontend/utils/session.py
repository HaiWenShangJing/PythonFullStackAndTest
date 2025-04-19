"""
管理Streamlit会话状态的功能
"""
import uuid
import streamlit as st


def initialize_session_state():
    """
    初始化会话状态变量
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'items' not in st.session_state:
        st.session_state.items = []


def get_welcome_message():
    """
    获取默认欢迎消息
    """
    return "👋 你好！我是AI助手，有什么可以帮助你的吗？"


def initialize_chat_history():
    """
    初始化聊天历史，如果为空则添加默认欢迎消息
    """
    if not st.session_state.chat_history:
        st.session_state.chat_history = [
            {"role": "assistant", "content": get_welcome_message()}
        ]


def format_chat_context(exclude_last=True):
    """
    将聊天历史格式化为API上下文
    
    Args:
        exclude_last: 是否排除最后一条消息（通常是刚添加的用户消息）
    
    Returns:
        格式化的上下文列表
    """
    history = st.session_state.chat_history[:-1] if exclude_last and st.session_state.chat_history else st.session_state.chat_history
    
    return [
        {"role": msg.get("role", "user" if msg.get("is_user", False) else "assistant"), 
         "content": msg["content"]}
        for msg in history
    ]


def clear_chat_history():
    """
    清空聊天历史并重新添加欢迎消息
    """
    st.session_state.chat_history = [
        {"role": "assistant", "content": get_welcome_message()}
    ]
    st.session_state.session_id = str(uuid.uuid4()) 