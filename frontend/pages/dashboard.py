import streamlit as st
import asyncio
from streamlit_app import (
    API_BASE_URL,
    fetch_items,
    initialize_session_state,
)

def dashboard_page():
    """Dashboard page with overview of app data"""
    # Initialize session state
    initialize_session_state()
    
    st.title("仪表盘")
    st.write("欢迎使用全栈AI CRUD应用")
    
    # 处理items以确保它是列表
    temp_items = st.session_state.get("items")
    if callable(temp_items) or not isinstance(temp_items, list):
        temp_items = []
        st.session_state["items"] = temp_items
    
    # 如果需要获取items
    if not temp_items:
        with st.spinner("加载数据中..."):
            try:
                items, total = asyncio.run(fetch_items())
                temp_items = items if isinstance(items, list) else []
                st.session_state["items"] = temp_items
            except Exception as e:
                st.error(f"获取数据出错: {str(e)}")
                temp_items = []
    
    # 指标行
    col1, col2, col3 = st.columns(3)
    
    # 计算指标
    total_items = len(temp_items)
    try:
        total_chats = len([msg for msg in st.session_state.chat_history if msg.get("is_user")])
    except:
        total_chats = 0
    
    with col1:
        st.metric(label="数据项总数", value=total_items)
    
    with col2:
        st.metric(label="AI聊天互动次数", value=total_chats)
    
    with col3:
        st.metric(label="会话状态", value="活跃" if st.session_state.session_id else "无")
    
    # 最近数据项
    st.subheader("最近数据项")
    if not temp_items:
        st.info("没有找到数据项。请前往数据管理页面创建!")
    else:
        for item in temp_items[:5]:
            with st.expander(f"{item['name']}"):
                st.write(f"**描述:** {item['description'] or '无描述'}")
                st.write(f"**创建时间:** {item['created_at']}")
    
    # 最近AI对话
    st.subheader("最近AI对话")
    if not st.session_state.chat_history:
        st.info("没有聊天记录。请前往AI助手页面开始对话!")
    else:
        for msg in st.session_state.chat_history[-4:]:
            if msg.get("is_user"):
                st.write(f"🧑 **您:** {msg.get('content', '')}")
            else:
                st.write(f"🤖 **AI:** {msg.get('content', '')}")

# 运行页面
if __name__ == "__main__":
    dashboard_page()