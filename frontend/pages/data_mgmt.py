import asyncio
import uuid
from typing import Dict, List, Optional

import streamlit as st

from frontend.streamlit_app import (
    API_BASE_URL,
    create_item,
    delete_item,
    fetch_items,
    initialize_session_state,
    update_item,
)


def data_management_page():
    """Data Management Page for CRUD operations"""
    st.title("数据管理")
    
    # Initialize session state
    initialize_session_state()
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["查看数据", "添加数据", "编辑/删除数据"])
    
    with tab1:
        view_items()
    
    with tab2:
        add_item_form()
    
    with tab3:
        edit_delete_items()


def view_items():
    """Display all items in a table"""
    st.subheader("所有数据项")
    
    # Refresh button
    if st.button("刷新数据", key="refresh_items"):
        st.session_state.items = []
    
    # Fetch items if not already in session state
    if not st.session_state.items:
        with st.spinner("加载数据中..."):
            items, total = asyncio.run(fetch_items())
            st.session_state.items = items
    
    # Display items in a table
    if st.session_state.items:
        # Convert to DataFrame for better display
        items_data = [
            {
                "ID": item["id"],
                "名称": item["name"],
                "描述": item["description"] or "",
                "创建时间": item["created_at"],
                "更新时间": item["updated_at"],
            }
            for item in st.session_state.items
        ]
        
        st.dataframe(items_data, use_container_width=True)
        st.info(f"共 {len(st.session_state.items)} 条记录")
    else:
        st.info("暂无数据")


def add_item_form():
    """Form for adding a new item"""
    st.subheader("添加新数据项")
    
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
                        # Clear form
                        st.session_state.add_name = ""
                        st.session_state.add_description = ""
                        # Refresh items list
                        st.session_state.items = []


def edit_delete_items():
    """Interface for editing and deleting items"""
    st.subheader("编辑/删除数据项")
    
    # Fetch items if not already in session state
    if not st.session_state.items:
        with st.spinner("加载数据中..."):
            items, total = asyncio.run(fetch_items())
            st.session_state.items = items
    
    if not st.session_state.items:
        st.info("暂无数据可编辑")
        return
    
    # Select an item to edit/delete
    item_options = {f"{item['name']} (ID: {item['id']})": item for item in st.session_state.items}
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