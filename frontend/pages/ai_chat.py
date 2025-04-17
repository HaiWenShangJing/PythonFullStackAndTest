import asyncio
import uuid
from typing import Dict, List, Optional

import streamlit as st

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
                for msg in st.session_state.chat_history
                if msg["role"] in ["user", "assistant"]
            ]
            
            # Send message to API
            with st.spinner("AI思考中..."):
                response = asyncio.run(
                    send_message_to_ai(user_input)
                )
                
                if response:
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )
                    
                    # Update session ID
                    st.session_state.session_id = str(response["session_id"])
                    
                    # Force a rerun to display the new message
                    st.rerun()


# Run the page
if __name__ == "__main__":
    ai_chat_page()