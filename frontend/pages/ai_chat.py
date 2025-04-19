import asyncio
import uuid
from typing import Dict, List, Optional

import streamlit as st
import httpx

from streamlit_app import (
    API_BASE_URL,
    create_item,
    delete_item,
    fetch_items,
    initialize_session_state,
    update_item,
    send_message_to_ai,
)


def ai_chat_page():
    """AI Chat Assistant Page"""
    st.title("AI 助手")
    
    # 添加自定义CSS来隐藏Streamlit的主进度条和状态消息
    hide_streamlit_elements = """
        <style>
        #MainMenu {visibility: hidden;}
        div[data-testid="stStatusWidget"] {display: none !important;}
        div.stSpinner > div {display:none !important;}
        /* 隐藏RUNNING...指示器 */
        .element-container:has(> div.stMarkdown > div > p:contains("RUNNING")) {display: none;}
        </style>
    """
    st.markdown(hide_streamlit_elements, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    if not hasattr(st.session_state, "items") or not isinstance(st.session_state.items, list):
        st.session_state.items = []
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    chat_input()


def display_chat_history():
    """Display the chat history"""
    # Create a container for the chat history
    chat_container = st.container()
    
    with chat_container:
        # Display a welcome message if no chat history
        if not st.session_state.chat_history:
            st.info("👋 你好！我是AI助手，有什么可以帮助你的吗？")
        
        # Display chat messages
        for message in st.session_state.chat_history:
            is_user = message.get("role") == "user"
            avatar = "👤" if is_user else "🤖"
            message_align = "right" if is_user else "left"
            
            # Create columns for better layout
            col1, col2 = st.columns([1, 9])
            
            with col1:
                st.text(avatar)
            
            with col2:
                st.markdown(
                    f"<div style='text-align: {message_align};'>"
                    f"<p style='background-color: {'#e6f7ff' if not is_user else '#f0f0f0'}; "
                    f"padding: 10px; border-radius: 10px; display: inline-block; "
                    f"max-width: 80%;'>"
                    f"{message['content']}</p></div>",
                    unsafe_allow_html=True
                )


def chat_input():
    """Chat input form"""
    # Create a form for the chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "输入你的问题:",
            key="user_message",
            height=100,
        )
        
        submit_button = st.form_submit_button("发送")
        
        if submit_button and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Prepare context for the API
            context = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history[:-1]  # 排除刚刚添加的消息
                if msg.get("role") in ["user", "assistant"]
            ]
            
            # 添加一个空占位符用于流式显示AI回应
            ai_response_placeholder = st.empty()
            
            # 累积的响应内容
            streaming_content = ""
            
            # 流式发送消息到API
            async def stream_response():
                nonlocal streaming_content
                try:
                    async with httpx.AsyncClient() as client:
                        request_data = {
                            "message": user_input,
                            "session_id": st.session_state.session_id,
                            "context": context
                        }
                        
                        # 创建流式请求
                        async with client.stream("POST", f"{API_BASE_URL}/chat/stream", json=request_data, timeout=60.0) as response:
                            if response.status_code == 200:
                                # 流式处理响应
                                async for chunk in response.aiter_text():
                                    # 更新累积内容
                                    streaming_content += chunk
                                    
                                    # 更新显示占位符
                                    ai_response_placeholder.markdown(
                                        f"<div style='text-align: left;'>"
                                        f"<p style='background-color: #e6f7ff; "
                                        f"padding: 10px; border-radius: 10px; display: inline-block; "
                                        f"max-width: 80%;'>"
                                        f"{streaming_content}</p></div>",
                                        unsafe_allow_html=True
                                    )
                            else:
                                # 处理错误响应
                                error_text = await response.text()
                                error_message = f"Error: {response.status_code} - {error_text}"
                                ai_response_placeholder.error(f"API错误: {error_message}")
                                streaming_content = f"抱歉，我遇到了一个技术问题，无法回应。请稍后再试。"
                    
                    # 流式响应完成后，将最终内容添加到聊天历史
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": streaming_content}
                    )
                    
                except Exception as e:
                    error_message = f"发生错误: {str(e)}"
                    ai_response_placeholder.error(error_message)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": f"抱歉，发生了错误: {str(e)}"}
                    )
            
            # 执行异步流式响应
            try:
                asyncio.run(stream_response())
            except RuntimeError:
                # 处理asyncio运行时错误
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(stream_response())
                
            # 更新会话状态
            st.rerun()


# Run the page
if __name__ == "__main__":
    ai_chat_page()