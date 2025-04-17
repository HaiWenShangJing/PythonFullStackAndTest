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


def data_management_page():
    """Data Management Page for CRUD operations"""
    st.title("数据管理")
    
    # Initialize session state
    initialize_session_state()
    if not hasattr(st.session_state, "items") or not isinstance(st.session_state.items, list):
        st.session_state.items = []
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["查看数据", "添加数据", "编辑/删除数据"])
    
    with tab1:
        view_items()
    
    with tab2:
        add_item_form()
    
    with tab3:
        edit_delete_items()


def view_items():
    """Display items in a table format"""
    
    # 使用临时变量并检查items类型
    temp_items = st.session_state.get("items")
    
    # 如果items是方法或者不是列表，重置为空列表
    if callable(temp_items) or not isinstance(temp_items, list):
        temp_items = []
        # 同时更新session state
        st.session_state["items"] = temp_items
    
    # 现在使用temp_items而不是直接访问session_state
    if not temp_items:
        st.info("No items found. Create some using the form above.")
        return
    
    # 使用临时变量创建数据
    try:
        items_data = []
        for item in temp_items:
            items_data.append({
                "ID": item["id"],
                "Name": item["name"],
                "Description": item["description"] or "",
                "Created": item["created_at"]
            })
        
        # 创建数据框并显示
        st.dataframe(items_data, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying items: {str(e)}")
        # 如果出错，重置items为空列表
        st.session_state["items"] = []


def add_item_form():
    """Form for adding a new item"""
    st.subheader("添加新数据项")
    
    # Initialize form state if needed
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    
    # Reset form if previously submitted
    if st.session_state.form_submitted:
        # Use this approach to clear the form fields through rerun
        st.session_state.form_submitted = False
        st.session_state.add_name = ""
        st.session_state.add_description = ""
        st.rerun()
    
    with st.form("add_item_form"):
        name = st.text_input("名称", key="add_name")
        description = st.text_area("描述", key="add_description")
        
        submitted = st.form_submit_button("添加")
        
        if submitted:
            if not name:
                st.error("名称不能为空")
            else:
                with st.spinner("添加中..."):
                    new_item = asyncio.run(create_item(name, description))
                    
                    if new_item:
                        st.success(f"成功添加: {name}")
                        # Set flag to clear form on next render
                        st.session_state.form_submitted = True
                        # Refresh items list
                        st.session_state.items = []
                        st.rerun()


def edit_delete_items():
    """Interface for editing and deleting items"""
    st.subheader("编辑/删除数据项")
    
    # 使用临时变量并检查类型
    temp_items = st.session_state.get("items")
    
    # 如果items是方法或者不是列表，重置为空列表
    if callable(temp_items) or not isinstance(temp_items, list):
        temp_items = []
        # 同时更新session state
        st.session_state["items"] = temp_items
    
    # Fetch items if needed
    if not temp_items:
        with st.spinner("加载数据中..."):
            items, total = asyncio.run(fetch_items())
            temp_items = items if isinstance(items, list) else []
            st.session_state["items"] = temp_items
    
    if not temp_items:
        st.info("暂无数据可编辑")
        return
    
    # 使用临时变量而非直接访问session_state
    item_options = {f"{item['name']} (ID: {item['id']})": item for item in temp_items}
    
    # Select an item to edit/delete
    selected_item_key = st.selectbox(
        "选择要编辑/删除的数据项",
        options=list(item_options.keys()),
        key="edit_select"
    )
    
    if selected_item_key:
        selected_item = item_options[selected_item_key]
        
        # Display current values
        st.text(f"当前名称: {selected_item['name']}")
        st.text(f"当前描述: {selected_item['description'] or '无'}")
        
        # Edit form
        with st.form("edit_item_form"):
            new_name = st.text_input("新名称", value=selected_item['name'], key="edit_name")
            new_description = st.text_area(
                "新描述", 
                value=selected_item['description'] or "", 
                key="edit_description"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                update_button = st.form_submit_button("更新")
            with col2:
                delete_button = st.form_submit_button("删除", type="primary")
            
            if update_button:
                if not new_name:
                    st.error("名称不能为空")
                else:
                    with st.spinner("更新中..."):
                        updated_item = asyncio.run(
                            update_item(
                                selected_item['id'],
                                new_name,
                                new_description
                            )
                        )
                        
                        if updated_item:
                            st.success(f"成功更新: {new_name}")
                            # Refresh items list
                            st.session_state.items = []
            
            if delete_button:
                with st.spinner("删除中..."):
                    deleted_item = asyncio.run(delete_item(selected_item['id']))
                    
                    if deleted_item:
                        st.success(f"成功删除: {selected_item['name']}")
                        # Refresh items list
                        st.session_state.items = []


# Run the page
if __name__ == "__main__":
    data_management_page()