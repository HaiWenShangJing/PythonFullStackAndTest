"""
数据管理页面
"""
import os
import sys
from pathlib import Path
import logging

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
import json

from frontend.utils.session import initialize_session_state
from frontend.utils.api import API_BASE_URL

# Get logger instance
logger = logging.getLogger(__name__)

async def fetch_items():
    """从API获取项目. Returns (list | None, error_message | None)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/items")
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            items = data.get("items") # Safely get items
            
            # Validate that items is a list
            if items is None or not isinstance(items, list):
                logger.error(f"API response format error: 'items' key missing or not a list. Response: {data}")
                return None, "API response format error: 'items' missing or not a list."
                
            # Return (data, None) on success
            return items, None 
    except httpx.HTTPStatusError as e:
        error_msg = f"API Error ({e.response.status_code}): {e.response.text[:200]}" # Limit error text length
        logger.error(f"fetch_items failed: {error_msg}", exc_info=True)
        return None, error_msg # Return (None, error_message)
    except httpx.RequestError as e:
        error_msg = f"Request Error: Failed to connect to API at {API_BASE_URL}. Details: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg # Return (None, error_message)
    except json.JSONDecodeError as e:
        error_msg = f"JSON Decode Error: Invalid response from API. Details: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg # Return (None, error_message)
    except Exception as e:
        error_msg = f"Unexpected error fetching items: {type(e).__name__}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg # Return (None, error_message)


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
    
    # Use a more specific key: data_mgmt_items
    if "data_mgmt_items" not in st.session_state or not isinstance(st.session_state.data_mgmt_items, list):
        st.session_state.data_mgmt_items = [] # Initialize/reset as empty list

    # Fetch items if the list is empty or refresh requested
    refresh_needed = not st.session_state.data_mgmt_items or st.session_state.get("data_refresh_requested", False)
    
    if refresh_needed:
         st.session_state.data_refresh_requested = False # Reset flag
         with st.spinner("加载项目列表中..."):
            items_list, error_msg = asyncio.run(fetch_items())
            
            # Check if there was an error message
            if error_msg:
                st.error(f"加载项目失败: {error_msg}")
                st.session_state.data_mgmt_items = [] 
            elif items_list is not None: # Check if list is not None (means success)
                 # Assign the fetched list on success
                st.session_state.data_mgmt_items = items_list 
            else:
                 # Handle unexpected case where both are None (shouldn't happen with new fetch_items)
                 st.error("加载项目时发生未知错误。")
                 logger.error("fetch_items returned (None, None) unexpectedly.")
                 st.session_state.data_mgmt_items = []

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
    
    # 处理表单提交 
    if hasattr(st.session_state, "form_submitted") and st.session_state.form_submitted:
        with st.spinner("创建项目中..."):
            result = asyncio.run(create_item(
                st.session_state.form_data["name"],
                st.session_state.form_data["description"]
            ))
            if result:
                st.success("项目创建成功!")
                # Refresh item list - use new fetch_items signature
                refreshed_items, refresh_error = asyncio.run(fetch_items())
                if refresh_error:
                     st.warning(f"创建成功，但刷新列表失败: {refresh_error}")
                elif refreshed_items is not None:
                     st.session_state.data_mgmt_items = refreshed_items
        
        # Reset form state
        del st.session_state.form_submitted
        del st.session_state.form_data
    
    # 显示项目表格
    st.subheader("项目列表")
    
    # Get items using the new key
    temp_items = st.session_state.data_mgmt_items 
    
    # --- Explicit Type Check --- 
    if not isinstance(temp_items, list):
        st.error(f"Internal Error: Expected temp_items to be a list, but got {type(temp_items)}. Resetting.")
        logger.error(f"Data Mgmt Error: Expected list for temp_items, got {type(temp_items)}. Value: {temp_items}") # Log the problematic value
        temp_items = []
        st.session_state.data_mgmt_items = [] # Also reset state

    if not temp_items:
        st.info("没有找到项目。")
    else:
        # Create dataframe for display
        df_data = []
        for item in temp_items: # Iterate (should be safe now)
            # Ensure item is a dict before accessing keys
            if isinstance(item, dict):
                 df_data.append({
                     "ID": item.get("id", "N/A"),
                     "名称": item.get("name", "N/A"),
                     "描述": item.get("description") or "",
                     # Use .get() for created_at and handle potential absence/format issues
                     "创建时间": item.get("created_at", "").split("T")[0] if isinstance(item.get("created_at"), str) else "", 
                 })
            else:
                 st.warning(f"Skipping invalid item in list: {item}") # Log invalid item
                 logger.warning(f"Data Mgmt Warning: Skipped invalid item type {type(item)} in list: {item}")
        
        # Display dataframe
        st.dataframe(df_data, use_container_width=True)
        
        # Item operations
        st.subheader("项目操作")
        
        # Select item (check if temp_items is still valid after potential reset)
        if temp_items: # Add check here
             item_names = [f"{item.get('name', 'Invalid Item')} ({item.get('id', 'N/A')[:8]}...)" for item in temp_items if isinstance(item, dict)]
             if not item_names:
                 st.warning("No valid items available for selection.")
             else:
                 # Filter temp_items to only include valid dicts for indexing
                 valid_items = [item for item in temp_items if isinstance(item, dict)]
                 selected_item_idx = st.selectbox("选择一个项目", range(len(item_names)), format_func=lambda i: item_names[i])
                 # Ensure index is valid before accessing
                 if selected_item_idx < len(valid_items):
                     selected_item = valid_items[selected_item_idx]
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
                 else:
                      st.error("Selected item index out of bounds after filtering.")
        else:
             st.info("No items available to perform operations.")

    # --- Handle update/delete submissions (use new session state key) --- 
    if hasattr(st.session_state, "update_submitted") and st.session_state.update_submitted:
        with st.spinner("更新项目中..."):
            result = asyncio.run(update_item(
                st.session_state.update_data["id"], 
                st.session_state.update_data["name"],
                st.session_state.update_data["description"]
            ))
            if result:
                st.success("项目更新成功!")
                # Refresh item list - use new fetch_items signature
                refreshed_items, refresh_error = asyncio.run(fetch_items())
                if refresh_error:
                     st.warning(f"更新成功，但刷新列表失败: {refresh_error}")
                elif refreshed_items is not None:
                     st.session_state.data_mgmt_items = refreshed_items
        
        # Reset update state
        del st.session_state.update_submitted
        del st.session_state.update_data
    
    if hasattr(st.session_state, "delete_id"):
        with st.spinner("删除项目中..."):
            result = asyncio.run(delete_item(st.session_state.delete_id))
            if result:
                st.success("项目删除成功!")
                # Refresh item list - use new fetch_items signature
                refreshed_items, refresh_error = asyncio.run(fetch_items())
                if refresh_error:
                     st.warning(f"删除成功，但刷新列表失败: {refresh_error}")
                elif refreshed_items is not None:
                     st.session_state.data_mgmt_items = refreshed_items
        
        # Reset delete state
        del st.session_state.delete_id


# 运行页面
if __name__ == "__main__":
    # Need logger setup if run standalone
    # import logging
    # logger = logging.getLogger(__name__)
    # ... (add handler etc.)
    display_data_management()