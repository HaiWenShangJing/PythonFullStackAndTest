"""
AI聊天助手页面
"""
import os
import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime

# 添加必要的路径以确保导入正常工作
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
frontend_dir = pages_dir.parent
project_root = frontend_dir.parent

# 将项目根目录添加到Python路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

# 导入工具模块
from frontend.utils.styles import get_chat_css
from frontend.utils.session import (
    initialize_session_state, 
    initialize_chat_history,
    format_chat_context,
    clear_chat_history
)
from frontend.utils.api import run_async, stream_chat_message

# 导入组件
from frontend.components.chat_message import render_chat_history
from frontend.components.model_selector import model_selector
from frontend.components.chat_input import fixed_bottom_input_container


def ai_chat_page():
    """AI聊天助手页面 (using st.chat_input and st.chat_message)"""
    # Page config should ideally be in the main app file (streamlit_app.py)
    # But we keep it here for now if this page can be run standalone
    st.set_page_config(
        page_title="AI 助手",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom CSS
    st.markdown(get_chat_css(), unsafe_allow_html=True)
    
    # Initialize session state (chat history, session_id, etc.)
    initialize_session_state()
    initialize_chat_history() # Ensures st.session_state.chat_history exists
    
    # --- Sidebar --- 
    with st.sidebar:
        st.title("模型选择")
        selected_model = model_selector()
        if st.button("清空聊天记录", key="clear_chat_sidebar"):
            clear_chat_history()
            st.rerun()

    # --- Main Chat Area --- 
    st.markdown("## AI 助手") # Title for the main area

    # Display existing chat messages using the updated renderer
    # This now uses st.chat_message internally
    render_chat_history(st.session_state.chat_history)
    
    # Placeholder for streaming AI response
    # This needs to be defined *before* the input, but updated *after* the input is processed
    streaming_placeholder = st.empty()

    # --- Chat Input --- 
    # Use the function that wraps st.chat_input
    prompt, send_triggered = fixed_bottom_input_container() 

    # --- Process Input and Call API --- 
    if send_triggered and prompt: 
        current_input = prompt # Input from st.chat_input

        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": current_input})
        
        # Immediately display the user message by re-rendering history
        # (st.chat_input causes a rerun, so this should happen automatically)
        # We might still need a rerun if the user message doesn't show up instantly.
        # st.rerun() # Temporarily commented out, let st.chat_input handle rerun

        # Prepare for AI response
        context = format_chat_context()
        message_index = len(st.session_state.chat_history) # Index for the upcoming AI message
        st.session_state.chat_history.append({"role": "assistant", "content": ""}) # Add empty AI message

        # Set streaming flag
        st.session_state.streaming = True

        # Callback function to update the *separate* placeholder
        def update_placeholder(content):
            streaming_placeholder.markdown(content + "▌")
            # Update the actual content in history silently
            st.session_state.chat_history[message_index]["content"] = content

        # Call the streaming API
        full_response = run_async(
            stream_chat_message,
            current_input,
            st.session_state.session_id,
            context,
            selected_model if selected_model != "默认模型" else None,
            update_placeholder # Pass the callback
        )
        
        # Streaming finished
        st.session_state.streaming = False
        
        # Update the final message in history and clear the placeholder
        if full_response:
            st.session_state.chat_history[message_index]["content"] = full_response
            streaming_placeholder.empty() # Clear the external placeholder
        else:
             # Handle potential errors if needed, e.g., display error in chat
             error_content = "抱歉，AI回复时出现错误。"
             st.session_state.chat_history[message_index]["content"] = error_content
             streaming_placeholder.empty()

        # Rerun to display the final AI message rendered by render_chat_history
        st.rerun()


# Run page if executed directly
if __name__ == "__main__":
    ai_chat_page()