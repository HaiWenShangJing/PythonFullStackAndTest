"""
数据管理页面
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

import asyncio
import streamlit as st
import httpx

from frontend.utils.session import initialize_session_state
from frontend.utils.api import API_BASE_URL


async def fetch_items():
    """从API获取项目"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/items")
        if response.status_code == 200:
            data = response.json()
            return data["items"], data["total"]
        else:
            st.error(f"获取项目错误: {response.text}")
            return [], 0


async def create_item(name, description=None):
    """通过API创建新项目"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/items",
            json={"name": name, "description": description},
        )
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"创建项目错误: {response.text}")
            return None


async def update_item(item_id, name=None, description=None):
    """通过API更新项目"""
    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{API_BASE_URL}/items/{item_id}",
            json=data,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"更新项目错误: {response.text}")
            return None


async def delete_item(item_id):
    """通过API删除项目"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE_URL}/items/{item_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"删除项目错误: {response.text}")
            return False


def display_data_management():
    """显示数据管理页面"""
    st.title("数据管理")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 修复items问题
    temp_items = st.session_state.get("items")
    if callable(temp_items) or not isinstance(temp_items, list):
        temp_items = []
        st.session_state["items"] = temp_items
    
    # 如果刚进入页面且没有数据，自动获取
    if not temp_items and not hasattr(st.session_state, "data_loaded"):
        with st.spinner("加载数据中..."):
            try:
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
                st.session_state.data_loaded = True
            except Exception as e:
                st.error(f"加载数据失败: {e}")
                st.session_state.items = []
    
    # 添加新项目表单
    with st.expander("添加新项目", expanded=False):
        with st.form("new_item_form"):
            name = st.text_input("名称")
            description = st.text_area("描述")
            submit_button = st.form_submit_button("创建项目")
            
            if submit_button and name:
                st.session_state.form_submitted = True
                st.session_state.form_data = {"name": name, "description": description}
                st.rerun()
    
    # 处理表单提交 (重新运行后，避免streamlit表单问题)
    if hasattr(st.session_state, "form_submitted") and st.session_state.form_submitted:
        with st.spinner("创建项目中..."):
            result = asyncio.run(create_item(
                st.session_state.form_data["name"],
                st.session_state.form_data["description"]
            ))
            if result:
                st.success("项目创建成功!")
                # 刷新项目列表
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
        
        # 重置表单状态
        del st.session_state.form_submitted
        del st.session_state.form_data
    
    # 显示项目表格
    st.subheader("项目列表")
    
    # 获取最新的项目列表
    temp_items = st.session_state.items
    
    if not temp_items:
        st.info("没有找到项目。")
    else:
        # 创建用于显示的数据框
        df_data = []
        for item in temp_items:
            df_data.append({
                "ID": item["id"],
                "名称": item["name"],
                "描述": item["description"] or "",
                "创建时间": item["created_at"].split("T")[0],  # 只显示日期部分
            })
        
        # 显示为数据框
        st.dataframe(df_data, use_container_width=True)
        
        # 项目操作
        st.subheader("项目操作")
        
        # 选择一个项目
        item_names = [f"{item['name']} ({item['id'][:8]}...)" for item in temp_items]
        selected_item_idx = st.selectbox("选择一个项目", range(len(item_names)), format_func=lambda i: item_names[i])
        selected_item = temp_items[selected_item_idx]
        
        # 操作选项卡
        tab1, tab2 = st.tabs(["编辑", "删除"])
        
        with tab1:
            with st.form("edit_item_form"):
                edit_name = st.text_input("名称", value=selected_item["name"])
                edit_description = st.text_area("描述", value=selected_item["description"] or "")
                update_button = st.form_submit_button("更新项目")
                
                if update_button:
                    st.session_state.update_submitted = True
                    st.session_state.update_data = {
                        "id": selected_item["id"],
                        "name": edit_name,
                        "description": edit_description
                    }
                    st.rerun()
        
        with tab2:
            st.write("确定要删除这个项目吗?")
            if st.button(f"删除 {selected_item['name']}", type="primary"):
                st.session_state.delete_id = selected_item["id"]
                st.rerun()
    
    # 处理更新提交
    if hasattr(st.session_state, "update_submitted") and st.session_state.update_submitted:
        with st.spinner("更新项目中..."):
            result = asyncio.run(update_item(
                st.session_state.update_data["id"], 
                st.session_state.update_data["name"],
                st.session_state.update_data["description"]
            ))
            if result:
                st.success("项目更新成功!")
                # 刷新项目列表
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
        
        # 重置更新状态
        del st.session_state.update_submitted
        del st.session_state.update_data
    
    # 处理删除提交
    if hasattr(st.session_state, "delete_id"):
        with st.spinner("删除项目中..."):
            result = asyncio.run(delete_item(st.session_state.delete_id))
            if result:
                st.success("项目删除成功!")
                # 刷新项目列表
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
        
        # 重置删除状态
        del st.session_state.delete_id


# 运行页面
if __name__ == "__main__":
    display_data_management()