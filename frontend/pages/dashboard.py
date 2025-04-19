"""
仪表盘页面
"""
import os
import sys
from pathlib import Path

# 添加必要的路径以确保导入正常工作
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
frontend_dir = pages_dir.parent
project_root = frontend_dir.parent

# 将项目根目录添加到Python路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import asyncio
from frontend.utils.session import initialize_session_state

def display_dashboard():
    """显示仪表盘页面"""
    st.title("仪表盘")
    st.write("欢迎使用全栈AI CRUD应用!")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 确保items是一个有效的列表
    try:
        # 通过字典表示法而不是属性表示法访问
        local_items = st.session_state["items"]
        # 检查它是否可调用（一个方法）
        if callable(local_items):
            local_items = []
        # 确保它是一个列表
        if not isinstance(local_items, list):
            local_items = []
    except:
        local_items = []
    
    # 将修正的值存回去
    st.session_state["items"] = local_items
    
    # 指标行
    col1, col2, col3 = st.columns(3)
    
    total_items = len(local_items)  # 使用局部变量
    
    # 统计聊天消息数量
    try:
        total_chats = len([msg for msg in st.session_state.chat_history if isinstance(msg, dict) and (msg.get("is_user", False) or msg.get("role") == "user")])
    except:
        total_chats = 0
    
    with col1:
        st.metric(label="项目总数", value=total_items)
    
    with col2:
        st.metric(label="AI聊天互动", value=total_chats)
    
    with col3:
        st.metric(label="活跃会话", value="是" if st.session_state.session_id else "否")
    
    # 使用局部变量显示最近的项目
    st.subheader("最近项目")
    if not local_items:
        st.info("没有找到项目。前往数据管理页面创建一些!")
    else:
        for item in local_items[:5]:
            with st.expander(f"{item['name']}"):
                st.write(f"**描述:** {item['description'] or '无描述'}")
                st.write(f"**创建时间:** {item['created_at']}")
    
    # 最近的AI对话
    st.subheader("最近AI对话")
    if not st.session_state.chat_history:
        st.info("没有聊天记录。前往AI助手页面开始对话!")
    else:
        for msg in st.session_state.chat_history[-4:]:
            # 添加安全检查，确保是字典
            if isinstance(msg, dict):
                is_user = msg.get("is_user", False) or msg.get("role") == "user"
                if is_user:
                    st.write(f"🧑 **你:** {msg.get('content', '')}")
                else:
                    st.write(f"🤖 **AI:** {msg.get('content', '')}")
            else:
                # 处理不是字典的情况
                st.write(f"🤖 **消息:** {str(msg)}")


# 运行页面
if __name__ == "__main__":
    display_dashboard()