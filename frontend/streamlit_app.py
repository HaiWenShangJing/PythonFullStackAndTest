"""
主Streamlit应用入口
"""
import asyncio
import sys
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# 获取绝对路径
current_file = Path(__file__).resolve()
frontend_dir = current_file.parent
project_root = frontend_dir.parent
print(f"当前文件: {current_file}")
print(f"前端目录: {frontend_dir}")
print(f"项目根目录: {project_root}")

# 确保前端模块可导入
sys.path.insert(0, str(project_root))
print(f"Python路径: {sys.path}")

# 加载环境变量
ENV_FILE = project_root / ".env"
print(f"加载环境变量从: {ENV_FILE}")
load_dotenv(dotenv_path=ENV_FILE)

# 导入工具和组件
try:
    from frontend.utils.styles import get_chat_css
    from frontend.utils.session import (
        initialize_session_state, 
        initialize_chat_history
    )
    from frontend.utils.api import check_api_connection, run_async, API_BASE_URL
    print("成功导入frontend模块")
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)


def main():
    """主Streamlit应用"""
    st.set_page_config(
        page_title="Full-Stack AI CRUD App",
        page_icon="🤖",
        layout="wide",
    )
    
    # 添加自定义CSS
    st.markdown(get_chat_css(), unsafe_allow_html=True)
    
    # 初始化会话状态
    initialize_session_state()
    
    # 添加状态指示器，在侧边栏显示
    with st.sidebar:
        st.title("导航")
        status_container = st.empty()
        
        # 显示当前API连接状态
        api_status = run_async(check_api_connection)
        
        if api_status:
            status_container.success("✅ API 已连接")
        else:
            status_container.error("❌ API 连接失败")
            st.error(f"无法连接到API: {API_BASE_URL}")
            st.info("请确保后端服务器正在运行。")
            st.code("docker-compose up -d")
            
        page = st.radio(
            "Go to",
            ["Dashboard", "Data Management", "AI Assistant"],
        )
        
        st.divider()
        st.write("Session ID:", st.session_state.session_id)
        
        # 刷新数据按钮
        if st.button("刷新数据"):
            st.session_state.data_refresh_requested = True
            st.rerun()
    
    # 显示选择的页面
    if page == "Dashboard":
        import frontend.pages.dashboard as dashboard
        dashboard.display_dashboard()
    elif page == "Data Management":
        import frontend.pages.data_mgmt as data_mgmt
        data_mgmt.display_data_management()
    elif page == "AI Assistant":
        import frontend.pages.ai_chat as ai_chat
        ai_chat.ai_chat_page()


if __name__ == "__main__":
    main()