"""
聊天消息组件，用于显示用户和AI的消息
"""
import streamlit as st


def render_chat_history(messages: list):
    """
    Renders the chat history using st.chat_message.
    Handles the streaming placeholder logic internally.

    Args:
        messages: List of message dictionaries.
    """
    for i, msg in enumerate(messages):
        role = msg.get("role")
        content = msg.get("content", "")
        is_last = (i == len(messages) - 1)
        is_streaming = is_last and role == "assistant" and "streaming" in st.session_state and st.session_state.streaming

        # Use Streamlit's built-in chat elements
        with st.chat_message(name=role):
            if is_streaming:
                # Use empty placeholder which will be updated externally
                st.markdown("", key=f"stream_placeholder_{i}") 
            else:
                st.markdown(content) # Render final content

# --- Placeholder Function (for potential future use) ---
# This function is intended to update the placeholder within the chat message.
# It might be called from the streaming callback.
# Note: Directly updating elements inside st.chat_message from a callback can be tricky.
# The current ai_chat.py approach updates a separate st.empty placeholder, which is more reliable.
# Keeping this commented out for reference.
# def update_streaming_placeholder(index, content):
#     placeholder_key = f"stream_placeholder_{index}"
#     if placeholder_key in st.session_state:
#         st.markdown(content + "▌", key=placeholder_key)
#     else:
#         # Attempt to access the element directly (less reliable)
#         try:
#             placeholder = st.session_state[placeholder_key]
#             placeholder.markdown(content + "▌")
#         except KeyError:
#              print(f"Warning: Placeholder {placeholder_key} not found for streaming update.") 