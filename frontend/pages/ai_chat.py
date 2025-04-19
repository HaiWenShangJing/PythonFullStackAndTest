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

    # --- Input Handling --- 
    # Use Streamlit's built-in chat input
    prompt = st.chat_input("有什么我可以帮你的？", key="chat_input_main")

    if prompt:
        # 1. Add user message immediately to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # 2. Store the prompt to be processed in the next rerun
        st.session_state.prompt_to_process = prompt
        # 3. Trigger the next rerun. This will display the user message 
        #    and then process the prompt in the logic below.
        st.rerun()

    # --- Display History --- 
    # This runs *after* the input handling logic in each rerun.
    # In the rerun triggered by st.rerun() above, it will show the user message.
    render_chat_history(st.session_state.chat_history)
    
    # --- AI Response Placeholder --- 
    # Define placeholder for potential streaming output
    # It's placed *after* history rendering
    streaming_placeholder = st.empty()

    # --- Process Pending Input & Call API --- 
    # Check if there's a prompt stored from the previous rerun
    if prompt_to_process := st.session_state.get("prompt_to_process"):
        # Clear the flag/stored prompt now that we are processing it
        st.session_state.prompt_to_process = None 
        
        current_input = prompt_to_process # Use the stored prompt

        # Prepare for AI response
        context = format_chat_context()
        # Add empty AI message placeholder in history *before* calling API
        st.session_state.chat_history.append({"role": "assistant", "content": ""})
        message_index = len(st.session_state.chat_history) - 1 
        
        # Set streaming flag (optional, but can be useful)
        st.session_state.streaming = True

        # Callback function to update the *separate* placeholder
        def update_placeholder(content):
            try:
                # Update the placeholder element's display
                streaming_placeholder.markdown(content + "▌")
                # Update the actual content in history silently
                # Check index validity before updating state
                if message_index < len(st.session_state.chat_history):
                    st.session_state.chat_history[message_index]["content"] = content
                else:
                    print(f"Error in callback: message_index {message_index} out of bounds.")
            except Exception as e:
                 # Log potential errors during placeholder update
                 print(f"Error updating placeholder: {e}")

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
        st.session_state.streaming = False # Unset flag
        
        # Update the final message in history and clear the placeholder
        if message_index < len(st.session_state.chat_history):
            if full_response:
                st.session_state.chat_history[message_index]["content"] = full_response
            else:
                 # Handle potential errors if run_async returned None or empty
                 error_content = "抱歉，AI回复时出现错误或无内容返回。"
                 st.session_state.chat_history[message_index]["content"] = error_content
                 print(f"API call for '{current_input}' returned empty/None response.") # Log details
        else:
             # Log error if index is still invalid after streaming
             print(f"Error after stream: message_index {message_index} out of bounds.")

        streaming_placeholder.empty() # Clear the external placeholder

        # Rerun one last time to display the final AI message rendered by render_chat_history
        st.rerun()


# Run page if executed directly
if __name__ == "__main__":
    ai_chat_page()