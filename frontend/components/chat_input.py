"""
聊天输入组件
"""
import streamlit as st


def fixed_bottom_input_container():
    """
    创建固定在底部的输入容器并包含输入元素
    
    Returns:
        用户输入的文本和发送按钮的状态
    """
    # Initialize state if needed
    if "user_message" not in st.session_state:
        st.session_state.user_message = ""
    if "should_send" not in st.session_state:
        st.session_state.should_send = False
    if "should_clear_input" not in st.session_state:
        st.session_state.should_clear_input = False

    # Auto-focus script remains the same
    st.markdown(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Short delay to ensure element exists
            setTimeout(function() {
                const textareas = document.querySelectorAll('textarea[data-testid="stChatInputTextArea"]');
                if (textareas.length > 0) {
                     // Check if it's already focused
                     if (document.activeElement !== textareas[0]) {
                          textareas[0].focus();
                     }
                }
            }, 300);
        });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    user_input_value = st.session_state.get("user_message", "")
    send_pressed = False
    auto_send = False

    # --- Use st.chat_input for a standard, fixed input --- 
    prompt = st.chat_input("有什么我可以帮你的？", key="chat_input_main")
    
    # Check if the user submitted input via chat_input
    if prompt:
        user_input_value = prompt
        # Set flag for processing in ai_chat.py
        st.session_state.should_process_input = True 
        # Clear internal state of chat_input by triggering rerun
        # We need to store the prompt before rerun
        st.session_state.user_message_to_send = prompt
        st.rerun()
        
    # --- Old custom input logic (commented out, using st.chat_input instead) --- 
    # st.markdown('<div class="input-container">', unsafe_allow_html=True)
    # with st.container():
    #      st.markdown('<div style="max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True)
    #      cols = st.columns([8, 1])
    #      with cols[0]:
    #          def on_input_change(): ... # Callback logic
    #          current_value = st.session_state.get("user_message", "")
    #          if st.session_state.should_clear_input: ... # Clearing logic
    #          user_input_value = st.text_area(...)
    #      with cols[1]:
    #          send_pressed = st.button("发送", ...)
    #      st.markdown('</div>', unsafe_allow_html=True)
    # st.markdown('</div>', unsafe_allow_html=True)
    # # REMOVED: st.markdown("<div style='height: 100px;'></div>", ...)
    # if st.session_state.should_send: ... # Auto send logic

    # Determine if sending is needed based on the flag set by chat_input
    send_action = st.session_state.get("should_process_input", False)
    final_input = st.session_state.get("user_message_to_send", "")

    # Reset flags after checking
    if send_action:
        st.session_state.should_process_input = False
        st.session_state.user_message_to_send = "" 
        # The input value for processing is 'final_input'
        # The return value indicates an action was triggered
        return final_input, True 
    else:
        # Return current (potentially unused) input value and False for action
        return "", False


# 移除旧的 chat_input_area 函数 (如果存在)
# def chat_input_area():
#    ... 